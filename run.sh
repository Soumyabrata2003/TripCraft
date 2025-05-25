#!/bin/bash

# Export environment variables with paths
export OUTPUT_DIR="/home/soumya/TripCraft/output"    # Path to your output directory
export MODEL_NAME="gpt-4o"     #qwen    #phi4             # Model name (you can change it as needed)
export OPENAI_API_KEY="YOUR_OPENAI_KEY"             # Your OpenAI API key
# export GOOGLE_API_KEY="YOUR_GOOGLE_KEY"                 # Your Google API key
export SET_TYPE="3day_gpt4o_orig"                            # Set type- name of folder in O/P directory where generated outputs get saved 
export STRATEGY="direct_og"                                # direct_parameter_info / direct_og
export CSV_FILE="/home/soumya/TripCraft/final_3day_dataset.csv"  # Path to your CSV file

# Navigate to the planner directory
cd tools/planner

# Run the Python script with the environment variables
python sole_planning_mltp.py \
    --set_type $SET_TYPE \
    --output_dir $OUTPUT_DIR \
    --csv_file $CSV_FILE \
    --model_name $MODEL_NAME \
    --strategy $STRATEGY
