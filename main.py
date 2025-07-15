from flask import Flask, request, send_file, render_template_string
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ["OPENAI_API_KEY"]

# Store last output for download
last_lesson = ""

# HTML Template with Jinja
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SEL Lesson Generator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 30px;
            padding: 20px;
            background-color: #f6f8fa;
        }
        textarea {
            width: 100%;
            padding: 10px;
            font-size: 16px;
        }
        button {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 10px 18px;
            text-align: center;
            font-size: 16px;
            margin: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .output-box {
            white-space: pre-wrap;
            background-color: #fff;
            border: 1px solid #ccc;
            padding: 15px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h2>🌱 SEL + Academic Lesson Generator</h2>

    <div>
        <strong>Example Templates:</strong><br>
        <button onclick="setPrompt(`Create a 10-minute 3rd grade math lesson on fractions that supports self-regulation. Include a game and quick reflection.`)">3rd Grade Math</button>
        <button onclick="setPrompt(`Design a 15-minute science group activity for 5th graders focused on ecosystems. Emphasize teamwork and communication.`)">5th Grade Science</button>
        <button onclick="setPrompt(`Write a 10-minute mini-lesson about empathy using a historical event like the Civil Rights Movement.`)">History + Empathy</button>
        <button onclick="setPrompt(`Create a short check-in routine to start the school day that builds growth mindset.`)">Morning Check-In</button>
    </div>

    <form method="POST">
        <textarea name="prompt" rows="5" placeholder="e.g. Design a lesson on empathy and animal habitats for 2nd grade."></textarea><br><br>
        <button type="submit">Generate Lesson</button>
    </form>

    {% if output %}
        <div class="output-box" id="lessonOutput">{{ output }}</div>
        <button onclick="copyText()">📋 Copy to Clipboard</button>
        <form method="GET" action="/download">
            <button type="submit">⬇️ Download as .txt</button>
        </form>
    {% endif %}

    <script>
        function setPrompt(text) {
            document.querySelector('textarea[name="prompt"]').value = text;
        }

        function copyText() {
            const text = document.getElementById("lessonOutput").innerText;
            navigator.clipboard.writeText(text)
                .then(() => alert("Lesson copied!"))
                .catch(err => alert("Failed to copy: " + err));
        }
    </script>
</body>
</html>
"""

# Home route
@app.route("/", methods=["GET", "POST"])
def home():
    global last_lesson
    output = ""

    if request.method == "POST":
        prompt = request.form["prompt"]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful lesson planning assistant that combines academic topics with social-emotional learning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        output = response.choices[0].message.content
        last_lesson = output

        # Save to file
        with open("lesson.txt", "w", encoding="utf-8") as f:
            f.write(output)

    return render_template_string(HTML_TEMPLATE, output=last_lesson)

# Download route
@app.route("/download")
def download():
    return send_file("lesson.txt", as_attachment=True)



# Start the app
app.run(host="0.0.0.0", port=81)
