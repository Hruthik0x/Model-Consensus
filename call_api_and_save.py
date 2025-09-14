# call_api_and_save.py
import argparse
import pandas as pd
import requests
import time
import sys
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", default="TruthfulQA_demo.csv", help="input CSV (must contain question column)")
    p.add_argument("--output", "-o", default="TruthfulQA_with_api.csv", help="output CSV (will add answers column)")
    p.add_argument("--api", default="http://127.0.0.1:5000/ask", help="API endpoint (POST expecting JSON {'question':...})")
    p.add_argument("--qcol", default=None, help="question column name in CSV (auto try 'Question' then 'question')")
    p.add_argument("--acol", default="api_model", help="name of new answer column to store responses")
    p.add_argument("--delay", type=float, default=0.2, help="delay between requests (seconds)")
    p.add_argument("--timeout", type=float, default=10.0, help="request timeout (seconds)")
    args = p.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        print("Input file not found:", inp.resolve())
        sys.exit(1)

    df = pd.read_csv(inp)
    # try to find a question column
    qcol = args.qcol
    if qcol is None:
        for trycol in ("Question", "question", "prompt", "text"):
            if trycol in df.columns:
                qcol = trycol
                break
    if qcol is None:
        print("Could not find question column. Columns available:", df.columns.tolist())
        sys.exit(1)

    print(f"Using question column: {qcol}")
    answers = []
    session = requests.Session()
    for i, q in enumerate(df[qcol].astype(str).tolist()):
        if i % 10 == 0:
            print(f"Processing {i}/{len(df)}")
        try:
            resp = session.post(args.api, json={"question": q}, timeout=args.timeout)
            if resp.status_code == 200:
                data = resp.json()
                # assume reply in data['answer'] (adjust if your API uses a different key)
                answer = data.get("answer") if isinstance(data, dict) else str(data)
            else:
                answer = f"[HTTP {resp.status_code}]"
        except Exception as e:
            answer = f"[ERR] {e}"
        answers.append(answer)
        time.sleep(args.delay)

    df[args.acol] = answers
    df.to_csv(args.output, index=False)
    print("Saved results to", args.output)

if __name__ == "__main__":
    main()
