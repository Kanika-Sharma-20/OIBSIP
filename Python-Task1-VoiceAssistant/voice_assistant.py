import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import time
import threading
import re
import json
import os
import subprocess
import requests
import smtplib
import spacy

from email.message import EmailMessage
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

CONFIG_FILE = "config.json"


# ============================================================
# SPACY NLP MODEL
# ============================================================

try:
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
    print("spaCy NLP model loaded successfully.")

except Exception as error:
    print("spaCy model could not be loaded:", error)
    SPACY_AVAILABLE = False
    nlp = None


# ============================================================
# LOAD CONFIGURATION
# ============================================================

def load_config():

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        return {
            "contacts": {},
            "custom_commands": {}
        }


def save_config(config):

    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4)


config = load_config()


# ============================================================
# TEXT TO SPEECH
# ============================================================

try:
    engine = pyttsx3.init()

    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)

    PYTTSX3_AVAILABLE = True

except Exception as error:
    print("pyttsx3 initialization error:", error)
    PYTTSX3_AVAILABLE = False


def windows_speak(text):

    try:

        safe_text = text.replace("'", "''")

        command = (
            "Add-Type -AssemblyName System.Speech; "
            "$speaker = New-Object "
            "System.Speech.Synthesis.SpeechSynthesizer; "
            "$speaker.Rate = 0; "
            "$speaker.Volume = 100; "
            f"$speaker.Speak('{safe_text}');"
        )

        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                command
            ],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        return True

    except Exception as error:

        print("Windows speech error:", error)
        return False


def speak(text):

    print("Assistant:", text)

    if windows_speak(text):
        return

    if PYTTSX3_AVAILABLE:

        try:
            engine.say(text)
            engine.runAndWait()
            return

        except Exception as error:
            print("pyttsx3 speech error:", error)

    print("Voice output is unavailable.")


# ============================================================
# SPEECH RECOGNITION
# ============================================================

recognizer = sr.Recognizer()


