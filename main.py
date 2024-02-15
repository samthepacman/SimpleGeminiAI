import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import subprocess
import os
import tkinter as tk
import time


def on_key_press(event):
    if event.keysym == 'Escape':
        root.destroy()

def close_window():
    global root
    if root:
        root.destroy()


def show(text):
    global root
    root = tk.Tk()
    root.title("Text Viewer")
    root.geometry("900x700") 

    screenWidth = root.winfo_screenwidth()
    screenHeight = root.winfo_screenheight()
    xCoordinate = (screenWidth - 900) / 2
    yCoordinate = (screenHeight - 700) / 2

    root.geometry(f"900x700+{int(xCoordinate)}+{int(yCoordinate)}")
    root.overrideredirect(True)

    bottomFrame = tk.Frame(root, bg="black")
    bottomFrame.pack(side="bottom", fill="both", expand=True)
    topPadding = 50
    sidePadding = 20
    root.geometry(f"900x700+{int(xCoordinate - sidePadding)}+{int(yCoordinate - topPadding)}")
    closeButton = tk.Button(
        bottomFrame,
        text="Close Window",
        command=closeWindow,
        bg="black",
        fg="white",
        font=("Iosevka SS07", 12)
    )
    closeButton.pack(pady=10)
    root.bind_all('<Escape>', on_key_press)
    textWidget = tk.Text(
        root,
        wrap="word",
        bg="black",
        fg="white",
        font=("Iosevka SS07", 12),
        padx=sidePadding,
        pady=topPadding
    )
    textWidget.insert(tk.END, text)
    textWidget.configure(state=tk.DISABLED)
    textWidget.pack(expand=1, fill="both")
    root.mainloop()


genai.configure(api_key="<your - api - key>")

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 150,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  }
]

def speak(text):
    try:
        tts = gTTS(text=text, lang="en", slow=False, tld="co.uk")
        tts.save("temp.mp3")
        subprocess.run(["mpv", "temp.mp3"])
        os.remove("temp.mp3")
    except Exception as e:
        print(f"Error speaking: {e}")

def listen_and_return_command():
    recognizer = sr.Recognizer()

    while True:
        with sr.Microphone() as source:
            os.system("notify-send 'AI listening for keyword'")
            print("Listening for keyword...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            print(f"Recognized: {text}")

            if "hey maya" in text.lower():
                print("Keyword detected: 'Hey Maya'")
                print("Listening for command...")
                
                # Listen for a command after the keyword
                with sr.Microphone() as command_source:
                    os.system("notify-send 'Listening for command...'")
                    recognizer.adjust_for_ambient_noise(command_source)
                    command_audio = recognizer.listen(command_source)

                try:
                    command_text = recognizer.recognize_google(command_audio)
                    print(f"You said: {command_text}")
                    return str(command_text)

                except sr.UnknownValueError:
                    print("Could not understand the command")
                except sr.RequestError as e:
                    print(f"Error with the speech recognition service; {e}")
                  
                time.sleep(20)

        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Error with the speech recognition service; {e}")
        time.sleep(1)

model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)
while True:
    inputParam = listen_and_return_command()
    promptParts = [ inputParam ]
    response = model.generate_content(promptParts)
    
    if len(response.text) < 500 :
        speak(response.text)
    else:
        speak("Since the description is too large , it would be better to show it")
        show(response.text)
