from langchain.prompts import PromptTemplate


# ZEROSHOT_REACT_INSTRUCTION = """Collect information for a query plan using interleaving 'Thought', 'Action', and 'Observation' steps. Ensure you gather valid information related to transportation, dining, attractions, and accommodation. All information should be written in Notebook, which will then be input into the Planner tool. Note that the nested use of tools is prohibited. 'Thought' can reason about the current situation, and 'Action' can have 8 different types:
# (1) FlightSearch[Departure City, Destination City, Date]:
# Description: A flight information retrieval tool.
# Parameters:
# Departure City: The city you'll be flying out from.
# Destination City: The city you aim to reach.
# Date: The date of your travel in YYYY-MM-DD format.
# Example: FlightSearch[New York, London, 2022-10-01] would fetch flights from New York to London on October 1, 2022.

# (2) GoogleDistanceMatrix[Origin, Destination, Mode]:
# Description: Estimate the distance, time and cost between two cities.
# Parameters:
# Origin: The departure city of your journey.
# Destination: The destination city of your journey.
# Mode: The method of transportation. Choices include 'self-driving' and 'taxi'.
# Example: GoogleDistanceMatrix[Paris, Lyon, self-driving] would provide driving distance, time and cost between Paris and Lyon.

# (3) AccommodationSearch[City]:
# Description: Discover accommodations in your desired city.
# Parameter: City - The name of the city where you're seeking accommodation.
# Example: AccommodationSearch[Rome] would present a list of hotel rooms in Rome.

# (4) RestaurantSearch[City]:
# Description: Explore dining options in a city of your choice.
# Parameter: City – The name of the city where you're seeking restaurants.
# Example: RestaurantSearch[Tokyo] would show a curated list of restaurants in Tokyo.

# (5) AttractionSearch[City]:
# Description: Find attractions in a city of your choice.
# Parameter: City – The name of the city where you're seeking attractions.
# Example: AttractionSearch[London] would return attractions in London.

# (6) CitySearch[State]
# Description: Find cities in a state of your choice.
# Parameter: State – The name of the state where you're seeking cities.
# Example: CitySearch[California] would return cities in California.

# (7) NotebookWrite[Short Description]
# Description: Writes a new data entry into the Notebook tool with a short description. This tool should be used immediately after FlightSearch, AccommodationSearch, AttractionSearch, RestaurantSearch or GoogleDistanceMatrix. Only the data stored in Notebook can be seen by Planner. So you should write all the information you need into Notebook.
# Parameters: Short Description - A brief description or label for the stored data. You don't need to write all the information in the description. The data you've searched for will be automatically stored in the Notebook.
# Example: NotebookWrite[Flights from Rome to Paris in 2022-02-01] would store the informatrion of flights from Rome to Paris in 2022-02-01 in the Notebook.

# (8) Planner[Query]
# Description: A smart planning tool that crafts detailed plans based on user input and the information stroed in Notebook.
# Parameters: 
# Query: The query from user.
# Example: Planner[Give me a 3-day trip plan from Seattle to New York] would return a detailed 3-day trip plan.
# You should use as many as possible steps to collect engough information to input to the Planner tool. 

# Each action only calls one function once. Do not add any description in the action.

# Query: {query}{scratchpad}"""



# zeroshot_react_agent_prompt = PromptTemplate(
#                         input_variables=["query", "scratchpad"],
#                         template=ZEROSHOT_REACT_INSTRUCTION,
#                         )

# PLANNER_INSTRUCTION = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and accommodation names. Note that all the information in your plan should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with commonsense. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B).

# ***** Example *****
# Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?
# Travel Plan:
# Day 1:
# Current City: from Ithaca to Charlotte
# Transportation: Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46
# Breakfast: Nagaland's Kitchen, Charlotte
# Attraction: The Charlotte Museum of History, Charlotte
# Lunch: Cafe Maple Street, Charlotte
# Dinner: Bombay Vada Pav, Charlotte
# Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

