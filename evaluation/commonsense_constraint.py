from utils.func import get_valid_name_city,extract_before_parenthesis,extract_numbers_from_filenames
from tools.flights.apis import Flights
from tools.accommodations.apis import Accommodations
from tools.restaurants.apis import Restaurants
from tools.googleDistanceMatrix.apis import GoogleDistanceMatrix
from tools.attractions.apis import Attractions
from tools.events.apis import Events
import math
import json
import re   
import os
import sys
from tqdm import tqdm
import argparse
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

flight = Flights()
accommodation = Accommodations()
restaurants = Restaurants()
googleDistanceMatrix = GoogleDistanceMatrix()
attractions = Attractions()
events = Events()
pois = pd.read_csv('/home/soumya/ATP_database/all_poi_nearest_stops.csv')

city_state_set = open('/home/soumya/ATP_database/background/citySet_with_states_140.txt','r').read().split('\n')
city_state_map = {x:y for x,y in [unit.split('\t') for unit in city_state_set]}


def load_line_json_data(filename):
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f.read().strip().split('\n'):
            unit = json.loads(line)
            data.append(unit)
    return data


def count_consecutive_values(lst):
    if not lst:
        return []

    result = []
    current_string = lst[0]
    count = 1

    for i in range(1, len(lst)):
        if lst[i] == current_string:
            count += 1
        else:
            result.append((current_string, count))
            current_string = lst[i]
            count = 1

    result.append((current_string, count))  # Add the last group of values
    return result


def transportation_match(text: str):

    if 'taxi' in text.lower():
        return 'Taxi'
    
    elif 'self-driving' in text.lower():
        return 'Self-driving'
    
    elif 'flight' in text.lower():
        return 'Flight'


def extract_from_to(text: str):
    """
    Extracts 'A' and 'B' from the format "from A to B" in the given text, with B ending at a comma or the end of the string.
    
    Args:
    - text (str): The input string.
    
    Returns:
    - tuple: A tuple containing 'A' and 'B'. If no match is found, returns (None, None).
    """
    pattern = r"from\s+(.+?)\s+to\s+([^,]+)(?=[,\s]|$)"
    matches = re.search(pattern, text)
    return matches.groups() if matches else (None, None)



def is_valid_city_sequence(city_list):
    """
    Checks if the city sequence is valid. A valid sequence has every city (except the first and last) 
    appearing consecutively, and no city should appear again once its sequence is over.
    
    Args:
    - city_list (list): List of cities.
    
    Returns:
    - bool: True if the sequence is valid, False otherwise.
    """
    
    # If the list has less than 3 cities, it's invalid.
    if len(city_list) < 3:
        return False
    
    # Set to keep track of visited cities
    visited_cities = set()
    
    i = 0
    while i < len(city_list):
        city = city_list[i]
        
        # If the city was already visited, it's invalid.
        if city in visited_cities and (i != 0 and i != len(city_list) - 1):
            return False
        
        # Count the consecutive occurrences of the city
        count = 0
        while i < len(city_list) and city_list[i] == city:
            count += 1
            i += 1
        
        # If the city appeared only once in the medium, it's invalid.
        if count == 1 and 0 < i - 1 < len(city_list) - 1:
            return False
        
        visited_cities.add(city)
    
    return True



def is_reasonable_visiting_city(question, tested_data):

    city_list = []
    
    # print(tested_data)
    for i in range(min(question['days'],len(tested_data))):
        city_value = tested_data[i]['current_city']

        if 'from' in city_value:
            city1, city2 = extract_from_to(city_value)
            # city1 = extract_before_parenthesis(city1)
            # city2 = extract_before_parenthesis(city2)
            if i==0 and  city1 != question['org']:
                return False, f"The first day's city should be {question['org']}."

            city_list += [city1, city2]

        else:
            city_list.append(extract_before_parenthesis(city_value))
    
    if city_list[0] != city_list[-1]:
        return False, "The trip should be a closed circle."

    if not is_valid_city_sequence(city_list):
        return False, "The city sequence is invalid."
    
    for idx, city in enumerate(city_list):
        if city not in city_state_map:
            return False, f"{city} is not a valid city."
        if idx not in [0,len(city_list)-1] and question['days'] >3 and city_state_map[city] != question['dest']:
            return False, f"{city} is not in {question['dest']}."
    
    return True, None


