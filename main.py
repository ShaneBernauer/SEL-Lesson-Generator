from openai import OpenAI
import os
from flask import Flask, request, send_file

# Use OpenAI API key from Replit Secrets
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

app = Flask(__name__)
lesson_text = ""  # Stores the most recent lesson

def generate_lesson(prompt_text):
    global lesson_text
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert lesson designer who blends SEL with academic content. Keep the response under 500 words."},
            {"role": "user", "content": prompt_text}
        ],
        temperature=0.7,
        max_tokens=800
    )
    lesson_text = response.choices[0].message.content
    return lesson_text

@app.route("/", methods=["GET", "POST"])
def home():
    output = ""
    download_button = ""

    if request.method == "POST":
        prompt = request.form["prompt"]
        lesson = generate_lesson(prompt)
        output = f"<pre>{lesson}</pre>"
        download_button = """
        <form method="GET" action="/download">
            <button type="submit">⬇️ Download Lesson as .txt</button>
        </form>
        """

    html = f"""
    <html>
    <body style="font-family:Arial; padding:20px;">
        <h2>🌸 SEL Lesson Generator</h2>

        <div style="margin-bottom: 10px;">
            <strong>Try a template:</strong><br>
            <button type="button" onclick="setPrompt(`Create a 10-minute 3rd grade math lesson on fractions that supports self-regulation. Include a game and quick reflection.`)">3rd Grade Math + Self-Reg</button><br>
            <button type="button" onclick="setPrompt(`Design a 15-minute science group activity for 5th graders focused on ecosystems. Emphasize teamwork and communication.`)">Science Groupwork + Relationship Skills</button><br>
            <button type="button" onclick="setPrompt(`Write a 10-minute history mini-lesson on the Civil Rights Movement for 6th grade. Focus on empathy and perspective-taking.`)">History + Empathy</button><br>
            <button type="button" onclick="setPrompt(`Create a morning check-in with a growth mindset focus for 2nd graders. Include a mood scale and short activity.`)">Morning Check-In + Growth Mindset</button><br>
            <button type="button" onclick="setPrompt(`Build a 20-minute ELA writing activity for 4th grade that helps students manage frustration during editing.`)">ELA + Frustration Tolerance</button>
        </div>

        <form method="POST">
            <textarea name="prompt" rows="5" cols="60" placeholder="e.g. 10-minute 4th grade math lesson on fractions + self-regulation"></textarea><br><br>
            <input type="submit" value="Generate Lesson">
        </form>

        <div style="margin-top: 20px;">{output}</div>
        {download_button}

        <script>
            function setPrompt(text) {{
                document.querySelector('textarea[name="prompt"]').value = text;
            }}
        </script>
    </body>
    </html>
    """
    return html

@app.route("/download")
def download():
    file_path = "/tmp/lesson.txt"
    with open(file_path, "w") as f:
        f.write(lesson_text)
    return send_file(file_path, as_attachment=True)

app.run(host="0.0.0.0", port=81)