# Day 2:
# Current City: Charlotte
# Transportation: -
# Breakfast: Olive Tree Cafe, Charlotte
# Attraction: The Mint Museum, Charlotte;Romare Bearden Park, Charlotte.
# Lunch: Birbal Ji Dhaba, Charlotte
# Dinner: Pind Balluchi, Charlotte
# Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

# Day 3:
# Current City: from Charlotte to Ithaca
# Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26
# Breakfast: Subway, Charlotte
# Attraction: Books Monument, Charlotte.
# Lunch: Olive Tree Cafe, Charlotte
# Dinner: Kylin Skybar, Charlotte
# Accommodation: -

# ***** Example Ends *****

# Given information: {text}
# Query: {query}
# Travel Plan:"""

PLANNER_INSTRUCTION_OG = """You are a proficient planner. Based on the provided information, query and persona, please give a detailed travel plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and accommodation names. Note that all the information in your plans should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with common sense. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the "Current City" section as in the example (i.e., from A to B). Include events happening on that day, if any. Provide a Point of Interest List, which is an ordered list of places visited throughout the day. This list should include only accommodations, attractions, or restaurants and their starting and ending timestamps. Each day must start and end with the accommodation where the traveler is staying.
 

****** Example ******  

Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?  
Traveler Persona:
Traveler Type: Laidback Traveler;
Purpose of Travel: Relaxation;
Spending Preference: Economical Traveler;
Location Preference: Beaches
  
Travel Plan:  
Day 1:  
Current City: from Ithaca to Charlotte  
Transportation: Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:15, Arrival Time: 07:28  
Breakfast: Nagaland's Kitchen, Charlotte  
Attraction: The Charlotte Museum of History, Charlotte  
Lunch: Cafe Maple Street, Charlotte
Dinner: Bombay Vada Pav, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte
Event: -  
Point of Interest List: Affordable Spacious Refurbished Room in Bushwick!, stay from 08:00 to 08:30, nearest transit: Bushwick Stop, 100m away; Nagaland's Kitchen, visit from 09:00 to 09:45, nearest transit: Uptown Station, 200m away; The Charlotte Museum of History, visit from 10:30 to 13:30, nearest transit: Museum Station, 300m away; Cafe Maple Street, visit from 14:00 to 15:00, nearest transit: Maple Avenue Stop, 100m away; Bombay Vada Pav, visit from 19:00 to 20:00, nearest transit: Bombay Stop, 150m away; Affordable Spacious Refurbished Room in Bushwick!, stay from 21:00 to 07:00, nearest transit: Bushwick Stop, 100m away.  

Day 2:  
Current City: Charlotte  
Transportation: -  
Breakfast: Olive Tree Cafe, Charlotte  
Attraction: The Mint Museum, Charlotte; Romare Bearden Park, Charlotte  
Lunch: Birbal Ji Dhaba, Charlotte  
Dinner: Pind Balluchi, Charlotte  
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte  
Event: -  
Point of Interest List: Affordable Spacious Refurbished Room in Bushwick!, stay from 07:00 to 08:30, nearest transit: Bushwick Stop, 100m away; Olive Tree Cafe, visit from 09:00 to 09:45, nearest transit: Cafe Station, 250m away; The Mint Museum, visit from 10:30 to 13:00, nearest transit: Mint Stop, 200m away; Birbal Ji Dhaba, visit from 14:00 to 15:30, nearest transit: Dhaba Stop, 120m away; Romare Bearden Park, visit from 16:00 to 18:00, nearest transit: Park Stop, 150m away; Pind Balluchi, visit from 19:30 to 21:00, nearest transit: Pind Stop, 150m away; Affordable Spacious Refurbished Room in Bushwick!, stay from 21:30 to 07:00, nearest transit: Bushwick Stop, 100m away.  

Day 3:  
Current City: from Charlotte to Ithaca  
Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26  
Breakfast: Subway, Charlotte  
Attraction: Books Monument, Charlotte  
Lunch: Olive Tree Cafe, Charlotte  
Dinner: Kylin Skybar, Charlotte  
Accommodation: -  
Event: -  
Point of Interest List: Affordable Spacious Refurbished Room in Bushwick!, stay from 07:00 to 08:30, nearest transit: Bushwick Stop, 100m away; Subway, visit from 09:00 to 10:00, nearest transit: Subway Station, 150m away; Books Monument, visit from 10:30 to 13:30, nearest transit: Central Library Stop, 200m away; Olive Tree Cafe, visit from 14:00 to 15:00, nearest transit: Cafe Station, 250m away; Kylin Skybar, visit from 19:00 to 20:00, nearest transit: Skybar Stop, 180m away.  

****** Example Ends ******

Given information: {text}
Query: {query}
Traveler Persona:
{persona}
Output: """

