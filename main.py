
import os
from flask import Flask, request, send_file, make_response
from openai import OpenAI
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import io
from models import db, Lesson

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lessons.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# HTML Template with modern orange/blue design
html = """
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
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #f39c12 100%);
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
            background: linear-gradient(135deg, #2c5aa0 0%, #f39c12 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .form-container {
            padding: 40px;
            background: #f8f9fa;
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group.full-width {
            grid-column: 1 / -1;
        }
        
        label {
            font-weight: 600;
            color: #2c5aa0;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        
        input[type=text], select, textarea {
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: white;
        }
        
        input[type=text]:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #f39c12;
            box-shadow: 0 0 0 3px rgba(243, 156, 18, 0.1);
        }
        
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
            margin: 5px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(243, 156, 18, 0.3);
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(243, 156, 18, 0.4);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #2c5aa0 0%, #1e3c72 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(44, 90, 160, 0.3);
        }
        
        .btn-secondary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(44, 90, 160, 0.4);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
        }
        
        .btn-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(39, 174, 96, 0.4);
        }
        
        .output-container {
            background: white;
            margin: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .output-header {
            background: linear-gradient(135deg, #2c5aa0 0%, #f39c12 100%);
            color: white;
            padding: 20px;
            font-size: 1.4em;
            font-weight: 600;
        }
        
        .output-content {
            padding: 30px;
            line-height: 1.8;
            color: #333;
            font-size: 16px;
        }
        
        .action-buttons {
            padding: 20px;
            background: #f8f9fa;
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        @media (max-width: 768px) {
            .form-grid {
                grid-template-columns: 1fr;
            }
            
            .action-buttons {
                flex-direction: column;
            }
            
            .btn {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 SEL Lesson Generator</h1>
            <p>Create engaging lessons that combine academics with social-emotional learning</p>
        </div>
        
        <div class="form-container">
            <form method="POST">
                <div class="form-grid">
                    <div class="form-group">
                        <label for="grade">📚 Grade Level:</label>
                        <select name="grade" id="grade">
                            <option value="Kindergarten">Kindergarten</option>
                            <option value="1st">1st Grade</option>
                            <option value="2nd">2nd Grade</option>
                            <option value="3rd">3rd Grade</option>
                            <option value="4th">4th Grade</option>
                            <option value="5th">5th Grade</option>
                            <option value="6th">6th Grade</option>
                            <option value="7th">7th Grade</option>
                            <option value="8th">8th Grade</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="subject">📖 Subject:</label>
                        <select name="subject" id="subject">
                            <option value="Math">Mathematics</option>
                            <option value="ELA">English Language Arts</option>
                            <option value="Science">Science</option>
                            <option value="Social Studies">Social Studies</option>
                            <option value="History">History</option>
                        </select>
                    </div>

                    <div class="form-group full-width">
                        <label for="topic">🎯 Academic Topic:</label>
                        <input type="text" name="topic" id="topic" placeholder="e.g., fractions, photosynthesis, American Revolution" required>
                    </div>

                    <div class="form-group full-width">
                        <label for="sel">❤️ SEL Focus:</label>
                        <select name="sel" id="sel">
                            <option value="Self-Awareness">Self-Awareness</option>
                            <option value="Self-Management">Self-Management</option>
                            <option value="Social Awareness">Social Awareness</option>
                            <option value="Relationship Skills">Relationship Skills</option>
                            <option value="Responsible Decision-Making">Responsible Decision-Making</option>
                        </select>
                    </div>
                </div>

                <div style="text-align: center;">
                    <button type="button" onclick="showPrompt()" class="btn btn-secondary">👁️ Preview Prompt</button>
                    <button type="submit" name="action" value="generate" class="btn btn-primary">✨ Generate Lesson Plan</button>
                </div>
            </form>
            
            <!-- Prompt History Section -->
            <div style="margin-top: 30px; padding: 25px; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                <h3 style="color: #2c5aa0; margin-bottom: 15px;">📚 Prompt History</h3>
                {prompt_history_html}
            </div>
            
            <!-- Prompt Preview/Edit Section -->
            <div id="promptSection" style="display: none; margin-top: 30px; padding: 25px; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                <h3 style="color: #2c5aa0; margin-bottom: 15px;">📝 Generated Prompt</h3>
                <form method="POST" id="promptForm">
                    <textarea id="promptText" name="custom_prompt" rows="8" style="width: 100%; padding: 15px; border: 2px solid #e9ecef; border-radius: 10px; font-family: 'Segoe UI', sans-serif; font-size: 14px; line-height: 1.5; resize: vertical;" placeholder="Edit the prompt before generating..."></textarea>
                    <div style="text-align: center; margin-top: 20px;">
                        <button type="submit" name="action" value="generate_custom" class="btn btn-primary">✨ Generate with Custom Prompt</button>
                        <button type="button" onclick="hidePrompt()" class="btn btn-secondary">❌ Cancel</button>
                    </div>
                </form>
            </div>
        </div>

        <script>
            function showPrompt() {
                const grade = document.getElementById('grade').value;
                const subject = document.getElementById('subject').value;
                const topic = document.getElementById('topic').value;
                const sel = document.getElementById('sel').value;
                
                if (!topic.trim()) {
                    alert('Please enter an academic topic first.');
                    return;
                }
                
                const prompt = `Design a comprehensive integrated lesson plan for ${grade} students on the topic of '${topic}' in ${subject}. Include an SEL focus on ${sel}. The lesson should include: a creative hook, clear learning objectives, direct instruction, an engaging activity or game, guided practice, reflection questions that connect to the SEL focus, and an exit slip. Make it detailed and practical for teachers to implement.`;
                
                document.getElementById('promptText').value = prompt;
                document.getElementById('promptSection').style.display = 'block';
                document.getElementById('promptText').focus();
            }
            
            function hidePrompt() {
                document.getElementById('promptSection').style.display = 'none';
            }
        </script>

        {output}

        {action_buttons}
    </div>
</body>
</html>
"""

