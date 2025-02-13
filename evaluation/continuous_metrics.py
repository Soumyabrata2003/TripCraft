import json
import pandas as pd
import numpy as np
import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import math
import numpy as np
from scipy.stats import multivariate_normal, poisson


# Load the cleaned attractions data
attractions_data = pd.read_csv('attraction_csv_path')

def get_mu_d_type(attraction, city, attractions_data):
    """
    Get the visit duration (mu_d_type) for a given attraction and city.

    Args:
        attraction (str): The name of the attraction.
        city (str): The city of the attraction.
        attractions_data (pd.DataFrame): DataFrame containing attraction information.

    Returns:
        float: The visit duration (mu_d_type) for the matching attraction and city.
    """
    # Filter rows that match both the attraction name and city
    match = attractions_data[
        (attractions_data["City"].str.strip().str.lower() == city.strip().lower()) &
        (attractions_data["name"].str.strip().str.lower() == attraction.strip().lower())
    ]
    
    # If a match is found, return the visit duration
    if not match.empty:
        return int(match.iloc[0]["visit_duration"])
    else:
        # Handle the case where no match is found (default or raise an error)
        raise ValueError(f"No matching entry found for attraction '{attraction}' in city '{city}'.")

def get_bert_embedding(text, tokenizer, model):
    """Encodes text into a BERT embedding."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze(0).numpy()


def compute_persona_score(travel_plan, bert_model, bert_tokenizer):
    """Compute the persona score for the travel plan."""
    # Extract persona details
    persona = travel_plan["persona"]
    persona_components = {
        "Traveler Type": None,
        "Purpose of Travel": None,
        "Spending Preference": None,
        "Location Preference": None
    }

    for key in persona_components.keys():
        start_idx = persona.find(key + ":") + len(key) + 1
        end_idx = persona.find(";", start_idx)
        if end_idx == -1:  # Last component
            end_idx = len(persona)
        persona_components[key] = persona[start_idx:end_idx].strip()

    # Encode persona components
    persona_embeddings = {
        key: get_bert_embedding(value, bert_tokenizer, bert_model)
        for key, value in persona_components.items()
    }

    # Initialize counters
    total_score = 0
    total_pois = 0

    # Iterate through all days in the plan
    for day in travel_plan["plan"]:
        poi_list = day["point_of_interest_list"].split(";")
        # all_events = day["event"].split(";")

        for poi in poi_list:
            # Extract PoI name (up to first comma)
            # poi_name = poi.split(",")[0].strip()
            if "stay" in poi:
                poi_name = poi.split("stay")[0].strip()[:-1]
            else:
                poi_name = poi.split("visit")[0].strip()[:-1]

            poi_embedding = get_bert_embedding(poi_name, bert_tokenizer, bert_model)

            # Compute similarity for each persona component
            poi_score = 0
            for key, persona_embedding in persona_embeddings.items():
                poi_score += cosine_similarity([persona_embedding], [poi_embedding])[0][0]

            # Average similarity over persona components
            poi_score /= len(persona_components)

            # Add to total score and increment counter
            total_score += poi_score
            total_pois += 1

    # Final persona score (average over all PoIs)
    avg_persona_score = total_score / total_pois if total_pois > 0 else 0

    return avg_persona_score

def calculate_persona_score(travel_plan):
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertModel.from_pretrained("bert-base-uncased")
    persona_score = compute_persona_score(travel_plan, model, tokenizer)
    return persona_score

# Function to calculate Weighted Edit Distance (WED)
def calculate_wed(gen_sequence, anno_sequence, weight_fn):
    m, n = len(gen_sequence), len(anno_sequence)
    dp = np.full((m + 1, n + 1), np.inf)  # Initialize the DP matrix
    dp[0][0] = 0  # Base case: no cost for empty sequences
    
    # Fill DP table with the edit distance calculation
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = weight_fn(gen_sequence[i - 1], anno_sequence[j - 1])
            dp[i][j] = cost + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    return dp[m][n]

# Define a basic weight function for cost calculation
def weight_fn(a, b):
    if a == b:
        return 0
    if {a, b} == {"x", "y"} or {a, b} == {"y", "z"} or {a, b} == {"x", "z"}:
        return 1  # Unweighted ED # Mismatched types with high cost
    return 1  # Default cost for other mismatches

def get_poi_sequence(plan_day):
    poi_list = plan_day["point_of_interest_list"]
    
    # Extract names from the relevant fields using rsplit to get rid of extra details
    accommodation = plan_day.get("accommodation", "").rsplit(",", 1)[0].strip()
    breakfast = plan_day.get("breakfast", "").rsplit(",", 1)[0].strip()
    lunch = plan_day.get("lunch", "").rsplit(",", 1)[0].strip()
    dinner = plan_day.get("dinner", "").rsplit(",", 1)[0].strip()
    # attractions_list = [attraction.rsplit(",", 1)[0].strip() for attraction in plan_day.get("attraction", "").split(";")]

    seq = []
    
    # Split the poi_list into items based on semicolons
    for poi in poi_list.split(";"):
        if breakfast in poi:
            seq.append("y")  # Restaurant (breakfast)
        elif lunch in poi:
            seq.append("y")  # Restaurant (lunch)
        elif dinner in poi:
            seq.append("y")  # Restaurant (dinner)
        elif accommodation in poi:
            seq.append("x")  # Accommodation
        else:
            seq.append("z")  # Attraction
    
    return seq


# Function to calculate average WED over days in the travel plan
def calculate_ordering_score(travel_plan, gen_travel_plan):
    total_wed = 0
    num_days = len(travel_plan["plan"])

    for day in travel_plan["plan"][:2]:  # First 2 days of travel_plan
        for day_dash in gen_travel_plan["plan"][:2]:  # First 2 days of gen_travel_plan
            gen_sequence = get_poi_sequence(day_dash)
            anno_sequence = get_poi_sequence(day)
        
            # Calculate WED and add to total
            wed = calculate_wed(gen_sequence, anno_sequence, weight_fn)
            total_wed += wed

    # Add WED for day 3 of travel_plan with day 3 of gen_travel_plan
    gen_sequence_day3 = get_poi_sequence(gen_travel_plan["plan"][2])  # Day 3 of gen_travel_plan
    anno_sequence_day3 = get_poi_sequence(travel_plan["plan"][2])  # Day 3 of travel_plan
    wed_day3 = calculate_wed(gen_sequence_day3, anno_sequence_day3, weight_fn)

    # Add to total WED
    total_wed += wed_day3

    # Average WED over all days
    # average_wed = total_wed / (num_days*num_days)
    # average_wed = total_wed / (num_days)
    average_wed = total_wed / ((num_days-1)*(num_days-1) + 1)
    return 1 - (average_wed / max(len(gen_sequence), len(anno_sequence)))


def calculate_spatial_score(travel_plan):
    def lin_exp_score(distance):
        if distance <= 5000:
            return 1 - 0.5 * (distance / 5000)
        else:
            return 0.5 * np.exp(-0.0002 * (distance - 5000))

    total_days_score = 0
    total_days = 0

    for day in travel_plan["plan"]:
        point_of_interest_list = day["point_of_interest_list"]
        pois = point_of_interest_list.split(";")
        day_scores = []

        for poi in pois:
            if "nearest transit:" in poi:
                transit_info = poi.split("nearest transit:")[1].strip()
                if "," in transit_info:
                    distance_str = transit_info.split(",")[-1].strip().split("m")[0].strip()
                    try:
                        distance = float(distance_str)
                        day_scores.append(lin_exp_score(distance))
                    except ValueError:
                        continue  # Skip if distance cannot be parsed

        if day_scores:
            average_day_score = np.mean(day_scores)
            total_days_score += average_day_score
            total_days += 1

    if total_days > 0:
        overall_average_score = total_days_score / total_days
    else:
        overall_average_score = 0  # Default to 0 if no valid data found

    return overall_average_score


def calculate_temporal_score(travel_plan):
    results = []

    # Parameters for restaurants
    restaurant_params = {
        "breakfast": {"mean_time": 9.84, "mean_duration": 50.71/60, "std_time": 1.34, "std_duration": 14.09/60, "beta": 0.03},
        "lunch": {"mean_time": 14.44, "mean_duration": 59.19/60, "std_time": 1.07, "std_duration": 15.82/60, "beta": 0.30},
        "dinner": {"mean_time": 20.42, "mean_duration": 69.27/60, "std_time": 1.66, "std_duration": 69.07/60, "beta": -0.07},
    }

    lambda_laidback = 1.11
    lambda_adventurous = 1.82 #3.5
    sigma_d = 53.82/60
    # mu_d_type = 2.0
    mu_d_max = 4 #2.5
    mu_d_min = 0 #1.0
    k = 16.61/60

    for day_plan in travel_plan["plan"]:
        day_result = {"day": day_plan["days"]}

        # Calculate restaurant scores
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

                    if day_plan_meal in poi:
                        # time_info = poi.split("from")[1].split("to")
                        # start_time = time_info[0].strip()
                        # end_time = time_info[1].split(",")[0].strip()
                        try:
                            time_info = poi.split("from")[1].split("to")
                            print(time_info)
                            start_time = time_info[0].strip()
                            end_time = time_info[1].split(",")[0].strip()
                        except:
                            time_info = poi.rsplit("from", 1)[1].split("to")
                            print(time_info)
                            start_time = time_info[0].strip()
                            end_time = time_info[1].split(",")[0].strip()

                        start_hour = int(start_time.split(":")[0]) + int(start_time.split(":")[1]) / 60
                        end_hour = int(end_time.split(":")[0]) + int(end_time.split(":")[1]) / 60

                        midpoint = (start_hour + end_hour) / 2
                        duration = end_hour - start_hour

                        params = restaurant_params[meal]
                        mu = [params["mean_time"], params["mean_duration"]]
                        cov = [
                            [params["std_time"] ** 2, params["beta"] * params["std_time"] * params["std_duration"]],
                            [params["beta"] * params["std_time"] * params["std_duration"], params["std_duration"] ** 2],
                        ]

                        score = multivariate_normal.pdf([midpoint, duration], mean=mu, cov=cov)
                        k = len(mu)  # Dimensionality of the distribution
                        det_cov = np.linalg.det(cov)
                        max_pdf = 1 / np.sqrt((2 * np.pi) ** k * det_cov)
    
                        # Normalize the score
                        normalized_score = score / max_pdf
                        day_result[f"{meal}_score"] = normalized_score
                        break

        # Calculate attraction score
        attractions = day_plan["attraction"].split(";")
        num_attractions = len(attractions)
        attraction_scores = []

        for attraction in attractions:
            if "," in attraction:
                attraction, city = attraction.rsplit(",", 1)
                attraction = attraction.strip()
                city = city.strip()
            else:
                # Fallback if no city is mentioned
                attraction = attraction.strip()
                city = ""

            for poi in day_plan["point_of_interest_list"].split(";"):
                if attraction.strip() in poi and attraction.strip() != "-":
                    try:
                        time_info = poi.split("from")[1].split("to")
                        print(time_info)
                        start_time = time_info[0].strip()
                        end_time = time_info[1].split(",")[0].strip()
                    except:
                        time_info = poi.rsplit("from", 1)[1].split("to")
                        print(time_info)
                        start_time = time_info[0].strip()
                        end_time = time_info[1].split(",")[0].strip()
                    
                    start_hour = int(start_time.split(":")[0]) + int(start_time.split(":")[1]) / 60
                    end_hour = int(end_time.split(":")[0]) + int(end_time.split(":")[1]) / 60
                    duration = end_hour - start_hour

                    # Dynamically calculate mu_d_type
                    try:
                        mu_d_type = get_mu_d_type(attraction, city, attractions_data)
                    except ValueError as e:
                        print(e)
                        continue  # Skip this attraction if no match is found

                    if "Adventure Seeker" in travel_plan["persona"]:
                        # mu_d = 195.53 - k * num_attractions 
                        mu_d = mu_d_type - k * (num_attractions - mu_d_min)
                        duration_score = np.exp(-((duration - mu_d) ** 2) / (2 * sigma_d**2))
                        num_attraction_prob = poisson.pmf(num_attractions, lambda_adventurous)
                    else:
                        # mu_d = 195.53 - k * num_attractions 
                        mu_d = mu_d_type + k * (mu_d_max - num_attractions)
                        duration_score = np.exp(-((duration - mu_d) ** 2) / (2 * sigma_d**2))
                        num_attraction_prob = poisson.pmf(num_attractions, lambda_laidback)

                    attraction_scores.append(duration_score * num_attraction_prob)

        if attraction_scores:
            day_result["attraction_score"] = np.mean(attraction_scores)

        results.append(day_result)

    total_meal_score = 0
    total_attraction_score = 0
    meal_count = 0  # Counter for meals
    attraction_count = 0
    # days_count = len(results)

    # Iterate through results to calculate sums
    for entry in results:
        # Add meal scores only if they exist
        if "breakfast_score" in entry:
            total_meal_score += entry["breakfast_score"]
            meal_count += 1
        if "lunch_score" in entry:
            total_meal_score += entry["lunch_score"]
            meal_count += 1
        if "dinner_score" in entry:
            total_meal_score += entry["dinner_score"]
            meal_count += 1
        if "attraction_score" in entry:
            total_attraction_score += entry["attraction_score"]
            attraction_count += 1

    # Calculate averages
    average_meal_score = total_meal_score / meal_count if meal_count > 0 else 0
    average_attraction_score = total_attraction_score / attraction_count if attraction_count > 0 else 0


    return {"meal_score": average_meal_score, "attraction_score": average_attraction_score}


if __name__ == '__main__':
    # Path to your jsonl file
    jsonl_file_path = 'path_to_output_jsonl.jsonl'
    gen_jsonl_file_path = 'path_to_anno_jsonl.jsonl'

    metrics_list = []
    progress = 0

    # Open both files simultaneously
    with open(jsonl_file_path, 'r', encoding='utf-8') as file1, open(gen_jsonl_file_path, 'r', encoding='utf-8') as file2:
        for line1, line2 in zip(file1, file2):
            # Parse each line as a JSON object
            progress += 1
            json_object1 = json.loads(line1)
            json_object2 = json.loads(line2)
        
            if json_object1["plan"][0]["days"] == 0:
                metrics_list.append({"temporal_score": -1, "spatial_score": -1, "ordering_score": -1, "persona_score": -1})
            else:
                metrics_list.append({"temporal_score": calculate_temporal_score(json_object1), "spatial_score": calculate_spatial_score(json_object1, json_object2), "ordering_score": calculate_ordering_score(json_object1), "persona_score": calculate_persona_score(json_object1)})
            print(progress)  # Access the JSON object (a dictionary in Python)

    print(len(metrics_list))
    for met_dict in metrics_list:
        print(met_dict)

    sum_meal_sc = 0
    sum_attrac_sc = 0
    sum_spatial_sc = 0
    sum_ord_sc = 0
    sum_persona_sc = 0
    num = 0 #len(metrics_list_new)

    for i in range(len(metrics_list)):
        for key in metrics_list[i]:
            if key == "temporal_score":
                if metrics_list[i][key] == -1:
                    continue
                else:
                    sum_meal_sc += metrics_list[i][key]["meal_score"]
                    sum_attrac_sc += metrics_list[i][key]["attraction_score"]
                    num +=1
            elif key == "spatial_score":
                if metrics_list[i][key] == -1:
                    continue
                else:
                    sum_spatial_sc += metrics_list[i][key]
            elif key == "ordering_score":
                if metrics_list[i][key] == -1:
                    continue
                else:
                    sum_ord_sc += metrics_list[i][key]
            else:
                if metrics_list[i][key] == -1:
                    continue
                else:
                    sum_persona_sc += metrics_list[i][key]

    print(num)
    print("avg_meal_temporal:", sum_meal_sc/num)
    print("avg_attrac_temporal:", sum_attrac_sc/num)
    print("avg_spatial:", sum_spatial_sc/num)
    print("avg_ord:", sum_ord_sc/num)
    print("avg_persona:", sum_persona_sc/num)