def is_valid_restaurants(question, tested_data):

    restaurants_list = []

    for i in range(min(question['days'],len(tested_data))):
        unit = tested_data[i]

        if 'breakfast' in unit and unit['breakfast'] and unit['breakfast'] != '-':
            if unit['breakfast'] not in restaurants_list:
                restaurants_list.append(unit['breakfast'])
            else:
                return False, f"The restaurant in day {i+1} breakfast is repeated."
        # elif 'breakfast' not in unit :
        #     return False, f"No Breakfast Info."
            
        if 'lunch' in unit and unit['lunch'] and unit['lunch'] != '-':
            if unit['lunch'] not in restaurants_list:
                restaurants_list.append(unit['lunch'])
            else:
                return False, f"The restaurant in day {i+1} lunch {unit['lunch']} is repeated."
        # elif 'lunch' not in unit:
        #     return False, f"No Lunch Info."
        
        if 'dinner' in unit and unit['dinner'] and unit['dinner'] != '-':
            if unit['dinner'] not in restaurants_list:
                restaurants_list.append(unit['dinner'])
            else:
                return False, f"The restaurant in day {i+1} dinner is repeated."
        # elif 'dinner' not in unit:
        #     return False, f"No Dinner Info."

    return True, None
            
def is_valid_attractions(question, tested_data):

    attractions_list = []

    for i in range(min(question['days'],len(tested_data))):
        unit = tested_data[i]

        if 'attraction' in unit and unit['attraction'] and unit['attraction'] != '-':
            for attraction in unit['attraction'].split(';'):
                if attraction not in attractions_list:
                    attractions_list.append(attraction)
                else:
                    return False, f"The attraction '{attraction}' in day {i+1} is repeated."
                
        # elif 'attraction' not in unit:
        #     return False, f"No Attraction Info."
        
    return True, None

def is_valid_event(question, tested_data):

    events_list = []

    for i in range(min(question['days'],len(tested_data))):
        unit = tested_data[i]

        if 'event' in unit and unit['event'] and unit['event'] != '-':
            for event in unit['event'].split(';'):
                if event not in events_list:
                    events_list.append(event)
                else:
                    return False, f"The event '{event}' in day {i+1} is repeated."
                
        # elif 'attraction' not in unit:
        #     return False, f"No Attraction Info."
        
    return True, None

def is_time_difference_valid(time1, time2, min_difference):
    from datetime import datetime, timedelta
    fmt = "%H:%M"
    time1 = datetime.strptime(time1, fmt)
    time2 = datetime.strptime(time2, fmt)
    return abs((time2 - time1).total_seconds()) / 60 >= min_difference

