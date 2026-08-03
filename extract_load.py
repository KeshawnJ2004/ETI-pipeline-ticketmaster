import os
import pandas as pd
from dotenv import load_dotenv 
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from typing import Optional
import requests

# 1. Load Environment Variables
load_dotenv()

CLIENT_ID = os.getenv("TICKET_MASTER_API_KEY")
CLIENT_SECRET = os.getenv("TICKET_MASTER_API_SECRET")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# 2. Pydantic Data Validation Schema
class EventSchema(BaseModel):
    event_id: str
    name: str
    local_date: str                   
    local_time: Optional[str] = None  
    city: Optional[str] = None
    venue_name: Optional[str] = None
    min_price: Optional[float] = None  
    max_price: Optional[float] = None 


# 3. GET Request --> All events in a 25 mile radius of Baltimore
url = "https://app.ticketmaster.com/discovery/v2/events.json" 
params = {
    "apikey": CLIENT_ID,          
    "city": "Baltimore", 
    "radius": "10",
    "unit": "miles",
    "size": 50
}

r = requests.get(url, params=params, timeout=5)
print(r.status_code)
print("\n Response received. Printing data...")
data = r.json()

# 4. Filtering data --> turning raw data into useful data
events = data.get("_embedded", {}).get("events", [])
numberOfEvents = len(events)
print(f"Number of events: {numberOfEvents}")

# 5. Extract, Validate with Pydantic, & Load to Pandas
validated_records = []

for event in events:

    # Prices
    price_ranges = event.get("priceRanges", [{}])
    min_price = price_ranges[0].get("min") if price_ranges else None
    max_price = price_ranges[0].get("max") if price_ranges else None
    
    # Venues & City
    venues = event.get("_embedded", {}).get("venues", [{}])
    venue_name = venues[0].get("name") if venues else None
    city_name = venues[0].get("city", {}).get("name", "Baltimore") if venues else "Baltimore"
    
    # Dates & Times
    start_dates = event.get("dates", {}).get("start", {})
    local_date = start_dates.get("localDate")
    local_time = start_dates.get("localTime")

    # Construct intermediate dict
    raw_dict = {
        "event_id": event.get("id"),
        "name": event.get("name"),
        "local_date": local_date,
        "local_time": local_time,
        "city": city_name,
        "venue_name": venue_name,
        "min_price": min_price,
        "max_price": max_price,
    }
    
    # Validate w/ Pydantic
    validated_event = EventSchema(**raw_dict)
    
    # Push validated data to list
    validated_records.append(validated_event.model_dump())


# 6. Convert to Pandas DataFrame

df = pd.DataFrame(validated_records)

df["ingested_at"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

print("\n================ CLEAN TRANSFORMED DATAFRAME ================")
print(df.head(50))
print("\n")

# 7. Push to postgreSQL db
db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}" # "DB Domain : // Username : Password @ Host : Port / DB Name"
engine = create_engine(db_url) # Establish connection using engine
df.to_sql(name="ticketmaster_events", con=engine, if_exists="replace", index=False) # Push pandas dataframe w/ table into postgresql database

print("\nSUCCESS: Data successfully loaded into PostgreSQL table 'ticketmaster_events'!")