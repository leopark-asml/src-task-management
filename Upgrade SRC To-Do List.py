import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import requests
from datetime import datetime

BASE_URL = "https://your-api-endpoint.com"  # API의 기본 URL

def api_get(endpoint):
    response = requests.get(f"{BASE_URL}/{endpoint}")
    response.raise_for_status()
    return response.json()

def api_post(endpoint, data):
    response = requests.post(f"{BASE_URL}/{endpoint}", json=data)
    response.raise_for_status()
    return response.json()

def api_put(endpoint, data):
    response = requests.put(f"{BASE_URL}/{endpoint}", json=data)
    response.raise_for_status()
    return response.json()

def api_delete(endpoint):
    response = requests.delete(f"{BASE_URL}/{endpoint}")
    response.raise_for_status()

# 사용자 등록
def register_user(email, password, four_letter):
    data = {
        "email": email,
        "password": password,
        "four_letter": four_letter
    }
    try:
        api_post("users/register", data)  # API 호출
        messagebox.showinfo("Registration", "User registration request submitted for approval!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# 로그인
def login_user(four_letter, password=None):
    endpoint = f"users/login?four_letter={four_letter}"
    if password:
        endpoint += f"&password={password}"
    try:
        user = api_get(endpoint)  # API 호출
        return user if user['approved'] else None
    except Exception:
        return None

# 회원가입 다이얼로그
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

# TO-DO 항목 생성
def create_task(user):
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
    try:
        users = api_get("users?approved=true")  # API 호출
        for user in users:
            user_listbox.insert(tk.END, f"{user['four_letter']} (E-Mail: {user['email']})")
    except Exception as e:
        messagebox.showerror("Error", str(e))

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

        assigned_user_ids = [users[i]['id'] for i in selected_users]

        data = {
            "title": title,
            "description": description,
            "due_date": str(due_date),
            "assigned_user_ids": assigned_user_ids
        }

        try:
            api_post("tasks", data)  # API 호출
            messagebox.showinfo("Success", "Tasks created successfully for selected users!")
            task_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

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
        try:
            tasks = api_get(f"tasks?assigned_user_id={user[0]}")  # API 호출
            for task in tasks:
                state = "✅ Done" if task['completed'] else "❌ Not Done"
                task_listbox.insert(tk.END, f"📌 Title: {task['title']}")
                task_listbox.insert(tk.END, f"📝 Description: {task['description']}")
                task_listbox.insert(tk.END, f"📅 Due Date: {task['due_date']}")
                task_listbox.insert(tk.END, f"📍 State: {state}")
                task_listbox.insert(tk.END, f"💬 Remark: {task['remark'] or 'N/A'}")
                task_listbox.insert(tk.END, "-" * 60)
        except Exception as e:
            messagebox.showerror("Error", str(e))

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
            task_id = tasks[index]['id']

            response_window = tk.Toplevel(tasks_window)
            response_window.title("Respond to Task")
            response_window.geometry("300x200")
            response_window.configure(bg=bg_color)

            tk.Label(response_window, text="Select your response:", bg=bg_color, fg=fg_color, font=("Arial", 10)).pack(pady=10)

            button_frame = tk.Frame(response_window, bg=bg_color)
            button_frame.pack(expand=True)

            def submit_response(response):
                data = {
                    "completed": response == "Done",
                    "remark": "N/A" if response == "N/A" else None
                }
                try:
                    api_put(f"tasks/{task_id}", data)  # API 호출
                    messagebox.showinfo("Success", "Task response recorded successfully!")
                    update_task_list()
                    response_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

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
            task_id = tasks[index]['id']
            remark = simpledialog.askstring("Remark", "Enter your remark:")
            if remark:
                data = {
                    "remark": remark
                }
                try:
                    api_put(f"tasks/{task_id}", data)  # API 호출
                    messagebox.showinfo("Success", "Remark added successfully!")
                    update_task_list()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

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

# 어드민 패널
def open_admin_panel():
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

    task_listbox = tk.Listbox(admin_window, width=100, height=15, bg=entry_bg, fg=fg_color, font=("Arial", 10))
    task_listbox.pack(pady=10, padx=10)

    try:
        tasks = api_get("tasks")  # API 호출
        for task in tasks:
            task_listbox.insert(
                tk.END,
                f"📌 Title: {task['title']} | 📅 Due: {task['due_date']} | 👤 User ID: {task['assigned_user_id']} | ✅ Completed: {'Yes' if task['completed'] else 'No'}"
            )
    except Exception as e:
        messagebox.showerror("Error", str(e))

    def delete_task():
        selected = task_listbox.curselection()
        if selected:
            index = selected[0]
            task_id = tasks[index]['id']
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?")
            if not confirm:
                return

            try:
                api_delete(f"tasks/{task_id}")  # API 호출
                messagebox.showinfo("Success", "Task deleted successfully!")
                admin_window.destroy()
                open_admin_panel()  # 새로고침
            except Exception as e:
                messagebox.showerror("Error", str(e))

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

def open_main_application(user):
    root.withdraw()

    bg_color = "#cce7f0"
    fg_color = "#002244"
    button_bg = "#3399cc"
    button_fg = "#ffffff"
    accent_color = "#2277aa"

    main_window = tk.Toplevel(root)
    main_window.title("ASML SRC TO-DO List")
    main_window.geometry("1000x700")
    main_window.configure(bg=bg_color)

    create_icon = ImageTk.PhotoImage(file="create_task_icon.png").subsample(5, 5)
    manage_icon = ImageTk.PhotoImage(file="manage_tasks_icon.png").subsample(5, 5)
    view_icon = ImageTk.PhotoImage(file="view_tasks_icon.png").subsample(3, 3)

    login_status_label = tk.Label(
        main_window,
        text=f"Logged in as: {user['four_letter']} (Admin: {'Yes' if user['is_admin'] else 'No'})",
        bg=bg_color,
        fg=fg_color,
        font=("Arial", 10, "bold")
    )
    login_status_label.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)

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

    center_frame = tk.Frame(main_window, bg=bg_color)
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

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

    button_frames = []

    if user['is_admin']:
        button_frames.append(icon_button(center_frame, create_icon, "Create Task", lambda: create_task(user)))
        button_frames.append(icon_button(center_frame, manage_icon, "Manage Tasks", open_manage_tasks_window))

    button_frames.append(icon_button(center_frame, view_icon, "View My Tasks", lambda: view_my_tasks(user)))

    for i, frame in enumerate(button_frames):
        frame.grid(row=0, column=i, padx=30)

    if user['is_admin']:
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

