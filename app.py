from flask import Flask, request, jsonify
from flask_cors import CORS
from core import generate_workout_plan

app = Flask(__name__)
CORS(app)  # Allow frontend (like React/Vite) to access this API

@app.route("/")
def health_check():
    return jsonify({"status": "ok", "message": "ShyFit API is up and running!"})

# @app.route("/api/workout-plan", methods=["POST"])
@app.route("/api/workout-plan", methods=["POST"])


def workout_plan():
    try:
        user_data = request.get_json()
        # user_data = {
        # "age": 24,
        # "gender": "male",
        # "height": 100,
        # "weight": 180,
        # "goal": "fat loss",
        # "muscles": "full body",
        # "level": "beginner",
        # "duration": 60,
        # "days": 6,
        # "location": "Home"
        # }

        if not user_data:
            return jsonify({"error": "Missing JSON data"}), 400

        response = generate_workout_plan(user_data)
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
