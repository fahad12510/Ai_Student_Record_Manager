
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def get_api_key():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_actual_api_key":
        raise ValueError("Groq API key is missing. Add GROQ_API_KEY to your .env file.")
    return api_key


def choose_model(client):
    """Use the configured model, or find an available text model from Groq."""
    configured_model = os.getenv("GROQ_MODEL", "").strip()
    if configured_model:
        return configured_model

    try:
        models = client.models.list()
        for model in models.data:
            model_id = getattr(model, "id", "")
            if model_id and "whisper" not in model_id.lower() and "guard" not in model_id.lower():
                return model_id
    except Exception as error:
        raise RuntimeError(
            "Could not discover an available Groq model. Set GROQ_MODEL in .env."
        ) from error

    raise RuntimeError("No suitable text-generation model was found. Set GROQ_MODEL in .env.")


def ask_ai(prompt):
    client = Groq(api_key=get_api_key())
    model = choose_model(client)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a supportive academic study assistant. Give clear, "
                    "practical, age-appropriate advice. Do not invent marks or facts."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
        max_tokens=900,
    )
    return response.choices[0].message.content.strip()


def describe_student(student):
    """Build an AI description using academic information only."""
    subjects = ", ".join(
        f"{subject}: {mark:g}/100" for subject, mark in student["marks"].items()
    )
    return (
        f"Class/Semester: {student['class']}\n"
        f"Subjects and marks: {subjects}\n"
        f"Total marks: {student['total']}\n"
        f"Average percentage: {student['average']}%\n"
        f"Grade: {student['grade']}"
    )


def analyze_performance(student):
    prompt = (
        "Analyze this student's academic performance. Identify stronger and weaker "
        "subjects using the marks, give a short balanced summary, and suggest practical "
        "ways to improve. Treat a higher mark as stronger performance. "
        "Do not include personal identity information.\n\n"
        + describe_student(student)
    )
    return ask_ai(prompt)


def generate_study_tips(student):
    prompt = (
        "Create a personalized and realistic weekly study plan based on this academic "
        "record. Include suggestions for weaker subjects, daily study tips, practical "
        "learning methods, and a short encouraging closing message. Keep the plan simple "
        "and balanced. Do not include personal identity information.\n\n"
        + describe_student(student)
    )
    return ask_ai(prompt)
