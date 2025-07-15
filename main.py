from flask import Flask, request, send_file
import openai
import os

app = Flask(__name__)
lesson_text = ""

# Setup OpenAI API Key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Generate Lesson
def generate_lesson(prompt_text):
    global lesson_text
    response = openai.ChatCompletion.create(
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
    html = """
    <html>
    <head>
        <title>SEL Lesson Generator</title>
        <link href="https://fonts.googleapis.com/css2?family=Nunito&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Nunito', sans-serif;
                background-color: #f1f5f9;
                padding: 30px;
                max-width: 800px;
                margin: auto;
                color: #333;
            }}
            h2 {{ color: #2d6a4f; }}
            textarea {{
                width: 100%;
                padding: 10px;
                font-size: 16px;
                border-radius: 6px;
                border: 1px solid #ccc;
            }}
            button, input[type="submit"] {{
                background-color: #2d6a4f;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
            }}
            button:hover, input[type="submit"]:hover {{
                background-color: #40916c;
            }}
            .footer {{
                margin-top: 40px;
                font-size: 14px;
                color: #666;
                text-align: center;
            }}
            .template-buttons button {{
                margin: 4px 4px 4px 0;
            }}
            pre {{
                background-color: #ffffff;
                padding: 15px;
                border-radius: 6px;
                white-space: pre-wrap;
                box-shadow: 0 0 5px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>
        <h2>🌞 SEL Lesson Generator</h2>

        <div class="template-buttons">
            <strong>Try a template:</strong><br>
            <button type="button" onclick="setPrompt(`Create a 10-minute 3rd grade math lesson on fractions that supports self-regulation. Include a game and quick reflection.`)">3rd Grade Math + Self-Reg</button>
            <button type="button" onclick="setPrompt(`Design a 15-minute science group activity for 5th graders focused on ecosystems. Emphasize teamwork and communication.`)">Science Groupwork + Relationship Skills</button>
            <button type="button" onclick="setPrompt(`Write a 10-minute history mini-lesson on the Civil Rights Movement for 6th grade. Focus on empathy and perspective-taking.`)">History + Empathy</button>
            <button type="button" onclick="setPrompt(`Create a morning check-in with a growth mindset focus for 2nd graders. Include a mood scale and short activity.`)">Morning Check-In + Growth Mindset</button>
            <button type="button" onclick="setPrompt(`Build a 20-minute ELA writing activity for 4th grade that helps students manage frustration during editing.`)">ELA + Frustration Tolerance</button>
        </div>

        <form method="POST">
            <textarea name="prompt" rows="5" placeholder="Type your custom prompt here..."></textarea><br>
            <input type="submit" value="Generate Lesson">
        </form>

        <div style="margin-top: 20px;">{output}</div>
        {download_button}

        <div class="footer">Built with ❤️ by Shane | Powered by GPT-4</div>

        <script>
            function setPrompt(text) {
                document.querySelector('textarea[name="prompt"]').value = text;
            }
        </script>
    </body>
    </html>
    """
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

    return html.format(output=output, download_button=download_button)

@app.route("/download", methods=["GET"])
def download():
    with open("lesson.txt", "w", encoding="utf-8") as f:
        f.write(lesson_text)
    return send_file("lesson.txt", as_attachment=True)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


