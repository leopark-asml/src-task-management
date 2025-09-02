import pyodbc
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
from datetime import datetime

# Azure SQL Database 연결 정보
server = 'upgrade-src-todolist.database.windows.net'
database = 'Upgrade-SRC-Todolist'
username = 'jpark56'
password = '990506qw!?'
driver = '{ODBC Driver 18 for SQL Server}'  # 설치된 드라이버 이름

def connect_to_database():
    try:
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=upgrade-src-todolist.database.windows.net,1433;"
            "DATABASE=Upgrade-SRC-Todolist;"
            "UID=jpark56;"
            "PWD=990506qw!?;"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        conn = pyodbc.connect(conn_str)
        print("Connection successful!")
        return conn
    except pyodbc.Error as e:
        print("Connection failed:", e)
        return None


def initialize_database():
    conn = connect_to_database()
    if conn is None:
        return
    cursor = conn.cursor()

    # Users 테이블 생성
    cursor.execute('''
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
    CREATE TABLE Users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        email VARCHAR(255) UNIQUE,
        password VARCHAR(255),
        approved BIT DEFAULT 0,
        is_admin BIT DEFAULT 0,
        four_letter VARCHAR(255) UNIQUE
    )
    ''')

    # Tasks 테이블 생성
    cursor.execute('''
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Tasks' AND xtype='U')
    CREATE TABLE Tasks (
        id INT IDENTITY(1,1) PRIMARY KEY,
        title VARCHAR(255),
        description TEXT,
        due_date DATE,
        assigned_user_id INT,
        completed BIT DEFAULT 0,
        remark TEXT,
        FOREIGN KEY (assigned_user_id) REFERENCES Users(id)
    )
    ''')

