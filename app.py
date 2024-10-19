from flask import Flask, request, render_template, send_file, jsonify
import os
import speech_recognition as sr
import pyttsx3
from moviepy.editor import VideoFileClip
from cryptography.fernet import Fernet
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import threading
import mysql.connector
from fpdf import FPDF
from docx import Document
import assemblyai as aai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Google Drive API
gauth = GoogleAuth()
drive = GoogleDrive(gauth)

# MySQL database connection
def get_db_connection():
    return mysql.connector.connect(
        host='DB_HOST',
        user='DB_USER',
        password='DB_PASS',
        database='DB_NAME'
    )

def log_uploaded_file(task_type, file_name, file_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO uploaded_files (task_type, file_name, file_path) VALUES (%s, %s, %s)",
        (task_type, file_name, file_path)
    )
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

# 1. Speech-to-Text
@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    if 'audio' not in request.files:
        return "No file part"
    file = request.files['audio']
    if file.filename == '':
        return "No selected file"
    
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        log_uploaded_file("Speech-to-Text", file.filename, file_path)

        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return render_template('index.html', speech_to_text_output=text)
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError:
            return "Could not request results from Google Speech Recognition service"

# 2. Text-to-Speech
@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    text = request.form['text']
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    return "Speech has been synthesized successfully."

# 3. Automated Transcription
@app.route('/automated-transcription', methods=['POST'])
def automated_transcription():
    if 'audio' not in request.files:
        return "No file part"
    file = request.files['audio']
    if file.filename == '':
        return "No selected file"

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        log_uploaded_file("Automated Transcription", file.filename, file_path)

        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return render_template('index.html', automated_transcription_output=text)
        except sr.UnknownValueError:
            return "Could not understand the audio"
        except sr.RequestError:
            return "API request error"

# 4. Real-time Transcription
@app.route('/real-time-transcription', methods=['POST'])
def real_time_transcription():
    def listen():
        nonlocal text
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=20)
                text = recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                text = "Could not understand the audio"
            except sr.RequestError:
                text = "API request error"

    text = ""
    transcription_thread = threading.Thread(target=listen)
    transcription_thread.start()
    transcription_thread.join(timeout=40)  # Allow time for real-time transcription
    return jsonify(text)

# 5. Speaker Identification
aai.settings.api_key = "608c1b16509240659f256854057b1962"  # Set AssemblyAI API Key

@app.route('/speaker-identification', methods=['POST'])
def speaker_identification():
    if 'audio' not in request.files:
        return "No file part", 400

    file = request.files['audio']
    if file.filename == '':
        return "No selected file", 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        log_uploaded_file("Speaker Identification", file.filename, file_path)

        # Create transcription config with speaker labels
        config = aai.TranscriptionConfig(speaker_labels=True)
        transcript = aai.Transcriber().transcribe(file_path, config)

        speaker_identification_output = ""
        for utterance in transcript.utterances:
            speaker_identification_output += f"Speaker {utterance.speaker}: {utterance.text}\n"

        os.remove(file_path)  # Clean up uploaded file
        return render_template('index.html', speaker_identification_output=speaker_identification_output)

# 6. Audio & Video Integration
@app.route('/audio-video-integration', methods=['POST'])
def audio_video_integration():
    if 'media' not in request.files:
        return "No file part"
    file = request.files['media']
    if file.filename == '':
        return "No selected file"

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        log_uploaded_file("Audio & Video Integration", file.filename, file_path)

        video = VideoFileClip(file_path)
        audio_file = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_audio.wav')
        video.audio.write_audiofile(audio_file)
        return send_file(audio_file, as_attachment=True)

# 7. Search and Indexing
UPLOAD_FOLDER = 'uploads/'  # Ensure this folder exists
ALLOWED_EXTENSIONS = {'txt'}

