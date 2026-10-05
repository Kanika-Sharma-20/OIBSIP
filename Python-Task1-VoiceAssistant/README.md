# AI Voice Assistant

## Objective

To develop a Python-based voice assistant that listens to spoken
commands, understands the user's intent, performs useful actions,
and responds using speech.

## Features

### Beginner Features

- Voice input through microphone
- Speech recognition
- Text-to-speech response
- Greeting commands
- Current time
- Current date
- Web search
- Website opening
- Speech recognition error handling

### Advanced Features

- Natural-language intent detection
- Background reminders
- Live weather information
- Email sending using SMTP
- General knowledge retrieval
- Custom commands
- Contact configuration
- Continuous conversation
- Privacy considerations

## Technologies

- Python
- SpeechRecognition
- PyAudio
- pyttsx3
- Requests
- datetime
- webbrowser
- threading
- regular expressions
- JSON
- SMTP
- OpenWeather API
- Wikipedia API

## Installation

Install the required packages:

pip install -r requirements.txt

## Running the Assistant

Run:

python voice_assistant.py

## Example Commands

Hello

What is the time?

What is today's date?

Search for artificial intelligence

Open YouTube

What is machine learning?

Who is Albert Einstein?

What is the weather in Nagpur?

Remind me to drink water in 20 seconds

Send an email

Add custom command study mode response Study mode activated

Goodbye

## Privacy

The application uses the microphone to capture spoken commands.

Speech recognition may use an online speech recognition service.

Weather information is obtained from the configured weather API.

Email is sent through the configured SMTP account.

API keys and email credentials are stored in the .env file.

The .env file should never be shared publicly or uploaded to GitHub.

The application does not intentionally save microphone recordings
to disk.

Users should avoid providing sensitive personal information
through third-party online services.

## Future Scope

- Wake-word detection
- Offline speech recognition
- Advanced conversational AI
- Smart-home integration
- Calendar integration
- GUI interface
- Voice-controlled applications