# Generate lesson using the OpenAI API
def generate_lesson(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def add_to_history(grade, subject, topic, sel):
    """Add a new prompt to history, keeping only the last 10"""
    global prompt_history
    
    prompt_entry = {
        'grade': grade,
        'subject': subject,
        'topic': topic,
        'sel': sel,
        'timestamp': f"{grade} - {subject} - {topic} - {sel}"
    }
    
    # Remove if already exists to avoid duplicates
    prompt_history = [p for p in prompt_history if not (
        p['grade'] == grade and p['subject'] == subject and 
        p['topic'] == topic and p['sel'] == sel
    )]
    
    # Add to beginning and keep only last 10
    prompt_history.insert(0, prompt_entry)
    prompt_history = prompt_history[:10]

def create_pdf(lesson_content, filename="lesson.pdf"):
    """Create a nicely formatted PDF of the lesson"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
    
    # Get styles and create custom ones
    styles = getSampleStyleSheet()
    
    # Custom styles with orange/blue theme
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=HexColor('#2c5aa0'),
        spaceAfter=20,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#f39c12'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HexColor('#333333'),
        spaceAfter=10,
        leading=16
    )
    
    # Build PDF content
    story = []
    
    # Add title
    story.append(Paragraph("🧠 SEL Lesson Plan", title_style))
    story.append(Spacer(1, 20))
    
    # Process lesson content
    lines = lesson_content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 10))
            continue
            
        # Check if it's a heading (contains colons or is all caps)
        if ':' in line and len(line) < 100:
            story.append(Paragraph(line, heading_style))
        else:
            story.append(Paragraph(line, body_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

last_prompt = ""
last_lesson = ""
prompt_history = []  # Store last 10 prompts

@app.route("/", methods=["GET", "POST"])
def home():
    global last_prompt, last_lesson
    output = ""
    action_buttons = ""

    if request.method == "POST":
        action = request.form.get("action")

        if action == "generate":
            grade = request.form["grade"]
            subject = request.form["subject"]
            topic = request.form["topic"]
            sel = request.form["sel"]
            
            # Add to history
            add_to_history(grade, subject, topic, sel)

            last_prompt = (
                f"Design a comprehensive integrated lesson plan for {grade} students "
                f"on the topic of '{topic}' in {subject}. Include an SEL focus on {sel}. "
                f"The lesson should include: a creative hook, clear learning objectives, "
                f"direct instruction, an engaging activity or game, guided practice, "
                f"reflection questions that connect to the SEL focus, and an exit slip. "
                f"Make it detailed and practical for teachers to implement."
            )
            
        elif action == "use_history":
            # Handle clicking on a history item
            grade = request.form["grade"]
            subject = request.form["subject"]
            topic = request.form["topic"]
            sel = request.form["sel"]
            
            last_prompt = (
                f"Design a comprehensive integrated lesson plan for {grade} students "
                f"on the topic of '{topic}' in {subject}. Include an SEL focus on {sel}. "
                f"The lesson should include: a creative hook, clear learning objectives, "
                f"direct instruction, an engaging activity or game, guided practice, "
                f"reflection questions that connect to the SEL focus, and an exit slip. "
                f"Make it detailed and practical for teachers to implement."
            )

        elif action == "generate_custom":
            custom_prompt = request.form.get("custom_prompt", "").strip()
            if custom_prompt:
                last_prompt = custom_prompt
            else:
                return "Custom prompt cannot be empty", 400

        elif action == "regenerate" and last_prompt:
            pass  # just reuse the last prompt

        if last_prompt:
            lesson = generate_lesson(last_prompt)
            last_lesson = lesson
            
            # Save to database if we have the required fields
            if action in ["generate", "use_history"]:
                grade = request.form.get("grade", "")
                subject = request.form.get("subject", "")
                topic = request.form.get("topic", "")
                sel = request.form.get("sel", "")
                
                lesson_record = Lesson(
                    grade=grade,
                    subject=subject,
                    topic=topic,
                    sel_focus=sel,
                    lesson_text=lesson
                )
                db.session.add(lesson_record)
                db.session.commit()
            
            output = f"""
            <div class="output-container">
                <div class="output-header">
                    📋 Your Generated Lesson Plan
                </div>
                <div class="output-content">
                    {lesson.replace(chr(10), '<br>')}
                </div>
            </div>
            """
            
            action_buttons = f"""
            <div class="action-buttons">
                <form method="POST" style="display: inline;">
                    <input type="hidden" name="action" value="regenerate">
                    <button type="submit" class="btn btn-secondary">🔄 Regenerate Lesson</button>
                </form>
                <a href="/download/txt" class="btn btn-success">📄 Download as TXT</a>
                <a href="/download/pdf" class="btn btn-primary">📑 Download as PDF</a>
            </div>
            """
            
            # Save text version
            with open("lesson.txt", "w", encoding="utf-8") as f:
                f.write(lesson)

    # Generate prompt history HTML
    prompt_history_html = ""
    if prompt_history:
        prompt_history_html = "<div style='max-height: 200px; overflow-y: auto;'>"
        for i, prompt in enumerate(prompt_history):
            prompt_history_html += f"""
            <div style="margin-bottom: 10px; padding: 12px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #f39c12;">
                <div style="font-weight: 600; color: #2c5aa0; margin-bottom: 5px;">
                    {prompt['grade']} • {prompt['subject']} • {prompt['sel']}
                </div>
                <div style="color: #666; margin-bottom: 8px;">
                    Topic: {prompt['topic']}
                </div>
                <form method="POST" style="display: inline;">
                    <input type="hidden" name="action" value="use_history">
                    <input type="hidden" name="grade" value="{prompt['grade']}">
                    <input type="hidden" name="subject" value="{prompt['subject']}">
                    <input type="hidden" name="topic" value="{prompt['topic']}">
                    <input type="hidden" name="sel" value="{prompt['sel']}">
                    <button type="submit" style="background: #f39c12; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-size: 12px;">
                        ↻ Use This Prompt
                    </button>
                </form>
            </div>
            """
        prompt_history_html += "</div>"
    else:
        prompt_history_html = "<p style='color: #666; font-style: italic;'>No prompt history yet. Generate your first lesson to see prompts here!</p>"

    return html.replace("{output}", output).replace("{action_buttons}", action_buttons).replace("{prompt_history_html}", prompt_history_html)

@app.route("/download/<format_type>", methods=["GET"])
def download(format_type):
    global last_lesson
    
    if format_type == "txt":
        return send_file("lesson.txt", as_attachment=True, download_name="lesson_plan.txt")
    elif format_type == "pdf":
        if not last_lesson:
            return "No lesson available for download", 404
            
        pdf_buffer = create_pdf(last_lesson)
        
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=lesson_plan.pdf'
        
        return response
    else:
        return "Invalid format", 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81)
