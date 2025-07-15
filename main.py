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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px 30px;
        }
        
        .templates-section {
            margin-bottom: 40px;
        }
        
        .templates-section h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3rem;
            font-weight: 600;
        }
        
        .template-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .template-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            padding: 15px 20px;
            border-radius: 12px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .template-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        .form-section {
            margin-bottom: 30px;
        }
        
        .form-section h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3rem;
            font-weight: 600;
        }
        
        textarea {
            width: 100%;
            min-height: 120px;
            padding: 20px;
            border: 2px solid #e1e8ed;
            border-radius: 12px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            transition: border-color 0.3s ease;
            background: #f8f9fa;
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
            background: white;
        }
        
        .generate-btn {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            border: none;
            color: white;
            padding: 15px 40px;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
            margin-top: 20px;
        }
        
        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
        }
        
        .output-section {
            margin-top: 40px;
            padding-top: 30px;
            border-top: 2px solid #e9ecef;
        }
        
        .output-box {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 25px;
            margin: 20px 0;
            white-space: pre-wrap;
            font-family: 'Georgia', serif;
            line-height: 1.6;
            font-size: 15px;
            color: #333;
        }
        
        .action-buttons {
            display: flex;
            gap: 15px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .action-btn {
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
            border: none;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .action-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
        }
        
        .copy-btn {
            background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
        }
        
        .download-btn {
            background: linear-gradient(135deg, #fd7e14 0%, #e55347 100%);
        }
        
        @media (max-width: 768px) {
            .header {
                padding: 30px 20px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .content {
                padding: 30px 20px;
            }
            
            .template-buttons {
                grid-template-columns: 1fr;
            }
            
            .action-buttons {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌱 SEL Lesson Generator</h1>
            <p>Create engaging lessons that blend academics with social-emotional learning</p>
        </div>
        
        <div class="content">
            <div class="templates-section">
                <h3>✨ Quick Start Templates</h3>
                <div class="template-buttons">
                    <button class="template-btn" onclick="setPrompt('Create a 10-minute 3rd grade math lesson on fractions that supports self-regulation. Include a game and quick reflection.')">
                        📊 3rd Grade Math + Self-Regulation
                    </button>
                    <button class="template-btn" onclick="setPrompt('Design a 15-minute science group activity for 5th graders focused on ecosystems. Emphasize teamwork and communication.')">
                        🔬 5th Grade Science + Teamwork
                    </button>
                    <button class="template-btn" onclick="setPrompt('Write a 10-minute mini-lesson about empathy using a historical event like the Civil Rights Movement.')">
                        📚 History + Empathy
                    </button>
                    <button class="template-btn" onclick="setPrompt('Create a short check-in routine to start the school day that builds growth mindset.')">
                        🌅 Morning Check-In + Growth Mindset
                    </button>
                </div>
            </div>

            <div class="form-section">
                <h3>💭 Custom Lesson Request</h3>
                <form method="POST">
                    <textarea name="prompt" placeholder="Describe your ideal lesson... For example: 'Design a lesson on empathy and animal habitats for 2nd grade that includes hands-on activities and reflection time.'"></textarea>
                    <button type="submit" class="generate-btn">🚀 Generate Lesson</button>
                </form>
            </div>

            {% if output %}
            <div class="output-section">
                <h3>📝 Your Generated Lesson</h3>
                <div class="output-box" id="lessonOutput">{{ output }}</div>
                <div class="action-buttons">
                    <button class="action-btn copy-btn" onclick="copyText()">📋 Copy to Clipboard</button>
                    <form method="GET" action="/download" style="display: inline;">
                        <button type="submit" class="action-btn download-btn">⬇️ Download as .txt</button>
                    </form>
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

        function copyText() {
            const text = document.getElementById("lessonOutput").innerText;
            navigator.clipboard.writeText(text)
                .then(() => {
                    // Create a temporary success message
                    const btn = event.target;
                    const originalText = btn.innerHTML;
                    btn.innerHTML = '✅ Copied!';
                    btn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
                    setTimeout(() => {
                        btn.innerHTML = originalText;
                        btn.style.background = 'linear-gradient(135deg, #17a2b8 0%, #138496 100%)';
                    }, 2000);
                })
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