def listen():

    try:

        with sr.Microphone() as source:

            print("\nListening...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

    except sr.WaitTimeoutError:

        print("No speech detected.")
        return ""

    except Exception as error:

        print("Microphone error:", error)

        speak(
            "I could not access the microphone."
        )

        return ""

    try:

        text = recognizer.recognize_google(audio)

        print("You:", text)

        return text.lower().strip()

    except sr.UnknownValueError:

        speak(
            "Sorry, I could not understand you. "
            "Please try again."
        )

        return ""

    except sr.RequestError as error:

        print("Speech recognition error:", error)

        speak(
            "I cannot connect to the speech recognition "
            "service. Please check your internet connection."
        )

        return ""


# ============================================================
# SPACY NLP PROCESSING
# ============================================================

def analyze_text(command):

    if not SPACY_AVAILABLE:
        return None

    try:
        return nlp(command)

    except Exception as error:

        print("spaCy processing error:", error)
        return None


def get_entities(command):

    doc = analyze_text(command)

    entities = {}

    if doc is None:
        return entities

    for entity in doc.ents:

        entities.setdefault(
            entity.label_,
            []
        )

        entities[entity.label_].append(
            entity.text
        )

    return entities


def extract_location(command):

    doc = analyze_text(command)

    if doc is not None:

        for entity in doc.ents:

            if entity.label_ in ["GPE", "LOC"]:
                return entity.text

    patterns = [
        r"weather in (.+)",
        r"weather at (.+)",
        r"weather for (.+)",
        r"temperature in (.+)",
        r"temperature at (.+)"
    ]

    for pattern in patterns:

        match = re.search(pattern, command)

        if match:
            return match.group(1).strip()

    return None


# ============================================================
# GREETING
# ============================================================

def get_greeting():

    hour = datetime.datetime.now().hour

    if hour < 12:
        return "Good morning"

    elif hour < 18:
        return "Good afternoon"

    else:
        return "Good evening"


# ============================================================
# TIME
# ============================================================

def tell_time():

    current_time = datetime.datetime.now().strftime(
        "%I:%M %p"
    )

    speak(
        f"The current time is {current_time}."
    )


# ============================================================
# DATE
# ============================================================

def tell_date():

    current_date = datetime.datetime.now().strftime(
        "%A, %d %B %Y"
    )

    speak(
        f"Today is {current_date}."
    )


# ============================================================
# WEB SEARCH
# ============================================================

def search_web(query):

    query = query.strip()

    if not query:

        speak(
            "What would you like me to search for?"
        )

        return

    speak(
        f"Searching for {query}."
    )

    url = (
        "https://www.google.com/search?q="
        + query.replace(" ", "+")
    )

    webbrowser.open(url)


# ============================================================
# OPEN WEBSITES
# ============================================================

def open_website(command):

    websites = {

        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://github.com",
        "gmail": "https://mail.google.com",
        "linkedin": "https://www.linkedin.com",
        "instagram": "https://www.instagram.com"
    }

    for name, url in websites.items():

        if re.search(
            rf"\b{re.escape(name)}\b",
            command
        ):

            speak(
                f"Opening {name}."
            )

            webbrowser.open(url)

            return True

    return False


# ============================================================
# REMINDER
# ============================================================

def reminder_worker(delay, reminder_text):

    time.sleep(delay)

    if reminder_text:

        speak(
            "Reminder: " + reminder_text
        )

    else:

        speak(
            "Reminder: Time is up."
        )


def set_reminder(command):

    pattern = (
        r"remind me"
        r"(?: to (.*?))?"
        r" in "
        r"(\d+) "
        r"(second|seconds|minute|minutes|hour|hours)"
    )

    match = re.search(
        pattern,
        command
    )

    if not match:

        speak(
            "Please say something like "
            "remind me to drink water in 20 minutes."
        )

        return

    reminder_text = match.group(1)

    number = int(match.group(2))
    unit = match.group(3)

    if "hour" in unit:
        delay = number * 3600

    elif "minute" in unit:
        delay = number * 60

    else:
        delay = number

    thread = threading.Thread(
        target=reminder_worker,
        args=(delay, reminder_text),
        daemon=True
    )

    thread.start()

    speak(
        f"Okay. I will remind you to "
        f"{reminder_text} in "
        f"{number} {unit}."
    )


# ============================================================
# WEATHER
# ============================================================

def get_weather(command):

    if not WEATHER_API_KEY:

        speak(
            "Weather is not configured yet. "
            "Please add the weather API key in the .env file."
        )

        return

    city = extract_location(command)

    if not city:

        speak(
            "Which city should I check?"
        )

        city = listen()

        if not city:
            return

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
    )

    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = response.json()

        if response.status_code != 200:

            speak(
                "I could not find the weather "
                "for that location."
            )

            return

        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"]

        speak(
            f"The weather in {city} is "
            f"{description}. "
            f"The temperature is "
            f"{temperature:.1f} degrees Celsius. "
            f"It feels like "
            f"{feels_like:.1f} degrees, "
            f"with {humidity} percent humidity."
        )

    except requests.RequestException:

        speak(
            "I could not connect to the weather service."
        )


# ============================================================
# GENERAL KNOWLEDGE / QA
# ============================================================

def clean_question(question):

    question = question.strip()

    prefixes = [

        "can you tell me ",
        "could you tell me ",
        "please tell me ",
        "tell me about ",
        "tell me ",
        "what is ",
        "what are ",
        "who is ",
        "who was ",
        "where is ",
        "when was ",
        "why is ",
        "why are ",
        "how does ",
        "how do "
    ]

    for prefix in prefixes:

        if question.startswith(prefix):

            question = question[len(prefix):]
            break

    return question.strip(" ?.")


