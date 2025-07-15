
from openai import OpenAI
import os
from flask import Flask, request, send_file, render_template_string

# Use OpenAI API key from Replit Secrets
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

app = Flask(__name__)
lesson_text = ""  # Stores the most recent lesson
last_prompt = ""  # Stores the last prompt for regeneration

def generate_lesson(prompt_text, is_regenerate=False):
    global lesson_text
    # Use higher temperature for regeneration to get different results
    temperature = 0.9 if is_regenerate else 0.7
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert lesson designer who blends SEL with academic content. Keep the response under 500 words."},
            {"role": "user", "content": prompt_text}
        ],
        temperature=temperature,
        max_tokens=800
    )
    lesson_text = response.choices[0].message.content
    return lesson_text

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEL Lesson Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            text-align: center;
            padding: 30px 20px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .templates-section {
            margin-bottom: 30px;
        }
        
        .templates-section h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .template-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .template-btn {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            border: none;
            padding: 15px 20px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 500;
            transition: all 0.3s ease;
            text-align: left;
            line-height: 1.4;
        }
        
        .template-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(116, 185, 255, 0.4);
        }
        
        .input-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
        }
        
        .input-section h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        textarea {
            width: 100%;
            min-height: 120px;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            font-size: 1em;
            font-family: inherit;
            resize: vertical;
            transition: border-color 0.3s ease;
        }
        
        textarea:focus {
            outline: none;
            border-color: #74b9ff;
            box-shadow: 0 0 0 3px rgba(116, 185, 255, 0.1);
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 184, 148, 0.4);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
            color: white;
        }
        
        .btn-secondary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(253, 121, 168, 0.4);
        }
        
        .btn-download {
            background: linear-gradient(135deg, #6c5ce7 0%, #5f3dc4 100%);
            color: white;
        }
        
        .btn-download:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(108, 92, 231, 0.4);
        }
        
        .output-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin-top: 25px;
        }
        
        .output-section h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .lesson-output {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
            white-space: pre-wrap;
            font-family: 'Georgia', serif;
            line-height: 1.8;
            color: #2d3436;
            max-height: 500px;
            overflow-y: auto;
        }
        
        .action-buttons {
            display: flex;
            gap: 15px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        @media (max-width: 768px) {
            .template-grid {
                grid-template-columns: 1fr;
            }
            
            .button-group,
            .action-buttons {
                flex-direction: column;
            }
            
            .btn {
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌸 SEL Lesson Generator</h1>
            <p>Create engaging lessons that blend academics with social-emotional learning</p>
        </div>
        
        <div class="content">
            <div class="templates-section">
                <h3>📚 Quick Start Templates</h3>
                <div class="template-grid">
                    <button class="template-btn" onclick="setPrompt('Create a 10-minute 3rd grade math lesson on fractions that supports self-regulation. Include a game and quick reflection.')">
                        🧮 3rd Grade Math + Self-Regulation
                    </button>
                    <button class="template-btn" onclick="setPrompt('Design a 15-minute science group activity for 5th graders focused on ecosystems. Emphasize teamwork and communication.')">
                        🔬 Science + Relationship Skills
                    </button>
                    <button class="template-btn" onclick="setPrompt('Write a 10-minute history mini-lesson on the Civil Rights Movement for 6th grade. Focus on empathy and perspective-taking.')">
                        📚 History + Empathy
                    </button>
                    <button class="template-btn" onclick="setPrompt('Create a morning check-in with a growth mindset focus for 2nd graders. Include a mood scale and short activity.')">
                        🌅 Morning Check-In + Growth Mindset
                    </button>
                    <button class="template-btn" onclick="setPrompt('Build a 20-minute ELA writing activity for 4th grade that helps students manage frustration during editing.')">
                        ✍️ ELA + Frustration Tolerance
                    </button>
                </div>
            </div>
            
            <form method="POST">
                <div class="input-section">
                    <h3>✨ Custom Lesson Request</h3>
                    <textarea name="prompt" placeholder="Describe your ideal lesson... (e.g., '10-minute 4th grade math lesson on fractions that builds self-regulation skills')"></textarea>
                    <div class="button-group">
                        <button type="submit" class="btn btn-primary">🚀 Generate Lesson</button>
                    </div>
                </div>
            </form>
            
            {% if output %}
            <div class="output-section">
                <h3>📝 Your Generated Lesson</h3>
                <div class="lesson-output">{{ output }}</div>
                <div class="action-buttons">
                    <button class="btn btn-secondary" onclick="copyToClipboard()">📋 Copy to Clipboard</button>
                    {% if last_prompt %}
                    <form method="POST" style="display: inline;">
                        <input type="hidden" name="prompt" value="{{ last_prompt }}">
                        <input type="hidden" name="regenerate" value="true">
                        <button type="submit" class="btn btn-secondary">🔄 Regenerate</button>
                    </form>
                    {% endif %}
                    <a href="/download" class="btn btn-download">⬇️ Download as .txt</a>
                </div>
            </div>
            {% endif %}
        </div>
    </div>
    
    <script>
        function setPrompt(text) {
            document.querySelector('textarea[name="prompt"]').value = text;
            document.querySelector('textarea[name="prompt"]').focus();
        }
        
        function copyToClipboard() {
            const lessonText = document.querySelector('.lesson-output').textContent;
            navigator.clipboard.writeText(lessonText).then(function() {
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = '✅ Copied!';
                btn.style.background = 'linear-gradient(135deg, #00b894 0%, #00a085 100%)';
                setTimeout(function() {
                    btn.textContent = originalText;
                    btn.style.background = '';
                }, 2000);
            });
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    global lesson_text, last_prompt
    output = ""

    if request.method == "POST":
        prompt = request.form["prompt"]
        is_regenerate = request.form.get("regenerate") == "true"
        
        lesson = generate_lesson(prompt, is_regenerate)
        output = lesson
        last_prompt = prompt

    return render_template_string(HTML_TEMPLATE, output=output, last_prompt=last_prompt)

@app.route("/download")
def download():
    file_path = "/tmp/lesson.txt"
    with open(file_path, "w") as f:
        f.write(lesson_text)
    return send_file(file_path, as_attachment=True, download_name="sel_lesson.txt")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
