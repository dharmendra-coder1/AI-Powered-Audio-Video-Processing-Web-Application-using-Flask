import tkinter as tk
import threading
import speech_recognition as sr

class RealTimeTranscriber:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Transcription")
        self.textbox = tk.Text(root, height=20, width=80)
        self.textbox.pack(padx=10, pady=10)
        self.recognizer = sr.Recognizer()
        self.running = False

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Start", command=self.start).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Stop", command=self.stop).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save", command=self.save_text).pack(side=tk.LEFT, padx=5)

    def start(self):
        self.running = True
        threading.Thread(target=self.transcribe).start()

    def stop(self):
        self.running = False

    def save_text(self):
        with open("real_time_transcript.txt", "w", encoding='utf-8') as f:
            f.write(self.textbox.get("1.0", tk.END))
        print("Saved to real_time_transcript.txt")

    def transcribe(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.running:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text = self.recognizer.recognize_google(audio)
                    self.textbox.insert(tk.END, text + ' ')
                    self.textbox.see(tk.END)
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print("Error:", e)

if __name__ == "__main__":
    root = tk.Tk()
    app = RealTimeTranscriber(root)
    root.mainloop()