PLANNER_INSTRUCTION_PARAMETER_INFO = """You are a proficient planner. Based on the provided information, query and persona, please give a detailed travel plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and accommodation names. Note that all the information in your plans should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with common sense. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the "Current City" section as in the example (i.e., from A to B). Include events happening on that day, if any. Provide a Point of Interest List, which is an ordered list of places visited throughout the day. This list should include accommodations, attractions, or restaurants and their starting and ending timestamps. Each day must start and end with the accommodation where the traveler is staying. Breakfast is ideally scheduled at 9:40 AM and lasts about 50 minutes. Lunch is best planned for 2:20 PM, with a duration of around an hour. Dinner should take place at 8:45 PM, lasting approximately 1 hour and 15 minutes. Laidback Travelers typically explore one attraction per day and sometimes opt for more, while Adventure Seekers often visit 2 or 3 attractions, occasionally exceeding that number.
 

****** Example ******  

Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?  
Traveler Persona:
Traveler Type: Laidback Traveler;
Purpose of Travel: Relaxation;
Spending Preference: Economical Traveler;
Location Preference: Beaches
  
Travel Plan:  
Day 1:  
Current City: from Ithaca to Charlotte  
Transportation: Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:15, Arrival Time: 07:28  
Breakfast: Nagaland's Kitchen, Charlotte  
Attraction: The Charlotte Museum of History, Charlotte  
Lunch: Cafe Maple Street, Charlotte
Dinner: Bombay Vada Pav, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte
Event: -  
Point of Interest List: Affordable Spacious Refurbished Room in Bushwick!, stay from 08:00 to 08:30, nearest transit: Bushwick Stop, 100m away; Nagaland's Kitchen, visit from 09:00 to 09:45, nearest transit: Uptown Station, 200m away; The Charlotte Museum of History, visit from 10:30 to 13:30, nearest transit: Museum Station, 300m away; Cafe Maple Street, visit from 14:00 to 15:00, nearest transit: Maple Avenue Stop, 100m away; Bombay Vada Pav, visit from 19:00 to 20:00, nearest transit: Bombay Stop, 150m away; Affordable Spacious Refurbished Room in Bushwick!, stay from 21:00 to 07:00, nearest transit: Bushwick Stop, 100m away.  

Day 2:  
Current City: Charlotte  
Transportation: -  
Breakfast: Olive Tree Cafe, Charlotte  
Attraction: The Mint Museum, Charlotte; Romare Bearden Park, Charlotte  
Lunch: Birbal Ji Dhaba, Charlotte  
Dinner: Pind Balluchi, Charlotte  
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte  
Event: -  
Point of Interest List: Affordable Spacious Refurbished Room in Bushwick!, stay from 07:00 to 08:30, nearest transit: Bushwick Stop, 100m away; Olive Tree Cafe, visit from 09:00 to 09:45, nearest transit: Cafe Station, 250m away; The Mint Museum, visit from 10:30 to 13:00, nearest transit: Mint Stop, 200m away; Birbal Ji Dhaba, visit from 14:00 to 15:30, nearest transit: Dhaba Stop, 120m away; Romare Bearden Park, visit from 16:00 to 18:00, nearest transit: Park Stop, 150m away; Pind Balluchi, visit from 19:30 to 21:00, nearest transit: Pind Stop, 150m away; Affordable Spacious Refurbished Room in Bushwick!, stay from 21:30 to 07:00, nearest transit: Bushwick Stop, 100m away.  

Day 3:  
Current City: from Charlotte to Ithaca  
Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26  
Breakfast: Subway, Charlotte  
Attraction: Books Monument, Charlotte  
Lunch: Olive Tree Cafe, Charlotte  
Dinner: Kylin Skybar, Charlotte  
Accommodation: -  
Event: -  
Point of Interest List: Affordable Spacious Refurbished Room in Bushwick!, stay from 07:00 to 08:30, nearest transit: Bushwick Stop, 100m away; Subway, visit from 09:00 to 10:00, nearest transit: Subway Station, 150m away; Books Monument, visit from 10:30 to 13:30, nearest transit: Central Library Stop, 200m away; Olive Tree Cafe, visit from 14:00 to 15:00, nearest transit: Cafe Station, 250m away; Kylin Skybar, visit from 19:00 to 20:00, nearest transit: Skybar Stop, 180m away.  

****** Example Ends ******

Given information: {text}
Query: {query}
Traveler Persona:
{persona}
Output: """