def is_valid_poi_sequence(question, tested_data):
    current_accommodation = "abc"
    prev_accommodation = None
    
    for i in range(min(question['days'], len(tested_data))):
        unit = tested_data[i]
        
        # Determine current accommodation
        if unit["accommodation"] != "-":
            current_accommodation = unit["accommodation"]

        # Parse city if present
        if "," in current_accommodation:
            current_accommodation, city = current_accommodation.rsplit(",", 1)
            current_accommodation = current_accommodation.strip()
            city = city.strip()
        else:
            current_accommodation = current_accommodation.strip()
            city = ""

        poi_list = unit["point_of_interest_list"].split(";")

        # Day-specific logic for transitions (e.g., day 3 or day 5)
        if i+1 in [3,5] and prev_accommodation:
            if not (prev_accommodation.strip() in poi_list[0] and current_accommodation.strip() in poi_list[-1]):
                return False, f"Day {i+1} PoI list must start with previous day's accommodation and end with current day's accommodation."

        # Normal check: start and end with current accommodation if specified
        elif unit["accommodation"] != "-":
            if current_accommodation.strip() in poi_list[0] and current_accommodation.strip() in poi_list[-1]:
                pass
            else:
                return False, f"The PoI list for day {i+1} doesn't start and end with an accommodation."
        else:
            if current_accommodation.strip() in poi_list[0]:
                pass
            else:
                return False, f"The PoI list for day {i+1} doesn't start with an accommodation."

        # Check events
        if 'event' in unit and unit['event'] and unit['event'] != '-':
            events_list = list({e.rsplit(",", 1)[0].strip() for e in unit['event'].split(';') if e})
            for et in events_list:
                if et in unit["point_of_interest_list"]:
                    return False, f"The PoI list for day {i+1} shouldn't contain events."

        # Check attractions
        if 'attraction' in unit and unit['attraction'] and unit['attraction'] != '-':
            attractions_list = list({attr.rsplit(",", 1)[0].strip() for attr in unit['attraction'].split(';') if attr})
            for attr in attractions_list:
                if attr not in unit["point_of_interest_list"]:
                    return False, f"The PoI list for day {i+1} doesn't contain all attractions."

        # Check meals
        for meal in ['breakfast', 'lunch', 'dinner']:
            if meal in unit and unit[meal] and unit[meal] != '-':
                food_place = unit[meal].rsplit(",", 1)[0].strip()
                if food_place not in unit["point_of_interest_list"]:
                    return False, f"The PoI list for day {i+1} doesn't contain {meal}."

        # Check flight timing constraints
        if 'transportation' in unit and all(x in unit['transportation'].lower() for x in ['flight', 'departure', 'arrival']):
            transport_info = unit['transportation'].split(', ')
            departure_time = arrival_time = None
            for info in transport_info:
                if 'Departure Time' in info:
                    departure_time = info.split(': ')[1]
                elif 'Arrival Time' in info:
                    arrival_time = info.split(': ')[1]

            if i == 0 and poi_list[0] not in ['-', '']:
                for time_phrase in poi_list[0].split(','):
                    if 'stay from' in time_phrase or 'visit from' in time_phrase:
                        first_poi_time = time_phrase.split('from ')[1].split(' to ')[0].strip()
                        if not is_time_difference_valid(arrival_time, first_poi_time, 30):
                            return False, f"First PoI on day {i+1} starts too soon after the flight arrival."
                            
            if question['days'] > 3:            
                if i == 2 and poi_list[0] not in ['-', '']:
                    for time_phrase in poi_list[0].split(','):
                        if 'stay from' in time_phrase or 'visit from' in time_phrase:
                            first_poi_time = time_phrase.split('from ')[1].split(' to ')[0].strip()
                            if not is_time_difference_valid(arrival_time, first_poi_time, 30):
                                return False, f"First PoI on day {i+1} starts too soon after the flight arrival."

            if question['days'] > 5:
                if i == 4 and poi_list[0] not in ['-', '']:
                    for time_phrase in poi_list[0].split(','):
                        if 'stay from' in time_phrase or 'visit from' in time_phrase:
                            first_poi_time = time_phrase.split('from ')[1].split(' to ')[0].strip()
                            if not is_time_difference_valid(arrival_time, first_poi_time, 30):
                                return False, f"First PoI on day {i+1} starts too soon after the flight arrival."

            if i == len(tested_data) - 1 and poi_list[-1] not in ['-', '']:
                for time_phrase in poi_list[-1].split(','):
                    if 'stay from' in time_phrase or 'visit from' in time_phrase:
                        last_poi_time = time_phrase.split('from ')[1].split(' to ')[-1].strip()
                        if not is_time_difference_valid(last_poi_time, departure_time, 30):
                            return False, f"Last PoI on day {i+1} ends too close to the flight departure."

        # Update prev_accommodation only if a new one is provided
        if unit["accommodation"] != "-":
            prev_accommodation = current_accommodation

    return True, None