@app.route('/search-indexing', methods=['POST'])
def search_indexing():
    search_query = request.form['search-query']

    if 'file' not in request.files:
        return "No file part in the request."
    file = request.files['file']

    if file.filename == '':
        return "No file selected."

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        log_uploaded_file("Search and Indexing", filename, filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            transcript = f.read()

        found = search_query.lower() in transcript.lower()
        result_message = f"'{search_query}' found in transcript!" if found else f"'{search_query}' not found in transcript."
        return render_template('index.html', search_result=result_message)

    return "Invalid file format. Only .txt files are allowed."

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 8. Editing Tools
@app.route('/editing-tools', methods=['POST'])
def editing_tools():
    if 'file' not in request.files:
        return "No file part in the request", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if file and file.filename.endswith('.txt'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        log_uploaded_file("Editing Tools", file.filename, file_path)

        with open(file_path, 'r') as f:
            file_content = f.read()

        return render_template('index.html', file_content=file_content, file_name=file.filename)

    return "Only .txt files are allowed", 400

@app.route('/save-edited-text', methods=['POST'])
def save_edited_text():
    edited_text = request.form['edited_text']
    file_name = request.form['file_name']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

    try:
        with open(file_path, 'w') as f:
            f.write(edited_text)
        success_message = "File updated successfully!"
        return render_template('index.html', success_message=success_message)
    except Exception as e:
        return f"Failed to update the file. Error: {str(e)}"

# 9. Collaboration Features
@app.route('/collaboration-features', methods=['POST'])
def collaboration_features():
    email = request.form['email']
    if not email:
        return "Please provide an email address."

    sender_email = "aakritiprajapati90@gmail.com"  # Your Gmail address
    sender_password = "bvkuxcxyiynpuaug"  # Your Gmail password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Shared File"
    body = "You have been shared a file from the Speech Transcription System."
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email. Error: {str(e)}"


# 10. Export Options
@app.route('/export-options', methods=['POST'])
def export_options():
    if 'text' not in request.form or 'format' not in request.form:
        return "No file part in the request", 400  # Return a 400 error for bad requests

    # Get the text from the form
    text = request.form['text']  # Correct field name here
    format = request.form['format']  # Get the format (txt, pdf, docx)
    
    file_name = os.path.join(app.config['UPLOAD_FOLDER'], f'transcript.{format}')
    
    # Check the format and export accordingly
    if format == "txt":
        with open(file_name, "w") as file:
            file.write(text)
    
    elif format == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, text)
        pdf.output(file_name)
    
    elif format == "docx":
        doc = Document()
        doc.add_paragraph(text)
        doc.save(file_name)
    
    # Return the file for download
    return send_file(file_name, as_attachment=True)


# 11. Privacy and Security
@app.route('/privacy-security', methods=['POST'])
def privacy_security():
    if 'enable-encryption' not in request.form or 'data' not in request.form:
        return "No file part in the request", 400  # Return a 400 error for bad requests
    
    data = request.form['data']  # Retrieve data from form
    key = Fernet.generate_key()  # Generate a new key
    cipher_suite = Fernet(key)
    cipher_text = cipher_suite.encrypt(data.encode())
    
    return render_template('index.html', encrypted_data=cipher_text.decode(), key=key.decode())

@app.route('/decrypt', methods=['POST'])
def decrypt_data():
    if 'cipher_text' not in request.form or 'key' not in request.form:
        return "No file part in the request", 400  # Return a 400 error for bad requests

    cipher_text = request.form['cipher_text']
    key = request.form['key']
    try:
        # Decode the key from base64
        cipher_suite = Fernet(key.encode())
        decrypted_text = cipher_suite.decrypt(cipher_text.encode()).decode()
        return render_template('index.html', decrypted_data=decrypted_text)
    except ValueError as e:
        return f"Decryption failed. Error: {str(e)}"


# 12. Integration with Google Drive
@app.route('/upload-to-drive', methods=['POST'])
def upload_to_google_drive():
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    log_uploaded_file("Integration with Google Drive", file.filename, file_path)
    
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    
    gdrive_file = drive.CreateFile({'title': file.filename})
    gdrive_file.SetContentFile(file_path)
    gdrive_file.Upload()
    
    return f"File {file.filename} uploaded to Google Drive successfully."

if __name__ == '__main__':
    app.run(debug=True)


