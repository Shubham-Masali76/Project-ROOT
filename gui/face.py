import tkinter as tk
import math
import time

class RobotFace:
    def __init__(self, state_dict):
        self.state_dict = state_dict
        self.root = tk.Tk()
        self.root.title("R.O.O.T. Interface")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        # Distinct background color so it doesn't blend into other apps
        self.bg_color = '#0a1128' # Deep Rich Navy Blue instead of black/grey
        self.bg_color = '#0a1128' # Deep Rich Navy Blue instead of black/grey
        self.root.configure(bg=self.bg_color)
        
        try:
            import os
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.ico")
            self.root.iconbitmap(icon_path)
        except Exception:
            pass
        
        self.is_pinned = True
        
        # Add Drag-to-Move functionality
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)
        
        # Bind Escape key to trigger shutdown
        self.root.bind("<Escape>", self.trigger_shutdown)
        
        screen_width = self.root.winfo_screenwidth()
        x = screen_width - 340
        y = 50
        self.root.geometry(f"320x450+{x}+{y}")
        
        self.canvas = tk.Canvas(self.root, width=320, height=220, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack()
        
        # Bind canvas dragging (acting as a title bar)
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.do_move)
        
        # Bind double-click to collapse terminal
        self.canvas.bind("<Double-Button-1>", self.toggle_terminal)
        
        # Right-click context menu
        self.menu = tk.Menu(self.root, tearoff=0, bg='#14213d', fg='#00e5ff', activebackground='#00e5ff', activeforeground='black', font=("Segoe UI", 10))
        self.menu.add_command(label="Unpin from Top", command=self.toggle_pin)
        self.menu.add_separator()
        self.menu.add_command(label="Exit R.O.O.T.", command=self.trigger_shutdown)
        self.canvas.bind("<Button-3>", self.show_menu)
        
        # Single seamless terminal frame with glowing border
        self.terminal_frame = tk.Frame(self.root, bg='#00e5ff', bd=1)
        self.terminal_frame.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
        
        self.inner_frame = tk.Frame(self.terminal_frame, bg='#14213d')
        self.inner_frame.pack(fill=tk.BOTH, expand=True)
        
        self.console = tk.Text(self.inner_frame, height=6, bg='#14213d', fg='#00e5ff', font=("Consolas", 9), bd=0, padx=10, pady=10)
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Configure syntax highlighting tags for logs
        self.console.tag_config("timestamp", foreground="#556677", font=("Consolas", 8))
        self.console.tag_config("error", foreground="#ff003c", font=("Consolas", 9, "bold"))
        self.console.tag_config("exec", foreground="#00ff66", font=("Consolas", 9))
        self.console.tag_config("info", foreground="#00e5ff", font=("Consolas", 9))
        self.console.tag_config("system", foreground="#ffbb00", font=("Consolas", 9, "italic"))
        
        self.console.insert(tk.END, "Welcome user, R.O.O.T. system online.\nType /help to see all available commands.\n", "system")
        self.console.insert(tk.END, "-"*40 + "\n", "timestamp")
        self.console.config(state=tk.DISABLED)
        
        # Subtle glowing separator line
        self.separator = tk.Frame(self.inner_frame, bg='#00e5ff', height=1)
        self.separator.pack(fill=tk.X, padx=5)
        
        # The prompt prefix label and entry box side-by-side
        self.entry_row = tk.Frame(self.inner_frame, bg='#14213d')
        self.entry_row.pack(fill=tk.X, padx=10, pady=5)
        
        self.prompt_label = tk.Label(self.entry_row, text=">", bg='#14213d', fg='#00ff66', font=("Consolas", 10, "bold"))
        self.prompt_label.pack(side=tk.LEFT)
        
        self.entry = tk.Entry(self.entry_row, bg='#14213d', fg='white', font=("Consolas", 10), bd=0, insertbackground='#00e5ff')
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=3)
        self.entry.bind("<Return>", self.on_enter)
        
        # Custom Resize Grip for Frameless Window
        self.grip = tk.Label(self.entry_row, text="◢", bg='#14213d', fg='#00e5ff', cursor="size_nw_se", font=("Consolas", 10))
        self.grip.pack(side=tk.RIGHT, anchor=tk.SE)
        self.grip.bind("<ButtonPress-1>", self.start_resize)
        self.grip.bind("<B1-Motion>", self.do_resize)
        
        self.last_log = ""
        self.update_gui()
        
    def on_enter(self, event):
        from core.state import execution_queue, STATE_DICT
        from core.audio_out import speak
        import os
        import threading
        import re
        from core.intent import extract_time_delay
        
        command = self.entry.get().strip()
        if not command: return
        self.entry.delete(0, tk.END)
        STATE_DICT["CURRENT_LOG"] = f"Executing: {command}"
        
        if command in ["/exit", "exit", "shutdown", "quit"]:
            self.trigger_shutdown()
        elif command == "/silent":
            import core.state
            core.state.SILENT_MODE = True
            STATE_DICT["CURRENT_LOG"] = "Stealth mode engaged. TTS disabled."
        elif command == "/voice":
            import core.state
            core.state.SILENT_MODE = False
            STATE_DICT["CURRENT_LOG"] = "Voice mode engaged. TTS enabled."
        elif command == "/mic off":
            import core.state
            core.state.MIC_ACTIVE = False
            STATE_DICT["CURRENT_LOG"] = "Microphone muted. The Ear is offline."
        elif command == "/mic on":
            import core.state
            core.state.MIC_ACTIVE = True
            STATE_DICT["CURRENT_LOG"] = "Microphone unmuted. The Ear is online."
        elif command == "/help":
            from core.keyboard import HELP_TEXT
            STATE_DICT["CURRENT_LOG"] = HELP_TEXT.strip()
        else:
            delay = extract_time_delay(command)
            if delay > 0:
                clean_command = re.sub(r'in \d+ (second|minute|hour)s?', '', command).strip()
                speak(f"Scheduling that for {delay} seconds from now.")
                threading.Timer(delay, execution_queue.put, args=[clean_command]).start()
            else:
                execution_queue.put(command)
                
    def trigger_shutdown(self, event=None):
        from core.state import STATE_DICT
        from core.audio_out import speak
        import os
        import threading
        
        STATE_DICT["CURRENT_LOG"] = "Executing: /exit"
        STATE_DICT["EMOTION"] = "SAD"
        speak("Shutting down all core systems. Goodbye.")
        threading.Timer(4.0, lambda: os._exit(0)).start()

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        # Calculate new coordinates based on drag
        deltax = event.x - self._x
        deltay = event.y - self._y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        
        # Keep current width and height to prevent jumping when dragged
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        
    def start_resize(self, event):
        self._start_x = event.x_root
        self._start_y = event.y_root
        self._start_w = self.root.winfo_width()
        self._start_h = self.root.winfo_height()
        return "break"

    def do_resize(self, event):
        deltax = event.x_root - self._start_x
        deltay = event.y_root - self._start_y
        new_w = max(320, self._start_w + deltax)
        new_h = max(220, self._start_h + deltay)
        self.root.geometry(f"{new_w}x{new_h}")
        return "break"
        
    def toggle_terminal(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        if self.terminal_frame.winfo_ismapped():
            self.terminal_frame.pack_forget()
            self.root.geometry(f"320x220+{x}+{y}")
        else:
            self.terminal_frame.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
            self.root.geometry(f"320x450+{x}+{y}")
            
    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        self.root.wm_attributes("-topmost", self.is_pinned)
        new_label = "Unpin from Top" if self.is_pinned else "Pin to Top"
        self.menu.entryconfig(0, label=new_label)
        
    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)
                
    def draw_glow_line(self, x1, y1, x2, y2, base_color):
        """Draws a neon glowing line"""
        self.canvas.create_line(x1, y1, x2, y2, fill=base_color, width=9, capstyle=tk.ROUND, stipple='gray50', tags="face")
        self.canvas.create_line(x1, y1, x2, y2, fill=base_color, width=4, capstyle=tk.ROUND, tags="face")
        self.canvas.create_line(x1, y1, x2, y2, fill='#ffffff', width=1, capstyle=tk.ROUND, tags="face")

    def draw_glow_arc(self, x1, y1, x2, y2, start, extent, base_color):
        """Draws a neon glowing arc"""
        self.canvas.create_arc(x1, y1, x2, y2, start=start, extent=extent, outline=base_color, width=7, style=tk.ARC, stipple='gray50', tags="face")
        self.canvas.create_arc(x1, y1, x2, y2, start=start, extent=extent, outline=base_color, width=3, style=tk.ARC, tags="face")
        self.canvas.create_arc(x1, y1, x2, y2, start=start, extent=extent, outline='#ffffff', width=1, style=tk.ARC, tags="face")
        
    def update_gui(self):
        state = self.state_dict.get("STATE", "IDLE")
        amp = self.state_dict.get("MOUTH_AMPLITUDE", 0)
        log_text = self.state_dict.get("CURRENT_LOG", "Initializing...")
        emotion = self.state_dict.get("EMOTION", "NEUTRAL")
        
        self.canvas.delete("all")
        
        # Top Holographic Nameplate
        self.canvas.create_text(160, 25, text="R . O . O . T .", fill="#00e5ff", font=("Consolas", 16, "bold"), tags="face")
        self.canvas.create_line(80, 40, 240, 40, fill="#005577", width=2, tags="face")
        
        # Color Themes
        color = '#00e5ff' # Default Cyan
        if state == "LISTENING": color = '#00ff66' # Neon Green
        elif state == "THINKING": color = '#ffbb00' # Gold
        elif emotion == "ANGRY": color = '#ff003c' # Neon Red
        elif emotion in ["SAD", "CRYING"]: color = '#0066ff' # Deep Blue
        elif state == "IDLE": color = '#0088aa' # Dim Cyan
        
        # Animation Offset
        t = time.time()
        offset_x = 0
        offset_y = math.sin(t * 2) * 5 # Constant floating effect
        if emotion == "DANCING" and state == "SPEAKING":
            offset_x = math.sin(t * 10) * 15
            offset_y += math.cos(t * 10) * 10
            
        lx, rx = 90 + offset_x, 230 + offset_x
        ey = 90 + offset_y
        
        # EYES
        if emotion == "HAPPY":
            self.draw_glow_arc(lx-30, ey-15, lx+30, ey+25, 0, 180, color)
            self.draw_glow_arc(rx-30, ey-15, rx+30, ey+25, 0, 180, color)
        elif emotion in ["SAD", "CRYING"]:
            self.draw_glow_line(lx-25, ey+15, lx+25, ey-10, color)
            self.draw_glow_line(rx-25, ey-10, rx+25, ey+15, color)
            if emotion == "CRYING" and state == "SPEAKING":
                tear_y = ey + 15 + (int(t * 100) % 60)
                self.canvas.create_oval(lx-4, tear_y, lx+4, tear_y+12, fill='#00e5ff', width=0, tags="face")
                self.canvas.create_oval(rx-4, tear_y, rx+4, tear_y+12, fill='#00e5ff', width=0, tags="face")
        elif emotion == "ANGRY":
            self.draw_glow_line(lx-30, ey-15, lx+25, ey+10, color)
            self.draw_glow_line(rx-25, ey+10, rx+30, ey-15, color)
        else:
            if state == "THINKING":
                # Spinning loading eyes
                spin = int(t * 300) % 360
                self.draw_glow_arc(lx-20, ey-20, lx+20, ey+20, spin, 270, color)
                self.draw_glow_arc(rx-20, ey-20, rx+20, ey+20, spin, 270, color)
            elif state == "LISTENING":
                # Wide hollow listening eyes
                self.draw_glow_arc(lx-25, ey-25, lx+25, ey+25, 0, 359, color)
                self.draw_glow_arc(rx-25, ey-25, rx+25, ey+25, 0, 359, color)
            else:
                # Normal pill eyes
                self.canvas.create_oval(lx-25, ey-15, lx+25, ey+15, fill=color, outline='#ffffff', width=2, tags="face")
                self.canvas.create_oval(rx-25, ey-15, rx+25, ey+15, fill=color, outline='#ffffff', width=2, tags="face")
                
        # MOUTH (Dynamic Audio Visualizer)
        mx, my = 160 + offset_x, 160 + offset_y
        
        if amp < 0.05:
            if emotion == "HAPPY":
                self.draw_glow_arc(mx-40, my-20, mx+40, my+20, 180, 180, color)
            elif emotion in ["SAD", "CRYING"]:
                self.draw_glow_arc(mx-40, my, mx+40, my+40, 0, 180, color)
            elif emotion == "ANGRY":
                self.draw_glow_line(mx-30, my+10, mx-10, my-5, color)
                self.draw_glow_line(mx-10, my-5, mx+10, my+10, color)
                self.draw_glow_line(mx+10, my+10, mx+30, my-5, color)
            else:
                self.draw_glow_line(mx-30, my, mx+30, my, color)
        else:
            # High-Tech Equalizer Mouth
            bars = 7
            spacing = 12
            max_height = 40
            
            for i in range(bars):
                # Calculate wave height based on amplitude and sine wave for organic feel
                dist_from_center = abs(i - (bars-1)/2)
                wave = math.sin(t * 15 + i) * 0.3 + 0.7
                
                # Center bars are taller
                height_multiplier = 1.0 - (dist_from_center * 0.2)
                
                bar_h = int(amp * max_height * wave * height_multiplier) + 4
                
                bx = mx - ((bars-1)/2 * spacing) + (i * spacing)
                self.canvas.create_line(bx, my - bar_h, bx, my + bar_h, fill=color, width=6, capstyle=tk.ROUND, tags="face")
            
        if log_text.strip() != "" and log_text != getattr(self, "last_log", ""):
            import datetime
            ts = datetime.datetime.now().strftime("[%H:%M:%S] ")
            
            self.console.config(state=tk.NORMAL)
            self.console.insert(tk.END, ts, "timestamp")
            
            # Syntax highlighting logic
            log_lower = log_text.lower()
            if "error" in log_lower or "fail" in log_lower or "damage" in log_lower:
                self.console.insert(tk.END, f"{log_text}\n", "error")
            elif "executing:" in log_lower or "patch" in log_lower:
                self.console.insert(tk.END, f"{log_text}\n", "exec")
            elif "system" in log_lower or "initializing" in log_lower:
                self.console.insert(tk.END, f"{log_text}\n", "system")
            else:
                self.console.insert(tk.END, f"{log_text}\n", "info")
                
            self.console.see(tk.END)
            self.last_log = log_text
            
            # Keep terminal from growing infinitely (keep last 50 lines)
            lines = self.console.get('1.0', tk.END).split('\n')
            if len(lines) > 50:
                self.console.delete('1.0', f"{len(lines)-50}.0")
            self.console.config(state=tk.DISABLED)
        
        self.root.after(30, self.update_gui)

def start_gui(state_dict):
    app = RobotFace(state_dict)
    app.root.mainloop()
