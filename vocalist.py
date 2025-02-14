import speech_recognition as sr
import google.generativeai as genai

genai.configure(api_key='')

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

sys_instruction = '''The user will be prompted to speak after the system says "Listening...". 
The system will then take the user's input and convert it to text. The text will then be sent 
to you. We are a to-do list application, and your job is to take the user's input and convert 
it into a bulleted list. We will be adding these as tasks to a to-do list, so try to analyze the
user's input and extract actionable tasks.'''

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
  system_instruction=sys_instruction
)

chat_session = model.start_chat(
  history=[
  ]
)

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print("You said: " + text)
        speech_to_gemini(text)
    except sr.UnknownValueError:
        print("Could not understand the audio")
    except sr.RequestError:
        print("Error connecting to the speech recognition service")

def speech_to_gemini(speech):
    response = chat_session.send_message(speech)
    print("Gemini said: " + response.text)
    return response.text

if __name__ == "__main__":
    recognize_speech()