# 사용자 등록
def register_user(email, password, four_letter):
    conn = connect_to_database()  # 데이터베이스 연결
    if conn is None:
        return  # 연결 실패 시 함수 종료
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO Users (email, password, four_letter)
        VALUES (?, ?, ?)
        ''', (email, password if password else None, four_letter))  # 비밀번호가 없으면 None으로 설정
        conn.commit()  # 변경 사항 커밋
        messagebox.showinfo("Registration", "User registration request submitted for approval!")
    except pyodbc.IntegrityError:
        messagebox.showwarning("Registration Error", "Email or four letter already exists.")
    except Exception as e:
        messagebox.showerror("Error", str(e))  # 일반적인 에러 처리
    finally:
        conn.close()  # 연결 종료

def login_user(four_letter, password=None):
    conn = connect_to_database()  # 데이터베이스 연결
    if conn is None:
        return None  # 연결 실패 시 None 반환
    cursor = conn.cursor()

    # four_letter를 소문자로 변환하여 비교
    if password:
        cursor.execute('''
        SELECT * FROM Users WHERE LOWER(four_letter) = LOWER(?) AND password = ?
        ''', (four_letter, password))
    else:
        cursor.execute('''
        SELECT * FROM Users WHERE LOWER(four_letter) = LOWER(?)
        ''', (four_letter,))

    user = cursor.fetchone()
    conn.close()

    if user and user[3] == 1:  # user[3]는 approved 필드
        return user
    else:
        return None

# 회원가입 다이얼로그
def open_registration_dialog():
    # 색상 테마
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

    # 라벨 및 입력 필드
    tk.Label(reg_window, text="Email:", bg=bg_color, fg=fg_color, font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=10, sticky='e')
    tk.Label(reg_window, text="Password (optional):", bg=bg_color, fg=fg_color, font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    tk.Label(reg_window, text="Four Letter:", bg=bg_color, fg=fg_color, font=("Arial", 10)).grid(row=2, column=0, padx=10, pady=10, sticky='e')

    email_entry = tk.Entry(reg_window, bg=entry_bg, fg=fg_color, insertbackground=fg_color)
    password_entry = tk.Entry(reg_window, show='*', bg=entry_bg, fg=fg_color, insertbackground=fg_color)
    four_letter_entry = tk.Entry(reg_window, bg=entry_bg, fg=fg_color, insertbackground=fg_color)

    email_entry.grid(row=0, column=1, padx=10, pady=10)
    password_entry.grid(row=1, column=1, padx=10, pady=10)
    four_letter_entry.grid(row=2, column=1, padx=10, pady=10)

    # 등록 함수
    def register():
        email = email_entry.get()
        password = password_entry.get()
        four_letter = four_letter_entry.get()
        if email and four_letter:
            register_user(email, password, four_letter)
            reg_window.destroy()
        else:
            messagebox.showwarning("Input Error", "Please fill in all required fields.")

    # 등록 버튼
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


# TO-DO 항목 생성
def create_task(user):
    # 색상 테마
    bg_color = "#cce7f0"
    fg_color = "#002244"
    entry_bg = "#f0f8ff"
    button_bg = "#3399cc"
    button_fg = "#ffffff"
    accent_color = "#2277aa"

    task_window = tk.Toplevel()
    task_window.title("Create Task")
    task_window.geometry("700x600")
    task_window.configure(bg=bg_color)

    frame = tk.Frame(task_window, bg=bg_color)
    frame.pack(expand=True, fill=tk.BOTH)

    for i in range(6):
        frame.grid_rowconfigure(i, weight=2)
    for i in range(2):
        frame.grid_columnconfigure(i, weight=2)

    def styled_label(master, text, row):
        tk.Label(master, text=text, bg=bg_color, fg=fg_color, font=("Arial", 10)).grid(
            row=row, column=0, padx=10, pady=10, sticky='e'
        )

    def styled_entry(master, row):
        entry = tk.Entry(master, width=40, bg=entry_bg, fg=fg_color, insertbackground=fg_color)
        entry.grid(row=row, column=1, padx=10, pady=10, sticky='ew')
        return entry

    styled_label(frame, "Task Title:", 0)
    title_entry = styled_entry(frame, 0)

    styled_label(frame, "Description:", 1)
    description_entry = styled_entry(frame, 1)

    styled_label(frame, "Due Date (YYYY-MM-DD):", 2)
    due_date_entry = styled_entry(frame, 2)

    styled_label(frame, "Assign Task To:", 3)
    user_listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, height=10, width=40, bg=entry_bg, fg=fg_color)
    user_listbox.grid(row=3, column=1, padx=10, pady=10, sticky='ew')

    # 사용자 목록 가져오기
    conn = connect_to_database()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute('SELECT id, four_letter, email FROM Users WHERE approved = 1')
    users = cursor.fetchall()
    conn.close()

    for user in users:
        user_listbox.insert(tk.END, f"{user[1]} (E-Mail: {user[2]})")

    def select_all_users():
        user_listbox.select_set(0, tk.END)

    tk.Button(
        frame,
        text="Select All",
        command=select_all_users,
        bg=button_bg,
        fg=button_fg,
        activebackground=accent_color,
        activeforeground=button_fg,
        width=15,
        height=2
    ).grid(row=4, column=0, pady=10, padx=5, sticky='ew')

    def save_task():
        title = title_entry.get()
        description = description_entry.get()
        due_date_str = due_date_entry.get()
        selected_users = user_listbox.curselection()

        if not selected_users:
            messagebox.showwarning("Warning", "Please select at least one user.")
            return

        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid Date", "Please fill the Due Date form like (YYYY-MM-DD).")
            return

        assigned_user_ids = [users[i][0] for i in selected_users]

        conn = connect_to_database()
        if conn is None:
            return
        cursor = conn.cursor()
        for user_id in assigned_user_ids:
            cursor.execute('''
                INSERT INTO Tasks (title, description, due_date, assigned_user_id, completed, remark)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, description, due_date, user_id, 0, ""))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Tasks created successfully for selected users!")
        task_window.destroy()

    tk.Button(
        frame,
        text="Create Task",
        command=save_task,
        bg=button_bg,
        fg=button_fg,
        activebackground=accent_color,
        activeforeground=button_fg,
        width=15,
        height=2
    ).grid(row=4, column=1, pady=10, padx=5, sticky='ew')



