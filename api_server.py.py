from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    # Dummy answer (you can replace with model/API call later)
    answer = f"Dummy answer for: {question}"
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(port=5000)
