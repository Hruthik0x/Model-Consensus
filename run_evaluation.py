import os

os.system(
    "python -m truthfulqa.evaluate "
    "--models api_model --metrics mc bleu "
    "--input_path data/TruthfulQA_with_api.csv "
    "--output_path data/TruthfulQA_api_answers.csv"
)
