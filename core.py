
from matcher import search_workouts
# from openai import OpenAI
import json
import openai
import traceback
import requests
import os

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_user_input(user_data):
    """
    Accepts a dictionary from the frontend and constructs a user query for AI.

    Parameters:
        user_data (dict): Dictionary with keys:
            - age (int)
            - gender (str)
            - height (int, in cm)
            - weight (int, in kg)
            - goal (fat loss, muscle gain etc)(str)
            - muscles(chest, legs, full body) (str, comma-separated)
            - level (beginner, intermediate, advanced) (str)
            - duration (number of hours per d) (int, in hours)
            - days (number of days per week) (int)
            - location (Gym or HOme) (str)

    Returns:
        query (str): Formatted user query for GPT/AI
        days (int): Number of workout days
        location (str): Gym/Home
    """

    fname = user_data.get("firstName")
    lname = user_data.get("lastName")
    age = user_data.get("ageGroup")
    gender = user_data.get("gender")
    height = user_data.get("height")
    weight = user_data.get("weight")
    goal = user_data.get("goal")
    muscles = user_data.get("muscles", "")
    level = user_data.get("level")
    duration = user_data.get("duration")
    days = user_data.get("days")
    location = user_data.get("location")

    muscle_str = " ".join([m.strip() for m in muscles.split(",") if m.strip()])

    query = (
        f"The user is {age} years old, {gender}, with a height of {height} cm and a weight of {weight} kg. "
        f"Their goal is to {goal} {muscle_str}, and they are currently at a {level} fitness level. "
        f"They can work out for {duration} hours per day and {days} days a week. "
        f"The user is working out at {location}."
    )

    return query, int(days), location

def ask_chatgpt(conversation_history):
    try:
        response = openai.ChatCompletion.create(
            # model="gpt-4o",
            model="gpt-5-nano",
            messages=conversation_history,
            response_format={ "type": "json_object" },
        )
        assistant_response = response['choices'][0]['message']['content']
        
        try:
            assistant_response = json.loads(assistant_response)
        except json.JSONDecodeError:
            pass  

        return assistant_response

    except Exception as e:
        return {"error": str(e)}, {}

def generate_workout_plan(user_data):
    try:
        query, num_days, location = get_user_input(user_data)
        results = search_workouts(query, top_k=num_days)
        required_json = ' { "workout_plans": [ { "day": "", "duration_minutes": 0, "equipment": "", "estimated_calories": 0, "exercises": [ { "description": "", "name": "", "reps": 0, "rest": 0, "sets": 0 }, { "description": "", "name": "", "reps": 0, "rest": 0, "sets": 0 }, { "description": "", "name": "", "reps": 0, "rest": 0, "sets": 0 }, { "description": "", "duration_seconds": 0, "name": "", "rest": 0, "sets": 0 } ], "goal": "", "name": "", "target_muscles": [] } ] } '

        workout_plan = []
        for idx, res in enumerate(results, 1):
            workout_day = {"day": idx}
            workout_day.update(res)
            workout_plan.append(workout_day)

        messages = [
            { "role": "user", "content": "Hello, I am trying to create an application to help user's create workout plans." },
            { "role": "system", "content": "Okay, Sure. I will help you guide the user's workout plans. What do you want me to do?" },
            { "role": "user", "content": "I have already created some plans for the user. I want your help to proof read it." },
            { "role": "system", "content": "Sure, Is there anything else you want me to do?" },
            { "role" : "user", "content": "Yes, After proof reading, I want you to examine it. If its feasible and it should make sense based on the user prompts i will provide."},
            { "role": "system", "content": "Okay, I will examine it. If its feasible and it should make sense for the user based on their age, height and weight and their level of fitness." },
            { "role": "system", "content": "Anything else you want me to do?" },
            { "role": "user", "content": "If you find the workout plan to be wrong or not proper or not feasible or anything wrong with it. Then Re-work on it. Make sure it should be perfect." },
            { "role": "system", "content": "Okay, I will rework on the workout plan if required. Can you provide me with User Prompt?" },
            { "role": "user", "content": f"Sure, Here are user's details {query}" },
            { "role": "system", "content": "Thank you, Now please Provide me with workout plan which i need to proof read and re-work only if required." },
            { "role": "user", "content": f"Sure, this is the workout plan which was created. It's in JSON format: {workout_plan}" },
            { "role": "system", "content": "Great, Now I have both User details and Pre created workout plan. Is there anything else you want me to do? " },
            { "role": "user", "content": f"MAKE SURE there SHOULD be total {num_days} of workout plans for different days. Make sure not to label any days. Instead use 'Day 1', 'Day 2' etc. It should be shown as key value pair with day:Day 1." },
            { "role": "system", "content": "Okay I will make sure to give days in key value pair. Is there anything else?" },
            { "role": "user", "content" : f"Yes, Keep in  mind the user is working out at {location}"},
            { "role": "system", "content" : f"Okay, I will keep in mind that user is working out at {location} while working on the workout plan"},
            { "role": "user", "content": "Also for each workout add a short description on how to do it. It should not exceed more than 25 words." },
            { "role": "system", "content": "Sure, I will add the description. Is there any other conditions I should stick to?" },
            { "role": "user", "content": f"Yes, No Matter What. Always stick to this JSON format. {required_json}. You can increase the number of days based on {num_days}. But The Output should be in this format ONLY." },
            { "role": "system", "content": f"Okay Sure, I will Always stick to {required_json} and I will increase the json inside 'workout_plans' based on {num_days}" },
            { "role": "user", "content": "Make sure you minimum of 5-6 different kinds of workouts planned for each day. If its not provided earlier you can add it yourself." },
            { "role": "system", "content": "Okay, I will make sure to have atleast 5-6 different kind of workouts for each day." },
            { "role": "user", "content": "Make sure your final response is a valid JSON array of the workout plan." },
            { "role": "system", "content": "Okay, I will make sure to give final response in valid JSON array." },
        ]
        
        ai_response = ask_chatgpt(messages)
        if ai_response:
            try:
                if not isinstance(ai_response, dict):
                    ai_response = json.loads(ai_response)
                print(json.dumps(ai_response, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(ai_response)

    except Exception as e:
        print("[ERROR] Exception in generate_workout_plan:", str(e))
        traceback.print_exc()
        return {"error": str(e)}

    return ai_response
