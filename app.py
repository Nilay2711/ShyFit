from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from core import generate_workout_plan

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html") 

@app.route("/health")
def health_check():
    return jsonify({"status": "ok", "message": "ShyFit API is up and running!"})

@app.route("/api/workout-plan", methods=["POST"])
def workout_plan():
    try:
        user_data = request.get_json()

        if not user_data:
            return jsonify({"error": "Missing JSON data"}), 400

        response = generate_workout_plan(user_data)
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)