PLANNER_INSTRUCTION_FEWSHOT = """You are a proficient planner. Based on the provided information, query and persona, please give a detailed travel plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and accommodation names. Note that all the information in your plans should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with common sense. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the "Current City" section as in the example (i.e., from A to B). Include events happening on that day, if any. Provide a Point of Interest List, which is an ordered list of places visited throughout the day. This list should include accommodations, attractions, or restaurants and their starting and ending timestamps in HH:MM format. Each day must start and end with the accommodation where the traveler is staying. 
The common sense that you will be using encompasses all human behavior and habits. For example, schedule breakfast during morning, lunch during afternoon, and dinner at night. The nearest transit should be within walking distance and not tens of kilometers away. And, all other rules that humans perceive as common sense in a schedule.

****** Example 1 ******  

Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?  
Traveler Persona:
Traveler Type: Laidback Traveler;
Purpose of Travel: Relaxation;
Spending Preference: Economical Traveler;
Location Preference: Beaches
  
Travel Plan:  
Day 1:  
Current City: from Ithaca to Charlotte  
Transportation: Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46  
Breakfast: Nagaland's Kitchen, Charlotte  
Attraction: The Charlotte Museum of History, Charlotte  
Lunch: Cafe Maple Street, Charlotte
Dinner: Bombay Vada Pav, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte
Event: -  
Point of Interest List: Affordable Spacious Refurbished Room in Bushwick!, stay from 05:00 to 07:30, nearest transit: Bushwick Stop, 100m away; Nagaland's Kitchen, visit from 08:30 to 09:30, nearest transit: Uptown Station, 200m away; The Charlotte Museum of History, visit from 10:00 to 12:30, nearest transit: Museum Station, 300m away; Cafe Maple Street, visit from 13:00 to 14:00, nearest transit: Maple Avenue Stop, 100m away; Bombay Vada Pav, visit from 19:00 to 20:00, nearest transit: Bombay Stop, 150m away; Affordable Spacious Refurbished Room in Bushwick!, stay from 21:00 to 07:00, nearest transit: Bushwick Stop, 100m away.  

Day 2:  
Current City: Charlotte  
Transportation: -  
Breakfast: Olive Tree Cafe, Charlotte  
Attraction: The Mint Museum, Charlotte; Romare Bearden Park, Charlotte  
Lunch: Birbal Ji Dhaba, Charlotte  
Dinner: Pind Balluchi, Charlotte  
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte  
Event: -  
Point of Interest List: Affordable Spacious Refurbished Room in Bushwick!, stay from 07:00 to 08:30, nearest transit: Bushwick Stop, 100m away; Olive Tree Cafe, visit from 09:00 to 09:45, nearest transit: Cafe Station, 250m away; The Mint Museum, visit from 10:00 to 12:00, nearest transit: Mint Stop, 200m away; Birbal Ji Dhaba, visit from 12:30 to 13:30, nearest transit: Dhaba Stop, 120m away; Romare Bearden Park, visit from 14:00 to 16:00, nearest transit: Park Stop, 150m away; Pind Balluchi, visit from 19:00 to 20:00, nearest transit: Pind Stop, 150m away; Affordable Spacious Refurbished Room in Bushwick!, stay from 21:00 to 07:00, nearest transit: Bushwick Stop, 100m away.  

Day 3:  
Current City: from Charlotte to Ithaca  
Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26  
Breakfast: Subway, Charlotte  
Attraction: Books Monument, Charlotte  
Lunch: Olive Tree Cafe, Charlotte  
Dinner: Kylin Skybar, Charlotte  
Accommodation: -  
Event: -  
Point of Interest List: Affordable Spacious Refurbished Room in Bushwick!, stay from 07:00 to 08:30, nearest transit: Bushwick Stop, 100m away; Subway, visit from 09:00 to 10:00, nearest transit: Subway Station, 150m away; Books Monument, visit from 10:30 to 12:30, nearest transit: Central Library Stop, 200m away; Olive Tree Cafe, visit from 13:00 to 14:00, nearest transit: Cafe Station, 250m away; Kylin Skybar, visit from 19:00 to 20:00, nearest transit: Skybar Stop, 180m away.  

****** Example 1 Ends ******

****** Example 2 ******  

Query: Plan a 5-day trip for 1 person from Washington to Las Vegas from November 5th to November 9th, 2024, with a budget of $2,600.
Traveler Type: Laidback Traveler; 
Purpose of Travel: Nature;
Spending Preference: Luxury Traveler;
Location Preference: Forests/Wildlife

Travel Plan:
Day 1:  
Current City: from Washington to Las Vegas  
Transportation: Flight Number: F0522148, from Washington to Las Vegas, Departure Time: 09:12, Arrival Time: 12:23    
Breakfast: -  
Attraction: Bellagio Conservatory & Botanical Garden, Las Vegas
Lunch: John Mull's Meats & Road Kill Grill, Las Vegas
Dinner: SW Steakhouse, Las Vegas
Accommodation: Luxury Suite - Balcony & Las Vegas Strip Views!, Las Vegas  
Event: -  
Point of Interest List:  
Luxury Suite - Balcony & Las Vegas Strip Views!, stay from 13:00 to 14:00, nearest transit: The Strat, 4778.06m away; John Mull's Meats & Road Kill Grill, visit from 14:00 to 14:45, nearest transit: Symphony Park, 8322.69m away; Bellagio Conservatory & Botanical Garden, visit from 15:30 to 18:00, nearest transit: The Strat, 4344.51m away; SW Steakhouse, visit from 18:30 to 20:00, nearest transit: The Strat, 2548.07m away; Luxury Suite - Balcony & Las Vegas Strip Views!, stay from 20:30 to 09:00, nearest transit: The Strat, 4778.06m away.

Day 2: 
Current City: Las Vegas  
Transportation: -
Breakfast: Eggscellent, Las Vegas  
Attraction: The Mob Museum, Las Vegas; Fremont Street Experience, Las Vegas
Lunch: Triple George Grill, Las Vegas
Dinner: Top of the World, Las Vegas
Accommodation: Luxury Suite - Balcony & Las Vegas Strip Views!, Las Vegas
Event: -  
Point of Interest List:
Luxury Suite - Balcony & Las Vegas Strip Views!, stay from 09:00 to 10:00, nearest transit: The Strat, 4778.06m away; Eggscellent, visit from 10:30 to 11:30, nearest transit: The Strat, 4208.46m away; The Mob Museum, visit from 12:00 to 15:00, nearest transit: Mob Museum, 48.14m away; Triple George Grill, visit from 15:30 to 16:30, nearest transit: Mob Museum, 87.09m away; Fremont Street Experience, visit from 17:00 to 19:00, nearest transit: Circa, 232.83m away; Top of the World, visit from 20:00 to 21:30, nearest transit: The Strat, 140.60m away; Luxury Suite - Balcony & Las Vegas Strip Views!, stay from 22:00 to 09:00, nearest transit: The Strat, 4778.06m away.

Day 3:
Current City: from Las Vegas to San Diego  
Transportation: Flight Number: F0562048, from Las Vegas to San Diego, Departure Time: 13:12, Arrival Time: 14:23  
Breakfast: Ameribrunch Cafe, Las Vegas
Attraction: Stratosphere Tower, Las Vegas
Lunch: -
Dinner: The Fish Market, San Diego
Accommodation: Beachside Resort, San Diego  
Event: -  
Point of Interest List:  
Luxury Suite - Balcony & Las Vegas Strip Views!, stay from 09:00 to 09:30, nearest transit: The Strat, 4778.06m away; Ameribrunch Cafe, visit from 10:00 to 10:30, nearest transit: Fremont East Entertainment District, 393.75m away; Stratosphere Tower, visit from 11:00 to 12:00, nearest transit: The Strat, 146.81m away; Beachside Resort, stay from 15:00 to 18:30, nearest transit: San Diego Downtown, 800.42m away; The Fish Market, visit from 19:00 to 20:30, nearest transit: San Diego Downtown, 500.76m away; Beachside Resort, stay from 21:00 to 09:00, nearest transit: San Diego Downtown, 800.42m away.

Day 4:  
Current City: San Diego  
Transportation: -  
Breakfast: Richard Walker's Pancake House, San Diego
Attraction: Balboa Park, San Diego; San Diego Zoo, San Diego
Lunch: The Prado at Balboa Park, San Diego
Dinner: George's at the Cove, San Diego
Accommodation: Beachside Resort, San Diego  
Event: -  
Point of Interest List:  
Beachside Resort, stay from 09:00 to 09:30, nearest transit: San Diego Downtown, 800.42m away; Richard Walker's Pancake House, visit from 10:00 to 10:30, nearest transit: San Diego Downtown, 200.23m away; Balboa Park, visit from 11:30 to 14:00, nearest transit: Balboa Transit Center, 300.45m away; The Prado at Balboa Park, visit from 14:30 to 15:30, nearest transit: Balboa Transit Center, 300.45m away; San Diego Zoo, visit from 16:00 to 18:30, nearest transit: Zoo Transit, 150.89m away; George's at the Cove, visit from 19:30 to 21:30, nearest transit: La Jolla Transit Center, 500.76m away; Beachside Resort, stay from 22:00 to 09:00, nearest transit: San Diego Downtown, 800.42m away.

Day 5:  
Current City: from San Diego to Washington  
Transportation: Flight Number: F0562049, from San Diego to Washington, Departure Time: 13:30, Arrival Time: 20:23  
Breakfast: Cafe 222, San Diego
Attraction: La Jolla Shores Beach, San Diego
Lunch: -
Dinner: -  
Accommodation: -  
Event: -  
Point of Interest List:  
Beachside Resort, stay from 09:00 to 09:30, nearest transit: San Diego Downtown, 800.42m away; Cafe 222, visit from 10:00 to 10:30, nearest transit: San Diego Downtown, 400.32m away; La Jolla Shores Beach, visit from 11:00 to 12:00, nearest transit: La Jolla Transit Center, 600.89m away.

****** Example 2 Ends ******

Given information: {text}
Query: {query}
Traveler Persona:
{persona}
Travel Plan:"""


