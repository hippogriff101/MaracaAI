import os, pyttsx3
from dotenv import load_dotenv
from openrouter import OpenRouter
import speech_recognition as sr

load_dotenv(dotenv_path='C:\\Users\\' + os.getlogin() + '\\AppData\\Local\\MaracaAI\\.env')

api_key = os.getenv("API_KEY")

def call_api(messages, user_input):
    messages.append({"role": "user", "content": user_input})

    response = client.chat.send(
        model="qwen/qwen3-32b",
        messages=messages,
        stream=False,
    )
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    return reply

def speech_to_text():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            speak("Say something...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=20)
    except sr.WaitTimeoutError:
        speak("No speech detected in time.")
        return None
    except Exception as exc:
        speak(f"Microphone error: {exc}")
        return None

    try:
        text = recognizer.recognize_google(audio)
        speak(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        speak("Sorry, I could not understand that.")
        return None
    except sr.RequestError as exc:
        speak(f"Speech service error: {exc}")
        return None

def speak(input):
    print(input)
    pyttsx3.speak(input)  

def set_key():
    api_key = input("Press paste key here to continue: ")
    dirr = "C:\\Users\\" + os.getlogin() + "\\AppData\\Local\\MaracaAI"
    os.makedirs(dirr, exist_ok=True)
    with open(dirr + "\\.env", "w") as f:
        f.write(f"API_KEY={api_key}")
        f.close()

speak("""\nContinuous chat. Say 'exit' to quit.\n""")

if not api_key:
    speak("Missing API key. Please enter your API key to continue.")
    set_key()

client = OpenRouter(
    api_key=api_key,
    server_url="https://ai.hackclub.com/proxy/v1",
)

messages = [
    {"role": "system",
        "content": (
            "You are an audio chatbot named Maraca. "
            "Your tone is friendly, modern, concise. "
            "You are a text to audio chatbot so NEVER use markdown formatting or emojis as it simply will not show up properly."
            "Always keep answers short but useful."
            "Remember you are talking to a human so use some natural language and avoid sounding robotic. Ironicly the TTS engin I'm using makes you sound very robotic."
        )
    }
]

while True:
    user_input = speech_to_text()
    if not user_input:
        continue

    if user_input.strip().lower() == "exit" or user_input.strip().lower() == "end":
        break
    
    try:
        reply = call_api(messages, user_input)
        speak(reply)
    except Exception as exc:
        error_text = str(exc)
        if "Authentication failed" in error_text or "Status 401" in error_text:
            speak("Authentication failed. Please check your API key. Paste it below, then the app will end. Open it again and you'll be good to go.")
            set_key()
            break
        speak(f"API error: {error_text}")
        speak("Please check your internet connection or contact the app's developer if issues persist.")
speak("Chat ended.")
