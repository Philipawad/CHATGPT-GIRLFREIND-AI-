import openai
import tkinter as tk
from tkinter import ttk
import random
from ttkthemes import ThemedTk


api_key = "YOUR API KEY HERE"
openai.api_key = api_key

name = "YOUR NAME HERE"
file_name = "conversation_history.txt"

with open(file_name, "r") as file:
    conversation_history = file.readlines()

def remove_first_lines_if_limit_reached(file_name, line_limit=20, lines_to_remove=15):
    with open(file_name, "r") as file:
        lines = file.readlines()

    if len(lines) > line_limit:
        with open(file_name, "w") as file:
            file.writelines(lines[lines_to_remove:])




def get_chatgpt_response(user_input):
    remove_first_lines_if_limit_reached(file_name)
    conversation_history.append(f"{name}: {user_input}\n")
    prompt = f"HI {name}!YOUR PROMT HERE.\n\nKonversationshistorik:\n"

    for message in conversation_history:
        prompt += message

    prompt += "AI: YOUR PROMT NR 2 HERE"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=600,
        n=3,
        temperature=0.9,
        presence_penalty=0.6,
        frequency_penalty=0.3,
    )

    answer = random.choice(response.choices).text.strip()
    conversation_history.append(f"AI: {answer}\n")

    with open("user_inputs.txt", "a") as f:
        f.write(f"{name}: {user_input}\n")

    return answer


def speak(chatgpt_response, voice):
    pass


def on_send():
    user_input = user_input_var.get()
    chatgpt_response = get_chatgpt_response(user_input)

    chat_text.config(state="normal")
    chat_text.insert(tk.END, f"{name}: {user_input}\n\n")
    chat_text.insert(tk.END, f"CHAT BOT NAME HERE: {chatgpt_response}\n\n")
    chat_text.config(state="disabled")

    user_input_var.set("")

    with open(file_name, "w") as file:
        file.writelines(conversation_history)


root = ThemedTk(theme="equilux")
root.title("YOUR CHAT BOT NAME HERE")

style = ttk.Style()
style.configure("TEntry", font=("Helvetica", 35))
style.configure("TButton", font=("Helvetica", 35))

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

chat_text = tk.Text(frame, wrap="word", width=55, height=30, state="disabled")
chat_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
chat_text.configure(font=("Helvetica", 25))

user_input_var = tk.StringVar()
user_input_entry = ttk.Entry(frame, textvariable=user_input_var, width=20, font=("Helvetica", 35))
user_input_entry.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

send_button = ttk.Button(frame, text="Send", command=on_send, style="TButton")
send_button.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)



user_input_entry.focus()

root.mainloop()