# COT_PLANNER_INSTRUCTION = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and hotel names. Note that all the information in your plan should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with common sense. Attraction visits and meals are expected to be diverse. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B). 

# ***** Example *****
# Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?
# Travel Plan:
# Day 1:
# Current City: from Ithaca to Charlotte
# Transportation: Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46
# Breakfast: Nagaland's Kitchen, Charlotte
# Attraction: The Charlotte Museum of History, Charlotte
# Lunch: Cafe Maple Street, Charlotte
# Dinner: Bombay Vada Pav, Charlotte
# Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

# Day 2:
# Current City: Charlotte
# Transportation: -
# Breakfast: Olive Tree Cafe, Charlotte
# Attraction: The Mint Museum, Charlotte;Romare Bearden Park, Charlotte.
# Lunch: Birbal Ji Dhaba, Charlotte
# Dinner: Pind Balluchi, Charlotte
# Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

# Day 3:
# Current City: from Charlotte to Ithaca
# Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26
# Breakfast: Subway, Charlotte
# Attraction: Books Monument, Charlotte.
# Lunch: Olive Tree Cafe, Charlotte
# Dinner: Kylin Skybar, Charlotte
# Accommodation: -

# ***** Example Ends *****

# Given information: {text}
# Query: {query}
# Travel Plan: Let's think step by step. First, """

