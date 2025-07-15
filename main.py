from openai import OpenAI
import os
from flask import Flask, request, send_file

# Get API key from Replit Secrets
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

app = Flask(__name__)
lesson_text = ""  # Stores the latest lesson

# Generate lesson from prompt
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

# Home route with form and buttons
@app.route("/", methods=["GET", "POST"])
def home():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SEL Lesson Generator</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
                background: white;
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }}
            
            .header h1 {{
                font-size: 2.5em;
                color: #5a67d8;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }}
            
            .header p {{
                color: #666;
                font-size: 1.1em;
            }}
            
            .templates-section {{
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
            
            .templates-title {{
                font-size: 1.3em;
                color: #5a67d8;
                margin-bottom: 20px;
                font-weight: 600;
            }}
            
            .template-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }}
            
            .template-btn {{
                background: linear-gradient(45deg, #ed64a6, #d53f8c);
                color: white;
                border: none;
                padding: 15px 20px;
                border-radius: 12px;
                cursor: pointer;
                font-size: 0.9em;
                font-weight: 500;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(237, 100, 166, 0.3);
                text-align: left;
            }}
            
            .template-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(237, 100, 166, 0.4);
            }}
            
            .custom-section {{
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
            
            .custom-title {{
                font-size: 1.3em;
                color: #5a67d8;
                margin-bottom: 20px;
                font-weight: 600;
            }}
            
            .form-group {{
                margin-bottom: 20px;
            }}
            
            textarea {{
                width: 100%;
                padding: 15px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-family: inherit;
                font-size: 1em;
                resize: vertical;
                transition: border-color 0.3s ease;
                min-height: 120px;
            }}
            
            textarea:focus {{
                outline: none;
                border-color: #5a67d8;
                box-shadow: 0 0 0 3px rgba(90, 103, 216, 0.1);
            }}
            
            .generate-btn {{
                background: linear-gradient(45deg, #4299e1, #3182ce);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 12px;
                cursor: pointer;
                font-size: 1.1em;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(66, 153, 225, 0.3);
            }}
            
            .generate-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(66, 153, 225, 0.4);
            }}
            
            .output-section {{
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
            
            .lesson-content {{
                background: #f8fafc;
                padding: 25px;
                border-radius: 12px;
                border-left: 5px solid #5a67d8;
                white-space: pre-wrap;
                font-family: 'Georgia', serif;
                line-height: 1.8;
                color: #2d3748;
            }}
            
            .download-btn {{
                background: linear-gradient(45deg, #48bb78, #38a169);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 10px;
                cursor: pointer;
                font-size: 1em;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
                margin-top: 20px;
            }}
            
            .download-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(72, 187, 120, 0.4);
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    padding: 15px;
                }}
                
                .header h1 {{
                    font-size: 2em;
                }}
                
                .template-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .header, .templates-section, .custom-section, .output-section {{
                    padding: 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌸 SEL Lesson Generator</h1>
                <p>Create engaging Social-Emotional Learning lessons that blend SEL with academic content</p>
            </div>

            <div class="templates-section">
                <div class="templates-title">🚀 Quick Start Templates</div>
                <div class="template-grid">
                    <button type="button" class="template-btn" onclick="setPrompt(`Create a 10-minute 3rd grade math lesson on fractions that supports self-regulation. Include a game and quick reflection.`)">
                        📊 3rd Grade Math + Self-Regulation<br>
                        <small style="opacity: 0.8;">Fractions with mindfulness</small>
                    </button>
                    <button type="button" class="template-btn" onclick="setPrompt(`Design a 15-minute science group activity for 5th graders focused on ecosystems. Emphasize teamwork and communication.`)">
                        🔬 Science + Relationship Skills<br>
                        <small style="opacity: 0.8;">Ecosystems teamwork activity</small>
                    </button>
                    <button type="button" class="template-btn" onclick="setPrompt(`Write a 10-minute history mini-lesson on the Civil Rights Movement for 6th grade. Focus on empathy and perspective-taking.`)">
                        📚 History + Empathy<br>
                        <small style="opacity: 0.8;">Civil Rights perspective-taking</small>
                    </button>
                    <button type="button" class="template-btn" onclick="setPrompt(`Create a morning check-in with a growth mindset focus for 2nd graders. Include a mood scale and short activity.`)">
                        🌅 Morning Check-In + Growth Mindset<br>
                        <small style="opacity: 0.8;">Daily mindset builder</small>
                    </button>
                    <button type="button" class="template-btn" onclick="setPrompt(`Build a 20-minute ELA writing activity for 4th grade that helps students manage frustration during editing.`)">
                        ✍️ ELA + Frustration Tolerance<br>
                        <small style="opacity: 0.8;">Writing with emotional regulation</small>
                    </button>
                </div>
            </div>

            <div class="custom-section">
                <div class="custom-title">✨ Create Your Custom Lesson</div>
                <form method="POST">
                    <div class="form-group">
                        <textarea name="prompt" placeholder="Describe your lesson idea... 
e.g., 10-minute 4th grade math lesson on fractions + self-regulation

Include:
• Grade level
• Subject area
• Duration
• SEL focus (self-awareness, self-management, social awareness, relationship skills, responsible decision-making)
• Any specific activities or requirements"></textarea>
                    </div>
                    <button type="submit" class="generate-btn">🎯 Generate Lesson</button>
                </form>
            </div>

            {output_section}
        </div>

        <script>
            function setPrompt(text) {{
                document.querySelector('textarea[name="prompt"]').value = text;
                document.querySelector('textarea[name="prompt"]').scrollIntoView({{ behavior: 'smooth' }});
            }}
        </script>
    </body>
    </html>
    """

    if request.method == "POST":
        prompt = request.form["prompt"]
        lesson = generate_lesson(prompt)
        output_section = f"""
            <div class="output-section">
                <div class="templates-title">📝 Your Generated Lesson</div>
                <div class="lesson-content">{lesson}</div>
                <form method="GET" action="/download">
                    <button type="submit" class="download-btn">📥 Download Lesson as .txt</button>
                </form>
            </div>
        """
        return html.format(output_section=output_section)

    return html.format(output_section="")

# Download route
@app.route("/download")
def download():
    with open("lesson.txt", "w", encoding="utf-8") as f:
        f.write(lesson_text)
    return send_file("lesson.txt", as_attachment=True)

# Start the app
app.run(host="0.0.0.0", port=81)