def is_valid_meal_gaps(question, tested_data):
    for i in range(min(question['days'], len(tested_data))):
        day_plan = tested_data[i]
        # Store meal start and end times
        meal_times = {}
        for meal in ["breakfast", "lunch", "dinner"]:
            if meal in day_plan and day_plan[meal] != "-":
                poi_info = day_plan["point_of_interest_list"].split(";")
                for poi in poi_info:
                    if "," in day_plan[meal]:
                        day_plan_meal = day_plan[meal]
                        day_plan_meal, city = day_plan_meal.rsplit(",", 1)
                        day_plan_meal = day_plan_meal.strip()
                        city = city.strip()
                    else:
                        # Fallback if no city is mentioned
                        day_plan_meal = day_plan[meal]
                        day_plan_meal = day_plan_meal.strip()
                        city = ""

                    if day_plan_meal in poi and poi not in ['-','']:
                        try:
                            # Extract the "from" and "to" times
                            time_info = poi.split("from")[1].split("to")
                            start_time = time_info[0].strip()
                            end_time = time_info[1].split(",")[0].strip()
                        except:
                            try:
                                time_info = poi.rsplit("from", 1)[1].split("to")
                                start_time = time_info[0].strip()
                                end_time = time_info[1].split(",")[0].strip()
                            except:
                                return False, f"Incorrect format."   
                        # Convert times to decimal hours
                        # print(time_info)
                        try:
                            start_hour = int(start_time.split(":")[0]) + int(start_time.split(":")[1]) / 60
                            end_hour = int(end_time.split(":")[0]) + int(end_time.split(":")[1]) / 60
                        except:
                            return False, f"PoI time intervals are not in correct format."

                        # Save meal start and end times
                        meal_times[meal] = (start_hour, end_hour)
                        break

        # Validate meal time gaps
        sorted_meals = ["breakfast", "lunch", "dinner"]
        for j in range(len(sorted_meals) - 1):
            meal1 = sorted_meals[j]
            meal2 = sorted_meals[j + 1]
            if meal1 in meal_times and meal2 in meal_times:
                _, meal1_end = meal_times[meal1]
                meal2_start, _ = meal_times[meal2]
                # Check if the gap is at least 4 hours
                if meal2_start - meal1_end < 4:
                    return False, f"Not sufficient time gap between {meal1} and {meal2} of day {i+1}"  # Invalid gap

    return True, None  # All meal gaps are valid

    
def is_valid_transportation(question, tested_data):
    
    if tested_data[0]['transportation'] and tested_data[0]['transportation'] != '-':
        transportation_list = [transportation_match(tested_data[0]['transportation'])]
    
    else:
        return False, "The transportation in day 1 should not be empty."

    for i in range(min(question['days'],len(tested_data))):
        unit = tested_data[i]

        if 'transportation' in unit and unit['transportation'] and unit['transportation'] != '-':
            transportation_list.append(transportation_match(unit['transportation']))
        # elif 'transportation' not in unit:
        #     return False, f"No Transportation Info."
    
    if (('Self-driving' in transportation_list) and ('Flight' in transportation_list)) or (('Taxi' in transportation_list) and ('Self-driving' in transportation_list)):
        return False, "The transportation is conflicting."

    return True, None

def is_valid_information_in_current_city(question, tested_data):

    for i in range(min(question['days'],len(tested_data))):
        unit = tested_data[i]
        current_city = unit['current_city']
        final_city_list = []

        if 'from' in current_city:
            city1, city2 = extract_from_to(current_city)
            # city1 = extract_before_parenthesis(city1)
            # city2 = extract_before_parenthesis(city2)
            final_city_list = [city1, city2]
        else:
            return False, f"Invalid current city format."
            # final_city_list = extract_before_parenthesis(current_city)

        if 'transportation' in unit and unit['transportation'] and unit['transportation'] != '-':
            for city in final_city_list:
                if ('Self-driving' not in unit['transportation'] and 'Taxi' not in unit['transportation']) and (city not in unit['transportation']):
                    # print(city)
                    return False, f"The transportation in day {i+1} is invalid city choice."
        # elif 'transportation' not in unit:
        #     return False, f"No Transportation Info."
        
        if 'breakfast' in unit and unit['breakfast'] and unit['breakfast'] != '-':
            flag = False

            for city in final_city_list:
                if city  in unit['breakfast']:
                    flag = True

            if not flag:
                return False, f"The breakfast in day {i+1} is invalid city choice."
        # elif 'breakfast' not in unit:
        #     return False, f"No Breakfast Info."
        
        if 'lunch' in unit and unit['lunch'] and unit['lunch'] != '-':
            flag = False

            for city in final_city_list:
                if city  in unit['lunch']:
                    flag = True
            
            if not flag:
                return False, f"The lunch in day {i+1} is invalid city choice."
        # elif 'lunch' not in unit:
        #     return False, f"No Lunch Info."
            
        if 'dinner' in unit and unit['dinner'] and unit['dinner'] != '-':
            flag = False

            for city in final_city_list:
                if city  in unit['dinner']:
                    flag = True
            
            if not flag:
                return False, f"The dinner in day {i+1} is invalid city choice."
        # elif 'dinner' not in unit:
        #     return False, f"No Dinner Info."
        
        if 'attraction' in unit and unit['attraction'] and unit['attraction'] != '-':
            
            attraction_list = unit['attraction'].split(';')

            for attraction in attraction_list:
                flag = False
                for city in final_city_list:
                    if city  in attraction:
                        flag = True
                if not flag:
                    return False, f"The attraction in day {i+1} is invalid city choice."
                
        # elif 'attraction' not in unit:
        #     return False, f"No Attraction Info."
            
            
        if 'accommodation' in unit and unit['accommodation'] and unit['accommodation'] != '-':
            
            if final_city_list[-1] not in unit['accommodation']:
                return False, f"The accommodation in day {i+1} is invalid city choice."
            
        # elif 'accommodation' not in unit:
        #     return False, f"No Accommodation Info."
    
    return True, None
        
