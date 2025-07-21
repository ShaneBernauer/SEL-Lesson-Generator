
import os
from flask import Flask, request, send_file, make_response, render_template, render_template_string, jsonify, redirect
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
            
            lesson_html_template = """
            <div class="card shadow-sm mt-4">
                <div class="card-header bg-warning text-dark">
                    <h5 class="mb-0">📋 Your Generated Lesson Plan</h5>
                </div>
                <div class="card-body">
                    <div style="line-height: 1.8; color: #333; white-space: pre-wrap;">{{ lesson_text }}</div>
                </div>
            </div>
            """
            
            output = render_template_string(lesson_html_template, lesson_text=lesson)
            
            action_buttons = f"""
            <div class="text-center mt-4 mb-4">
                <form method="POST" style="display: inline;">
                    <input type="hidden" name="action" value="regenerate">
                    <button type="submit" class="btn btn-outline-secondary me-2">🔄 Regenerate Lesson</button>
                </form>
                <a href="/download/txt" class="btn btn-success me-2">📄 Download as TXT</a>
                <a href="/download/pdf" class="btn btn-warning">📑 Download as PDF</a>
            </div>
            """
            
            # Save text version
            with open("lesson.txt", "w", encoding="utf-8") as f:
                f.write(lesson)

    # Generate prompt history HTML
    prompt_history_html = ""
    if prompt_history:
        prompt_history_html = "<div style='max-height: 300px; overflow-y: auto;'>"
        for i, prompt in enumerate(prompt_history):
            prompt_history_html += f"""
            <div class="border-start border-warning border-3 ps-3 mb-3">
                <div class="fw-semibold text-primary mb-1">
                    {prompt['grade']} • {prompt['subject']} • {prompt['sel']}
                </div>
                <div class="text-muted mb-2">
                    Topic: {prompt['topic']}
                </div>
                <form method="POST" style="display: inline;">
                    <input type="hidden" name="action" value="use_history">
                    <input type="hidden" name="grade" value="{prompt['grade']}">
                    <input type="hidden" name="subject" value="{prompt['subject']}">
                    <input type="hidden" name="topic" value="{prompt['topic']}">
                    <input type="hidden" name="sel" value="{prompt['sel']}">
                    <button type="submit" class="btn btn-sm btn-warning">
                        ↻ Use This Prompt
                    </button>
                </form>
            </div>
            """
        prompt_history_html += "</div>"
    else:
        prompt_history_html = "<p class='text-muted fst-italic'>No prompt history yet. Generate your first lesson to see prompts here!</p>"

    return render_template('index.html', 
                         output=output, 
                         action_buttons=action_buttons, 
                         prompt_history_html=prompt_history_html)

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

@app.route('/dashboard')
def dashboard():
    lessons = Lesson.query.order_by(Lesson.created_at.desc()).all()
    return render_template('dashboard.html', lessons=lessons)

@app.route('/lesson/<int:lesson_id>')
def view_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    return render_template('lesson_detail.html', lesson=lesson)

@app.route('/set_lesson_for_download', methods=['POST'])
def set_lesson_for_download():
    global last_lesson, last_prompt
    lesson_id = request.json.get('lesson_id')
    lesson = Lesson.query.get_or_404(lesson_id)
    last_lesson = lesson.lesson_text
    last_prompt = f"Lesson for {lesson.grade} grade {lesson.subject} on {lesson.topic} with SEL focus on {lesson.sel_focus}"
    
    # Save text version for download
    with open("lesson.txt", "w", encoding="utf-8") as f:
        f.write(lesson.lesson_text)
    
    return jsonify({"success": True})

@app.route('/toggle_favorite/<int:lesson_id>', methods=['POST'])
def toggle_favorite(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    lesson.is_favorite = not lesson.is_favorite
    db.session.commit()
    return redirect('/dashboard')

@app.route('/voice_command', methods=['POST'])
def voice_command():
    try:
        command = request.json.get("command", "").lower().strip()
        print("🔊 Voice input received:", command)  # Debug logging

        if not command:
            return jsonify({"error": "No voice input detected"}), 400

        # Extract grade level
        grade = None
        if "grade 4" in command or "fourth grade" in command or "4th grade" in command:
            grade = "4th"
        elif "grade 5" in command or "fifth grade" in command or "5th grade" in command:
            grade = "5th"
        elif "grade 3" in command or "third grade" in command or "3rd grade" in command:
            grade = "3rd"
        
        # Extract subject
        subject = "Math"  # Default to Math for now
        if "mathematics" in command or "math" in command:
            subject = "Math"
        elif "science" in command:
            subject = "Science"
        elif "english" in command or "ela" in command:
            subject = "ELA"
        
        # Extract SEL focus
        sel_focus = None
        if "self-awareness" in command or "self awareness" in command:
            sel_focus = "Self-Awareness"
        elif "empathy" in command:
            sel_focus = "Empathy"
        elif "self-regulation" in command or "self regulation" in command:
            sel_focus = "Self-Regulation"
        elif "social awareness" in command:
            sel_focus = "Social Awareness"
        elif "relationship" in command:
            sel_focus = "Relationship Skills"
        
        # Extract topic (basic patterns)
        topic = "General Math Skills"  # Default
        if "fractions" in command:
            topic = "Fractions"
        elif "volume" in command:
            topic = "Volume of Prisms"
        elif "addition" in command:
            topic = "Addition"
        elif "multiplication" in command:
            topic = "Multiplication"
        
        # Validate we have minimum required info
        if not grade:
            return jsonify({"error": "Please specify a grade level (e.g., 'grade 4', 'fourth grade')"}), 400
        if not sel_focus:
            return jsonify({"error": "Please specify an SEL focus (e.g., 'self-awareness', 'empathy')"}), 400

        # Generate the lesson
        prompt = f"Create a {grade} grade lesson about {topic} in {subject}, integrating the SEL skill of {sel_focus}. Make it short and usable."
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a creative SEL lesson planner."},
                {"role": "user", "content": prompt}
            ]
        )
        lesson_text = response.choices[0].message.content.strip()

        # Save to DB
        lesson = Lesson(grade=grade, subject=subject, topic=topic, sel_focus=sel_focus, lesson_text=lesson_text)
        db.session.add(lesson)
        db.session.commit()

        # Update global variables for PDF export
        global last_lesson, last_prompt
        last_lesson = lesson_text
        last_prompt = prompt
        
        # Save text version for download
        with open("lesson.txt", "w", encoding="utf-8") as f:
            f.write(lesson_text)

        return jsonify({
            "lesson": lesson_text,
            "download_available": True
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81)
