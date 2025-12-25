import pandas as pd
import glob
import os
from datetime import datetime, timedelta
import re

def get_weekend_dates(date_scraped_str):
    """
    Replicates logic from booking_scraper.py to identify the target weekend
    """
    scrape_date = datetime.strptime(date_scraped_str, "%Y-%m-%d")
    # 0 = Monday, 4 = Friday
    days_until_friday = (4 - scrape_date.weekday() + 7) % 7
    if days_until_friday == 0:
        days_until_friday = 7
    checkin = scrape_date + timedelta(days=days_until_friday)
    checkout = checkin + timedelta(days=2)
    return checkin, checkout

def parse_price(price_str):
    if pd.isna(price_str): return None
    # Remove $ and commas
    clean = re.sub(r'[^\d.]', '', str(price_str))
    try:
        return float(clean)
    except:
        return None

def parse_event_date(date_str):
    # Expecting formats like "Dec 24" or "Dec 24, 2025"
    try:
        current_year = datetime.now().year
        # Try appending year if missing
        dt = datetime.strptime(f"{date_str} {current_year}", "%b %d %Y")
        return dt
    except:
        return None

def run_analysis():
    print("Loading data...")
    # 1. Load Data
    hotel_files = glob.glob("data/vegas_hotels_*.csv")
    event_files = glob.glob("data/vegas_events_*.csv")
    
    if not hotel_files:
        print("No hotel data found.")
        return
    if not event_files:
        print("No event data found.")
        return

    hotels = pd.concat((pd.read_csv(f) for f in hotel_files), ignore_index=True)
    events = pd.concat((pd.read_csv(f) for f in event_files), ignore_index=True)
    
    # 2. Clean Data
    print("Cleaning data...")
    hotels['price_numeric'] = hotels['price'].apply(parse_price)
    hotels = hotels.dropna(subset=['price_numeric'])
    
    events['parsed_date'] = events['date'].apply(parse_event_date)
    # Create valid date strings (YYYY-MM-DD) for matching
    valid_events = events.dropna(subset=['parsed_date'])
    event_dates_set = set(valid_events['parsed_date'].dt.strftime("%Y-%m-%d"))
    
    print(f"Loaded {len(hotels)} hotel records and {len(valid_events)} valid event records.")

    # 3. Analysis: Check for events during stay
    results = []
    
    for _, row in hotels.iterrows():
        # Determine the stay window for this price
        checkin_dt, checkout_dt = get_weekend_dates(row['date_scraped'])
        
        # We consider an event "relevant" if it happens on Friday or Saturday of the stay
        fri_str = checkin_dt.strftime("%Y-%m-%d")
        sat_str = (checkin_dt + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Find events on these days
        relevant_events = []
        
        # This simple check allows for duplicates if we have multiple event rows for same day/event
        # Ideally we'd filter unique events.
        
        friday_events = valid_events[valid_events['parsed_date'].dt.strftime("%Y-%m-%d") == fri_str]
        saturday_events = valid_events[valid_events['parsed_date'].dt.strftime("%Y-%m-%d") == sat_str]
        
        event_count = len(friday_events) + len(saturday_events)
        
        results.append({
            'hotel': row['name'],
            'price': row['price_numeric'],
            'rating': row.get('rating'),
            'distance': row.get('distance'),
            'checkin_date': fri_str,
            'event_count': event_count,
            'event_names': "; ".join(friday_events['name'].tolist() + saturday_events['name'].tolist())
        })
        
    df_res = pd.DataFrame(results)
    
    # 4. Output Results
    print("\n--- Average Price by Event Count ---")
    if not df_res.empty:
        summary = df_res.groupby('event_count')['price'].mean().reset_index()
        summary.columns = ['Events During Stay', 'Average Price']
        print(summary)
        
        output_file = "data/analysis_summary.csv"
        df_res.to_csv(output_file, index=False)
        print(f"\nDetailed analysis saved to {output_file}")
    else:
        print("No analysis generated (empty result set).")

if __name__ == "__main__":
    run_analysis()