# hallucination 
def is_valid_information_in_sandbox(question, tested_data):
    
    for i in range(min(question['days'],len(tested_data))):
        unit = tested_data[i]
        
        if unit['transportation'] and unit['transportation'] != '-':
            value = unit['transportation']
            # org_city, dest_city = extract_from_to(value)
            # if org_city == None or dest_city == None:
            # print(unit['current_city'], type(unit['current_city']))
            org_city, dest_city = extract_from_to(unit['current_city'])
            if 'flight number' in value.lower():
                try:
                    # print("(",org_city, dest_city,")")
                    org_city = extract_before_parenthesis(org_city)
                    dest_city = extract_before_parenthesis(dest_city)
                except TypeError:
                    org_city, dest_city = extract_from_to(unit['transportation'])
                    # raise ValueError("The transportation {} in day {} can not be parsed.".format(value,i+1))
                # print(value)
                try:
                    if len(flight.data[(flight.data['Flight Number'] == value.split('Flight Number: ')[1].split(',')[0]) & (flight.data['OriginCityName']==org_city) & (flight.data['DestCityName']==dest_city)]) < 1:
                        return False, f"The flight number in day {i+1} is invalid in the sandbox."
                except:
                    return False, f"Incorrect Flight format."
            
            elif 'self-driving' in value.lower() or 'taxi' in value.lower():
                try:
                    org_city = extract_before_parenthesis(org_city)
                    dest_city = extract_before_parenthesis(dest_city)
                except TypeError:
                    org_city = '-'
                    dest_city = '-'
                    print("The transportation {} in day {} can not be parsed and '-' will be used instead.".format(value,i+1))
                
                if 'self-driving' in value.lower():
                    if googleDistanceMatrix.run_for_evaluation(org_city, dest_city, mode='self-driving')['cost'] == None:
                        return False, f"The self-driving in day {i+1} is invalid in the sandbox."
                else:
                    if googleDistanceMatrix.run_for_evaluation(org_city, dest_city, mode='taxi')['cost'] == None:
                        return False, f"The taxi in day {i+1} is invalid in the sandbox."

        if 'breakfast' in unit and unit['breakfast'] and unit['breakfast'] != '-':
            name, city = get_valid_name_city(unit['breakfast'])
            if len(restaurants.data[(restaurants.data['name'].astype(str).str.contains(re.escape(name))) & (restaurants.data['City'] == city)]) < 1:
                return False, f"The breakfast in day {i+1} is invalid in the sandbox."
        elif 'breakfast' not in unit:
            return False, f"No Breakfast Info."
        
        if 'lunch' in unit and unit['lunch'] and unit['lunch'] != '-':
            name, city = get_valid_name_city(unit['lunch'])
            if len(restaurants.data[(restaurants.data['name'].astype(str).str.contains(re.escape(name))) & (restaurants.data['City'] == city)]) < 1:
                return False, f"The lunch in day {i+1} is invalid in the sandbox."
        elif 'lunch' not in unit:
            return False, f"No Lunch Info."
        
        if 'dinner' in unit and unit['dinner'] and unit['dinner'] != '-':
            name, city = get_valid_name_city(unit['dinner'])
            if len(restaurants.data[(restaurants.data['name'].astype(str).str.contains(re.escape(name))) & (restaurants.data['City'] == city)]) < 1:
                return False, f"The dinner in day {i+1} is invalid in the sandbox."
        elif 'dinner' not in unit:
            return False, f"No Dinner Info."
            
        if 'attraction' in unit and unit['attraction'] and unit['attraction'] != '-':
            attractions_list = unit['attraction'].split(';')
            for attraction in attractions_list:
                name, city = get_valid_name_city(attraction)
                # name = attraction
                if 'from' in unit['current_city']:
                    city = unit['current_city'].split("to")[1].strip()
                else:
                    city = unit['current_city'].strip()
                if len(attractions.data[(attractions.data['name'].astype(str).str.contains(re.escape(name))) & (attractions.data['City'] == city)]) < 1:
                    return False, f"The attraction {attraction} in day {i+1} is invalid in the sandbox."
        

        if 'event' in unit and unit['event'] and unit['event'] != '-':
            events_list = unit['event'].split(';')
            for event in events_list:
                # name, city = get_valid_name_city(event)
                name = event.split(',')[0].strip()
                # city = question['dest'] 
                city = event.rsplit(",",1)[-1].strip()
                if len(events.data[(events.data['name'].astype(str).str.contains(re.escape(name))) & (events.data['city'] == city)]) < 1:
                    return False, f"The event {event} in day {i+1} is invalid in the sandbox."
                
        if 'accommodation' in unit and unit['accommodation'] and unit['accommodation'] != '-':
            name, city = get_valid_name_city(unit['accommodation'])
            # print(name,city)
            # print(accommodation.data[accommodation.data['NAME'].astype(str).str.contains(re.escape(name))])
            if len(accommodation.data[(accommodation.data['name'].astype(str).str.contains(re.escape(name))) & (accommodation.data['City'] == city)]) < 1:
                return False, f"The accommodation in day {i+1} is invalid in the sandbox."
        elif 'accommodation' not in unit:
            return False, f"No Accommodation Info."

        if 'point_of_interest_list' in unit and unit['point_of_interest_list'] and unit['point_of_interest_list'] != '-':
            poi_info = unit["point_of_interest_list"].split(";")
            for poi in poi_info:
                if "nearest transit:" in poi:
                    transit_info = poi.split("nearest transit:")[1].strip()
                    transit_stop = transit_info.rsplit(",", 1)[0].strip()
                    if "," in transit_info:
                        # print(transit_info)
                        transit_value = transit_info.rsplit(",", 1)[-1].strip().split("m")[0].strip()  
                        try:
                            stop_distance = float(transit_value)
                        except:
                            stop_distance = 0
                    else:
                        return False, f"PoI list is not formatted correctly."

                    # pois['nearest_stop_distance'] = pd.to_numeric(pois['nearest_stop_distance'], errors='coerce')
                    # print(pois['nearest_stop_distance'].dtype)
                    try:
                        if question['days']==3:
                            if ((i+1)==3):
                                city = unit['current_city'].split("from")[-1].split(" to ")[0].strip()
                                if len(pois[(pois['nearest_stop_name'].astype(str).str.contains(re.escape(transit_stop))) & (pois['City'] == city) & (abs(pois['nearest_stop_distance'] - stop_distance) <= 5)]) < 1:
                                        return False, f"The PoI nearest stops in day {i+1} have hallucinated data."
                            else:
                                if len(pois[(pois['nearest_stop_name'].astype(str).str.contains(re.escape(transit_stop))) & (pois['City'] == city) & (abs(pois['nearest_stop_distance'] - stop_distance) <= 5)]) < 1:
                                        return False, f"The PoI nearest stops in day {i+1} have hallucinated data."
                        if question['days']==5:
                            if ((i+1)==3):
                                if len(pois[(pois['nearest_stop_name'].astype(str).str.contains(re.escape(transit_stop))) & (pois['City'] == org_city) & (abs(pois['nearest_stop_distance'] - stop_distance) <= 5)]) < 1:
                                    if len(pois[(pois['nearest_stop_name'].astype(str).str.contains(re.escape(transit_stop))) & (pois['City'] == dest_city) & (abs(pois['nearest_stop_distance'] - stop_distance) <= 5)]) < 1:
                                        return False, f"The PoI nearest stops in day {i+1} have hallucinated data."
                            elif ((i+1)==5):
                                city = unit['current_city'].split("from")[-1].split(" to ")[0].strip()
                                if len(pois[(pois['nearest_stop_name'].astype(str).str.contains(re.escape(transit_stop))) & (pois['City'] == city) & (abs(pois['nearest_stop_distance'] - stop_distance) <= 5)]) < 1:
                                        return False, f"The PoI nearest stops in day {i+1} have hallucinated data."
                            else:
                                if len(pois[(pois['nearest_stop_name'].astype(str).str.contains(re.escape(transit_stop))) & (pois['City'] == city) & (abs(pois['nearest_stop_distance'] - stop_distance) <= 5)]) < 1:
                                        return False, f"The PoI nearest stops in day {i+1} have hallucinated data."
                        if question['days']==7:
                            if ((i+1)==3) or ((i+1)==5):
                                if len(pois[(pois['nearest_stop_name'].astype(str).str.contains(re.escape(transit_stop))) & (pois['City'] == org_city) & (abs(pois['nearest_stop_distance'] - stop_distance) <= 5)]) < 1:
                                    if len(pois[(pois['nearest_stop_name'].astype(str).str.contains(re.escape(transit_stop))) & (pois['City'] == dest_city) & (abs(pois['nearest_stop_distance'] - stop_distance) <= 5)]) < 1:
                                        return False, f"The PoI nearest stops in day {i+1} have hallucinated data."
                            elif ((i+1)==7):
                                city = unit['current_city'].split("from")[-1].split(" to ")[0].strip()
                                if len(pois[(pois['nearest_stop_name'].astype(str).str.contains(re.escape(transit_stop))) & (pois['City'] == city) & (abs(pois['nearest_stop_distance'] - stop_distance) <= 5)]) < 1:
                                        return False, f"The PoI nearest stops in day {i+1} have hallucinated data."
                            else:
                                if len(pois[(pois['nearest_stop_name'].astype(str).str.contains(re.escape(transit_stop))) & (pois['City'] == city) & (abs(pois['nearest_stop_distance'] - stop_distance) <= 5)]) < 1:
                                        return False, f"The PoI nearest stops in day {i+1} have hallucinated data."
                    except:
                        return False, f"Incorrect format."
    return True, None


