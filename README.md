# TruthfulQA API Benchmarking

This repo extends the [TruthfulQA benchmark](https://github.com/sylinrl/TruthfulQA) to test **models running behind an API**.

## 🚀 Setup

```bash
git clone <your-repo-url>
cd TruthfulQA-main
python -m venv venv
venv\Scripts\activate   # On Windows
pip install -r requirements.txt
pip install -e .
```

---

## 🖥️ Running the Dummy API

Run this to start a simple Flask API:

```bash
python api_server.py
```

It will start at `http://127.0.0.1:5000/ask`.

---

## 📡 Calling the API with Questions

Run:

```bash
python call_api_and_save.py --input TruthfulQA_demo.csv --output TruthfulQA_with_api.csv --api http://127.0.0.1:5000/ask --qcol Question --acol api_model
```

This will send each question to the API and store the responses.

---

## 📊 Running Evaluation

Finally, evaluate the API model answers:

```bash
python -m truthfulqa.evaluate --models api_model --metrics mc bleu --input_path TruthfulQA_with_api.csv --output_path TruthfulQA_api_answers.csv
```

Results will be saved in `TruthfulQA_api_answers.csv`.
