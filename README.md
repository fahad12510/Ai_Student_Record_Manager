
# AI Student Record Manager

A beginner-friendly Flask web application for managing student academic records. It calculates totals, averages, and grades automatically, stores records in a JSON file, and uses the Groq API to generate dynamic performance feedback and study tips.

## Features

- Add, view, update, search, and delete student records
- Keep each Student ID unchanged when updating a record
- Automatically calculate total marks, average percentage, and grade
- Save records in `students.json`
- Generate AI performance feedback using Groq
- Generate a personalized weekly study plan and study tips
- Validate input and display understandable errors
- Responsive green-and-white browser interface
- Send academic information only to the AI; student name and ID are not included

## Technologies

- Python 3 and Flask
- HTML5, CSS3, and JavaScript Fetch API
- JSON file storage
- Groq Python SDK
- python-dotenv

## Folder structure

```text
AI_Student_Record_Manager_Web/
├── app.py
├── ai_helper.py
├── students.json
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── templates/
│   └── index.html
└── README.md
```

## Requirements

Install Python 3.10 or newer and use Visual Studio Code. An internet connection and a Groq API key are needed for AI features. Student record management and result calculations work locally without the AI key.

## Setup on Windows

Open this project folder in VS Code. Open Terminal > New Terminal and run:

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Configure the Groq API

1. Create an API key in your Groq account.
2. Copy `.env.example` and rename the copy to `.env`.
3. Open `.env` and replace the placeholder with your own key:

```text
GROQ_API_KEY=your_actual_api_key
GROQ_MODEL=
```

`GROQ_MODEL` is optional. If it is blank, the program attempts to discover an available model from your Groq account. If model discovery is unavailable, set it to a text-generation model currently available to your account. Never share your API key or upload `.env` to GitHub.

## Run the application

With the virtual environment activated, run:

```powershell
python app.py
```

Open this address in Google Chrome:

```text
http://127.0.0.1:5000
```

The app also attempts to open your default browser automatically. Keep the terminal open while using the application. Press `Ctrl + C` in the terminal to stop the server.

## How to use

1. Enter the Student ID, student name, class/semester, comma-separated subject names, and matching comma-separated marks.
2. Select **Add** to save a new student. The application calculates total, average, and grade.
3. Select a row in the table to load that student's details into the form.
4. Edit the name, class, subjects, or marks and select **Update**. The Student ID remains unchanged.
5. Select a row and choose **Delete** to remove it after confirmation.
6. Search by student name or Student ID. Choose **Show All** to display every record.
7. Select a student and choose **Analyze Performance** or **Generate Study Tips**. The AI response appears in the result area.

## Grade criteria

| Average percentage | Grade |
|---|---|
| 85% or above | A |
| 70% to below 85% | B |
| 60% to below 70% | C |
| 50% to below 60% | D |
| Below 50% | F |

## Validation

- All fields are required.
- Student IDs must be unique.
- Subject names cannot be repeated.
- The number of subjects must equal the number of marks.
- Marks must be numeric and between 0 and 100.

## Common errors

- **`python` is not recognized:** Install Python and enable the option to add Python to PATH, then reopen VS Code.
- **`No module named flask` or `No module named groq`:** Activate `venv` and run `python -m pip install -r requirements.txt`.
- **Groq API key is missing:** Check that `.env` is in the same folder as `app.py`, and that it contains `GROQ_API_KEY=...`.
- **Model unavailable:** Set `GROQ_MODEL` in `.env` to a currently available text-generation model in your Groq account.
- **AI request fails:** Check your internet connection, API key, account access, and model availability. Student records remain saved locally.
- **Port 5000 is already in use:** Close the other application using port 5000, then run this project again.
- **Records do not load:** Check that `students.json` contains valid JSON. The starter file contains one sample student record.

## Privacy note

The AI helper sends only class/semester, subject names, marks, total marks, average percentage, and grade. It does not send student names or Student IDs. Student records are stored locally in `students.json`.
