<div align="center">
<h1 align="center">🧙‍♀️TripCraft🌍: A Benchmark for Spatio-Temporally Fine Grained Travel Planning【ACL'25 (Main)】</h1>

<p align="center">
  <a href="https://arxiv.org/abs/2502.20508">
    <img src="https://img.shields.io/badge/Arxiv-2311.15732-b31b1b.svg?logo=arXiv" alt="arXiv">
  </a>
</p>


<p align="center">
    <img src="images/fig1.png" width="100%"> <br>
</p>

This is the official implementation of **TripCraft**, a new benchmark for LLM driven personalized travel planning, offering a more realistic, constraint aware framework for itinerary generation.
</div>

<p align="center">
[<a href="https://arxiv.org/abs/2502.20508">Paper</a>] •
[<a>Dataset_to_be_updated</a>] 
</p>

## 📢 News

- 2025/05/16: 🎉 Our **TripCraft** has been accepted to the Main Track of ACL 2025.

# 🧭 TripCraft Overview

We introduce TripCraft, a spatiotemporally coherent travel planning dataset that integrates real world constraints, including public transit schedules, event availability, diverse attraction categories, and user personas for enhanced personalization. To evaluate LLM generated plans beyond existing binary validation methods, we propose five continuous evaluation metrics, namely Temporal Meal Score, Temporal Attraction Score, Spatial Score, Ordering Score, and Persona Score which assess itinerary quality across multiple dimensions. 

## 🐍 Setup Environment
Ensure that minconda/anaconda is installed in your system beforehand.
1. Check whether conda is installed using:
```bash
conda --version
```
2. Emulate Tripcraft's conda environment and install dependencies:
```bash
conda env create -f tpct_env.yml -n tripcraft
conda activate
```

2. Download the [database](link_yet_to_be_updated) and unzip it to the `TripCraft` directory (i.e., `your/path/TripCraft`).

## 🚀 Running
TripCraft offers experimentation in two settings: w/o parameter information and with parameter information mode. Change the run.sh file accordingly for both the settings.
Please refer to the paper for more details.

```bash
bash run.sh
```
*Note:* All Experiments were run on a single NVIDIA L40 GPU setup.

## 🛠️ Postprocess

In order to parse natural language plans, we use gpt-4 to convert these plans into json formats. We encourage developers to try different parsing prompts to obtain better-formatted plans.

```bash
export OUTPUT_DIR=path/to/your/output/file
export MODEL_NAME=MODEL_NAME
export OPENAI_API_KEY=YOUR_OPENAI_KEY
export SET_TYPE=validation
export STRATEGY=direct
# MODE in ['two-stage','sole-planning']
export MODE=two-stage
export TMP_DIR=path/to/tmp/parsed/plan/file
export SUBMISSION_DIR=path/to/your/evaluation/file

cd postprocess
python parsing.py  --set_type $SET_TYPE --output_dir $OUTPUT_DIR --model_name $MODEL_NAME --strategy $STRATEGY --mode $MODE --tmp_dir $TMP_DIR

# Then these parsed plans should be stored as the real json formats.
python element_extraction.py  --set_type $SET_TYPE --output_dir $OUTPUT_DIR --model_name $MODEL_NAME --strategy $STRATEGY --mode $MODE --tmp_dir $TMP_DIR

# Finally, combine these plan files for evaluation. We also provide a evaluation example file "example_evaluation.jsonl" in the postprocess folder.
python combination.py --set_type $SET_TYPE --output_dir $OUTPUT_DIR --model_name $MODEL_NAME --strategy $STRATEGY --mode $MODE  --submission_file_dir $SUBMISSION_DIR
```

<a name="testing"></a>
## ⚡ Evaluation


```sh


```

<a name="bibtex"></a>
## 📌 BibTeX & Citation

If you use our code in your research or wish to refer to the baseline results, please use the following BibTeX entry😁.


```bibtex
@article{chaudhuri2025tripcraft,
  title={Tripcraft: A benchmark for spatio-temporally fine grained travel planning},
  author={Chaudhuri, Soumyabrata and Purkar, Pranav and Raghav, Ritwik and Mallick, Shubhojit and Gupta, Manish and Jana, Abhik and Ghosh, Shreya},
  journal={arXiv preprint arXiv:2502.20508},
  year={2025}
```


<a name="acknowledgment"></a>
## 🎗️ Acknowledgement

This repository is partially built based on [TravelPlanner](https://github.com/OSU-NLP-Group/TravelPlanner?tab=readme-ov-file). Sincere thanks to their wonderful work.


## 👫 Contact
For any question, please file an issue.