# TO-DO 항목 조회 및 응답
def view_my_tasks(user):
    tasks = []  # 바깥에서 선언
    # 색상 테마
    bg_color = "#cce7f0"
    fg_color = "#002244"
    entry_bg = "#f0f8ff"
    button_bg = "#3399cc"
    button_fg = "#ffffff"
    accent_color = "#2277aa"

    tasks_window = tk.Toplevel()
    tasks_window.title("My Tasks")
    tasks_window.geometry("800x400")
    tasks_window.configure(bg=bg_color)

    # 리스트박스
    task_listbox = tk.Listbox(tasks_window, width=100, height=15, bg=entry_bg, fg=fg_color, font=("Arial", 10))
    task_listbox.pack(pady=10, padx=10)

    def update_task_list():
        task_listbox.delete(0, tk.END)
        conn = connect_to_database()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, description, due_date, completed, remark 
            FROM Tasks 
            WHERE assigned_user_id = ? 
            ORDER BY due_date ASC
        ''', (user[0],))
        nonlocal tasks
        tasks = cursor.fetchall()
        conn.close()

        for task in tasks:
            state = "✅ Done" if task[4] else "❌ Not Done"
            task_listbox.insert(tk.END, f"📌 Title: {task[1]}")
            task_listbox.insert(tk.END, f"📝 Description: {task[2]}")
            task_listbox.insert(tk.END, f"📅 Due Date: {task[3]}")
            task_listbox.insert(tk.END, f"📍 State: {state}")
            task_listbox.insert(tk.END, f"💬 Remark: {task[5] or 'N/A'}")
            task_listbox.insert(tk.END, "-" * 60)

    update_task_list()

    def select_task(event):
        selected = task_listbox.curselection()
        if selected:
            index = selected[0] // 6
            start_index = index * 6
            end_index = start_index + 5
            task_listbox.selection_clear(0, tk.END)
            task_listbox.selection_set(start_index, end_index)

    task_listbox.bind('<ButtonRelease-1>', select_task)

    def respond_to_task():
        selected = task_listbox.curselection()
        if selected:
            index = selected[0] // 6
            task_id = tasks[index][0]

            response_window = tk.Toplevel(tasks_window)
            response_window.title("Respond to Task")
            response_window.geometry("300x200")
            response_window.configure(bg=bg_color)

            tk.Label(response_window, text="Select your response:", bg=bg_color, fg=fg_color, font=("Arial", 10)).pack(pady=10)

            button_frame = tk.Frame(response_window, bg=bg_color)
            button_frame.pack(expand=True)

            def submit_response(response):
                conn = connect_to_database()
                if conn is None:
                    return
                cursor = conn.cursor()
                if response == "Done":
                    cursor.execute('UPDATE Tasks SET completed = ? WHERE id = ?', (1, task_id))
                elif response == "Not Done":
                    cursor.execute('UPDATE Tasks SET completed = ? WHERE id = ?', (0, task_id))
                elif response == "N/A":
                    cursor.execute('UPDATE Tasks SET completed = ?, remark = ? WHERE id = ?', (0, "N/A", task_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Task response recorded successfully!")
                update_task_list()
                response_window.destroy()

            for label in ["Done", "Not Done", "N/A"]:
                tk.Button(
                    button_frame,
                    text=label,
                    command=lambda l=label: submit_response(l),
                    bg=button_bg,
                    fg=button_fg,
                    activebackground=accent_color,
                    activeforeground=button_fg,
                    width=15,
                    height=2
                ).pack(pady=5)

    def add_remark():
        selected = task_listbox.curselection()
        if selected:
            index = selected[0] // 6
            task_id = tasks[index][0]
            remark = simpledialog.askstring("Remark", "Enter your remark:")
            if remark:
                conn = connect_to_database()
                if conn is None:
                    return
                cursor = conn.cursor()
                cursor.execute('UPDATE Tasks SET remark = ? WHERE id = ?', (remark, task_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Remark added successfully!")
                update_task_list()

    # 버튼 프레임
    button_frame = tk.Frame(tasks_window, bg=bg_color)
    button_frame.pack(pady=10)

    tk.Button(
        button_frame,
        text="Respond",
        command=respond_to_task,
        bg=button_bg,
        fg=button_fg,
        activebackground=accent_color,
        activeforeground=button_fg,
        width=15,
        height=2
    ).pack(side=tk.LEFT, padx=10)

    tk.Button(
        button_frame,
        text="Remark",
        command=add_remark,
        bg=button_bg,
        fg=button_fg,
        activebackground=accent_color,
        activeforeground=button_fg,
        width=15,
        height=2
    ).pack(side=tk.LEFT, padx=10)


    task_listbox.bind('<ButtonRelease-1>', select_task)  # 클릭 이벤트 바인딩

# 어드민 패널
def open_admin_panel():
    # 색상 테마
    bg_color = "#cce7f0"
    fg_color = "#002244"
    entry_bg = "#f0f8ff"
    button_bg = "#3399cc"
    button_fg = "#ffffff"
    accent_color = "#2277aa"

    admin_window = tk.Toplevel()
    admin_window.title("Admin Panel")
    admin_window.geometry("700x450")
    admin_window.configure(bg=bg_color)

    # 리스트박스
    task_listbox = tk.Listbox(admin_window, width=100, height=15, bg=entry_bg, fg=fg_color, font=("Arial", 10))
    task_listbox.pack(pady=10, padx=10)

    conn = connect_to_database()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, due_date, assigned_user_id, completed FROM Tasks')
    tasks = cursor.fetchall()
    conn.close()

    for task in tasks:
        task_listbox.insert(
            tk.END,
            f"📌 Title: {task[1]} | 📅 Due: {task[3]} | 👤 User ID: {task[4]} | ✅ Completed: {'Yes' if task[5] else 'No'}"
        )

    def delete_task():
        selected = task_listbox.curselection()
        if selected:
            index = selected[0]
            task_id = tasks[index][0]
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?")
            if not confirm:
                return

            conn = connect_to_database()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute('DELETE FROM Tasks WHERE id = ?', (task_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Task deleted successfully!")
            admin_window.destroy()
            open_admin_panel()  # 새로고침

    # 버튼 프레임
    button_frame = tk.Frame(admin_window, bg=bg_color)
    button_frame.pack(pady=10)

    tk.Button(
        button_frame,
        text="Delete Task",
        command=delete_task,
        bg=button_bg,
        fg=button_fg,
        activebackground=accent_color,
        activeforeground=button_fg,
        width=15,
        height=2
    ).pack()

from tkinter import PhotoImage

def open_main_application(user):
    # 로그인 창 숨기기
    root.withdraw()

    # 색상 테마
    bg_color = "#cce7f0"
    fg_color = "#002244"
    button_bg = "#3399cc"
    button_fg = "#ffffff"
    accent_color = "#2277aa"

    # 메인 애플리케이션 창 생성
    main_window = tk.Toplevel(root)
    main_window.title("ASML SRC TO-DO List")
    main_window.geometry("1000x700")
    main_window.configure(bg=bg_color)

    # 아이콘 이미지 로드
    create_icon = PhotoImage(file="create_task_icon.png").subsample(5, 5)
    manage_icon = PhotoImage(file="manage_tasks_icon.png").subsample(5, 5)
    view_icon = PhotoImage(file="view_tasks_icon.png").subsample(3, 3)


    # 로그인 상태 메시지
    login_status_label = tk.Label(
        main_window,
        text=f"Logged in as: {user[5]} (Admin: {'Yes' if user[4] == 1 else 'No'})",
        bg=bg_color,
        fg=fg_color,
        font=("Arial", 10, "bold")
    )
    login_status_label.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)

    # Change Password 버튼
    tk.Button(
        main_window,
        text="Change Password",
        command=lambda: change_password(user),
        bg=button_bg,
        fg=button_fg,
        activebackground=accent_color,
        activeforeground=button_fg,
        width=15
    ).place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=50)

    # 로그아웃 버튼
    tk.Button(
        main_window,
        text="Logout",
        command=lambda: logout(main_window),
        bg=button_bg,
        fg=button_fg,
        activebackground=accent_color,
        activeforeground=button_fg,
        width=15
    ).place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=90)

    # 중앙 프레임 (가로 정렬)
    center_frame = tk.Frame(main_window, bg=bg_color)
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

    # 버튼 + 아이콘 묶음 생성 함수
    def icon_button(master, icon, text, command):
        frame = tk.Frame(master, bg=bg_color)
        tk.Label(frame, image=icon, bg=bg_color).pack()
        tk.Button(
            frame,
            text=text,
            command=command,
            width=15,
            height=2,
            bg=button_bg,
            fg=button_fg,
            activebackground=accent_color,
            activeforeground=button_fg,
            font=("Arial", 10, "bold")
        ).pack(pady=5)
        return frame

    # 버튼 리스트
    button_frames = []

    if user[4] == 1:
        button_frames.append(icon_button(center_frame, create_icon, "Create Task", lambda: create_task(user)))
        button_frames.append(icon_button(center_frame, manage_icon, "Manage Tasks", open_manage_tasks_window))

    button_frames.append(icon_button(center_frame, view_icon, "View My Tasks", lambda: view_my_tasks(user)))

    # 버튼 프레임 가로 배치
    for i, frame in enumerate(button_frames):
        frame.grid(row=0, column=i, padx=30)

    # 어드민 전용 하단 버튼
    if user[4] == 1:
        tk.Button(
            main_window,
            text="Manage Users",
            command=open_user_management_window,
            bg=button_bg,
            fg=button_fg,
            activebackground=accent_color,
            activeforeground=button_fg,
            width=20
        ).place(relx=0.0, rely=1.0, anchor='sw', x=10, y=-35)

        tk.Button(
            main_window,
            text="Approval Panel",
            command=open_approval_panel,
            bg=button_bg,
            fg=button_fg,
            activebackground=accent_color,
            activeforeground=button_fg,
            width=20
        ).place(relx=0.0, rely=1.0, anchor='sw', x=10, y=-10)

    # 이미지 참조 유지
    main_window.create_icon = create_icon
    main_window.manage_icon = manage_icon
    main_window.view_icon = view_icon




# 로그아웃 함수
def logout(main_window):
    main_window.destroy()  # 메인 애플리케이션 창 닫기
    root.deiconify()  # 로그인 창 다시 보이기

# 비밀번호 변경 함수
def change_password(user):
    # 색상 테마
    bg_color = "#cce7f0"
    fg_color = "#002244"
    entry_bg = "#f0f8ff"
    button_bg = "#3399cc"
    button_fg = "#ffffff"
    accent_color = "#2277aa"

    dialog = tk.Toplevel()
    dialog.title("Change Password")
    dialog.geometry("350x250")
    dialog.configure(bg=bg_color)

    def labeled_entry(master, label_text, show=None):
        tk.Label(master, text=label_text, bg=bg_color, fg=fg_color, font=("Arial", 10)).pack(pady=5)
        entry = tk.Entry(master, show=show, bg=entry_bg, fg=fg_color, insertbackground=fg_color)
        entry.pack(pady=5)
        return entry

    current_pw_entry = labeled_entry(dialog, "Current Password:", show='*')
    new_pw_entry = labeled_entry(dialog, "New Password:", show='*')
    confirm_pw_entry = labeled_entry(dialog, "Confirm New Password:", show='*')

    def update_password():
        current_pw = current_pw_entry.get()
        new_pw = new_pw_entry.get()
        confirm_pw = confirm_pw_entry.get()

        if current_pw != user[3]:  # user[3] is the current password
            messagebox.showerror("Error", "Current password is incorrect.")
        elif new_pw != confirm_pw:
            messagebox.showerror("Error", "New passwords do not match.")
        else:
            conn = connect_to_database()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET password = ? WHERE id = ?", (new_pw, user[0]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Password updated successfully.")
            dialog.destroy()

    tk.Button(
        dialog,
        text="Update Password",
        command=update_password,
        bg=button_bg,
        fg=button_fg,
        activebackground=accent_color,
        activeforeground=button_fg,
        width=20,
        height=2
    ).pack(pady=15)

# 로그아웃 함수
def logout(main_window):
    main_window.destroy()  # 메인 애플리케이션 창 닫기
    root.deiconify()  # 로그인 창 다시 보이기

# 회원가입 승인 패널
def open_approval_panel():
    # 색상 테마
    bg_color = "#cce7f0"
    fg_color = "#002244"
    entry_bg = "#f0f8ff"
    button_bg = "#3399cc"
    button_fg = "#ffffff"
    accent_color = "#2277aa"

    approval_window = tk.Toplevel()
    approval_window.title("Approval Panel")
    approval_window.geometry("500x400")
    approval_window.configure(bg=bg_color)

    tk.Label(
        approval_window,
        text="Pending Registrations:",
        bg=bg_color,
        fg=fg_color,
        font=("Arial", 12, "bold")
    ).pack(pady=10)

    frame = tk.Frame(approval_window, bg=bg_color)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_pending_users():
        for widget in frame.winfo_children():
            widget.destroy()

        conn = connect_to_database()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT four_letter FROM Users WHERE approved = 0')
        pending_users = cursor.fetchall()
        conn.close()

        for i, user in enumerate(pending_users):
            user_label = tk.Label(
                frame,
                text=user[0],
                width=20,
                bg=entry_bg,
                fg=fg_color,
                font=("Arial", 10)
            )
            user_label.grid(row=i, column=0, padx=10, pady=5)

            approve_button = tk.Button(
                frame,
                text="Approve",
                command=lambda u=user[0]: approve_user(u),
                bg=button_bg,
                fg=button_fg,
                activebackground=accent_color,
                activeforeground=button_fg,
                width=10
            )
            approve_button.grid(row=i, column=1, padx=5, pady=5)

            reject_button = tk.Button(
                frame,
                text="Reject",
                command=lambda u=user[0]: reject_user(u),
                bg="#cc4444",
                fg=button_fg,
                activebackground="#aa2222",
                activeforeground=button_fg,
                width=10
            )
            reject_button.grid(row=i, column=2, padx=5, pady=5)

    def approve_user(four_letter):
        conn = connect_to_database()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('UPDATE Users SET approved = 1 WHERE four_letter = ?', (four_letter,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Approval", f"User {four_letter} has been approved.")
        load_pending_users()

    def reject_user(four_letter):
        conn = connect_to_database()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Users WHERE four_letter = ?', (four_letter,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Reject", f"User {four_letter} has been rejected.")
        load_pending_users()

    load_pending_users()

# GUI 설정 함수
def setup_gui():
    global root
    root = TkinterDnD.Tk()
    root.title("ASML SRC TO-DO List")
    root.geometry("800x600")

    # 부드러운 하늘색 테마
    bg_color = "#cce7f0"       # 톤 다운된 하늘색
    fg_color = "#002244"       # 어두운 남색
    entry_bg = "#f0f8ff"       # 연한 하늘색 (거의 흰색)
    button_bg = "#3399cc"      # 중간 하늘색
    button_fg = "#ffffff"      # 흰색
    accent_color = "#2277aa"   # 진한 블루

    root.configure(bg=bg_color)

    # 이미지 추가
    img = Image.open("Picture1.png")
    img = img.resize((200, 200), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)

    img_label = tk.Label(root, image=img_tk, bg=bg_color)
    img_label.image = img_tk
    img_label.pack(pady=(30, 10))

    # 로그인 프레임
    frame = tk.Frame(root, bg=bg_color)
    frame.pack(pady=10)

    # Four Letter
    tk.Label(frame, text="Four Letter:", bg=bg_color, fg=fg_color, font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky='e')
    four_letter_entry = tk.Entry(frame, width=25, bg=entry_bg, fg=fg_color, insertbackground=fg_color)
    four_letter_entry.grid(row=0, column=1, padx=10, pady=5)

    # Password
    tk.Label(frame, text="Password (optional):", bg=bg_color, fg=fg_color, font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky='e')
    password_entry = tk.Entry(frame, show='*', width=25, bg=entry_bg, fg=fg_color, insertbackground=fg_color)
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    # 로그인 함수
    def login():
        four_letter = four_letter_entry.get()
        password = password_entry.get()
        user = login_user(four_letter, password)
        if user:
            open_main_application(user)
        else:
            messagebox.showerror("Error", "Invalid four letter code or account not approved.")

    # 버튼 프레임
    button_frame = tk.Frame(frame, bg=bg_color)
    button_frame.grid(row=2, column=0, columnspan=2, pady=15)

    login_button = tk.Button(button_frame, text="Login", command=login, width=10, height=2,
                             bg=button_bg, fg=button_fg, activebackground=accent_color, activeforeground=button_fg)
    login_button.pack(side="left", padx=10)

    register_button = tk.Button(button_frame, text="Register", command=open_registration_dialog, width=10, height=2,
                                bg=button_bg, fg=button_fg, activebackground=accent_color, activeforeground=button_fg)
    register_button.pack(side="left", padx=10)

    # 하단 라벨
    made_by_label = tk.Label(root, text="Made by Leo Park", bg=bg_color, fg=fg_color, font=("Arial", 9, "italic"))
    made_by_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)




# 전역 변수 선언
users = []

def open_user_management_window():
    global users
    # 색상 테마
    bg_color = "#cce7f0"
    fg_color = "#002244"
    entry_bg = "#f0f8ff"
    button_bg = "#3399cc"
    button_fg = "#ffffff"
    accent_color = "#2277aa"

    user_management_window = tk.Toplevel()
    user_management_window.title("User Management")
    user_management_window.geometry("700x500")
    user_management_window.configure(bg=bg_color)

    user_listbox = tk.Listbox(user_management_window, width=100, height=15, bg=entry_bg, fg=fg_color, font=("Arial", 10))
    user_listbox.pack(pady=10, padx=10)

    def load_users():
        global users
        user_listbox.delete(0, tk.END)
        conn = connect_to_database()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, approved, is_admin, four_letter FROM Users')
        users = cursor.fetchall()
        conn.close()
        for user in users:
            user_listbox.insert(tk.END, f"ID: {user[0]}, Email: {user[1]}, Approved: {user[2]}, Admin: {user[3]}, Four Letter: {user[4]}")

    load_users()

    # 검색 프레임
    search_frame = tk.Frame(user_management_window, bg=bg_color)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Search Four Letter:", bg=bg_color, fg=fg_color, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    search_entry = tk.Entry(search_frame, bg=entry_bg, fg=fg_color, insertbackground=fg_color)
    search_entry.pack(side=tk.LEFT, padx=5)

    def search_users():
        search_term = search_entry.get().strip()
        user_listbox.delete(0, tk.END)
        conn = connect_to_database()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, approved, is_admin, four_letter FROM Users WHERE four_letter LIKE ?', ('%' + search_term + '%',))
        results = cursor.fetchall()
        conn.close()
        for user in results:
            user_listbox.insert(tk.END, f"ID: {user[0]}, Email: {user[1]}, Approved: {user[2]}, Admin: {user[3]}, Four Letter: {user[4]}")

    tk.Button(
        search_frame,
        text="Search",
        command=search_users,
        bg=button_bg,
        fg=button_fg,
        activebackground=accent_color,
        activeforeground=button_fg,
        width=10
    ).pack(side=tk.LEFT, padx=5)

    # 버튼 프레임
    button_frame = tk.Frame(user_management_window, bg=bg_color)
    button_frame.pack(pady=10)

    def edit_user():
        selected = user_listbox.curselection()
        if selected:
            index = selected[0]
            user = users[index]

            edit_window = tk.Toplevel()
            edit_window.title("Edit User")
            edit_window.geometry("400x300")
            edit_window.configure(bg=bg_color)

            edit_frame = tk.Frame(edit_window, bg=bg_color)
            edit_frame.pack(expand=True)

            labels = ["Email:", "Approved (1/0):", "Admin (1/0):", "Four Letter:"]
            values = [user[1], user[2], user[3], user[4]]
            entries = []

            for i, (label, value) in enumerate(zip(labels, values)):
                tk.Label(edit_frame, text=label, bg=bg_color, fg=fg_color).grid(row=i, column=0, padx=10, pady=5, sticky='e')
                entry = tk.Entry(edit_frame, bg=entry_bg, fg=fg_color, insertbackground=fg_color)
                entry.grid(row=i, column=1, padx=10, pady=5)
                entry.insert(0, value)
                entries.append(entry)

            def save_changes():
                new_email = entries[0].get().strip()
                new_approved = entries[1].get().strip()
                new_admin = entries[2].get().strip()
                new_four_letter = entries[3].get().strip()

                conn = connect_to_database()
                if conn is None:
                    return
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE Users SET email = ?, approved = ?, is_admin = ?, four_letter = ? WHERE id = ?
                ''', (new_email, new_approved, new_admin, new_four_letter, user[0]))
                conn.commit()
                conn.close()
                edit_window.destroy()
                load_users()

            tk.Button(
                edit_frame,
                text="Confirm",
                command=save_changes,
                bg=button_bg,
                fg=button_fg,
                activebackground=accent_color,
                activeforeground=button_fg,
                width=15,
                height=2
            ).grid(row=4, columnspan=2, pady=20)

    def delete_user(user_id):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?")
        if not confirm:
            return
        conn = connect_to_database()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Deleted", "User deleted successfully.")
        load_users()

    tk.Button(
        button_frame,
        text="Edit",
        command=edit_user,
        bg=button_bg,
        fg=button_fg,
        activebackground=accent_color,
        activeforeground=button_fg,
        width=15,
        height=2
    ).grid(row=0, column=0, padx=5)

    tk.Button(
        button_frame,
        text="Delete",
        command=lambda: delete_user(users[user_listbox.curselection()[0]][0]),
        bg="#cc4444",
        fg=button_fg,
        activebackground="#aa2222",
        activeforeground=button_fg,
        width=15,
        height=2
    ).grid(row=0, column=1, padx=5)