def is_valid_accommodaton(question, tested_data):
    data = []
    for i in range(min(question['days'],len(tested_data))):
        unit = tested_data[i]

        if 'accommodation' not in unit:
            return False, f"No Accommodation Info."
        
        data.append(unit['accommodation'])
    # data = [unit['accommodation'] for unit in tested_data]
    consectutive_accommodation = count_consecutive_values(data)
    for unit in consectutive_accommodation:
        # print(unit)
        if unit and unit[0] not in  ['-',''] :
            name, city = get_valid_name_city(unit[0])
            # print(unit[0],name,city)
            # try:
            if len(accommodation.data[(accommodation.data['name'].astype(str).str.contains(re.escape(name))) & (accommodation.data['City'] == city)]) == 1 and unit[1] <  accommodation.data[(accommodation.data['name'].astype(str).str.contains(re.escape(name))) & (accommodation.data['City'] == city)].iloc[0]['minimum nights']:
                return False, f"The accommodation {unit[0]} do not obey the minumum nights rule."
            # can not parse data
            # except re.error:
            #     continue
            
    return True, None

def is_valid_visiting_city_number(question, tested_data):

    city_set = set()
    

    for i in range(min(question['days'],len(tested_data))):
        city_value = tested_data[i]['current_city']

        if 'from' in city_value:
            city1, city2 = extract_from_to(city_value)
            city1 = extract_before_parenthesis(city1)
            city2 = extract_before_parenthesis(city2)
            if i==0 and  city1 != question['org']:
                return False, f"The first day's city should be {question['org']}."

            city_set.add(city1)
            city_set.add(city2)

        else:
            city_set.add(extract_before_parenthesis(city_value))
    
    city_set.discard(question['org'])

    if len(city_set) != question['visiting_city_number']:
        return False, f"The number of visiting cities should be {question['visiting_city_number']}."
    
    return True, None

