from flask import Flask, render_template, request, Response
import os
from pypdf import PdfReader

app = Flask(__name__)

# Folder Setup for uploads
UPLOAD_FOLDER = "resumes"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# AI Advice Database
AI_ADVICE = {
    "python": "Add a 'Technical Projects' section. Mention libraries like Pandas or NumPy to show depth.",
    "sql": "Describe a specific database schema you designed or a complex query you optimized.",
    "html": "Link to a live GitHub Pages or Netlify site to prove your frontend capability.",
    "css": "Mention 'Responsive Design' or 'Mobile-First' approach to impress modern recruiters.",
    "javascript": "Focus on DOM manipulation or Async/Await experience rather than just basic syntax.",
    "flask": "Detail how you handled routing, request methods, or template rendering in this specific app."
}

KEYWORDS = list(AI_ADVICE.keys())

def analyze_resume(text):
    found, missing, tips = [], [], []
    text = text.lower()
    for word in KEYWORDS:
        if word in text:
            found.append(word)
        else:
            missing.append(word)
            tips.append(AI_ADVICE[word])
    
    score = int((len(found) / len(KEYWORDS)) * 100) if KEYWORDS else 0
    return score, found, missing, tips

@app.route("/", methods=["GET", "POST"])
def index():
    data = {"score": None, "found": [], "missing": [], "tips": []}
    if request.method == "POST":
        file = request.files.get("resume")
        if file and file.filename != '':
            path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(path)
            content = ""
            try:
                if file.filename.lower().endswith('.pdf'):
                    reader = PdfReader(path)
                    for page in reader.pages:
                        content += page.extract_text()
                else:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                s, f, m, t = analyze_resume(content)
                data.update({"score": s, "found": f, "missing": m, "tips": t})
            except Exception as e:
                return f"Error: {e}"
    return render_template("index.html", **data)

@app.route("/download")
def download():
    score = request.args.get('score', '0')
    found = request.args.get('found', '').replace(',', ', ')
    missing = request.args.get('missing', '').replace(',', ', ')
    report = f"AI RESUME REPORT\nScore: {score}%\nFound: {found}\nMissing: {missing}"
    return Response(report, mimetype="text/plain", headers={"Content-disposition": "attachment; filename=Analysis.txt"})

if __name__ == "__main__":
    app.run(debug=True)