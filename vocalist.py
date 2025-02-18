import os
import speech_recognition as sr
import datetime
import google.generativeai as genai 
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

current_date = datetime.date.today().strftime("%Y-%m-%d") # Get today's date in the format "YYYY-MM-DD"

todo_instruction = '''The user will be prompted to speak after the system says "Listening...". 
The system will then take the user's input and convert it to text. The text will then be sent 
to you. We are a to-do list application, and your job is to take the user's input and convert 
it into a bulleted list. We will be adding these as tasks to a to-do list, so try to analyze the
user's input and extract actionable tasks. Do not say anything else to the user. Only the bulleted
list of tasks, with the date and time if provided by the user on the same line as the task, separated by
a colon. For the date, use the format "MM/DD/YYYY" and for the time, use the format "HH:MM AM/PM".
Try to use today's date if the user does not provide one. Today's date is ''' + current_date + '''.''' + '''
If no tasks provided, return nothing at all. Only print dates that are after the current date.'''

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
  system_instruction=todo_instruction
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
        return text
    except sr.UnknownValueError:
        print("Could not understand the audio")
    except sr.RequestError:
        print("Error connecting to the speech recognition service")

def speech_to_gemini(speech):
    response = chat_session.send_message(speech)
    return response.text

def text_to_gemini(text):
    response = chat_session.send_message(text)
    return response.text

def gemini_to_list(gemini_response):
  # Initialize an empty list to hold tasks.
  tasks = []
  # Split the response into lines
  for line in gemini_response.splitlines():
    stripped_line = line.strip()
    if not stripped_line:
      continue
    # Check if the line starts with a bullet or dash
    if stripped_line.startswith(("-", "*", "•")):
      # Remove the bullet and any punctuation following it
      task = stripped_line.lstrip("-*•").strip(" .:").strip()
      if task:
        tasks.append(task)
    # Check if the line seems to use numbering, e.g. "1. Task"
    elif stripped_line[0].isdigit():
      parts = stripped_line.split(".", 1)
      if len(parts) == 2:
        task = parts[1].strip()
        if task:
          tasks.append(task)
    else:
      # If no common list marker is found, add the whole line
      tasks.append(stripped_line)
  return tasks

import json

def save_results(data, filename="results.json"):
    with open(filename, "w") as file:
        json.dump(data, file)

def load_results(filename="results.json"):
    if os.path.exists(filename):  # Check if file exists
        with open(filename, "r") as file:
            return json.load(file)
    return {}  # Return an empty dictionary if file does not exist

def main():
    task_list = load_results()
    if not isinstance(task_list, list):
        task_list = []
    while True:
        print("\nSelect an option:")
        print("1. Speech Input")
        print("2. Type Input")
        print("3. Clear All Tasks")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            print("You selected Speech Input")
            text = recognize_speech()
            gemini_response = speech_to_gemini(text)
            tasks = gemini_to_list(gemini_response)
            task_list = tasks + task_list
            print(task_list)
            save_results(task_list)
        elif choice == "2":
            print("You selected Type Input")
            text = input("Yap away: ")
            gemini_response = text_to_gemini(text)
            tasks = gemini_to_list(gemini_response)
            task_list = tasks + task_list
            print(task_list)
            save_results(task_list)
        elif choice == "3":
            task_list = []
            print(task_list)
            save_results(task_list)
            print("All tasks cleared!")
            # Implement task clearing logic here
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
  main()
