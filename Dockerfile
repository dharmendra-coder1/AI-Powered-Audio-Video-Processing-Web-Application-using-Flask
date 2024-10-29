# Use the official Python image from Docker Hub
FROM python:3.11

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    espeak \
    espeak-ng \
    alsa-utils \  # Install alsa-utils for aplay command
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the container
COPY . .

# Set environment variables for espeak
ENV AUDIO_OUTPUT=stdout

# Set the command to run your application
CMD ["gunicorn", "app:app", "--workers", "1", "--threads", "2", "--timeout", "120", "-b", "0.0.0.0:8080"]
