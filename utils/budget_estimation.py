from tools.accommodations.apis import Accommodations
from tools.flights.apis import Flights
from tools.restaurants.apis import Restaurants
from tools.googleDistanceMatrix.apis import GoogleDistanceMatrix
from tools.attractions.apis import Attractions
from tools.events.apis import Events
import pandas as pd
import json

hotel = Accommodations()
flight = Flights()
flight.load_db()
restaurant = Restaurants()
distanceMatrix = GoogleDistanceMatrix()
attraction = Attractions()
event = Events()


def estimate_budget(data, mode):
    """
    Estimate the budget based on the mode (lowest, highest, average) for flight or restaurant data.
    """
    if mode == "lowest":
        return min(data)
    elif mode == "highest":
        return max(data)
    elif mode == "average":
        # filter the nan values
        data = [x for x in data if str(x) != 'nan']
        return sum(data) / len(data)
    
def estimate_budget_hotel(data, mode):
    """
    Estimate the budget based on the mode (lowest, highest, average) for hotel.
    The 'data' is expected to be a list of dictionaries containing a key 'price' with the value in the format '$<amount>'.
    """
    # Extract the numeric values from the price strings
    prices = []
    for entry in data:
        # print(type(entry),entry)
        entry = entry.strip().replace("'", '"').replace("None", "null")
        # print(type(entry),entry)
        entry=json.loads(entry)
        if "price" in entry:
            price_str = entry["price"]
            # Remove '$' and convert the remaining part to a float
            try:
                price_value = float(price_str.replace('$', '').replace(',', ''))
                prices.append(price_value)
            except ValueError:
                continue  # Skip if price conversion fails

    # If no valid prices are found, return None
    if not prices:
        return None

    # Estimate based on the mode
    if mode == "lowest":
        return min(prices)
    elif mode == "highest":
        return max(prices)
    elif mode == "average":
        return sum(prices) / len(prices)
    else:
        raise ValueError("Invalid mode specified. Use 'lowest', 'highest', or 'average'.")