def is_valid_days(question, tested_data):
    lens = 0
    for i in range(min(question['days'],len(tested_data))):
        if tested_data[i] != {} and tested_data[i]['current_city'] != "You don't need to fill in the information for this or later days.":
            lens += 1
        
    if lens != question['days']:
        # print(lens)
        return False, f"The number of days should be {question['days']}."
    else:
        return True, None

def is_not_absent(question, tested_data):
    needed_info = 8 * question['days']
    total_valid_info = 0

    if not is_valid_days(question, tested_data)[0]:
        return False, "Invalid Days"
    
    if not is_valid_visiting_city_number(question, tested_data)[0]:
        return False, "Invalid City Number"

    for i in range(min(question['days'],len(tested_data))):
        unit = tested_data[i]

        if 'transportation' not in unit:
            return False, f"No Transportation Info."
        
        if 'breakfast' not in unit:
            return False, f"No Breakfast Info."
        
        if 'lunch' not in unit:
            return False, f"No Lunch Info."
        
        if 'dinner' not in unit:
            return False, f"No Dinner Info."
        
        if 'attraction' not in unit:
            return False, f"No Attraction Info."
        
        if 'accommodation' not in unit:
            return False, f"No Accommodation Info."
        
        if 'event' not in unit:
            return False, f"No Event Info."
        
        if 'point_of_interest_list' not in unit:
            return False, f"No PoI Info."
        
        if 'point_of_interest_list' in unit and unit['point_of_interest_list'] and unit['point_of_interest_list'] != '-':
            poi_info = unit["point_of_interest_list"].split(";")
            for poi in poi_info:
                if "nearest transit:" in poi:
                    transit_info = poi.split("nearest transit:")[1].strip()
                    transit_stop = transit_info.rsplit(",", 1)[0].strip()
                    if "," in transit_info:
                        # print(transit_info)
                        transit_value = transit_info.rsplit(",", 1)[-1].strip().split("m")[0].strip()  
                        if transit_value == '-' or not transit_value:
                            return False, f"No transit stop distance mentioned."
        
        if ('from ' in unit['current_city'] or 'to ' in unit['current_city']) and unit['transportation'] in ['','-']:
            return False, f"No transportation in day {i+1} is not allowed."
        
        if ('from ' not in unit['current_city'] and  ' to ' not in unit['current_city']) and unit['attraction'] in ['','-']:
            return False, f"No attaction in day {i+1} is not allowed."

        if i != question['days'] - 1 and unit['accommodation'] in ['','-']:
            return False, f"No accommodation in day {i+1} is not allowed."

        if (unit['breakfast'] in ['','-'] or unit['lunch'] in ['','-'] or unit['dinner'] in ['','-']) and 'from ' not in unit['current_city']:
            return False, f"No meal in day {i+1} is not allowed."
        
        if (unit['point_of_interest_list'] in ['','-']):
            return False, f"Point of Interest list will never be empty."
        

        for key in unit:
            if unit[key] and unit[key] != '-':
                total_valid_info += 1


    if total_valid_info * 1.0 / needed_info < 0.5:
        return False, f"The absent information is more than 50%."
    
    return True, None