# 로그아웃 함수
def logout(main_window):
    main_window.destroy()  # 메인 애플리케이션 창 닫기
    root.deiconify()  # 로그인 창 다시 보이기

# 비밀번호 변경 함수
def change_password(user):
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

        if current_pw != user['password']:  # user['password'] is the current password
            messagebox.showerror("Error", "Current password is incorrect.")
        elif new_pw != confirm_pw:
            messagebox.showerror("Error", "New passwords do not match.")
        else:
            data = {
                "current_password": current_pw,
                "new_password": new_pw
            }
            try:
                api_put(f"users/{user['id']}/password", data)  # API 호출
                messagebox.showinfo("Success", "Password updated successfully.")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

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

# 회원가입 승인 패널
def open_approval_panel():
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

        try:
            pending_users = api_get("users/pending")  # API 호출
            for i, user in enumerate(pending_users):
                user_label = tk.Label(
                    frame,
                    text=user['four_letter'],
                    width=20,
                    bg=entry_bg,
                    fg=fg_color,
                    font=("Arial", 10)
                )
                user_label.grid(row=i, column=0, padx=10, pady=5)

                approve_button = tk.Button(
                    frame,
                    text="Approve",
                    command=lambda u=user['four_letter']: approve_user(u),
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
                    command=lambda u=user['four_letter']: reject_user(u),
                    bg="#cc4444",
                    fg=button_fg,
                    activebackground="#aa2222",
                    activeforeground=button_fg,
                    width=10
                )
                reject_button.grid(row=i, column=2, padx=5, pady=5)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def approve_user(four_letter):
        try:
            api_put(f"users/{four_letter}/approve", {})  # API 호출
            messagebox.showinfo("Approval", f"User {four_letter} has been approved.")
            load_pending_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reject_user(four_letter):
        try:
            api_delete(f"users/{four_letter}")  # API 호출
            messagebox.showinfo("Reject", f"User {four_letter} has been rejected.")
            load_pending_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    load_pending_users()

# GUI 설정 함수
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
    setup_gui()
    root.mainloop()  # 메인 루프 추가

if __name__ == "__main__":
    main()
