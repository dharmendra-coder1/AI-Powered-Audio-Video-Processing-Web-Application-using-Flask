from flask import Flask, render_template, request, send_file
import os
import pyttsx3
import speech_recognition as sr
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from moviepy.editor import VideoFileClip
from fpdf import FPDF
from docx import Document
import assemblyai as aai
from cryptography.fernet import Fernet
from moviepy.editor import VideoFileClip
from cryptography.fernet import Fernet
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import threading

from werkzeug.utils import secure_filename
import speech_recognition as sr
import tempfile
from pydub import AudioSegment
import soundfile as sf
import threading
import io
from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import subprocess
from flask_sock import Sock
from google.cloud import speech
import base64

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ------------------ HOME PAGE ------------------
@app.route('/')
def index():
    return render_template('index.html')



@app.route('/save-text', methods=['POST'])
def save_text():
    data = request.get_json()
    text = data.get("text", "")
    with open("transcription.txt", "w", encoding="utf-8") as f:
        f.write(text)
    return jsonify({"message": "Text saved successfully!"})


# Google Drive API Setup
SERVICE_ACCOUNT_FILE = "my-2nd-project-438807-3334600450dc.json"  # Your new JSON key
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Folder ID for direct uploads (Option 2)
FOLDER_ID = "134ZjsdK0tGj8dCGylaOqZgtbZHDC0ZAf"  # Replace with your Drive folder ID


# ---------------- TEXT TO SPEECH ----------------
@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    text = request.form['text']
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    return "Speech has been synthesized successfully."


# ---------------- Speech-to-Text ----------------
@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    if 'audio' not in request.files:
        return "No file part"
    file = request.files['audio']
    if file.filename == '':
        return "No selected file"

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

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



# -------------------- 3. Audio & Video Integration --------------------
@app.route('/audio-video-integration', methods=['POST'])
def audio_video_integration():
    file = request.files['media']
    if not file:
        return "No file uploaded", 400
    filename = file.filename
    filepath = os.path.join("uploads", filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(filepath)

    if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
        clip = VideoFileClip(filepath)
        audio_path = filepath.rsplit('.', 1)[0] + ".mp3"
        clip.audio.write_audiofile(audio_path)
        return send_file(audio_path, as_attachment=True)
    else:
        return "Unsupported file type", 400

# -------------------- 3. real-time-transcription --------------------
# Path to your Google credentials JSON file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "skilful-elixir-432611-q7-5a5c5e438a15.json"

sock = Sock(app)

@sock.route('/transcribe')
def transcribe(ws):
    client = speech.SpeechClient()
    streaming_config = speech.StreamingRecognitionConfig(
        config=speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US"
        ),
        interim_results=True
    )

    requests = []

    while True:
        data = ws.receive()
        if not data:
            break
        audio_content = base64.b64decode(data)
        requests.append(speech.StreamingRecognizeRequest(audio_content=audio_content))

        responses = client.streaming_recognize(streaming_config, iter(requests))
        for response in responses:
            for result in response.results:
                ws.send(result.alternatives[0].transcript)


# ---------------- Speaker Identification ----------------
aai.settings.api_key = "608c1b16509240659f256854057b1962"

@app.route('/speaker-identification', methods=['POST'])
def speaker_identification():
    if 'audio' not in request.files:
        return "No file part", 400

    file = request.files['audio']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    config = aai.TranscriptionConfig(speaker_labels=True)
    transcript = aai.Transcriber().transcribe(file_path, config)

    speaker_output = "\n".join([f"Speaker {u.speaker}: {u.text}" for u in transcript.utterances])
    os.remove(file_path)
    return render_template('index.html', speaker_identification_output=speaker_output)


# ---------------- Search & Indexing ----------------
ALLOWED_EXTENSIONS = {'txt'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/search-indexing', methods=['POST'])
def search_indexing():
    search_query = request.form['search-query']
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return "Invalid file format. Only .txt files are allowed."

    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        transcript = f.read()

    found = search_query.lower() in transcript.lower()
    result_message = f"'{search_query}' found in transcript!" if found else f"'{search_query}' not found in transcript."
    return render_template('index.html', search_result=result_message)


# ---------------- Editing Tools ----------------
@app.route('/editing-tools', methods=['POST'])
def editing_tools():
    file = request.files['file']
    if not file or not file.filename.endswith('.txt'):
        return "Only .txt files are allowed", 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    with open(file_path, 'r') as f:
        content = f.read()
    return render_template('index.html', file_content=content, file_name=file.filename)

@app.route('/save-edited-text', methods=['POST'])
def save_edited_text():
    edited_text = request.form['edited_text']
    file_name = request.form['file_name']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    with open(file_path, 'w') as f:
        f.write(edited_text)
    return render_template('index.html', success_message="File updated successfully!")

# -------------------- 4. Export Options --------------------
@app.route('/export-options', methods=['POST'])
def export_options():
    text = request.form['text']
    file_format = request.form['format']

    if file_format == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in text.split('\n'):
            pdf.multi_cell(190, 10, line)
        output_path = "output.pdf"
        pdf.output(output_path)
        return send_file(output_path, as_attachment=True)

    elif file_format == 'docx':
        doc = Document()
        doc.add_paragraph(text)
        output_path = "output.docx"
        doc.save(output_path)
        return send_file(output_path, as_attachment=True)

    elif file_format == 'txt':
        output_path = "output.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return send_file(output_path, as_attachment=True)

    else:
        return "Invalid format", 400


# ---------------- Privacy & Security ----------------
@app.route('/privacy-security', methods=['POST'])
def privacy_security():
    data = request.form.get('data')
    if not data:
        return "No data provided."

    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    cipher_text = cipher_suite.encrypt(data.encode())
    return render_template('index.html', encrypted_data=cipher_text.decode(), key=key.decode())

@app.route('/decrypt', methods=['POST'])
def decrypt_data():
    cipher_text = request.form.get('cipher_text')
    key = request.form.get('key')
    try:
        cipher_suite = Fernet(key.encode())
        decrypted_text = cipher_suite.decrypt(cipher_text.encode()).decode()
        return render_template('index.html', decrypted_data=decrypted_text)
    except Exception as e:
        return f"Decryption failed. Error: {str(e)}"


# -------------------- 5. Google Drive Integration --------------------
@app.route('/upload-to-drive', methods=['POST'])
def upload_to_google_drive():
    file = request.files['file']
    if not file:
        return "No file uploaded", 400

    file_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(file_path)

    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        drive_service = build('drive', 'v3', credentials=creds)

        file_metadata = {'name': file.filename, 'parents': [FOLDER_ID]}
        media = MediaFileUpload(file_path, resumable=True)

        uploaded_file = drive_service.files().create(
            body=file_metadata, media_body=media, fields='id'
        ).execute()

        return f"File '{file.filename}' uploaded successfully to Google Drive (File ID: {uploaded_file.get('id')})"
    except Exception as e:
        return f"Error uploading to Google Drive: {e}"

if __name__ == "__main__":
    app.run(debug=True)