def knowledge_search(question):

    original_question = question.strip()

    topic = clean_question(
        original_question
    )

    if not topic:

        speak(
            "Please ask me a question."
        )

        return

    # --------------------------------------------------------
    # spaCy entity detection
    # --------------------------------------------------------

    entities = get_entities(
        original_question
    )

    if entities:

        print(
            "Detected entities:",
            entities
        )

    # --------------------------------------------------------
    # Wikipedia Search API
    # --------------------------------------------------------

    search_url = (
        "https://en.wikipedia.org/w/api.php"
    )

    params = {

        "action": "query",

        "list": "search",

        "srsearch": topic,

        "format": "json",

        "utf8": 1,

        "srlimit": 3
    }

    headers = {

        "User-Agent":
            "OASIS-Voice-Assistant/1.0 "
            "(educational project)"
    }

    try:

        response = requests.get(
            search_url,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        results = (
            data
            .get("query", {})
            .get("search", [])
        )

        if results:

            page_title = results[0]["title"]

            summary_url = (
                "https://en.wikipedia.org/"
                "api/rest_v1/page/summary/"
                + page_title.replace(" ", "_")
            )

            summary_response = requests.get(
                summary_url,
                headers=headers,
                timeout=10
            )

            if summary_response.status_code == 200:

                summary_data = (
                    summary_response.json()
                )

                answer = summary_data.get(
                    "extract",
                    ""
                )

                if answer:

                    if len(answer) > 650:

                        answer = (
                            answer[:650]
                            + "."
                        )

                    speak(answer)

                    return

        # ----------------------------------------------------
        # Fallback to Google
        # ----------------------------------------------------

        speak(
            "I could not find a direct answer. "
            "I will search the web instead."
        )

        search_web(
            original_question
        )

    except requests.RequestException as error:

        print(
            "Knowledge API error:",
            error
        )

        speak(
            "I could not connect to the knowledge service. "
            "I will search the web instead."
        )

        search_web(
            original_question
        )

    except Exception as error:

        print(
            "Knowledge search error:",
            error
        )

        search_web(
            original_question
        )


# ============================================================
# EMAIL
# ============================================================

def send_email(
    recipient,
    subject,
    message
):

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:

        speak(
            "Email is not configured. "
            "Please add the email settings in the .env file."
        )

        return

    try:

        email = EmailMessage()

        email["From"] = EMAIL_ADDRESS
        email["To"] = recipient
        email["Subject"] = subject

        email.set_content(
            message
        )

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as smtp:

            smtp.login(
                EMAIL_ADDRESS,
                EMAIL_PASSWORD
            )

            smtp.send_message(
                email
            )

        speak(
            "The email was sent successfully."
        )

    except Exception as error:

        print(
            "Email error:",
            error
        )

        speak(
            "I could not send the email. "
            "Please check your email configuration."
        )


def send_email_by_voice():

    speak(
        "Who should I send the email to?"
    )

    recipient = listen()

    if not recipient:
        return

    contacts = config.get(
        "contacts",
        {}
    )

    if recipient in contacts:

        recipient = contacts[
            recipient
        ]

    speak(
        "What should be the subject?"
    )

    subject = listen()

    if not subject:
        return

    speak(
        "What should I write?"
    )

    message = listen()

    if not message:
        return

    speak(
        "I am sending the email."
    )

    send_email(
        recipient,
        subject,
        message
    )


# ============================================================
# CUSTOM COMMANDS
# ============================================================

def check_custom_commands(command):

    custom_commands = config.get(
        "custom_commands",
        {}
    )

    for trigger, action in custom_commands.items():

        if re.search(
            rf"\b{re.escape(trigger.lower())}\b",
            command
        ):

            action_type = action.get(
                "type"
            )

            value = action.get(
                "value",
                ""
            )

            if action_type == "response":

                speak(value)

                return True

            if action_type == "url":

                speak(
                    f"Opening {trigger}."
                )

                webbrowser.open(value)

                return True

    return False


def add_custom_command(command):

    pattern = (
        r"add custom command "
        r"(.+?) "
        r"response "
        r"(.+)"
    )

    match = re.search(
        pattern,
        command
    )

    if not match:

        speak(
            "Say something like: "
            "add custom command study mode "
            "response Study mode activated."
        )

        return

    trigger = match.group(1).strip()
    response = match.group(2).strip()

    config.setdefault(
        "custom_commands",
        {}
    )

    config["custom_commands"][trigger] = {

        "type": "response",

        "value": response
    }

    save_config(config)

    speak(
        f"I added the custom command {trigger}."
    )


# ============================================================
# NLP INTENT DETECTION
# ============================================================

def detect_intent(command):

    command = command.lower().strip()

    doc = analyze_text(command)

    lemmas = []

    if doc is not None:

        lemmas = [
            token.lemma_.lower()
            for token in doc
            if not token.is_punct
        ]

    # --------------------------------------------------------
    # GREETING
    # --------------------------------------------------------

    if re.search(
        r"\b(hello|hi|hey)\b",
        command
    ):

        return "greeting"

    if re.search(
        r"\b(good morning|good afternoon|good evening)\b",
        command
    ):

        return "greeting"

    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    if re.search(
        r"\b(goodbye|quit|exit)\b",
        command
    ):

        return "exit"

    if (
        "stop listening" in command
        or "close assistant" in command
    ):

        return "exit"

    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    if (
        "what time" in command
        or "current time" in command
        or "tell me the time" in command
        or "time right now" in command
        or "time is it" in command
        or command == "what is time"
        or command == "what is the time"
        or command == "tell time"
    ):

        return "time"

    if (
        "time" in lemmas
        and (
            "current" in lemmas
            or "tell" in lemmas
            or "know" in lemmas
        )
    ):

        return "time"

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    if (
        "today's date" in command
        or "today date" in command
        or "what date" in command
        or "what day is it" in command
        or "what is today's date" in command
        or "what is the date" in command
        or command == "date"
    ):

        return "date"

    if (
        "date" in lemmas
        and (
            "today" in lemmas
            or "current" in lemmas
            or "tell" in lemmas
        )
    ):

        return "date"

    # --------------------------------------------------------
    # REMINDER
    # --------------------------------------------------------

    if (
        "remind me" in command
        or "set a reminder" in command
        or re.search(r"\breminder\b", command)
    ):

        return "reminder"

    # --------------------------------------------------------
    # WEATHER
    # --------------------------------------------------------

    if (
        re.search(r"\bweather\b", command)
        or re.search(r"\btemperature\b", command)
        or re.search(r"\bforecast\b", command)
    ):

        return "weather"

    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    if (
        "send an email" in command
        or "send email" in command
        or "send a mail" in command
        or "send mail" in command
        or "write an email" in command
    ):

        return "email"

    # --------------------------------------------------------
    # CUSTOM COMMAND
    # --------------------------------------------------------

    if command.startswith(
        "add custom command"
    ):

        return "custom"

    # --------------------------------------------------------
    # WEBSITE
    # --------------------------------------------------------

    website_names = [
        "youtube",
        "google",
        "github",
        "gmail",
        "linkedin",
        "instagram"
    ]

    for website in website_names:

        if "open " + website in command:
            return "website"

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if (
        command.startswith("search")
        or "search for" in command
        or command.startswith("google ")
        or command.startswith("look up")
    ):

        return "search"

    # --------------------------------------------------------
    # KNOWLEDGE
    # --------------------------------------------------------

    question_words = [
        "who",
        "what",
        "when",
        "where",
        "why",
        "how",
        "which",
        "explain",
        "tell"
    ]

    if doc is not None:

        first_words = [
            token.lemma_.lower()
            for token in doc[:3]
            if not token.is_punct
        ]

        if any(
            word in question_words
            for word in first_words
        ):

            return "knowledge"

    if any(
        command.startswith(word + " ")
        for word in question_words
    ):

        return "knowledge"

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    return "unknown"


# ============================================================
# SEARCH QUERY
# ============================================================

def extract_search_query(command):

    prefixes = [
        "search for ",
        "search ",
        "google ",
        "look up "
    ]

    for prefix in prefixes:

        if command.startswith(prefix):

            return command[
                len(prefix):
            ].strip()

    return command


# ============================================================
# PROCESS COMMAND
# ============================================================

def process_command(command):

    if not command:
        return True

    # Custom commands first
    if check_custom_commands(command):
        return True

    intent = detect_intent(command)

    print(
        "Detected intent:",
        intent
    )

    if intent == "greeting":

        speak(
            f"{get_greeting()}! "
            "How can I help you?"
        )

    elif intent == "time":

        tell_time()

    elif intent == "date":

        tell_date()

    elif intent == "reminder":

        set_reminder(command)

    elif intent == "weather":

        get_weather(command)

    elif intent == "email":

        send_email_by_voice()

    elif intent == "website":

        open_website(command)

    elif intent == "search":

        query = extract_search_query(
            command
        )

        search_web(query)

    elif intent == "custom":

        add_custom_command(command)

    elif intent == "exit":

        speak(
            "Goodbye! Have a great day."
        )

        return False

    elif intent == "knowledge":

        knowledge_search(command)

    else:

        speak(
            "I am not completely sure what you mean. "
            "I will search the web for you."
        )

        search_web(command)

    return True


# ============================================================
# MAIN ASSISTANT
# ============================================================

def main():

    speak(
        "Hello! I am your voice assistant. "
        "How can I help you?"
    )

    while True:

        command = listen()

        if not command:
            continue

        should_continue = process_command(
            command
        )

        if not should_continue:
            break


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":
    main()