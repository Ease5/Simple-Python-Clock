import tkinter as tk
from tkinter import messagebox
import time
import threading
import winsound
import os
import ctypes
from datetime import datetime, timedelta

class SuperClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Retro Clock")
        self.root.geometry("450x600")
        
        # --- THEME & STATE ---
        self.is_dark = False
        self.current_tab = "Clock"
        # Initial Cities: (Display Name, UTC Offset)
        self.active_cities = [("London", 0), ("New York", -5), ("Tokyo", 9)]
        
        self.colors = {
            "light": {"bg": "#ffffff", "fg": "#000000", "tab_active": "#e1e1e1", "tab_inactive": "#f0f0f0"},
            "dark": {"bg": "#1e1e1e", "fg": "#ffffff", "tab_active": "#444444", "tab_inactive": "#252525"}
        }

        # --- NAVIGATION ---
        self.nav_frame = tk.Frame(self.root)
        self.nav_frame.pack(fill="x", side="top")

        self.tab_buttons = {}
        for name in ["Clock", "Alarm", "Timer", "Stopwatch"]:
            btn = tk.Button(self.nav_frame, text=name, font=("Arial", 10), relief="flat",
                            command=lambda n=name: self.show_tab(n), padx=10)
            btn.pack(side="left")
            self.tab_buttons[name] = btn

        self.btn_settings = tk.Button(self.nav_frame, text="⚙", font=("Arial", 12), 
                                      command=self.open_settings, relief="flat", padx=10)
        self.btn_settings.pack(side="right")

        # --- MAIN CONTAINER ---
        self.container = tk.Frame(self.root)
        self.container.pack(expand=True, fill="both")

        # 1. Clock Tab (Local + World)
        self.clock_frame = tk.Frame(self.container)
        self.lbl_local_title = tk.Label(self.clock_frame, text="Local Time", font=('Arial', 10))
        self.lbl_local_title.pack(pady=(20,0))
        self.lbl_clock = tk.Label(self.clock_frame, font=('Segoe UI', 40, 'bold'))
        self.lbl_clock.pack()

        self.world_section = tk.Frame(self.clock_frame)
        self.world_section.pack(pady=10, fill="both")
        self.world_ui_elements = []

        # 2. Alarm Tab
        self.alarm_frame = tk.Frame(self.container)
        self.lbl_a_title = tk.Label(self.alarm_frame, text="Set Alarm (24h HH:MM)")
        self.lbl_a_title.pack(pady=20)
        self.alarm_time = tk.Entry(self.alarm_frame, font=('Segoe UI', 18), justify='center')
        self.alarm_time.pack(pady=5)
        self.alarm_time.insert(0, "07:30")
        tk.Button(self.alarm_frame, text="Set Alarm", command=self.set_alarm).pack(pady=10)

        # 3. Timer Tab
        self.timer_frame = tk.Frame(self.container)
        self.lbl_timer = tk.Label(self.timer_frame, text="00:00", font=('Segoe UI', 40))
        self.lbl_timer.pack(pady=20)
        self.entry_timer = tk.Entry(self.timer_frame, justify='center')
        self.entry_timer.pack()
        tk.Button(self.timer_frame, text="Start Timer", command=self.start_timer).pack(pady=10)

        # 4. Stopwatch Tab
        self.stopwatch_frame = tk.Frame(self.container)
        self.lbl_sw = tk.Label(self.stopwatch_frame, text="0.0", font=('Segoe UI', 40))
        self.lbl_sw.pack(pady=20)
        tk.Button(self.stopwatch_frame, text="Start / Stop", command=self.toggle_sw).pack()

        self.frames = {"Clock": self.clock_frame, "Alarm": self.alarm_frame, 
                       "Timer": self.timer_frame, "Stopwatch": self.stopwatch_frame}

        # --- INITIALIZE ---
        self.refresh_world_display()
        self.show_tab("Clock")
        self.update_clock()
        
        # DELAYED UI HACKS (This prevents the crash)
        self.root.after(200, self.apply_theme)
        self.root.after(500, self.apply_icon)

    def set_title_bar_dark(self, is_dark):
        """Standard Windows 11 Title Bar Color Hack - Safe Version"""
        try:
            # We must use the window's actual ID
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = 1 if is_dark else 0
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(value)), 4)
        except: pass

    def apply_icon(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "clock_icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except: pass

    def refresh_world_display(self):
        for widget in self.world_section.winfo_children():
            widget.destroy()
        self.world_ui_elements = []
        for city, offset in self.active_cities:
            f = tk.Frame(self.world_section)
            f.pack(pady=2)
            l1 = tk.Label(f, text=f"{city}:", font=('Arial', 11))
            l1.pack(side="left", padx=5)
            l2 = tk.Label(f, text="", font=('Arial', 11, 'bold'))
            l2.pack(side="left")
            self.world_ui_elements.append((l2, offset, l1, f))
        self.apply_theme()

    def update_clock(self):
        self.lbl_clock.config(text=time.strftime('%I:%M:%S %p'))
        # Calculate world times
        utc_now = datetime.utcnow()
        for lbl, offset, name_lbl, frame in self.world_ui_elements:
            city_time = utc_now + timedelta(hours=offset)
            lbl.config(text=city_time.strftime('%I:%M:%S %p'))
        self.root.after(1000, self.update_clock)

    def show_tab(self, name):
        self.current_tab = name
        for f in self.frames.values(): f.pack_forget()
        self.frames[name].pack(expand=True, fill="both")
        self.apply_theme()

    def apply_theme(self):
        t = self.colors["dark"] if self.is_dark else self.colors["light"]
        self.root.configure(bg=t["bg"])
        self.nav_frame.configure(bg=t["bg"])
        self.container.configure(bg=t["bg"])
        
        # Apply the Windows Title Bar Hack
        self.set_title_bar_dark(self.is_dark)
        
        for name, btn in self.tab_buttons.items():
            bg_c = t["tab_active"] if self.current_tab == name else t["tab_inactive"]
            btn.configure(bg=bg_c, fg=t["fg"], activebackground=t["tab_active"])
        
        for frame in self.frames.values():
            frame.configure(bg=t["bg"])
            for widget in frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg=t["bg"], fg=t["fg"])
        
        self.btn_settings.configure(bg=t["bg"], fg=t["fg"])
        self.world_section.configure(bg=t["bg"])
        for lbl, offset, name_lbl, frame in self.world_ui_elements:
            lbl.configure(bg=t["bg"], fg=t["fg"])
            name_lbl.configure(bg=t["bg"], fg=t["fg"])
            frame.configure(bg=t["bg"])

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("350x450")
        tk.Button(win, text="Toggle Dark/Light Mode", command=self.toggle_theme).pack(pady=20)
        
        tk.Label(win, text="--- Add World City ---").pack()
        e_name = tk.Entry(win); e_name.insert(0, "City Name"); e_name.pack(pady=2)
        tk.Label(win, text="UTC Offset (e.g. -5 or 9)").pack()
        e_off = tk.Entry(win); e_off.insert(0, "0"); e_off.pack(pady=2)
        
        def add():
            try:
                self.active_cities.append((e_name.get(), int(e_off.get())))
                self.refresh_world_display()
            except: pass
        tk.Button(win, text="Add", command=add).pack(pady=5)
        tk.Button(win, text="Clear All", command=lambda: [self.active_cities.clear(), self.refresh_world_display()]).pack()

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.apply_theme()

    # --- ALARM / TIMER / SW LOGIC ---
    def set_alarm(self):
        t = self.alarm_time.get()
        messagebox.showinfo("Alarm", f"Set for {t}")
        threading.Thread(target=self.check_alarm, args=(t,), daemon=True).start()

    def check_alarm(self, t):
        while True:
            if time.strftime('%H:%M') == t:
                winsound.Beep(1000, 2000); messagebox.showwarning("ALARM", f"It is {t}!"); break
            time.sleep(10)

    def start_timer(self):
        try:
            self.timer_seconds = int(self.entry_timer.get())
            self.timer_running = True
            self.countdown()
        except: pass

    def countdown(self):
        if hasattr(self, 'timer_seconds') and self.timer_seconds > 0:
            self.lbl_timer.config(text=f"{self.timer_seconds}s")
            self.timer_seconds -= 1
            self.root.after(1000, self.countdown)
        else: self.lbl_timer.config(text="DONE!")

    def toggle_sw(self):
        if not hasattr(self, 'sw_running'): self.sw_running = False
        if not hasattr(self, 'sw_seconds'): self.sw_seconds = 0
        self.sw_running = not self.sw_running
        if self.sw_running: self.run_sw()

    def run_sw(self):
        if self.sw_running:
            self.sw_seconds += 0.1
            self.lbl_sw.config(text=f"{round(self.sw_seconds, 1)}")
            self.root.after(100, self.run_sw)

if __name__ == "__main__":
    root = tk.Tk()
    app = SuperClock(root)
    root.mainloop()