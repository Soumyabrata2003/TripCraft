from tqdm import tqdm
import argparse
import random
import json
import os
from openai_request import build_query_generation_prompt,prompt_chatgpt


def load_jsonl_file(file_path, n_samples):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    random.shuffle(lines)
    return [json.loads(line) for line in lines[:n_samples]]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--set_type", type=str, default="validation")
    parser.add_argument("--model_name", type=str, default="gpt-3.5-turbo-1106")
    parser.add_argument("--mode", type=str, default="two-stage")
    parser.add_argument("--strategy", type=str, default="direct")
    parser.add_argument("--output_dir", type=str, default="./")
    parser.add_argument("--jsonl_dir", type=str, default="./")
    parser.add_argument("--total_samples", type=int, default=50, help="Number of samples to be drawn equally from each JSONL file")
    args = parser.parse_args()

    if args.mode == 'two-stage':
        suffix = ''
    elif args.mode == 'sole-planning':
        suffix = f'_{args.strategy}'

    # Calculate samples per file
    samples_per_file = args.total_samples // 3

    # Load data from files
    easy_data = load_jsonl_file(os.path.join(args.jsonl_dir, 'final_annotation_easy.jsonl'), samples_per_file)
    medium_data = load_jsonl_file(os.path.join(args.jsonl_dir, 'final_annotation_medium.jsonl'), samples_per_file)
    hard_data = load_jsonl_file(os.path.join(args.jsonl_dir, 'final_annotation_hard.jsonl'), samples_per_file)
    combined_data = easy_data + medium_data + hard_data

    # Build prompts
    data = build_query_generation_prompt(combined_data)
    output_file = f'{args.tmp_dir}/{args.set_type}_{args.model_name}{suffix}_{args.mode}.txt'

    total_price = 0
    for idx, prompt in enumerate(tqdm(data)):
        if prompt == "":
            with open(output_file, 'a+', encoding='utf-8') as f:
                assistant_output = str(idx)
                f.write(assistant_output + '\n')
            continue
        results, _, price = prompt_chatgpt("You are a helpful assistant.", index=idx, save_path=output_file,
                                           user_input=prompt, model_name='gpt-4-1106-preview', temperature=0)
        total_price += price

    print(f"Parsing Cost:${total_price}")
