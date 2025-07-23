import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../..")))

# Now you can safely import the necessary modules
import re
import json
import time
import argparse
import pandas as pd
from tqdm import tqdm
# from langchain.callbacks import get_openai_callback
from langchain_community.callbacks.manager import get_openai_callback
from tools.planner.apis import Planner, ReactPlanner, ReactReflectPlanner
import openai

# Change the working directory if needed
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from agents.prompts import planner_agent_prompt_direct_og, planner_agent_prompt_direct_param


def load_csv_data(filename):
    data = pd.read_csv(filename)
    return data

def catch_openai_api_error():
    error = sys.exc_info()[0]
    if error == openai.error.APIConnectionError:
        print("APIConnectionError")
    elif error == openai.error.RateLimitError:
        print("RateLimitError")
        time.sleep(60)
    elif error == openai.error.APIError:
        print("APIError")
    elif error == openai.error.AuthenticationError:
        print("AuthenticationError")
    else:
        print("API error:", error)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=str, default="3day")
    parser.add_argument("--set_type", type=str, default="validation")
    parser.add_argument("--model_name", type=str, default="gpt4o")
    parser.add_argument("--output_dir", type=str, default="./")
    parser.add_argument("--strategy", type=str, default="direct_og")
    parser.add_argument("--csv_file", type=str, required=True, help="Path to the reference_info.csv file")
    args = parser.parse_args()

    # Load data from CSV
    data = load_csv_data(args.csv_file)

    # Ensure 'query', 'reference_information' columns exist
    
    # Prepare the dataset
    query_data_list = data.to_dict(orient='records')

    # Define planner based on strategy
    if args.strategy == 'direct_og':
        planner = Planner(model_name=args.model_name, agent_prompt=planner_agent_prompt_direct_og)
    else:
        if args.strategy == 'direct_param':
            planner = Planner(model_name=args.model_name, agent_prompt=cot_planner_agent_prompt_param)

    # Iterate over data and generate results
    with get_openai_callback() as cb:
        for number, query_data in enumerate(tqdm(query_data_list, desc="Processing data")):
            if args.day == '3day':
                reference_information = query_data['reference_information']
            elif args.day == '5day':
                reference_information_1 = json.loads(query_data['reference_information_1'])
                reference_information_2 = json.loads(query_data['reference_information_2'])
                reference_information = json.dumps(reference_information_1 + reference_information_2)
            else:
                reference_information_1 = json.loads(query_data['reference_information_1'])
                reference_information_2 = json.loads(query_data['reference_information_2'])
                reference_information_3 = json.loads(query_data['reference_information_3'])
                reference_information = json.dumps(reference_information_1 + reference_information_2 + reference_information_3)
            while True:
                if args.strategy in ['react', 'reflexion']:
                    planner_results, scratchpad = planner.run(reference_information, query_data['query'], query['persona'])
                else:
                    planner_results = planner.run(reference_information, query_data['query'],query_data['persona'])
                    time.sleep(8)
                if planner_results is not None:
                    break
            print(planner_results)

            # Ensure the directory exists
            output_dir = os.path.join(args.output_dir, args.set_type)
            os.makedirs(output_dir, exist_ok=True)

            # Load previous results if available
            result_file = os.path.join(output_dir, f'gpt4o_orig_generated_plan_{number+1}.json')
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    result = json.load(f)
            else:
                result = [{}]

            # Store the new results
            # if args.strategy in ['react', 'reflexion']:
            #     result[-1][f'{args.model_name}_{args.strategy}_sole-planning_results_logs'] = scratchpad
            
            result[-1][f'{args.model_name}_{args.strategy}_sole-planning_results'] = planner_results

            # Write to JSON file
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=4)

        print(cb)