def evaluation(query_data, tested_data):
    return_info = {}
    return_info['is_reasonable_visiting_city'] = is_reasonable_visiting_city(query_data, tested_data)
    return_info['is_valid_restaurants'] = is_valid_restaurants(query_data, tested_data)
    return_info['is_valid_attractions'] = is_valid_attractions(query_data, tested_data)
    # return_info['is_valid_accommodation'] = is_valid_accommodaton(query_data, tested_data)
    return_info['is_valid_transportation'] = is_valid_transportation(query_data, tested_data)
    return_info['is_valid_event'] = is_valid_event(query_data, tested_data) 
    return_info['is_valid_meal_gaps'] = is_valid_meal_gaps(query_data, tested_data)
    return_info['is_valid_poi_sequence'] = is_valid_poi_sequence(query_data, tested_data)
    return_info['is_valid_information_in_sandbox'] = is_valid_information_in_sandbox(query_data, tested_data) 
    return_info['is_valid_information_in_current_city'] = is_valid_information_in_current_city(query_data, tested_data) 
    return_info['is_not_absent'] = is_not_absent(query_data, tested_data)  
    return return_info

def boolean_evaluation(query_data, tested_data):
    return_info = {}
    return_info['is_reasonable_visiting_city'] = is_reasonable_visiting_city(query_data, tested_data)
    return_info['is_valid_restaurants'] = is_valid_restaurants(query_data, tested_data)
    return_info['is_valid_accommodation'] = is_valid_accommodaton(query_data, tested_data)
    return_info['is_valid_attractions'] = is_valid_attractions(query_data, tested_data)
    return_info['is_valid_transportation'] = is_valid_transportation(query_data, tested_data)
    return_info['is_valid_information_in_current_city'] = is_valid_information_in_current_city(query_data, tested_data)
    return_info['is_valid_information_in_sandbox'] = is_valid_information_in_sandbox(query_data, tested_data)
    return_info['is_not_absent'] = is_not_absent(query_data, tested_data)
    for key in return_info:
        if return_info[key][0] == False:
            print(return_info[key][1])
            return False
    return True
