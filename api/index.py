from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import sys
from werkzeug.utils import secure_filename

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.resume_parser import ResumeParser
from utils.matcher import ResumeMatcher

# Initialize Flask app
app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', '16777216'))

# Configuration
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page - upload form"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and process resumes"""
    try:
        # Check if job description is provided
        job_description = request.form.get('job_description', '').strip()
        if not job_description:
            flash('Please provide a job description', 'error')
            return redirect(url_for('index'))

        # Check if files are uploaded
        if 'resumes' not in request.files:
            flash('No resume files uploaded', 'error')
            return redirect(url_for('index'))

        files = request.files.getlist('resumes')
        if not files or all(file.filename == '' for file in files):
            flash('No files selected', 'error')
            return redirect(url_for('index'))

        # Process uploaded files
        resume_data = []
        parser = ResumeParser()
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                try:
                    # Parse resume
                    parsed_data = parser.parse_resume(filepath)
                    parsed_data['filename'] = filename
                    resume_data.append(parsed_data)
                    
                    # Clean up uploaded file
                    os.remove(filepath)
                    
                except Exception as e:
                    flash(f'Error processing {filename}: {str(e)}', 'error')
                    if os.path.exists(filepath):
                        os.remove(filepath)
            else:
                flash(f'Invalid file type for {file.filename}', 'error')

        if not resume_data:
            flash('No valid resumes could be processed', 'error')
            return redirect(url_for('index'))

        # Match resumes with job description
        matcher = ResumeMatcher()
        results = matcher.match_resumes(resume_data, job_description)
        
        return render_template('results.html', results=results, job_description=job_description)

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for analyzing resumes"""
    try:
        data = request.get_json()
        
        if not data or 'job_description' not in data or 'resumes' not in data:
            return jsonify({'error': 'Invalid request data'}), 400
            
        job_description = data['job_description']
        resumes_text = data['resumes']  # List of resume texts
        
        # Create resume data structure
        resume_data = []
        parser = ResumeParser()
        
        for i, resume_text in enumerate(resumes_text):
            parsed_data = parser.parse_text(resume_text)
            parsed_data['filename'] = f'Resume_{i+1}'
            resume_data.append(parsed_data)
        
        # Match resumes
        matcher = ResumeMatcher()
        results = matcher.match_resumes(resume_data, job_description)
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))

# For Vercel deployment
try:
    # Create necessary directories
    os.makedirs('../utils', exist_ok=True)
    os.makedirs('../templates', exist_ok=True)
    os.makedirs('../static', exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Create empty __init__.py file in utils directory
    init_file = os.path.join('../utils', '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            pass
except Exception:
    # In serverless environment, some operations might fail
    pass

# This is the handler that Vercel will call
def handler(request):
    return app(request.environ, lambda status, headers: None)

# For local development
if __name__ == '__main__':
    app.run(debug=True)
