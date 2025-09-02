from fastapi import FastAPI, HTTPException
import pyodbc
import pandas as pd
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import requests
from datetime import datetime
import threading

load_dotenv()

BASE_URL = "https://src-task-management.onrender.com/"  # API의 기본 URL

app = FastAPI()

def get_connection():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

@app.get("/")
def root():
    return {"message": "API 서버 정상 작동 중"}

@app.post("/users/register")
def register_user(email: str, password: str, four_letter: str):
    data = {
        "email": email,
        "password": password,
        "four_letter": four_letter
    }
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Users (email, password, four_letter)
            VALUES (?, ?, ?)
        ''', (email, password, four_letter))
        conn.commit()
        return {"message": "User registration request submitted for approval!"}
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Email or four letter already exists.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/users/login")
def login_user(four_letter: str, password: str = None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if password:
            cursor.execute('''
                SELECT * FROM Users WHERE LOWER(four_letter) = LOWER(?) AND password = ?
            ''', (four_letter, password))
        else:
            cursor.execute('''
                SELECT * FROM Users WHERE LOWER(four_letter) = LOWER(?)
            ''', (four_letter,))

        user = cursor.fetchone()
        if user and user[3] == 1:  # user[3]는 approved 필드
            return {"user": {"id": user[0], "email": user[1], "four_letter": user[4]}}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials or account not approved.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Tkinter GUI 코드
def api_get(endpoint):
    response = requests.get(f"{BASE_URL}/{endpoint}")
    response.raise_for_status()
    return response.json()

def api_post(endpoint, data):
    response = requests.post(f"{BASE_URL}/{endpoint}", json=data)
    response.raise_for_status()
    return response.json()

def open_registration_dialog():
    bg_color = "#cce7f0"
    fg_color = "#002244"
    entry_bg = "#f0f8ff"
    button_bg = "#3399cc"
    button_fg = "#ffffff"
    accent_color = "#2277aa"

    reg_window = tk.Toplevel()
    reg_window.title("Register")
    reg_window.geometry("350x250")
    reg_window.configure(bg=bg_color)

    tk.Label(reg_window, text="Email:", bg=bg_color, fg=fg_color, font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=10, sticky='e')
    tk.Label(reg_window, text="Password (optional):", bg=bg_color, fg=fg_color, font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    tk.Label(reg_window, text="Four Letter:", bg=bg_color, fg=fg_color, font=("Arial", 10)).grid(row=2, column=0, padx=10, pady=10, sticky='e')

    email_entry = tk.Entry(reg_window, bg=entry_bg, fg=fg_color, insertbackground=fg_color)
    password_entry = tk.Entry(reg_window, show='*', bg=entry_bg, fg=fg_color, insertbackground=fg_color)
    four_letter_entry = tk.Entry(reg_window, bg=entry_bg, fg=fg_color, insertbackground=fg_color)

    email_entry.grid(row=0, column=1, padx=10, pady=10)
    password_entry.grid(row=1, column=1, padx=10, pady=10)
    four_letter_entry.grid(row=2, column=1, padx=10, pady=10)

    def register():
        email = email_entry.get()
        password = password_entry.get()
        four_letter = four_letter_entry.get()
        if email and four_letter:
            register_user(email, password, four_letter)
            reg_window.destroy()
        else:
            messagebox.showwarning("Input Error", "Please fill in all required fields.")

    tk.Button(
        reg_window,
        text="Register",
        command=register,
        bg=button_bg,
        fg=button_fg,
        activebackground=accent_color,
        activeforeground=button_fg,
        width=15,
        height=2
    ).grid(row=3, column=0, columnspan=2, pady=20)

def setup_gui():
    global root
    root = tk.Tk()
    root.title("ASML SRC TO-DO List")
    root.geometry("800x600")

    bg_color = "#cce7f0"
    fg_color = "#002244"
    entry_bg = "#f0f8ff"
    button_bg = "#3399cc"
    button_fg = "#ffffff"
    accent_color = "#2277aa"

    root.configure(bg=bg_color)

    img = Image.open("Picture1.png")
    img = img.resize((200, 200), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)

    img_label = tk.Label(root, image=img_tk, bg=bg_color)
    img_label.image = img_tk
    img_label.pack(pady=(30, 10))

    frame = tk.Frame(root, bg=bg_color)
    frame.pack(pady=10)

    tk.Label(frame, text="Four Letter:", bg=bg_color, fg=fg_color, font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky='e')
    four_letter_entry = tk.Entry(frame, width=25, bg=entry_bg, fg=fg_color, insertbackground=fg_color)
    four_letter_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(frame, text="Password (optional):", bg=bg_color, fg=fg_color, font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky='e')
    password_entry = tk.Entry(frame, show='*', width=25, bg=entry_bg, fg=fg_color, insertbackground=fg_color)
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    def login():
        four_letter = four_letter_entry.get()
        password = password_entry.get()
        user = login_user(four_letter, password)
        if user:
            open_main_application(user)
        else:
            messagebox.showerror("Error", "Invalid four letter code or account not approved.")

    button_frame = tk.Frame(frame, bg=bg_color)
    button_frame.grid(row=2, column=0, columnspan=2, pady=15)

    login_button = tk.Button(button_frame, text="Login", command=login, width=10, height=2,
                             bg=button_bg, fg=button_fg, activebackground=accent_color, activeforeground=button_fg)
    login_button.pack(side="left", padx=10)

    register_button = tk.Button(button_frame, text="Register", command=open_registration_dialog, width=10, height=2,
                                bg=button_bg, fg=button_fg, activebackground=accent_color, activeforeground=button_fg)
    register_button.pack(side="left", padx=10)

    made_by_label = tk.Label(root, text="Made by Leo Park", bg=bg_color, fg=fg_color, font=("Arial", 9, "italic"))
    made_by_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

# 메인 함수
def main():
    # FastAPI 서버를 별도의 스레드에서 실행
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8000)).start()
    setup_gui()
    root.mainloop()  # 메인 루프 추가

if __name__ == "__main__":
    main()