def delete_user(user_id):
    conn = connect_to_database()  # 데이터베이스 연결
    if conn is None:
        return  # 연결 실패 시 함수 종료
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Users WHERE id = ?', (user_id,))
    conn.commit()  # 변경 사항 커밋
    conn.close()  # 연결 종료

def open_manage_tasks_window():
    # 색상 테마
    bg_color = "#cce7f0"
    fg_color = "#002244"
    entry_bg = "#f0f8ff"
    button_bg = "#3399cc"
    button_fg = "#ffffff"
    accent_color = "#2277aa"

    manage_window = tk.Toplevel()
    manage_window.title("Manage Tasks")
    manage_window.geometry("800x400")
    manage_window.configure(bg=bg_color)

    task_listbox = tk.Listbox(manage_window, width=100, height=15, bg=entry_bg, fg=fg_color, font=("Arial", 10))
    task_listbox.pack(pady=10, padx=10)

    conn = connect_to_database()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, due_date FROM Tasks')
    tasks = cursor.fetchall()
    conn.close()

    task_dict = {}
    for task in tasks:
        task_id, title, description, due_date = task
        if title not in task_dict:
            task_dict[title] = {'id': task_id, 'description': description, 'due_date': due_date, 'user_ids': []}
        task_dict[title]['user_ids'].append(task_id)

    for title, details in task_dict.items():
        task_listbox.insert(tk.END, f"📌 Task: {title} | 📅 Due: {details['due_date']}")

    def show_task_details(event):
        selected = task_listbox.curselection()
        if selected:
            index = selected[0]
            title = task_listbox.get(index).split("|")[0].replace("📌 Task: ", "").strip()

            conn = connect_to_database()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Users.four_letter, Tasks.completed, Tasks.remark 
                FROM Tasks 
                JOIN Users ON Tasks.assigned_user_id = Users.id 
                WHERE Tasks.title = ?
            ''', (title,))
            responses = cursor.fetchall()
            conn.close()

            details_window = tk.Toplevel(manage_window)
            details_window.title("Task Details")
            details_window.geometry("600x400")
            details_window.configure(bg=bg_color)

            details_text = tk.Text(details_window, wrap=tk.WORD, bg=entry_bg, fg=fg_color, font=("Arial", 10))
            details_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

            details_text.insert(tk.END, f"📌 Task: {title}\n")
            details_text.insert(tk.END, "-" * 50 + "\n")
            details_text.insert(tk.END, f"{'User':<20} {'State':<10} {'Remark'}\n")
            details_text.insert(tk.END, "-" * 50 + "\n")

            for response in responses:
                four_letter = response[0]
                completed = "✅ Done" if response[1] else "❌ Not Done"
                remark = response[2] if response[2] else "N/A"
                details_text.insert(tk.END, f"{four_letter:<20} {completed:<10} {remark}\n")

    task_listbox.bind('<Double-Button-1>', show_task_details)

    def edit_task():
        selected = task_listbox.curselection()
        if selected:
            index = selected[0]
            title = task_listbox.get(index).split("|")[0].replace("📌 Task: ", "").strip()
            description = task_dict[title]['description']
            due_date = task_dict[title]['due_date']

            edit_window = tk.Toplevel(manage_window)
            edit_window.title("Edit Task")
            edit_window.geometry("600x400")
            edit_window.configure(bg=bg_color)

            def labeled_entry(label_text, default_value):
                tk.Label(edit_window, text=label_text, bg=bg_color, fg=fg_color, font=("Arial", 10)).pack(pady=5)
                entry = tk.Entry(edit_window, font=("Arial", 10), width=40, bg=entry_bg, fg=fg_color, insertbackground=fg_color)
                entry.insert(0, default_value)
                entry.pack(pady=5)
                return entry

            title_entry = labeled_entry("Task Title:", title)
            description_entry = labeled_entry("Description:", description)
            due_date_entry = labeled_entry("Due Date (YYYY-MM-DD):", due_date)

            def save_changes():
                new_title = title_entry.get().strip()
                new_description = description_entry.get().strip()
                new_due_date = due_date_entry.get().strip()

                conn = connect_to_database()
                if conn is None:
                    return
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE Tasks SET title = ?, description = ?, due_date = ? WHERE title = ? AND due_date = ?
                ''', (new_title, new_description, new_due_date, title, due_date))
                conn.commit()
                conn.close()

                edit_window.destroy()
                manage_window.destroy()
                open_manage_tasks_window()

            tk.Button(
                edit_window,
                text="Save Changes",
                command=save_changes,
                bg=button_bg,
                fg=button_fg,
                activebackground=accent_color,
                activeforeground=button_fg,
                width=20,
                height=2
            ).pack(pady=20)

    def delete_task():
        selected = task_listbox.curselection()
        if selected:
            index = selected[0]
            title = task_listbox.get(index).split("|")[0].replace("📌 Task: ", "").strip()
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the task '{title}'?")
            if confirm:
                conn = connect_to_database()
                if conn is None:
                    return
                cursor = conn.cursor()
                cursor.execute('DELETE FROM Tasks WHERE title = ?', (title,))
                conn.commit()
                conn.close()
                manage_window.destroy()
                open_manage_tasks_window()

    button_frame = tk.Frame(manage_window, bg=bg_color)
    button_frame.pack(pady=10)

    tk.Button(
        button_frame,
        text="Edit",
        command=edit_task,
        bg=button_bg,
        fg=button_fg,
        activebackground=accent_color,
        activeforeground=button_fg,
        width=15,
        height=2
    ).pack(side=tk.LEFT, padx=10)

    tk.Button(
        button_frame,
        text="Delete",
        command=delete_task,
        bg="#cc4444",
        fg=button_fg,
        activebackground="#aa2222",
        activeforeground=button_fg,
        width=15,
        height=2
    ).pack(side=tk.LEFT, padx=10)


    
# 메인 함수
def main():
    initialize_database()
    setup_gui()
    root.mainloop()  # 메인 루프 추가

if __name__ == "__main__":
    main() 
