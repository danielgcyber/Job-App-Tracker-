#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os
import threading
import time
import webbrowser
import random
import math
import sys

# ==============================
# SINGLE INSTANCE LOCK
# ==============================
LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobtracker.lock")

def acquire_lock():
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except OSError:
        pass
    try:
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
    except OSError:
        pass

def release_lock():
    try:
        os.remove(LOCK_FILE)
    except OSError:
        pass

acquire_lock()

# ==============================
# FILE PATHS
# ==============================
APP_DIR = os.path.join(os.path.expanduser("~"), ".jobtracker")
os.makedirs(APP_DIR, exist_ok=True)

DATA_FILE = os.path.join(APP_DIR, "applications.json")
TYPES_FILE = os.path.join(APP_DIR, "job_types.json")
BACKUP_DIR = os.path.join(APP_DIR, "backups")
MILESTONE_FILE = os.path.join(APP_DIR, "milestones.json")

os.makedirs(BACKUP_DIR, exist_ok=True)

# ==============================
# DATA FUNCTIONS
# ==============================
def load_job_types():
    default_types = ["Software Engineer", "Data Analyst", "Product Manager", "DevOps Engineer"]
    try:
        if not os.path.exists(TYPES_FILE):
            save_job_types(default_types)
            return default_types
        with open(TYPES_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                return data
            else:
                save_job_types(default_types)
                return default_types
    except Exception as e:
        print(f"[JobTracker] Load error: {e}", file=sys.stderr)
        save_job_types(default_types)
        return default_types

def save_job_types(types):
    try:
        os.makedirs(APP_DIR, exist_ok=True)
        with open(TYPES_FILE, "w") as f:
            json.dump(types, f, indent=2)
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save job types:\n{str(e)}")

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        messagebox.showwarning("Data Load Error", f"Using empty data\n{str(e)}")
        return []

def save_data(data):
    try:
        os.makedirs(APP_DIR, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}.json")
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Save Error", str(e))

def load_milestones():
    if not os.path.exists(MILESTONE_FILE):
        return {"last_daily": ""}
    try:
        with open(MILESTONE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"last_daily": ""}

def save_milestones(milestones):
    try:
        with open(MILESTONE_FILE, "w") as f:
            json.dump(milestones, f)
    except:
        pass

def get_week_dates():
    today = datetime.today().date()
    return [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]

# ==============================
# FIREWORKS CELEBRATION
# ==============================
def show_fireworks(title, message):
    win = tk.Toplevel()
    win.title("🎉 Achievement Unlocked!")
    win.geometry("600x500")
    win.configure(bg="#000")
    win.resizable(False, False)
    win.transient()
    win.grab_set()

    tk.Label(win, text=title, font=("Segoe UI", 18, "bold"), fg="#ffcc00", bg="#000").pack(pady=(20, 5))
    tk.Label(win, text=message, font=("Segoe UI", 12), fg="#ffffff", bg="#000", wraplength=550).pack(pady=(0, 20))

    canvas = tk.Canvas(win, width=600, height=350, bg="#000", highlightthickness=0)
    canvas.pack()

    close_btn = ttk.Button(win, text="Close", command=win.destroy)
    close_btn.pack(pady=20)

    particles = []
    confetti = []
    colors = ["#ff5252", "#4fc3f7", "#69f0ae", "#bb86fc", "#ffff00", "#ff9800"]

    def create_firework(x, y):
        for _ in range(40):
            angle = random.uniform(0, 360)
            speed = random.uniform(2, 7)
            color = random.choice(colors)
            dx = speed * math.cos(math.radians(angle))
            dy = speed * math.sin(math.radians(angle))
            size = random.randint(2, 5)
            particle = {'x': x, 'y': y, 'dx': dx, 'dy': dy, 'color': color, 'size': size, 'life': 30}
            particles.append(particle)

    def create_confetti():
        for _ in range(100):
            x = random.randint(0, 600)
            y = random.randint(-100, -10)
            color = random.choice(colors)
            speed = random.uniform(1, 3)
            confetti.append({'x': x, 'y': y, 'speed': speed, 'color': color, 'size': random.randint(3, 6)})

    def animate():
        canvas.delete("all")
        for p in particles[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['dy'] += 0.1
            p['life'] -= 1
            if p['life'] > 0:
                canvas.create_oval(
                    p['x'] - p['size'], p['y'] - p['size'],
                    p['x'] + p['size'], p['y'] + p['size'],
                    fill=p['color'], outline=""
                )
            else:
                particles.remove(p)
        for c in confetti[:]:
            c['y'] += c['speed']
            if c['y'] < 400:
                canvas.create_oval(
                    c['x'] - c['size'], c['y'] - c['size'],
                    c['x'] + c['size'], c['y'] + c['size'],
                    fill=c['color'], outline=""
                )
            else:
                confetti.remove(c)
        if particles or confetti:
            win.after(30, animate)

    for i in range(2):
        win.after(i * 800, lambda x=150+i*300, y=150: create_firework(x, y))
    win.after(1600, create_confetti)
    win.after(100, animate)

# ==============================
# MAIN APP
# ==============================
class JobTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Application Tracker")
        self.root.geometry("1100x800")
        self.root.configure(bg="#0f0f0f")
        self.data = load_data()
        self.job_types = load_job_types()
        self.search_var = tk.StringVar()
        self.filter_start_date = tk.StringVar()
        self.filter_end_date = tk.StringVar()
        self.sound_enabled = True
        self.milestones = load_milestones()

        self.running = True
        self.refresh_thread = None
        self.milestone_thread = None

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Modern dark theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#0f0f0f")
        style.configure("TLabel", background="#0f0f0f", foreground="#e0e0e0", font=("Segoe UI", 10))
        style.configure("TButton", background="#2a2a2a", foreground="#ffffff", font=("Segoe UI", 10, "bold"), borderwidth=0, padding=4)
        style.map("TButton", background=[("active", "#3a3a3a")])
        style.configure("Treeview", background="#1a1a1a", foreground="#d0d0d0", fieldbackground="#1a1a1a", font=("Segoe UI", 9))
        style.map("Treeview", background=[('selected', '#2c2c2c')])
        style.configure("Treeview.Heading", background="#222222", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
        style.configure("Vertical.TScrollbar", gripcount=0, background="#2a2a2a", troughcolor="#1a1a1a")
        style.configure("Horizontal.TScrollbar", gripcount=0, background="#2a2a2a", troughcolor="#1a1a1a")

        # Header with glow animation
        self.header = tk.Label(root, text="🎯 Job Application Tracker", bg="#0f0f0f", fg="#4fc3f7", font=("Segoe UI", 18, "bold"))
        self.header.pack(pady=12)
        self.glow_phase = 0
        self.animate_glow()

        # Top control bar
        top_frame = ttk.Frame(root)
        top_frame.pack(pady=5, fill="x", padx=20)

        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side="left")
        ttk.Button(btn_frame, text="➕ Add", command=self.add_application).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="🔄 Refresh", command=self.load_data_view).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="📊 Graphs", command=self.show_graphs_window).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="📤 Export", command=self.export_summary).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="🔧 Types", command=self.manage_types).pack(side="left", padx=4)

        # Search
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side="left", padx=20)
        ttk.Label(search_frame, text="🔍 Search:", foreground="#bb86fc").pack(side="left")
        ttk.Entry(search_frame, textvariable=self.search_var, width=18).pack(side="left", padx=5)
        self.search_var.trace("w", lambda *args: self.load_data_view())

        # Date filter
        date_frame = ttk.Frame(top_frame)
        date_frame.pack(side="left", padx=10)
        ttk.Label(date_frame, text="📅 From:", foreground="#bb86fc").pack(side="left")
        start_entry = ttk.Entry(date_frame, textvariable=self.filter_start_date, width=9)
        start_entry.pack(side="left", padx=2)
        ttk.Button(date_frame, text="Pick", command=lambda: self.pick_date(self.filter_start_date)).pack(side="left", padx=2)
        
        ttk.Label(date_frame, text="To:", foreground="#bb86fc").pack(side="left")
        end_entry = ttk.Entry(date_frame, textvariable=self.filter_end_date, width=9)
        end_entry.pack(side="left", padx=2)
        ttk.Button(date_frame, text="Pick", command=lambda: self.pick_date(self.filter_end_date)).pack(side="left", padx=2)

        # Type filter
        self.filter_type_var = tk.StringVar(value="All")
        type_frame = ttk.Frame(top_frame)
        type_frame.pack(side="right")
        ttk.Label(type_frame, text="FilterWhere:", foreground="#bb86fc").pack(side="left")
        self.type_menu = ttk.OptionMenu(type_frame, self.filter_type_var, "All", "All")
        self._update_main_filter_menu()
        self.type_menu.pack(side="left", padx=5)

        # Stats bar
        self.stats_text = tk.Text(root, height=2, bg="#1a1a1a", fg="#a0a0a0", font=("Consolas", 9), wrap="word", relief="flat")
        self.stats_text.pack(pady=6, fill="x", padx=20)
        self.stats_text.config(state="disabled")

        # Treeview
        tree_frame = ttk.Frame(root)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Company", "Type", "HR Phone", "Apply Date", "Days Left", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            width = 50 if col == "ID" else (160 if col == "Company" else 90)
            self.tree.column(col, anchor="center", width=width)
            self.tree.heading(col, text=col)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        # Context menu
        self.context_menu = tk.Menu(root, tearoff=0, bg="#2a2a2a", fg="#ffffff", font=("Segoe UI", 10))
        self.context_menu.add_command(label="✏️ Edit", command=self.edit_application)
        self.context_menu.add_command(label="🗑️ Delete", command=self.delete_application)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📞 Called HR", command=self.mark_called_hr)
        self.context_menu.add_command(label="⏹️ Inactive", command=self.mark_inactive)
        self.tree.bind("<Button-3>", self.show_context_menu)

        self.load_data_view()
        self.start_auto_refresh()
        self.start_milestone_checker()

    def _update_main_filter_menu(self):
        menu = self.type_menu["menu"]
        menu.delete(0, "end")
        menu.add_command(label="All", command=lambda: self._set_filter_and_refresh("All"))
        for t in self.job_types:
            menu.add_command(label=t, command=lambda x=t: self._set_filter_and_refresh(x))

    def _set_filter_and_refresh(self, value):
        self.filter_type_var.set(value)
        self.load_data_view()

    def on_closing(self):
        self.running = False
        time.sleep(0.1)
        release_lock()
        self.root.destroy()

    def animate_glow(self):
        if not self.running:
            return
        intensity = 120 + int(60 * math.sin(self.glow_phase))
        color = f"#{intensity:02x}{intensity:02x}ff"
        self.header.config(fg=color)
        self.glow_phase += 0.1
        self.root.after(100, self.animate_glow)

    def pick_date(self, var):
        cal_win = tk.Toplevel(self.root)
        cal_win.title("Pick Date")
        cal_win.geometry("260x200")
        cal_win.configure(bg="#1a1a1a")
        cal_win.transient(self.root)
        cal_win.grab_set()

        today = datetime.today()
        year_var = tk.IntVar(value=today.year)
        month_var = tk.IntVar(value=today.month)
        day_var = tk.IntVar(value=today.day)

        tk.Label(cal_win, text="Year:", bg="#1a1a1a", fg="white", font=("Segoe UI", 9)).grid(row=0, column=0, padx=5, pady=4)
        tk.Spinbox(cal_win, from_=2020, to=2030, textvariable=year_var, width=6, font=("Segoe UI", 9)).grid(row=0, column=1, padx=5, pady=4)

        tk.Label(cal_win, text="Month:", bg="#1a1a1a", fg="white", font=("Segoe UI", 9)).grid(row=1, column=0, padx=5, pady=4)
        tk.Spinbox(cal_win, from_=1, to=12, textvariable=month_var, width=6, font=("Segoe UI", 9)).grid(row=1, column=1, padx=5, pady=4)

        tk.Label(cal_win, text="Day:", bg="#1a1a1a", fg="white", font=("Segoe UI", 9)).grid(row=2, column=0, padx=5, pady=4)
        tk.Spinbox(cal_win, from_=1, to=31, textvariable=day_var, width=6, font=("Segoe UI", 9)).grid(row=2, column=1, padx=5, pady=4)

        def set_date():
            try:
                d = datetime(year_var.get(), month_var.get(), day_var.get()).date()
                var.set(d.isoformat())
                cal_win.destroy()
                self.load_data_view()
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter a valid date.")

        tk.Button(cal_win, text="Set", command=set_date, bg="#2a2a2a", fg="white", font=("Segoe UI", 9)).grid(row=3, column=0, columnspan=2, pady=8)

    def manage_types(self):
        dialog = ManageTypesDialog(self.root, self.job_types)
        if dialog.result is not None:
            save_job_types(dialog.result)
            self.job_types = load_job_types()
            self._update_main_filter_menu()
            self.filter_type_var.set("All")
            self.load_data_view()

    def add_application(self):
        dialog = ApplicationDialog(self.root, lambda: self.job_types)
        if dialog.result:
            company, job_type, hr_phone = dialog.result
            new_entry = {
                "id": max([item["id"] for item in self.data], default=0) + 1,
                "company": company,
                "type": job_type,
                "hr_phone": hr_phone,
                "apply_date": datetime.today().date().isoformat(),
                "called_hr": False,
                "inactive": False
            }
            self.data.append(new_entry)
            save_data(self.data)
            self.load_data_view()
            self.check_daily_milestone()

    def edit_application(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select an entry to edit.")
            return
        app_id = self.tree.item(selected[0])["values"][0]
        item = next((x for x in self.data if x["id"] == app_id), None)
        if not item:
            return
        dialog = ApplicationDialog(self.root, lambda: self.job_types, initial=item)
        if dialog.result:
            company, job_type, hr_phone = dialog.result
            item.update({"company": company, "type": job_type, "hr_phone": hr_phone})
            save_data(self.data)
            self.load_data_view()

    def delete_application(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select an entry to delete.")
            return
        app_id = self.tree.item(selected[0])["values"][0]
        self.data = [x for x in self.data if x["id"] != app_id]
        save_data(self.data)
        self.load_data_view()

    def mark_called_hr(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select an entry.")
            return
        app_id = self.tree.item(selected[0])["values"][0]
        for item in self.data:
            if item["id"] == app_id:
                item["called_hr"] = True
                break
        save_data(self.data)
        self.load_data_view()

    def mark_inactive(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select an entry.")
            return
        app_id = self.tree.item(selected[0])["values"][0]
        for item in self.data:
            if item["id"] == app_id:
                item["inactive"] = True
                break
        save_data(self.data)
        self.load_data_view()

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def load_data_view(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        filter_type = self.filter_type_var.get()
        start_date = self.filter_start_date.get().strip()
        end_date = self.filter_end_date.get().strip()
        search_term = self.search_var.get().lower().strip()
        active_data = [x for x in self.data if not x.get("inactive", False)]

        if filter_type != "All":
            active_data = [x for x in active_data if x["type"] == filter_type]
        if start_date and end_date:
            try:
                start_dt = datetime.fromisoformat(start_date).date()
                end_dt = datetime.fromisoformat(end_date).date()
                active_data = [x for x in active_data if start_dt <= datetime.fromisoformat(x["apply_date"]).date() <= end_dt]
            except ValueError:
                pass
        elif start_date:
            try:
                start_dt = datetime.fromisoformat(start_date).date()
                active_data = [x for x in active_data if datetime.fromisoformat(x["apply_date"]).date() >= start_dt]
            except ValueError:
                pass
        elif end_date:
            try:
                end_dt = datetime.fromisoformat(end_date).date()
                active_data = [x for x in active_data if datetime.fromisoformat(x["apply_date"]).date() <= end_dt]
            except ValueError:
                pass
        if search_term:
            active_data = [x for x in active_data if search_term in x["company"].lower()]

        active_data.sort(key=lambda x: x["apply_date"], reverse=True)

        today = datetime.today().date()
        ready_to_call = False
        for item in active_data:
            apply_dt = datetime.fromisoformat(item["apply_date"]).date()
            days_diff = (today - apply_dt).days
            days_left = max(0, 7 - days_diff)
            if days_left == 0 and not item["called_hr"]:
                ready_to_call = True
            status = "✅ Called" if item["called_hr"] else ("⏳ Ready" if days_left == 0 else f"{days_left}d")
            tags = ("ready",) if (days_left == 0 and not item["called_hr"]) else ()
            self.tree.insert("", "end", values=(
                item["id"],
                item["company"],
                item["type"],
                item["hr_phone"] or "—",
                item["apply_date"],
                days_left,
                status
            ), tags=tags)

        self.tree.tag_configure("ready", background="#253525")

        if ready_to_call and self.sound_enabled:
            def play_alert():
                print('\a', end='', flush=True)
            threading.Thread(target=play_alert, daemon=True).start()

        today_str = today.isoformat()
        week_dates = set(get_week_dates())
        month_dates = {datetime(today.year, today.month, day).date().isoformat() for day in range(1, today.day + 1)}

        today_apps = sum(1 for x in active_data if x["apply_date"] == today_str)
        week_apps = sum(1 for x in active_data if x["apply_date"] in week_dates)
        month_apps = sum(1 for x in active_data if x["apply_date"] in month_dates)
        today_calls = sum(1 for x in active_data if x["apply_date"] == today_str and x.get("called_hr", False))
        week_calls = sum(1 for x in active_data if x["apply_date"] in week_dates and x.get("called_hr", False))
        month_calls = sum(1 for x in active_data if x["apply_date"] in month_dates and x.get("called_hr", False))

        stats = {
            "today_apps": today_apps,
            "week_apps": week_apps,
            "month_apps": month_apps,
            "today_calls": today_calls,
            "week_calls": week_calls,
            "month_calls": month_calls,
            "total_active": len(active_data)
        }
        self.update_stats_display(stats)

    def update_stats_display(self, stats):
        self.stats_text.config(state="normal")
        self.stats_text.delete(1.0, tk.END)
        text = (
            f"📅 Today: {stats['today_apps']} apps | {stats['today_calls']} calls   "
            f"📆 Week: {stats['week_apps']} apps | {stats['week_calls']} calls   "
            f"🗓️ Month: {stats['month_apps']} apps | {stats['month_calls']} calls   "
            f"💼 Active: {stats['total_active']}"
        )
        self.stats_text.insert(tk.END, text)
        self.stats_text.config(state="disabled")

    def start_auto_refresh(self):
        def refresh():
            while self.running:
                time.sleep(60)
                if self.running:
                    self.root.after(0, self.load_data_view)
        self.refresh_thread = threading.Thread(target=refresh, daemon=True)
        self.refresh_thread.start()

    def start_milestone_checker(self):
        def checker():
            while self.running:
                if self.running:
                    self.check_daily_milestone()
                time.sleep(60)
        self.milestone_thread = threading.Thread(target=checker, daemon=True)
        self.milestone_thread.start()

    def check_daily_milestone(self):
        today = datetime.today().date().isoformat()
        count = sum(1 for x in self.data if x["apply_date"] == today and not x.get("inactive", False))
        if count >= 10 and self.milestones["last_daily"] != today:
            self.milestones["last_daily"] = today
            save_milestones(self.milestones)
            msg = f"You submitted {count} applications today! Keep it up!"
            self.root.after(0, lambda: show_fireworks("🎉 Daily Milestone!", msg))

    def export_summary(self):
        filter_type = self.filter_type_var.get()
        start_date = self.filter_start_date.get().strip()
        end_date = self.filter_end_date.get().strip()
        active_data = [x for x in self.data if not x.get("inactive", False)]
        if filter_type != "All":
            active_data = [x for x in active_data if x["type"] == filter_type]
        if start_date and end_date:
            try:
                start_dt = datetime.fromisoformat(start_date).date()
                end_dt = datetime.fromisoformat(end_date).date()
                active_data = [x for x in active_data if start_dt <= datetime.fromisoformat(x["apply_date"]).date() <= end_dt]
            except ValueError:
                pass

        today = datetime.today().date()
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Job Application Summary</title>
            <style>
                body {{ font-family: Segoe UI, sans-serif; background: #0f0f0f; color: #d0d0d0; padding: 20px; }}
                h1 {{ color: #4fc3f7; text-align: center; }}
                .stats {{ background: #1a1a1a; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 10px; text-align: center; border-bottom: 1px solid #333; }}
                tr.ready {{ background: #253525; }}
                .status-called {{ color: #69f0ae; }}
                .status-ready {{ color: #ffcc00; }}
            </style>
        </head>
        <body>
            <h1>Job Application Summary</h1>
            <div class="stats">
                <strong>Filter:</strong> Type={filter_type}, Date={start_date or 'Any'} to {end_date or 'Any'}<br>
                <strong>Total Active Applications:</strong> {len(active_data)}
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Company</th>
                        <th>Type</th>
                        <th>Apply Date</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        """
        for item in sorted(active_data, key=lambda x: x["apply_date"], reverse=True):
            apply_dt = datetime.fromisoformat(item["apply_date"]).date()
            days_diff = (today - apply_dt).days
            days_left = max(0, 7 - days_diff)
            if item.get("called_hr", False):
                status = '<span class="status-called">✅ Called</span>'
                css_class = ""
            elif days_left == 0:
                status = '<span class="status-ready">⏳ Ready</span>'
                css_class = "ready"
            else:
                status = f"{days_left}d"
                css_class = ""

            html += f"""
                <tr class="{css_class}">
                    <td>{item["company"]}</td>
                    <td>{item["type"]}</td>
                    <td>{item["apply_date"]}</td>
                    <td>{status}</td>
                </tr>
            """
        html += """
                </tbody>
            </table>
            <p style="text-align: center; margin-top: 30px; color: #777;">
                Generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """
            </p>
        </body>
        </html>
        """
        summary_path = os.path.join(APP_DIR, "summary.html")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(html)
        webbrowser.open("file://" + os.path.abspath(summary_path))

    def show_graphs_window(self):
        graph_win = tk.Toplevel(self.root)
        graph_win.title("📊 Application Statistics")
        graph_win.geometry("850x550")
        graph_win.configure(bg="#0f0f0f")

        graph_filter_var = tk.StringVar(value="All")

        filter_frame = ttk.Frame(graph_win)
        filter_frame.pack(pady=10)

        ttk.Label(filter_frame, text="FilterWhere:", foreground="#bb86fc", background="#0f0f0f").pack(side="left")

        menu_container = ttk.Frame(filter_frame)
        menu_container.pack(side="left", padx=5)

        canvas = tk.Canvas(graph_win, bg="#1a1a1a", highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=20, pady=10)

        def update_graph_filter_menu():
            for widget in menu_container.winfo_children():
                widget.destroy()
            options = ["All"] + self.job_types
            menu = ttk.OptionMenu(menu_container, graph_filter_var, "All", *options)
            menu.pack()

        def draw_graph(filter_type):
            canvas.delete("all")
            active_data = [x for x in self.data if not x.get("inactive", False)]
            if filter_type != "All":
                active_data = [x for x in active_data if x["type"] == filter_type]

            dates = get_week_dates()
            app_counts = []
            call_counts = []
            for d in dates:
                apps = sum(1 for x in active_data if x["apply_date"] == d)
                calls = sum(1 for x in active_data if x["apply_date"] == d and x.get("called_hr", False))
                app_counts.append(apps)
                call_counts.append(calls)

            canvas.create_text(425, 25, text=f"Last 7 Days: Applications & HR Calls ({filter_type})", fill="#bb86fc", font=("Segoe UI", 13, "bold"))

            max_val = max(max(app_counts, default=0), max(call_counts, default=0), 1)
            chart_height = 260
            bar_width = 35
            spacing = 12
            start_x = 70
            start_y = 60

            for i, (apps, calls) in enumerate(zip(app_counts, call_counts)):
                x = start_x + i * (bar_width + spacing)
                app_h = (apps / max_val) * chart_height
                call_h = (calls / max_val) * chart_height
                canvas.create_rectangle(x, start_y + chart_height - app_h, x + bar_width//2, start_y + chart_height, fill="#4fc3f7", outline="")
                canvas.create_rectangle(x + bar_width//2, start_y + chart_height - call_h, x + bar_width, start_y + chart_height, fill="#69f0ae", outline="")
                date_label = dates[i][5:]
                canvas.create_text(x + bar_width//2, start_y + chart_height + 18, text=date_label, fill="#a0a0a0", font=("Segoe UI", 8))

            canvas.create_rectangle(680, 80, 700, 100, fill="#4fc3f7", outline="")
            canvas.create_text(710, 90, text="Applications", fill="#d0d0d0", anchor="w", font=("Segoe UI", 9))
            canvas.create_rectangle(680, 110, 700, 130, fill="#69f0ae", outline="")
            canvas.create_text(710, 120, text="HR Calls", fill="#d0d0d0", anchor="w", font=("Segoe UI", 9))

            for i in range(0, max_val + 1):
                y = start_y + chart_height - (i / max_val) * chart_height
                canvas.create_line(60, y, 65, y, fill="#555")
                canvas.create_text(50, y, text=str(i), fill="#777", font=("Segoe UI", 7), anchor="e")

        update_graph_filter_menu()
        ttk.Button(filter_frame, text="Refresh", command=lambda: draw_graph(graph_filter_var.get())).pack(side="left", padx=10)
        draw_graph("All")


# ==============================
# Dialogs
# ==============================
class ApplicationDialog:
    def __init__(self, parent, job_types_getter, initial=None):
        self.result = None
        self.win = tk.Toplevel(parent)
        self.win.title("Add Application" if not initial else "Edit Application")
        self.win.geometry("400x240")
        self.win.configure(bg="#1a1a1a")
        self.win.transient(parent)
        self.win.grab_set()

        fields = [("🏢 Company", "company"), ("🎯 Job Type", "type"), ("📞 HR Phone", "phone")]
        self.widgets = {}

        for i, (label, key) in enumerate(fields):
            tk.Label(self.win, text=label, bg="#1a1a1a", fg="#bb86fc", font=("Segoe UI", 10)).grid(row=i, column=0, sticky="w", padx=15, pady=10)
            if key == "type":
                job_types = job_types_getter()
                var = tk.StringVar(value=initial["type"] if initial else (job_types[0] if job_types else ""))
                combo = ttk.Combobox(self.win, textvariable=var, state="readonly", values=job_types, width=25)
                combo.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
                self.widgets[key] = var
            else:
                val = initial[key] if initial else ""
                entry = ttk.Entry(self.win, font=("Segoe UI", 10), width=25)
                entry.insert(0, val)
                entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
                self.widgets[key] = entry

        btn_frame = ttk.Frame(self.win)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="💾 Save", command=self.save).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="❌ Cancel", command=self.win.destroy).pack(side="left", padx=8)

        self.win.columnconfigure(1, weight=1)
        self.win.wait_window(self.win)

    def save(self):
        company = self.widgets["company"].get().strip()
        job_type = self.widgets["type"].get()
        hr_phone = self.widgets["phone"].get().strip()
        if not company or not job_type:
            messagebox.showerror("Error", "Company and Job Type are required.")
            return
        self.result = (company, job_type, hr_phone)
        self.win.destroy()


class ManageTypesDialog:
    def __init__(self, parent, current_types):
        self.result = None
        self.win = tk.Toplevel(parent)
        self.win.title("Manage Job Types")
        self.win.geometry("380x320")
        self.win.configure(bg="#1a1a1a")
        self.win.transient(parent)
        self.win.grab_set()

        tk.Label(self.win, text="Job Types", bg="#1a1a1a", fg="#bb86fc", font=("Segoe UI", 12, "bold")).pack(pady=8)

        self.listbox = tk.Listbox(self.win, bg="#2a2a2a", fg="#d0d0d0", font=("Segoe UI", 10), selectmode=tk.SINGLE, height=8)
        for t in current_types:
            self.listbox.insert(tk.END, t)
        self.listbox.pack(pady=8, padx=15, fill="both", expand=True)

        entry_frame = ttk.Frame(self.win)
        entry_frame.pack(pady=5, padx=15, fill="x")
        self.new_type = ttk.Entry(entry_frame, font=("Segoe UI", 10))
        self.new_type.pack(side="left", fill="x", expand=True)
        ttk.Button(entry_frame, text="Add", command=self.add_type, width=6).pack(side="right", padx=5)

        btn_frame = ttk.Frame(self.win)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Remove", command=self.remove_type, width=10).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Save", command=self.save, width=10).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Cancel", command=self.win.destroy, width=10).pack(side="left", padx=6)

        self.win.wait_window(self.win)

    def add_type(self):
        t = self.new_type.get().strip()
        if not t:
            messagebox.showwarning("Input Error", "Job type cannot be empty.")
            return
        if t in self.listbox.get(0, tk.END):
            messagebox.showinfo("Duplicate", "This job type already exists.")
            return
        self.listbox.insert(tk.END, t)
        self.new_type.delete(0, tk.END)

    def remove_type(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a job type to remove.")
            return
        idx = sel[0]
        current_list = list(self.listbox.get(0, tk.END))
        if len(current_list) <= 1:
            messagebox.showwarning("Cannot Delete", "At least one job type must remain.")
            return
        name = current_list[idx]
        if messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            self.listbox.delete(idx)

    def save(self):
        types = list(self.listbox.get(0, tk.END))
        if len(types) == 0:
            messagebox.showerror("Error", "At least one job type is required.")
            return
        self.result = types
        self.win.destroy()


# ==============================
# Run
# ==============================
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = JobTrackerApp(root)
        root.mainloop()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Startup Failed", f"Error:\n{str(e)}")
        root.destroy()