# REACT_PLANNER_INSTRUCTION = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and hotel names. Note that all the information in your plan should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with common sense. Attraction visits and meals are expected to be diverse. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B). Solve this task by alternating between Thought, Action, and Observation steps. The 'Thought' phase involves reasoning about the current situation. The 'Action' phase can be of two types:
# (1) CostEnquiry[Sub Plan]: This function calculates the cost of a detailed sub plan, which you need to input the people number and plan in JSON format. The sub plan should encompass a complete one-day plan. An example will be provided for reference.
# (2) Finish[Final Plan]: Use this function to indicate the completion of the task. You must submit a final, complete plan as an argument.
# ***** Example *****
# Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?
# You can call CostEnquiry like CostEnquiry[{{"people_number": 7,"day": 1,"current_city": "from Ithaca to Charlotte","transportation": "Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46","breakfast": "Nagaland's Kitchen, Charlotte","attraction": "The Charlotte Museum of History, Charlotte","lunch": "Cafe Maple Street, Charlotte","dinner": "Bombay Vada Pav, Charlotte","accommodation": "Affordable Spacious Refurbished Room in Bushwick!, Charlotte"}}]
# You can call Finish like Finish[Day: 1
# Current City: from Ithaca to Charlotte
# Transportation: Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46
# Breakfast: Nagaland's Kitchen, Charlotte
# Attraction: The Charlotte Museum of History, Charlotte
# Lunch: Cafe Maple Street, Charlotte
# Dinner: Bombay Vada Pav, Charlotte
# Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