def budget_calc(org, dest, days, date:list , people_number=None, local_constraint = None):
    """
    Calculate the estimated budget for all three modes: lowest, highest, average.
    grain: city, state
    """
    if days == 3:
        grain = "city"
    elif days in [5,7]:
        grain = "state"

    if grain not in ["city", "state"]:
        raise ValueError("grain must be one of city, state")
    
    # Multipliers based on days
    multipliers = {
        3: {"flight": 2, "hotel": 3, "restaurant": 9},
        5: {"flight": 3, "hotel": 5, "restaurant": 15},
        7: {"flight": 4, "hotel": 7, "restaurant": 21}
    }
    
    if grain == "city":
        hotel_data = hotel.run(dest)
        restaurant_data = restaurant.run(dest)
        attraction_data = attraction.run(dest)
        event_data = event.run(dest,date)
        flight_data = flight.data[(flight.data["DestCityName"] == dest) & (flight.data["OriginCityName"] == org)]
        # print("checkpt-1")


    elif grain == "state":
        city_set = open('/home/mtech/ATP_database/background/citySet_with_states_140.txt').read().strip().split('\n')
        
        all_hotel_data = []
        all_restaurant_data = []
        all_flight_data = []
        all_attraction_data = []
        all_event_data = []
        city_counter = 0
        
        for city in city_set:
            if dest == city.split('\t')[1]:
                candidate_city = city.split('\t')[0]
                
                # Fetch data for the current city
                current_hotel_data = hotel.run(candidate_city)
                current_restaurant_data = restaurant.run(candidate_city)
                current_flight_data = flight.data[(flight.data["DestCityName"] == candidate_city) & (flight.data["OriginCityName"] == org)]
                current_attraction_data = attraction.run(candidate_city)
                current_event_data = event.run(candidate_city,date)

                # Append the dataframes to the lists
                # all_hotel_data.append(current_hotel_data)
                all_flight_data.append(current_flight_data)
                if (type(current_restaurant_data)!=type("str") and type(current_hotel_data)!=type("str")
                and type(current_attraction_data)!=type("str") and type(current_event_data)!=type("str")):
                    all_restaurant_data.append(current_restaurant_data)
                    all_hotel_data.append(current_hotel_data)
                    all_attraction_data.append(current_attraction_data)
                    all_event_data.append(current_event_data)
                    city_counter = city_counter + 1
                else:
                    continue
                
                    
        if days == 3:
            if city_counter < 1:
                raise ValueError(f"Less number of available cities which has all constraints")
        elif days == 5:
            if city_counter < 2:
                raise ValueError(f"Less number of available cities which has all constraints")
        elif days == 7:
            if city_counter < 3:
                raise ValueError(f"Less number of available cities which has all constraints")
        
        # Use concat to combine all dataframes in the lists
        hotel_data = pd.concat(all_hotel_data, axis=0)
        restaurant_data = pd.concat(all_restaurant_data, axis=0)
        flight_data = pd.concat(all_flight_data, axis=0)
        attraction_data = pd.concat(all_attraction_data, axis=0)
        event_data = pd.concat(all_event_data, axis=0)
        # flight_data should be in the range of supported date
        flight_data = flight_data[flight_data['FlightDate'].isin(date)]

    if people_number:
        hotel_data = hotel_data[hotel_data['max_occupancy'] >= people_number]
        # print("checkpt-2")

    if local_constraint:

        if local_constraint['transportation'] == 'no self-driving':
            if grain == "city":
                if len(flight_data[flight_data['FlightDate'] == date[0]]) < 2:
                    raise ValueError("No flight data available for the given constraints.")
            elif grain == "state":
                if len(flight_data[flight_data['FlightDate'] == date[0]]) < 10:
                    raise ValueError("No flight data available for the given constraints.")
                
        elif local_constraint['transportation'] == 'no flight':
            if len(flight_data[flight_data['FlightDate'] == date[0]]) < 2 or flight_data.iloc[0]['Distance'] > 800:
                raise ValueError("Impossible")
            
        # if local_constraint['flgiht time']:
        #     if local_constraint['flgiht time'] == 'morning':
        #         flight_data = flight_data[flight_data['DepTime'] < '12:00']
        #     elif local_constraint['flgiht time'] == 'afternoon':
        #         flight_data = flight_data[(flight_data['DepTime'] >= '12:00') & (flight_data['DepTime'] < '18:00')]
        #     elif local_constraint['flgiht time'] == 'evening':
        #         flight_data = flight_data[flight_data['DepTime'] >= '18:00']

        if local_constraint['room type']:
            if local_constraint['room type'] == 'shared room':
                hotel_data = hotel_data[hotel_data['roomType'] == 'shared_room']
            elif local_constraint['room type'] == 'not shared room':
                hotel_data = hotel_data[(hotel_data['roomType'] == 'private_room') | (hotel_data['roomType'] == 'entire_home')]
            elif local_constraint['room type'] == 'private room':
                hotel_data = hotel_data[hotel_data['roomType'] == 'private_room']
            elif local_constraint['room type'] == 'entire room':
                hotel_data = hotel_data[hotel_data['roomType'] == 'entire_home']

            if days == 3:
                if type(hotel_data)==type("str") or len(hotel_data) < 3:
                    raise ValueError("No hotel data available for the given constraints.")
            elif days == 5:
                if type(hotel_data)==type("str") or len(hotel_data) < 5:
                    raise ValueError("No hotel data available for the given constraints.")
            elif days == 7:
                if type(hotel_data)==type("str") or len(hotel_data) < 7:
                    raise ValueError("No hotel data available for the given constraints.")
        
        if local_constraint['house rule']:
            if local_constraint['house rule'] == 'parties':
                # the house rule should not contain 'parties'
                hotel_data = hotel_data[~hotel_data['house_rules'].str.contains('No parties')]
            elif local_constraint['house rule'] == 'smoking':
                hotel_data = hotel_data[~hotel_data['house_rules'].str.contains('No smoking')]
            elif local_constraint['house rule'] == 'children under 10':
                hotel_data = hotel_data[~hotel_data['house_rules'].str.contains('No children under 10')]
            elif local_constraint['house rule'] == 'pets':
                hotel_data = hotel_data[~hotel_data['house_rules'].str.contains('No pets')]
            elif local_constraint['house rule'] == 'visitors':
                hotel_data = hotel_data[~hotel_data['house_rules'].str.contains('No visitors')]
        
            if days == 3:
                if type(hotel_data)==type("str") or len(hotel_data) < 3:
                    raise ValueError("No hotel data available for the given constraints.")
            elif days == 5:
                if type(hotel_data)==type("str") or len(hotel_data) < 5:
                    raise ValueError("No hotel data available for the given constraints.")
            elif days == 7:
                if type(hotel_data)==type("str") or len(hotel_data) < 7:
                    raise ValueError("No hotel data available for the given constraints.")

        if local_constraint['event']:
        # Filter based on event type
            event_type = local_constraint['event']
            if event_type == 'Sports':
                event_data = events_data[events_data['segmentName'] == 'Sports']
            elif event_type == 'Arts & Theatre':
                event_data = events_data[events_data['segmentName'] == 'Arts & Theatre']
            elif event_type == 'Film':
                event_data = events_data[events_data['segmentName'] == 'Film']
            elif event_type == 'Music':
                event_data = events_data[events_data['segmentName'] == 'Music']

            # Check if sufficient events are available based on `days`
            if days in [3, 5, 7]:
                if type(event_data)==type("str") or len(event_data) < days:
                    raise ValueError(f"No events available for the given constraints and duration of {days} days.")


        if local_constraint['cuisine']:
            # judge whether the cuisine is in the cuisine list
            # restaurant_data = restaurant_data[restaurant_data['Cuisines'].str.contains('|'.join(local_constraint['cuisine']))]
            try:
                restaurant_data = restaurant_data[restaurant_data['cuisines'].apply(lambda x: any(cuisine in x for cuisine in local_constraint['cuisine']))]
            except:
                raise ValueError(f"No restaurants available for the given constraints")

            if days == 3:
                if len(restaurant_data) < 3:
                    raise ValueError("No restaurant data available for the given constraints.")
            elif days == 5:
                if len(restaurant_data) < 5:
                    raise ValueError("No restaurant data available for the given constraints.")
            elif days == 7:
                if len(restaurant_data) < 7:
                    raise ValueError("No restaurant data available for the given constraints.")

        if local_constraint['attraction']:
            # Filter based on attraction type
            attraction_types = local_constraint['attraction']
            # print(attraction_data)
            try:
                attraction_data = attraction_data[attraction_data['subcategories'].apply(
                    lambda x: any(attraction in x for attraction in attraction_types)
                )]
            except:
                raise ValueError(f"No attraction data available for the given constraints")

            # Check if sufficient attractions are available based on `days`
            if days in [3, 5, 7]:
                if len(attraction_data) < days:
                    raise ValueError(f"No attraction data available for the given constraints and duration of {days} days.")


    # Calculate budgets for all three modes

    budgets = {}
    for mode in ["lowest", "highest", "average"]:
        if local_constraint and local_constraint['transportation'] == 'self driving':
            flight_budget = eval(distanceMatrix.run(org, dest)['cost'].replace("$","")) * multipliers[days]["flight"]
        else:
            # print("checkpt-3")
            flight_budget = estimate_budget(flight_data["Price"].tolist(), mode) * multipliers[days]["flight"]
            

        # print("f_budget:",flight_budget)
        hotel_budget = estimate_budget_hotel(hotel_data["pricing"].tolist(), mode) * multipliers[days]["hotel"]
        # print("checkpt-5")
        # print(type(restaurant_data),len(restaurant_data), restaurant_data)
        try:
            restaurant_budget = estimate_budget(restaurant_data["avg_cost"].tolist(), mode) * multipliers[days]["restaurant"]
        except:
            raise ValueError("No restaurant data available for the constraint s")
        total_budget = flight_budget + hotel_budget + restaurant_budget
        budgets[mode] = total_budget

    return budgets

