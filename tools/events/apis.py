import pandas as pd
from pandas import DataFrame
from typing import Optional
# from utils.func import extract_before_parenthesis
from datetime import datetime

class Events:
    def __init__(self, path='/home/mtech/ATP_database/events/events_cleaned.csv'):
        self.path = path
        # Read CSV and preprocess dates
        self.data = pd.read_csv(self.path)[['name', 'url', 'dateTitle', 'streetAddress', 'segmentName', 'city']].dropna(
            subset=['name', 'url', 'dateTitle', 'streetAddress', 'segmentName', 'city']
        )

        # Keep only rows with valid date formats (dd-mm-yyyy)
        self.data = self.data[self.data['dateTitle'].str.match(r'^\d{2}-\d{2}-\d{4}$', na=False)]

        # Convert date format in the CSV to datetime for filtering
        self.data['dateTitle'] = pd.to_datetime(self.data['dateTitle'], format='%d-%m-%Y')
        print("Events loaded.")

    def load_db(self):
        self.data = pd.read_csv(self.path)

    def run(self, city: str, date_range: list) -> pd.DataFrame:
        """
        Search for Events by city and date range.
        Parameters:
            city: City to filter events.
            date_range: List of two strings in 'yyyy-mm-dd' format representing start and end dates.
        Returns:
            Filtered DataFrame with events in the city within the given date range.
        """
        # Parse the input date range
        start_date = datetime.strptime(date_range[0], '%Y-%m-%d')
        end_date = datetime.strptime(date_range[-1], '%Y-%m-%d')
        
        # Filter by city and date range
        results = self.data[
            (self.data['city'] == city) &
            (self.data['dateTitle'] >= start_date) &
            (self.data['dateTitle'] <= end_date)
        ]
        
        # Reset index for cleaner output
        results = results.reset_index(drop=True)
        
        if len(results) == 0:
            return "There are no events in this city for the given date range."
        
        return results
      
    def run_for_annotation(self, city: str) -> DataFrame:
        """Search for Accommodations by city."""
        results = self.data[self.data["city"] == extract_before_parenthesis(city)]
        # The results should show the index
        results = results.reset_index(drop=True)
        return results