# Day 2:
# Current City: Charlotte
# Transportation: -
# Breakfast: Olive Tree Cafe, Charlotte
# Attraction: The Mint Museum, Charlotte;Romare Bearden Park, Charlotte.
# Lunch: Birbal Ji Dhaba, Charlotte
# Dinner: Pind Balluchi, Charlotte
# Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

# Day 3:
# Current City: from Charlotte to Ithaca
# Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26
# Breakfast: Subway, Charlotte
# Attraction: Books Monument, Charlotte.
# Lunch: Olive Tree Cafe, Charlotte
# Dinner: Kylin Skybar, Charlotte
# Accommodation: -]
# ***** Example Ends *****

# You must use Finish to indict you have finished the task. And each action only calls one function once.
# Given information: {text}
# Query: {query}{scratchpad} """

# REFLECTION_HEADER = 'You have attempted to give a sub plan before and failed. The following reflection(s) give a suggestion to avoid failing to answer the query in the same way you did previously. Use them to improve your strategy of correctly planning.\n'

# REFLECT_INSTRUCTION = """You are an advanced reasoning agent that can improve based on self refection. You will be given a previous reasoning trial in which you were given access to an automatic cost calculation environment, a travel query to give plan and relevant information. Only the selection whose name and city match the given information will be calculated correctly. You were unsuccessful in creating a plan because you used up your set number of reasoning steps. In a few sentences, Diagnose a possible reason for failure and devise a new, concise, high level plan that aims to mitigate the same failure. Use complete sentences.  

