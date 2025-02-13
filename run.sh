#!/bin/bash

# Export environment variables with paths
export OUTPUT_DIR="/home/mtech/TravelPlanner/output"    # Path to your output directory
export MODEL_NAME="gpt-4o" #"gpt-4-1106-preview"    # o1-preview" #"gpt-3.5-turbo"             # Model name (you can change it as needed)
export OPENAI_API_KEY="YOUR_OPENAI_KEY"             # Your OpenAI API key
# export GOOGLE_API_KEY="YOUR_GOOGLE_KEY"                 # Your Google API key
export SET_TYPE="sample_10"                            # Set type (change as needed)
export STRATEGY="direct"                                # Strategy type (change as needed)
export CSV_FILE="/home/mtech/MLTP/sample10_3day.csv"  # Path to your CSV file

# Navigate to the planner directory
cd tools/planner

# Run the Python script with the environment variables
python sole_planning_mltp.py \
    --set_type $SET_TYPE \
    --output_dir $OUTPUT_DIR \
    --csv_file $CSV_FILE \
    --model_name $MODEL_NAME \
    --strategy $STRATEGY
