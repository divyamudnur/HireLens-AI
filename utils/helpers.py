import os
import time
import re

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads', 'resumes')

def save_uploaded_resume(uploaded_file, candidate_id: int, job_id: int) -> tuple[str | None, str]:
    """
    Saves an uploaded PDF resume safely to uploads/resumes/.
    Returns (relative_filepath: str | None, message: str)
    """
    if uploaded_file is None:
        return None, "No file uploaded."

    filename = uploaded_file.name
    ext = os.path.splitext(filename)[1].lower()

    if ext != '.pdf':
        return None, "Invalid file format. Only PDF files (.pdf) are allowed."

    # Ensure uploads directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Generate safe unique filename
    safe_basename = re.sub(r'[^a-zA-Z0-9_-]', '_', os.path.splitext(filename)[0])
    timestamp = int(time.time())
    new_filename = f"cand_{candidate_id}_job_{job_id}_{timestamp}_{safe_basename}.pdf"
    
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    try:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Relative path for portable database storing
        relative_path = os.path.relpath(file_path, start=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return relative_path, "Resume uploaded successfully!"
    except Exception as e:
        return None, f"Failed to save resume: {str(e)}"