# Given information: {text}

# Previous trial:
# Query: {query}{scratchpad}

# Reflection:"""

# REACT_REFLECT_PLANNER_INSTRUCTION = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and hotel names. Note that all the information in your plan should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with common sense. Attraction visits and meals are expected to be diverse. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B). Solve this task by alternating between Thought, Action, and Observation steps. The 'Thought' phase involves reasoning about the current situation. The 'Action' phase can be of two types:
# (1) CostEnquiry[Sub Plan]: This function calculates the cost of a detailed sub plan, which you need to input the people number and plan in JSON format. The sub plan should encompass a complete one-day plan. An example will be provided for reference.
# (2) Finish[Final Plan]: Use this function to indicate the completion of the task. You must submit a final, complete plan as an argument.
# ***** Example *****
# Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?
# You can call CostEnquiry like CostEnquiry[{{"people_number": 7,"day": 1,"current_city": "from Ithaca to Charlotte","transportation": "Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46","breakfast": "Nagaland's Kitchen, Charlotte","attraction": "The Charlotte Museum of History, Charlotte","lunch": "Cafe Maple Street, Charlotte","dinner": "Bombay Vada Pav, Charlotte","accommodation": "Affordable Spacious Refurbished Room in Bushwick!, Charlotte"}}]
# You can call Finish like Finish[Day: 1
# Current City: from Ithaca to Charlotte
# Transportation: Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46
# Breakfast: Nagaland's Kitchen, Charlotte
# Attraction: The Charlotte Museum of History, Charlotte
# Lunch: Cafe Maple Street, Charlotte
# Dinner: Bombay Vada Pav, Charlotte
# Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

# Day 2:
# Current City: Charlotte
# Transportation: -
# Breakfast: Olive Tree Cafe, Charlotte
# Attraction: The Mint Museum, Charlotte;Romare Bearden Park, Charlotte.
# Lunch: Birbal Ji Dhaba, Charlotte
# Dinner: Pind Balluchi, Charlotte
# Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

# Day 3:
# Current City: from Charlotte to Ithaca
# Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26
# Breakfast: Subway, Charlotte
# Attraction: Books Monument, Charlotte.
# Lunch: Olive Tree Cafe, Charlotte
# Dinner: Kylin Skybar, Charlotte
# Accommodation: -]
# ***** Example Ends *****

# {reflections}

# You must use Finish to indict you have finished the task. And each action only calls one function once.
# Given information: {text}
# Query: {query}{scratchpad} """

# planner_agent_prompt = PromptTemplate(
#                         input_variables=["text","query"],
#                         template = PLANNER_INSTRUCTION,
#                         )


planner_agent_prompt_mltp = PromptTemplate(
                        input_variables=["text","query","persona"],
                        template = PLANNER_INSTRUCTION_OG,
                        )

# cot_planner_agent_prompt = PromptTemplate(
#                         input_variables=["text","query"],
#                         template = COT_PLANNER_INSTRUCTION,
#                         )

# react_planner_agent_prompt = PromptTemplate(
#                         input_variables=["text","query", "scratchpad"],
#                         template = REACT_PLANNER_INSTRUCTION,
#                         )

# reflect_prompt = PromptTemplate(
#                         input_variables=["text", "query", "scratchpad"],
#                         template = REFLECT_INSTRUCTION,
#                         )

# react_reflect_planner_agent_prompt = PromptTemplate(
#                         input_variables=["text", "query", "reflections", "scratchpad"],
#                         template = REACT_REFLECT_PLANNER_INSTRUCTION,
                        # )
