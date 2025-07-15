import os
from flask import Flask, request, send_file
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# HTML Template with dropdowns, regenerate button, and updated layout
html = """
<!DOCTYPE html>
<html>
<head>
    <title>SEL Lesson Generator</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f7fa; }}
        h1 {{ color: #333; }}
        label {{ display: block; margin-top: 20px; font-weight: bold; }}
        input[type=text], select {{
            width: 300px; padding: 8px; margin-top: 5px;
            border: 1px solid #ccc; border-radius: 4px;
        }}
        button {{
            margin-top: 20px; padding: 10px 20px;
            background-color: #007bff; color: white;
            border: none; border-radius: 4px; cursor: pointer;
        }}
        button:hover {{ background-color: #0056b3; }}
        pre {{ background-color: #eef; padding: 15px; white-space: pre-wrap; }}
    </style>
</head>
<body>
    <h1>🧠 SEL Lesson Generator</h1>
    <form method="POST">
        <label for="grade">Grade Level:</label>
        <select name="grade">
            <option value="Kindergarten">Kindergarten</option>
            <option value="1st">1st</option>
            <option value="2nd">2nd</option>
            <option value="3rd">3rd</option>
            <option value="4th">4th</option>
            <option value="5th">5th</option>
        </select>

        <label for="subject">Subject:</label>
        <select name="subject">
            <option value="Math">Math</option>
            <option value="ELA">ELA</option>
            <option value="Science">Science</option>
            <option value="History">History</option>
        </select>

        <label for="topic">Academic Topic:</label>
        <input type="text" name="topic" placeholder="e.g. fractions" required>

        <label for="sel">SEL Focus:</label>
        <select name="sel">
            <option value="Self-Awareness">Self-Awareness</option>
            <option value="Self-Management">Self-Management</option>
            <option value="Social Awareness">Social Awareness</option>
            <option value="Relationship Skills">Relationship Skills</option>
            <option value="Responsible Decision-Making">Responsible Decision-Making</option>
        </select>

        <button type="submit" name="action" value="generate">Generate Lesson</button>
    </form>

    {output}

    {regenerate_button}
    {download_button}
</body>
</html>
"""

# Generate lesson using the OpenAI API
def generate_lesson(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

last_prompt = ""

@app.route("/", methods=["GET", "POST"])
def home():
    global last_prompt
    output = ""
    download_button = ""
    regenerate_button = ""

    if request.method == "POST":
        action = request.form.get("action")

        if action == "generate":
            grade = request.form["grade"]
            subject = request.form["subject"]
            topic = request.form["topic"]
            sel = request.form["sel"]

            last_prompt = (
                f"Design a short integrated lesson plan for grade {grade} students "
                f"on the topic of {topic} in {subject}. Include an SEL focus on {sel}. "
                f"The lesson should include a hook, direct instruction, short game or practice, "
                f"reflection question, and an exit slip."
            )

        elif action == "regenerate" and last_prompt:
            pass  # just reuse the last prompt

        if last_prompt:
            lesson = generate_lesson(last_prompt)
            output = f"<h2>Lesson Plan:</h2><pre>{lesson}</pre>"
            regenerate_button = """
                <form method="POST">
                    <input type="hidden" name="action" value="regenerate">
                    <button type="submit">🔁 Regenerate Lesson</button>
                </form>
            """
            download_button = """
                <form method="GET" action="/download">
                    <button type="submit">⬇️ Download Lesson as .txt</button>
                </form>
            """
            with open("lesson.txt", "w", encoding="utf-8") as f:
                f.write(lesson)

    return html.format(output=output, regenerate_button=regenerate_button, download_button=download_button)

@app.route("/download", methods=["GET"])
def download():
    return send_file("lesson.txt", as_attachment=True)

# If you're using Replit, no need to set host/port
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81)