Project Title: Speech Transcription and Processing System

## Overview
This project is a comprehensive audio transcription and translation system that provides various features such as speech-to-text conversion, text-to-speech, real-time transcription, speaker identification, and collaboration tools. It leverages advanced technologies to enhance user experience and facilitate audio and video integration.

## Features

- **Speech-to-Text Converter**: Converts spoken language into written text using the SpeechRecognition library.
- **Text-to-Speech**: Converts written text into spoken words using `pyttsx3` and `gTTS` libraries.
- **Automated Transcription**: Automatically transcribes audio files with support for various formats.
- **Real-Time Transcription**: Provides real-time transcription capabilities with microphone support.
- **Speaker Identification**: Identifies different speakers in the audio using diarization techniques.
- **Audio & Video Integration**: Integrates audio and video files for processing.
- **Search and Indexing**: Allows users to search and index transcribed text for easy access.
- **Editing Tools**: Provides tools to edit transcribed text.
- **Collaboration Features**: Enables multiple users to collaborate on transcriptions.
- **Export Options**: Allows users to export transcriptions in different formats.
- **Privacy and Security**: Ensures data privacy and security throughout the transcription process.
- **Google Drive Integration**: Integrates with Google Drive for file uploads and storage.

## Technologies Used

- **Backend**: Flask
- **Database**: MySQL
- **Speech Recognition**: `speechrecognition`, `assemblyai`
- **Text-to-Speech**: `pyttsx3`, `gTTS`
- **Audio Processing**: `moviepy`, `pyaudio`
- **File Handling**: `docx`, `fpdf`, `python-docx`
- **Collaboration and File Management**: PyDrive, Google Drive API
  
  **Set Up Requirements**:
   - Create a `requirements.txt` file and include all the necessary dependencies:
     ```
     gunicorn==21.2.0
     psutil
     docx
     Flask
     speechrecognition
     pyttsx3
     moviepy
     cryptography
     PyDrive
     mysql-connector-python
     fpdf
     python-docx
     assemblyai
     werkzeug
     pydrive2
     tk
     pyaudio
     ffmpeg
     gTTS
     ```

## Creating JSON Files for Google API

1. **Creating OAuth 2.0 Client ID**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project or select an existing one.
   - Navigate to "APIs & Services" > "Credentials".
   - Click on "Create Credentials" and select "OAuth 2.0 Client IDs".
   - Download the JSON file and rename it to `client_secrets.json`.

2. **Creating Service Account for Google Drive**:
   - In the same project, navigate to "IAM & Admin" > "Service Accounts".
   - Create a new service account, grant it the required roles, and download the JSON key.
   - Save this file as `my-2nd-project-438807-d981994e5b71.json` (or similar).

## Creating AssemblyAI API Key

1. **Sign Up**: Create an account at [AssemblyAI](https://www.assemblyai.com/).
2. **API Key**: After signing in, navigate to the API section to generate your API key. Store this key securely as you'll need it for authentication in your application.
