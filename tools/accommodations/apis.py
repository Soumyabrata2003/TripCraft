import pandas as pd
from pandas import DataFrame
from typing import Optional
# from utils.func import extract_before_parenthesis


class Accommodations:
    def __init__(self, path='/home/mtech/ATP_database/accommodation/cleaned_listings_final_v2.csv'):
        self.path = path
        self.data = pd.read_csv(self.path).dropna()[['name','pricing','roomType', 'house_rules', 'max_occupancy', 'rating', 'City']]
        print("Accommodations loaded.")

    def load_db(self):
        self.data = pd.read_csv(self.path).dropna()

    def run(self,
            city: str,
            ) -> DataFrame:
        """Search for accommodations by city."""
        results = self.data[self.data["City"] == city]
        if len(results) == 0:
            return "There is no attraction in this city."
        
        return results
    
    def run_for_annotation(self,
            city: str,
            ) -> DataFrame:
        """Search for accommodations by city."""
        results = self.data[self.data["City"] == extract_before_parenthesis(city)]
        return results