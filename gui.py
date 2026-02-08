import customtkinter as ctk
from tkinter import CENTER
import tkinter as tk
import ctypes
from ctypes import wintypes
from database import Database
import customtkinter as ctk
from tkinter import CENTER, ttk
import math
from PIL import Image, ImageDraw
import io
import random
from random import randint
from tkinter import filedialog

db = Database()


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def launch_main_app():
    MainApp()


def enable_blur(window):
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())

    class ACCENTPOLICY(ctypes.Structure):
        _fields_ = [
            ("AccentState", ctypes.c_int),
            ("AccentFlags", ctypes.c_int),
            ("GradientColor", ctypes.c_int),
            ("AnimationId", ctypes.c_int)
        ]

    class WINCOMPATTRDATA(ctypes.Structure):
        _fields_ = [
            ("Attribute", ctypes.c_int),
            ("Data", ctypes.POINTER(ACCENTPOLICY)),
            ("SizeOfData", ctypes.c_size_t)
        ]

    ACCENT_ENABLE_BLURBEHIND = 3
    WCA_ACCENT_POLICY = 19

    accent = ACCENTPOLICY()
    accent.AccentState = ACCENT_ENABLE_BLURBEHIND
    accent.GradientColor = 0xAA000000

    data = WINCOMPATTRDATA()
    data.Attribute = WCA_ACCENT_POLICY
    data.Data = ctypes.pointer(accent)
    data.SizeOfData = ctypes.sizeof(accent)

    ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))

class BaseModal:
    def __init__(self, parent, width, height):
        self.parent = parent
        self.width = width
        self.height = height

        self.win = ctk.CTkToplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.0)
        self.win.configure(fg_color="#307ce0")
        self.win.grab_set()

        self.center_x = self.win.winfo_screenwidth() // 2 - width // 2 + 270
        self.center_y = self.win.winfo_screenheight() // 2 - height // 2 + 30

        self.start_y = self.center_y + 120  # slide from bottom
        self.win.geometry(f"{width}x{height}+{self.center_x}+{self.start_y}")

        enable_blur(self.win)

        self.alpha = 0.0
        self.current_y = self.start_y

        self.animate_in()

    def animate_in(self):
        if self.alpha < 1:
            self.alpha += 0.08
            self.current_y -= 12
            self.win.attributes("-alpha", self.alpha)
            self.win.geometry(
                f"{self.width}x{self.height}+{self.center_x}+{int(self.current_y)}"
            )
            self.win.after(16, self.animate_in)

class MessageModal(BaseModal):
    def __init__(self, parent, title, message, success=True):
        super().__init__(parent, 360, 220)

        color = "#00c2cb" if success else "#d9534f"

        ctk.CTkLabel(
            self.win,
            text=title,
            font=("Segoe UI Semibold", 22),
            text_color=color
        ).pack(pady=(25, 10))

        ctk.CTkLabel(
            self.win,
            text=message,
            wraplength=300,
            justify="center",
            text_color="#e0f7fa"
        ).pack(pady=10)

        ctk.CTkButton(
            self.win,
            text="OK",
            width=120,
            fg_color=color,
            command=self.win.destroy
        ).pack(pady=20)

class SplashScreen:
    def __init__(self, on_finish_callback):
        self.on_finish_callback = on_finish_callback

        self.root = ctk.CTk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        self.width, self.height = 850, 500

        self.colors = {
            "bg_dark": "#020817",
            "accent": "#0ea5e9",
            "accent_glow": "#38bdf8",
            "text_main": "#f8fafc",
            "text_dim": "#64748b",
            "progress_track": "#1e293b",
            "success": "#22c55e"
        }

        self.alpha = 0.0
        self.loading_progress = 0
        self.glow_val = 0
        self.glow_direction = 1

        self.center_window()
        self.setup_canvas()

        self.root.after(50, self.build_scene)
        self.fade_in()
        self.root.mainloop()

    # ---------------- CANVAS ----------------
    def setup_canvas(self):
        self.root.configure(fg_color=self.colors["bg_dark"])
        self.canvas = tk.Canvas(
            self.root,
            bg=self.colors["bg_dark"],
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

    def build_scene(self):
        self.create_particles()
        self.create_rings()
        self.create_branding()

    # ---------------- CENTER ----------------
    def get_canvas_center(self):
        self.root.update_idletasks()
        return self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2

    # ---------------- BRANDING ----------------
    def create_branding(self):
        cx, cy = self.get_canvas_center()

        self.logo_icon = self.canvas.create_text(
            cx, cy - 60,
            text="◈",
            font=("Segoe UI Symbol", 80),
            fill=self.colors["accent"]
        )

        self.title_text = self.canvas.create_text(
            cx, cy + 30,
            text="DIAGNOSIGHT AI",
            font=("Inter", 42, "bold"),
            fill=self.colors["text_main"]
        )

        self.subtitle = self.canvas.create_text(
            cx, cy + 75,
            text="NEXT-GEN DERMATOLOGIST ANALYTICS",
            font=("Futura", 12, "bold"),
            fill=self.colors["text_dim"]
        )

        track_width = 400
        self.track_y = cy + 160
        self.track_x1 = cx - track_width // 2
        self.track_x2 = cx + track_width // 2

        self.round_rectangle(
            self.track_x1, self.track_y,
            self.track_x2, self.track_y + 8,
            radius=10,
            fill=self.colors["progress_track"],
            tag="track"
        )

        self.bar = self.round_rectangle(
            self.track_x1, self.track_y,
            self.track_x1, self.track_y + 8,
            radius=10,
            fill=self.colors["accent"],
            tag="bar"
        )

        self.status_label = self.canvas.create_text(
            cx, self.track_y + 30,
            text="CALIBRATING NEURAL ENGINES...",
            font=("Consolas", 10),
            fill=self.colors["accent"]
        )

    # ---------------- SHAPES ----------------
    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1+radius, y1, x2-radius, y1, x2, y1,
            x2, y1+radius, x2, y2-radius, x2, y2,
            x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    # ---------------- PARTICLES ----------------
    def create_particles(self):
        self.root.update_idletasks()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.particles = []

        for _ in range(45):
            size = random.uniform(1, 2.2)
            x, y = random.randint(0, w), random.randint(0, h)
            p = self.canvas.create_oval(x, y, x+size, y+size, fill=self.colors["text_dim"], outline="")
            self.particles.append({"id": p, "speed": random.uniform(0.3, 1.0)})

    # ---------------- RINGS ----------------
    def create_rings(self):
        cx, cy = self.get_canvas_center()
        self.rings = []
        for i in range(3):
            r = 100 + (i * 15)
            ring = self.canvas.create_oval(
                cx-r, cy-r-30, cx+r, cy+r-30,
                outline=self.colors["accent"], width=1, dash=(10, 20)
            )
            self.rings.append(ring)

    # ---------------- ANIMATION ----------------
    def animate(self):
        self.glow_val += 0.02 * self.glow_direction
        if self.glow_val > 1 or self.glow_val < 0:
            self.glow_direction *= -1

        glow_color = self.lerp_color(
            self.colors["accent"],
            self.colors["accent_glow"],
            self.glow_val
        )

        self.canvas.itemconfig(self.logo_icon, fill=glow_color)

        # particles
        h = self.canvas.winfo_height()
        for p in self.particles:
            self.canvas.move(p["id"], 0, -p["speed"])
            if self.canvas.coords(p["id"])[3] < 0:
                self.canvas.move(p["id"], 0, h)

        # progress logic (RESTORED)
        if self.loading_progress < 100:
            self.loading_progress += random.uniform(0.2, 0.5)

            new_x = self.track_x1 + (
                (self.track_x2 - self.track_x1) * (self.loading_progress / 100)
            )

            self.canvas.delete("bar")
            self.bar = self.round_rectangle(
                self.track_x1, self.track_y,
                new_x, self.track_y + 8,
                radius=10,
                fill=glow_color,
                tag="bar"
            )

            if self.loading_progress > 80:
                self.canvas.itemconfig(self.status_label, text="SYSTEMS READY.")
            elif self.loading_progress > 40:
                self.canvas.itemconfig(self.status_label, text="SYNAPSING DATA MODELS...")

            self.root.after(20, self.animate)

        else:
            self.canvas.itemconfig(self.bar, fill=self.colors["success"])
            self.root.after(1000, self.fade_out)

    # ---------------- FADE ----------------
    def fade_in(self):
        if self.alpha < 1:
            self.alpha += 0.05
            self.root.attributes("-alpha", self.alpha)
            self.root.after(30, self.fade_in)
        else:
            self.animate()

    def fade_out(self):
        if self.alpha > 0:
            self.alpha -= 0.05
            self.root.attributes("-alpha", self.alpha)
            self.root.after(30, self.fade_out)
        else:
            self.root.destroy()
            self.on_finish_callback()

    # ---------------- WINDOW ----------------
    def center_window(self):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x = (sw - self.width) // 2
        y = (sh - self.height) // 2
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")

    # ---------------- COLOR ----------------
    def lerp_color(self, c1, c2, t):
        r1, g1, b1 = self.root.winfo_rgb(c1)
        r2, g2, b2 = self.root.winfo_rgb(c2)
        r = int((r1 + (r2 - r1) * t) / 256)
        g = int((g1 + (g2 - g1) * t) / 256)
        b = int((b1 + (b2 - b1) * t) / 256)
        return f"#{r:02x}{g:02x}{b:02x}"



import customtkinter as ctk
from typing import Callable, Dict, Any

# Assuming these exist in your project
# from your_module import BaseModal, MessageModal, db

class LoginWindow(BaseModal):
    def __init__(self, parent, on_success: Callable[[Dict[str, Any]], None]):
        self.on_success = on_success
        self.show_password = False

        super().__init__(parent, 480, 540)

        self.win.configure(fg_color="#0f0f11")

        # Main card
        card = ctk.CTkFrame(
            self.win,
            corner_radius=24,
            fg_color=("#1a1a1e", "#222226"),
            bg_color="transparent",
            border_width=1,
            border_color=("#333338", "#404046")
        )
        card.pack(padx=44, pady=44, fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", pady=(24, 0), padx=24)

        ctk.CTkLabel(
            header,
            text="Welcome Back",
            font=("Segoe UI", 30, "bold"),
            text_color="#00d4e0"
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="✕",
            width=38,
            height=38,
            corner_radius=19,
            font=("Segoe UI", 18, "bold"),
            fg_color="transparent",
            hover_color="#333338",
            text_color="#aaaaaa",
            command=self.win.destroy
        ).pack(side="right")

        # Subtitle
        ctk.CTkLabel(
            card,
            text="Sign in to continue",
            font=("Segoe UI", 14),
            text_color="#a0a0a5"
        ).pack(pady=(12, 36))

        # Email field
        self.email = ctk.CTkEntry(
            card,
            placeholder_text="Email or username",
            width=340,
            height=52,
            corner_radius=14,
            font=("Segoe UI", 15),
            fg_color="#212125",
            border_color="#44444a",
            border_width=2,
            text_color="#e0e0e5",
            placeholder_text_color="#707075"
        )
        self.email.pack(pady=10)
        self.email.focus_set()

        # ── Password with embedded eye icon ────────────────────────────────
        password_container = ctk.CTkFrame(
            card,
            fg_color="#212125",
            corner_radius=14,
            border_width=2,
            border_color="#44444a",
            width=340,
            height=52
        )
        password_container.pack(pady=10)
        password_container.pack_propagate(False)  # preserve fixed size

        self.password = ctk.CTkEntry(
            password_container,
            placeholder_text="Password",
            show="•",
            font=("Segoe UI", 15),
            text_color="#e0e0e5",
            fg_color="transparent",
            border_width=0,
            placeholder_text_color="#707075"
        )
        self.password.pack(side="left", fill="both", expand=True, padx=(16, 48))

        # Eye button placed INSIDE the entry field area
        self.eye_btn = ctk.CTkButton(
            password_container,
            text="👁",
            width=36,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#2a2a2f",
            text_color="#aaaaaa",
            font=("Segoe UI", 18),
            command=self.toggle_password_visibility
        )
        self.eye_btn.place(relx=1.0, rely=0.5, anchor="e", x=-8)

        # Login button
        self.login_btn = ctk.CTkButton(
            card,
            text="Sign In",
            width=340,
            height=52,
            corner_radius=14,
            font=("Segoe UI Semibold", 16),
            fg_color="#00d4e0",
            hover_color="#00b0c0",
            text_color="#0f0f11",
            command=self.start_login
        )
        self.login_btn.pack(pady=(32, 24))

        # Progress bar (thin, appears below button when loading)
        self.spinner = ctk.CTkProgressBar(
            card,
            width=340,
            height=6,
            corner_radius=3,
            fg_color="#333338",
            progress_color="#00d4e0",
            mode="indeterminate"
        )
        self.spinner.set(0)

        # Press Enter → login
        self.win.bind("<Return>", lambda e: self.start_login())

    def toggle_password_visibility(self):
        self.show_password = not self.show_password

        if self.show_password:
            self.password.configure(show="")
            self.eye_btn.configure(text="👁‍🗨")  # eye with slash = hidden mode now
        else:
            self.password.configure(show="•")
            self.eye_btn.configure(text="👁")

        # Alternative (text version - many apps prefer this):
        # self.eye_btn.configure(
        #     text="Hide" if self.show_password else "Show",
        #     font=("Segoe UI Semibold", 13),
        #     text_color="#00d4e0" if self.show_password else "#aaaaaa"
        # )

    def start_login(self):
        email = self.email.get().strip()
        password = self.password.get().strip()

        if not email or not password:
            MessageModal(self.parent, "Error", "Please fill in all fields", False)
            return

        self.login_btn.configure(state="disabled", text="Checking...")
        self.spinner.pack(pady=(0, 16))
        self.spinner.start()

        self.win.after(600, lambda: self.process_login(email, password))

    def process_login(self, email: str, password: str):
        success, result = db.verify_user(email, password)

        self.spinner.stop()
        self.spinner.pack_forget()
        self.login_btn.configure(state="normal", text="Sign In")

        if success:
            MessageModal(
                self.parent,
                "Success",
                f"Welcome back, {result.get('username', 'User')}!",
                True
            )
            self.win.after(180, lambda: self._finish_login(result))
        else:
            MessageModal(self.parent, "Login Failed", result, False)

    def _finish_login(self, user: Dict[str, Any]):
        if self.win.winfo_exists():
            self.win.destroy()
        self.on_success(user)
        
                        
import customtkinter as ctk
from typing import Callable, Dict, Any

# Assuming BaseModal, MessageModal, db are defined elsewhere in your project

class SignupWindow(BaseModal):
    def __init__(self, parent, on_success: Callable[[Dict[str, Any]], None]):
        self.on_success = on_success
        self.show_password = False

        super().__init__(parent, 480, 620)  # taller to accommodate fields nicely

        self.win.configure(fg_color="#0f0f11")

        # Main card
        card = ctk.CTkFrame(
            self.win,
            corner_radius=24,
            fg_color=("#1a1a1e", "#222226"),
            bg_color="transparent",
            border_width=1,
            border_color=("#333338", "#404046")
        )
        card.pack(padx=44, pady=44, fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", pady=(24, 0), padx=24)

        ctk.CTkLabel(
            header,
            text="Create Account",
            font=("Segoe UI", 30, "bold"),
            text_color="#00d4e0"
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="✕",
            width=38,
            height=38,
            corner_radius=19,
            font=("Segoe UI", 18, "bold"),
            fg_color="transparent",
            hover_color="#333338",
            text_color="#aaaaaa",
            command=self.win.destroy
        ).pack(side="right")

        # Subtitle
        ctk.CTkLabel(
            card,
            text="Join us and get started",
            font=("Segoe UI", 14),
            text_color="#a0a0a5"
        ).pack(pady=(12, 36))

        # ── Username ───────────────────────────────────────────────
        self.username = ctk.CTkEntry(
            card,
            placeholder_text="Username",
            width=340,
            height=52,
            corner_radius=14,
            font=("Segoe UI", 15),
            fg_color="#212125",
            border_color="#44444a",
            border_width=2,
            text_color="#e0e0e5",
            placeholder_text_color="#707075"
        )
        self.username.pack(pady=10)
        self.username.focus_set()  # auto focus

        # ── Email ──────────────────────────────────────────────────
        self.email = ctk.CTkEntry(
            card,
            placeholder_text="Email",
            width=340,
            height=52,
            corner_radius=14,
            font=("Segoe UI", 15),
            fg_color="#212125",
            border_color="#44444a",
            border_width=2,
            text_color="#e0e0e5",
            placeholder_text_color="#707075"
        )
        self.email.pack(pady=10)

        # ── Password with embedded eye icon ────────────────────────────────
        password_container = ctk.CTkFrame(
            card,
            fg_color="#212125",
            corner_radius=14,
            border_width=2,
            border_color="#44444a",
            width=340,
            height=52
        )
        password_container.pack(pady=10)
        password_container.pack_propagate(False)

        self.password = ctk.CTkEntry(
            password_container,
            placeholder_text="Password",
            show="•",
            font=("Segoe UI", 15),
            text_color="#e0e0e5",
            fg_color="transparent",
            border_width=0,
            placeholder_text_color="#707075"
        )
        self.password.pack(side="left", fill="both", expand=True, padx=(16, 48))

        self.eye_btn = ctk.CTkButton(
            password_container,
            text="👁",
            width=36,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#2a2a2f",
            text_color="#aaaaaa",
            font=("Segoe UI", 18),
            command=self.toggle_password_visibility
        )
        self.eye_btn.place(relx=1.0, rely=0.5, anchor="e", x=-8)

        # Sign Up button
        self.signup_btn = ctk.CTkButton(
            card,
            text="Create Account",
            width=340,
            height=52,
            corner_radius=14,
            font=("Segoe UI Semibold", 16),
            fg_color="#00d4e0",
            hover_color="#00b0c0",
            text_color="#0f0f11",
            command=self.start_signup
        )
        self.signup_btn.pack(pady=(32, 24))

        # Progress bar
        self.spinner = ctk.CTkProgressBar(
            card,
            width=340,
            height=6,
            corner_radius=3,
            fg_color="#333338",
            progress_color="#00d4e0",
            mode="indeterminate"
        )
        self.spinner.set(0)

        # Enter key → signup
        self.win.bind("<Return>", lambda e: self.start_signup())

    def toggle_password_visibility(self):
        self.show_password = not self.show_password

        if self.show_password:
            self.password.configure(show="")
            self.eye_btn.configure(text="👁‍🗨")  # slashed eye = now hidden
        else:
            self.password.configure(show="•")
            self.eye_btn.configure(text="👁")

        # Optional text version (cleaner in some UIs):
        # self.eye_btn.configure(
        #     text="Hide" if self.show_password else "Show",
        #     font=("Segoe UI Semibold", 13),
        #     text_color="#00d4e0" if self.show_password else "#aaaaaa"
        # )

    def start_signup(self):
        username = self.username.get().strip()
        email = self.email.get().strip()
        password = self.password.get().strip()

        if not username or not email or not password:
            MessageModal(self.parent, "Error", "Please fill in all fields", False)
            return

        self.signup_btn.configure(state="disabled", text="Creating...")
        self.spinner.pack(pady=(0, 16))
        self.spinner.start()

        self.win.after(600, lambda: self.process_signup(username, email, password))

    def process_signup(self, username: str, email: str, password: str):
        success, message = db.create_user(username, email, password)

        self.spinner.stop()
        self.spinner.pack_forget()
        self.signup_btn.configure(state="normal", text="Create Account")

        if success:
            MessageModal(
                self.parent,
                "Account Created",
                f"Welcome, {username}!",
                True
            )
            self.win.after(180, lambda: self._finish_signup(email, password))
        else:
            MessageModal(self.parent, "Signup Failed", message, False)

    def _finish_signup(self, email: str, password: str):
        login_success, user = db.verify_user(email, password)

        if login_success:
            if self.win.winfo_exists():
                self.win.destroy()
            self.on_success(user)
        else:
            MessageModal(self.parent, "Error", "Auto-login failed after signup", False)
            
                        
import customtkinter as ctk
import tkinter as tk
from tkinter import CENTER
import ctypes

# Windows blur effect function (updated)
def enable_blur(window):
    try:
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())

        class ACCENTPOLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_int),
                ("AccentFlags", ctypes.c_int),
                ("GradientColor", ctypes.c_int),
                ("AnimationId", ctypes.c_int)
            ]

        class WINCOMPATTRDATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.POINTER(ACCENTPOLICY)),
                ("SizeOfData", ctypes.c_size_t)
            ]

        ACCENT_ENABLE_BLURBEHIND = 3
        ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
        WCA_ACCENT_POLICY = 19

        # Try acrylic blur first (Windows 11), fallback to normal blur
        for accent_state in [ACCENT_ENABLE_ACRYLICBLURBEHIND, ACCENT_ENABLE_BLURBEHIND]:
            try:
                accent = ACCENTPOLICY()
                accent.AccentState = accent_state
                accent.AccentFlags = 2
                accent.GradientColor = 0x88000000  # Slightly more transparent
                accent.AnimationId = 0

                data = WINCOMPATTRDATA()
                data.Attribute = WCA_ACCENT_POLICY
                data.Data = ctypes.pointer(accent)
                data.SizeOfData = ctypes.sizeof(accent)

                ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
                break
            except:
                continue
    except:
        pass

class MainApp:
    def __init__(self):
        self.current_user = None
        self.user_menu_open = False
        self.active_button = None
        self.active_view_name = None

        # ----------------- ROOT -----------------
        self.root = ctk.CTk()
        self.root.title("DiagnoSight AI")
        self.root.configure(fg_color="#0a1628")
        self.root.focus_force()

        # OPEN IN FULL SCREEN
        self.root.attributes("-fullscreen", True)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.minsize(1100, 700)

        # Add ESC key to exit fullscreen
        self.root.bind("<Escape>", lambda e: self.toggle_fullscreen())

        # ================== TOP BAR ==================
        self.topbar = ctk.CTkFrame(
            self.root, height=70, fg_color="#0f1f38", corner_radius=0
        )
        self.topbar.pack(fill="x", side="top")
        self.topbar.pack_propagate(False)

        # App title
        ctk.CTkLabel(
            self.topbar,
            text="DiagnoSight AI",
            font=("Segoe UI Semibold", 28, "bold"),
            text_color="#00c2cb"
        ).pack(side="left", padx=30)

        # Fullscreen toggle button
        self.fullscreen_btn = ctk.CTkButton(
            self.topbar,
            text="⤢",  # Fullscreen icon
            width=40,
            height=40,
            corner_radius=20,
            font=("Segoe UI Semibold", 16),
            fg_color="transparent",
            hover_color="#1e3a5f",
            text_color="#00c2cb",
            command=self.toggle_fullscreen
        )
        self.fullscreen_btn.pack(side="left", padx=10)

        # ---- AUTH AREA ----
        self.auth_area = ctk.CTkFrame(self.topbar, fg_color="transparent")
        self.auth_area.pack(side="right", padx=30)

        self.login_btn = ctk.CTkButton(
            self.auth_area,
            text="Login",
            width=120,
            height=40,
            corner_radius=20,
            font=("Segoe UI Semibold", 14),
            fg_color="#00c2cb",
            hover_color="#00a5ad",
            command=lambda: LoginWindow(self.root, self.on_user_login)
        )
        self.login_btn.pack(side="right", padx=8)

        self.signup_btn = ctk.CTkButton(
            self.auth_area,
            text="Sign Up",
            width=120,
            height=40,
            corner_radius=20,
            font=("Segoe UI Semibold", 14),
            fg_color="#1b9aaa",
            hover_color="#16808d",
            command=lambda: SignupWindow(self.root, self.on_user_login)
        )
        self.signup_btn.pack(side="right")

        # ================== BODY ==================
        self.body = ctk.CTkFrame(self.root, fg_color="#0f1f38")
        self.body.pack(fill="both", expand=True)

        # ================== SIDEBAR ==================
        self.sidebar = ctk.CTkFrame(
            self.body, width=240, fg_color="#0a1628", corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.sidebar_buttons = [
            ("Dashboard", self.build_dashboard),
            ("Diagnosis", DiagnosisView),
            ("Chat Assistant", ChatAssistantView),
            ("Web Insights", WebInsightsView),
            ("Reports", ReportsView),
            ("Settings", SettingsView),
        ]

        self.button_widgets = []

        for text, view_cmd in self.sidebar_buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                width=220,
                height=50,
                fg_color="transparent",
                hover_color="#1e3a5f",
                text_color="#e6f7fa",
                font=("Segoe UI Semibold", 15),
                anchor="w",
                corner_radius=12,
                command=lambda cmd=view_cmd, name=text: self.navigate_to(cmd, name)
            )
            btn.pack(pady=8, padx=20)
            self.button_widgets.append(btn)

        # ================== CONTENT ==================
        self.content = ctk.CTkFrame(self.body, fg_color="transparent")
        self.content.pack(side="right", fill="both", expand=True, padx=30, pady=30)

        # Show dashboard by default
        self.navigate_to(self.build_dashboard, "Dashboard")
        
        # Start the main loop
        self.root.mainloop()

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        current_state = self.root.attributes("-fullscreen")
        
        if current_state:
            # Exit fullscreen
            self.root.attributes("-fullscreen", False)
            self.root.geometry("1280x800")
            self.fullscreen_btn.configure(text="⤡")  # Windowed icon
        else:
            # Enter fullscreen
            self.root.attributes("-fullscreen", True)
            self.fullscreen_btn.configure(text="⤢")  # Fullscreen icon

    # ================== NAVIGATION ==================
    def navigate_to(self, view_command, button_name):
        self.active_view_name = button_name

        if self.active_button:
            self.active_button.configure(fg_color="transparent")

        for btn in self.button_widgets:
            if btn.cget("text") == button_name:
                btn.configure(fg_color="#00c2cb")
                self.active_button = btn
                break

        self.clear_content()

        if button_name == "Dashboard":
            view_command()
        else:
            view_command(self.content, self)

    # ================== DASHBOARD ==================
    def build_dashboard(self):
        self.clear_content()

        user_text = (
            f"Welcome, {self.current_user['username']}!"
            if self.current_user else
            "Welcome (Guest Mode)"
        )

        subtitle = (
            "Advanced AI-Powered Medical Diagnosis at Your Fingertips"
            if self.current_user else
            "Sign in to unlock full AI diagnostics"
        )

        ctk.CTkLabel(
            self.content,
            text=user_text,
            font=("Segoe UI", 36, "bold"),
            text_color="#00c2cb"
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            self.content,
            text=subtitle,
            font=("Segoe UI", 16),
            text_color="#b0bec5"
        ).pack(anchor="w", pady=(0, 40))

        grid_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)

        actions = [
            ("Start New Diagnosis", "#00c2cb",
             lambda: self.navigate_to(DiagnosisView, "Diagnosis")),
            ("Chat with AI Assistant", "#1b9aaa",
             lambda: self.navigate_to(ChatAssistantView, "Chat Assistant")),
            ("View Recent Reports", "#2e8bc0",
             lambda: self.navigate_to(ReportsView, "Reports")),
        ]

        for i, (title, color, cmd) in enumerate(actions):
            card = ctk.CTkFrame(
                grid_frame, corner_radius=20,
                fg_color=("#17253a", "#1e2d42"), height=180
            )
            card.grid(row=0, column=i, padx=15, pady=15, sticky="nsew")
            card.grid_propagate(False)

            ctk.CTkLabel(
                card, text=title,
                font=("Segoe UI Semibold", 20),
                text_color="#ffffff"
            ).pack(pady=40)

            ctk.CTkButton(
                card, text="Go →",
                width=140, fg_color=color,
                hover_color="#00a5ad",
                command=cmd
            ).pack()

        stats = [
            ("Total Diagnoses", "48", "This month: +12"),
            ("AI Accuracy", "96.8%", "Industry leading"),
            ("Active Insights", "23", "From medical sources"),
        ]

        for i, (title, value, sub) in enumerate(stats):
            card = ctk.CTkFrame(
                grid_frame, corner_radius=20,
                fg_color=("#17253a", "#1e2d42"), height=160
            )
            card.grid(row=1, column=i, padx=15, pady=15, sticky="nsew")
            card.grid_propagate(False)

            ctk.CTkLabel(
                card, text=value,
                font=("Segoe UI", 42, "bold"),
                text_color="#00c2cb"
            ).pack(pady=(30, 5))

            ctk.CTkLabel(
                card, text=title,
                font=("Segoe UI", 16),
                text_color="#b0bec5"
            ).pack()

            ctk.CTkLabel(
                card, text=sub,
                font=("Segoe UI", 12),
                text_color="#78909c"
            ).pack(pady=(0, 20))

        for i in range(3):
            grid_frame.grid_columnconfigure(i, weight=1)
        grid_frame.grid_rowconfigure((0, 1), weight=1)

    # ================== UTIL ==================
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # ================== AUTH ==================
    def on_user_login(self, user):
        self.current_user = user

        self.login_btn.pack_forget()
        self.signup_btn.pack_forget()

        initial = user["username"][0].upper()
        self.user_btn = ctk.CTkButton(
            self.auth_area,
            text=initial,
            width=50,
            height=50,
            corner_radius=25,
            font=("Segoe UI Bold", 20),
            fg_color="#00c2cb",
            hover_color="#00a5ad",
            command=self.toggle_user_menu
        )
        self.user_btn.pack(side="right", padx=10)

        self.refresh_active_view()

    def logout(self):
        self.current_user = None
        self.user_btn.destroy()

        self.login_btn.pack(side="right", padx=8)
        self.signup_btn.pack(side="right")

        self.refresh_active_view()

    def refresh_active_view(self):
        if self.active_view_name == "Dashboard":
            self.build_dashboard()
        else:
            for name, view in self.sidebar_buttons:
                if name == self.active_view_name:
                    self.clear_content()
                    view(self.content, self)
                    break

    def toggle_user_menu(self):
        pass

import threading
import os
import webbrowser
from datetime import datetime
import random

import threading
import os
import webbrowser
from datetime import datetime
import random

class DiagnosisView:
    CONFIDENCE_HIGH = 75
    CONFIDENCE_LOW = 50

    def __init__(self, parent, app):
        self.app = app
        self.parent = parent

        self.image_path = None
        self.prediction_data = None
        self.current_image = None  # To keep reference to image
        self.processing = False
        
        # Check if model is available
        self.MODEL_AVAILABLE = self.check_model_availability()
        
        # Enhanced disease database with more details
        self.enhanced_disease_info = {
            "Eczema": {
                "causes": [
                    "Genetic factors (family history of allergies)",
                    "Environmental triggers (dust, pollen, mold)",
                    "Irritants (soaps, detergents, shampoos)",
                    "Stress and emotional factors",
                    "Climate (dry air, cold weather)"
                ],
                "prevention": [
                    "Moisturize skin daily",
                    "Use mild, fragrance-free soaps",
                    "Avoid known triggers and allergens",
                    "Wear soft, breathable fabrics",
                    "Manage stress through relaxation techniques"
                ],
                "when_to_see_doctor": [
                    "Home remedies don't relieve symptoms",
                    "Symptoms interfere with sleep or daily activities",
                    "Skin appears infected (yellow crusts, pus, redness)",
                    "Condition spreads to new areas",
                    "Painful cracking or bleeding occurs"
                ],
                "complications": [
                    "Skin infections (staph, herpes)",
                    "Sleep problems due to itching",
                    "Asthma and hay fever (atopic march)",
                    "Chronic itchy, scaly skin",
                    "Social/emotional distress"
                ]
            },
            "Melanoma": {
                "causes": [
                    "UV radiation exposure (sun, tanning beds)",
                    "Fair skin, light hair, blue/green eyes",
                    "Family history of melanoma",
                    "Presence of many moles",
                    "Weakened immune system"
                ],
                "prevention": [
                    "Use broad-spectrum SPF 30+ sunscreen",
                    "Avoid sun between 10 AM - 4 PM",
                    "Wear protective clothing and hats",
                    "Avoid tanning beds entirely",
                    "Regular skin self-exams"
                ],
                "when_to_see_doctor": [
                    "ANY new, changing, or unusual mole",
                    "Mole with ABCDE characteristics",
                    "Sore that doesn't heal",
                    "Spread of pigment beyond mole border",
                    "Redness/swelling beyond mole"
                ],
                "complications": [
                    "Metastasis to lymph nodes",
                    "Spread to other organs (lungs, liver, brain)",
                    "Recurrence after treatment",
                    "Treatment side effects",
                    "Psychological impact"
                ]
            },
            "Atopic Dermatitis": {
                "causes": [
                    "Genetic predisposition (filaggrin gene mutations)",
                    "Immune system dysfunction",
                    "Environmental allergens",
                    "Dry skin and impaired skin barrier",
                    "Microbiome imbalance"
                ],
                "prevention": [
                    "Daily bathing with lukewarm water",
                    "Apply moisturizer within 3 minutes of bathing",
                    "Use humidifier in dry climates",
                    "Avoid harsh fabrics (wool, synthetics)",
                    "Identify and avoid personal triggers"
                ],
                "when_to_see_doctor": [
                    "Severe itching affecting sleep",
                    "Signs of infection (yellow crust, pus)",
                    "Condition doesn't improve with home care",
                    "Spreads to large body areas",
                    "Affects daily activities significantly"
                ],
                "complications": [
                    "Skin infections (bacterial, viral, fungal)",
                    "Sleep disturbances",
                    "Mental health issues (anxiety, depression)",
                    "Social isolation",
                    "Asthma and allergic rhinitis"
                ]
            },
            "Basal Cell Carcinoma (BCC)": {
                "causes": [
                    "Cumulative sun exposure over years",
                    "Intense, intermittent sunburns",
                    "Fair skin that burns easily",
                    "Radiation therapy exposure",
                    "Arsenic exposure (rare)"
                ],
                "prevention": [
                    "Daily sunscreen use year-round",
                    "Seek shade during peak sun hours",
                    "Wear sun-protective clothing",
                    "Regular skin checks by dermatologist",
                    "Self-examine skin monthly"
                ],
                "when_to_see_doctor": [
                    "New growth or sore that doesn't heal",
                    "Pearly or waxy bump on skin",
                    "Flat, scar-like lesion",
                    "Brownish or flesh-colored lesion",
                    "Bleeding or oozing spot"
                ],
                "complications": [
                    "Local tissue destruction if untreated",
                    "Recurrence after treatment",
                    "Nerve/muscle damage if invasive",
                    "Cosmetic disfigurement",
                    "Rare metastasis (very uncommon)"
                ]
            },
            "Melanocytic Nevi (NV)": {
                "causes": [
                    "Genetic factors (family history)",
                    "Sun exposure (especially in childhood)",
                    "Hormonal changes (pregnancy, puberty)",
                    "Fair skin type",
                    "Immune suppression"
                ],
                "prevention": [
                    "Sun protection from childhood",
                    "Avoid tanning beds",
                    "Regular skin self-exams",
                    "Professional skin checks annually",
                    "Monitor existing moles for changes"
                ],
                "when_to_see_doctor": [
                    "Mole changes in size, shape, or color",
                    "New mole after age 30",
                    "Mole with irregular borders",
                    "Itching, bleeding, or pain in mole",
                    "Rapid growth of mole"
                ],
                "complications": [
                    "Potential transformation to melanoma",
                    "Cosmetic concerns",
                    "Anxiety about cancer risk",
                    "Need for biopsy/surgery",
                    "Scarring from removal"
                ]
            },
            "Psoriasis": {
                "causes": [
                    "Genetic predisposition (family history)",
                    "Immune system dysfunction (T-cells)",
                    "Environmental triggers (stress, infection)",
                    "Certain medications (lithium, beta-blockers)",
                    "Smoking and alcohol consumption"
                ],
                "prevention": [
                    "Manage stress effectively",
                    "Avoid skin injuries (Koebner phenomenon)",
                    "Treat infections promptly",
                    "Maintain healthy weight",
                    "Limit alcohol and quit smoking"
                ],
                "when_to_see_doctor": [
                    "Patches cover large areas of body",
                    "Joint pain or swelling develops",
                    "Symptoms don't improve with OTC treatments",
                    "Affects quality of life significantly",
                    "Nail changes occur"
                ],
                "complications": [
                    "Psoriatic arthritis (30% of cases)",
                    "Cardiovascular disease risk",
                    "Type 2 diabetes risk",
                    "Depression and anxiety",
                    "Metabolic syndrome"
                ]
            },
            "Seborrheic Keratoses": {
                "causes": [
                    "Aging (most common in people over 50)",
                    "Genetic predisposition",
                    "Sun exposure (controversial)",
                    "Pregnancy (hormonal changes)",
                    "Unknown factors"
                ],
                "prevention": [
                    "Sun protection may help",
                    "No proven prevention methods",
                    "Regular skin monitoring",
                    "Avoid picking or scratching",
                    "Gentle skin care"
                ],
                "when_to_see_doctor": [
                    "Rapid growth or change in appearance",
                    "Bleeding, itching, or pain develops",
                    "Cosmetic concern",
                    "Difficulty distinguishing from skin cancer",
                    "Irritation from clothing friction"
                ],
                "complications": [
                    "Misdiagnosis as melanoma",
                    "Cosmetic concerns",
                    "Itching or irritation",
                    "Infection if scratched",
                    "Anxiety about appearance"
                ]
            }
        }

        # Configure main frame
        self.main_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create two-column layout
        self.create_left_panel()
        self.create_right_panel()
    
    def check_model_availability(self):
        """Check if the prediction model is available"""
        try:
            from predict import predictor
            # Test if model loads
            if hasattr(predictor, 'model_available'):
                return predictor.model_available
            return False
        except (ImportError, AttributeError) as e:
            print(f"Model check error: {e}")
            return False

    def create_left_panel(self):
        """Left panel for image upload and preview"""
        self.left_frame = ctk.CTkFrame(self.main_frame, width=450, corner_radius=20)
        self.left_frame.pack(side="left", fill="y", padx=(0, 20))
        self.left_frame.pack_propagate(False)

        # Title
        ctk.CTkLabel(
            self.left_frame,
            text="📁 Upload Image",
            font=("Segoe UI", 24, "bold"),
            text_color="#0ea5e9"
        ).pack(pady=(30, 20))

        # Upload button (larger and centered)
        self.upload_btn = ctk.CTkButton(
            self.left_frame,
            text="📤 Upload Skin Image",
            width=350,
            height=60,
            corner_radius=15,
            font=("Segoe UI", 18, "bold"),
            fg_color="#0ea5e9",
            hover_color="#0284c7",
            command=self.upload_image
        )
        self.upload_btn.pack(pady=(0, 10))

        # New Analysis button right below upload button
        self.new_analysis_btn = ctk.CTkButton(
            self.left_frame,
            text="🔄 New Analysis",
            width=350,
            height=50,
            corner_radius=12,
            font=("Segoe UI", 16, "bold"),
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            command=self.clear_image,
            state="disabled"
        )
        self.new_analysis_btn.pack(pady=(0, 15))

        # Supported formats
        ctk.CTkLabel(
            self.left_frame,
            text="Supported Formats: JPG, PNG, JPEG, BMP, TIFF",
            font=("Segoe UI", 13),
            text_color="#9ca3af"
        ).pack(pady=(10, 30))

        # Image preview frame - Made larger
        self.preview_frame = ctk.CTkFrame(
            self.left_frame,
            corner_radius=15,
            fg_color=("#111827", "#1f2937"),  # Very dark background
            height=400  # Increased height for larger preview
        )
        self.preview_frame.pack(pady=20, padx=20, fill="x", expand=True)

        # Preview title
        ctk.CTkLabel(
            self.preview_frame,
            text="🖼️ Image Preview",
            font=("Segoe UI", 18, "bold"),
            text_color="#60a5fa"  # Bright blue
        ).pack(pady=(15, 10))

        # Image display area - Made larger
        self.image_display = ctk.CTkLabel(
            self.preview_frame,
            text="No image selected\n\nClick 'Upload Skin Image' button above",
            font=("Segoe UI", 14),
            text_color="#d1d5db",  # Light gray for visibility
            justify="center",
            height=300  # Increased height
        )
        self.image_display.pack(pady=10, padx=20, fill="both", expand=True)

        # File info
        self.file_info_label = ctk.CTkLabel(
            self.preview_frame,
            text="",
            font=("Segoe UI", 12),
            text_color="#9ca3af"
        )
        self.file_info_label.pack(pady=(0, 15))

        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            self.left_frame,
            text="Ready to upload image",
            font=("Segoe UI", 13),
            text_color="#10b981"
        )
        self.status_indicator.pack(pady=(10, 30))

    def create_right_panel(self):
        """Right panel for displaying detailed results"""
        self.right_frame = ctk.CTkFrame(self.main_frame, corner_radius=20)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Title
        ctk.CTkLabel(
            self.right_frame,
            text="🔍 AI Diagnosis Results",
            font=("Segoe UI", 28, "bold"),
            text_color="#60a5fa"  # Bright blue
        ).pack(pady=(30, 20))

        # Results container - initially empty
        self.results_container = ctk.CTkFrame(
            self.right_frame,
            fg_color="transparent"
        )
        self.results_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Initial message
        self.initial_message = ctk.CTkLabel(
            self.results_container,
            text="👈 Upload an image to get AI diagnosis\n\nThe system will analyze skin conditions and provide\ndetailed information including symptoms, treatment,\nand recommendations.",
            font=("Segoe UI", 16),
            text_color="#9ca3af",
            justify="center"
        )
        self.initial_message.pack(expand=True)

    def clear_image(self):
        """Clear the current image and reset the preview"""
        try:
            self.image_path = None
            self.current_image = None
            self.prediction_data = None
            
            # Safely reset image display
            self.image_display.configure(
                image=None,
                text="No image selected\n\nClick 'Upload Skin Image' button above"
            )
            
            # Clear file info
            self.file_info_label.configure(text="")
            
            # Reset status
            self.status_indicator.configure(
                text="Ready to upload image",
                text_color="#10b981"
            )
            
            # Disable new analysis button
            self.new_analysis_btn.configure(state="disabled")
            
            # Clear results if any
            self.clear_results()
            
            # Show initial message
            self.initial_message.pack(expand=True)
            
        except Exception as e:
            print(f"Error in clear_image: {e}")

    def upload_image(self):
        """Handle image upload"""
        if self.processing:
            return

        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
            ("All files", "*.*")
        ]
        
        path = filedialog.askopenfilename(
            title="Select Skin Image",
            filetypes=filetypes
        )

        if not path:
            return

        self.image_path = path
        self.show_image_preview(path)
        
        # Enable new analysis button
        self.new_analysis_btn.configure(state="normal")
        
        # Start analysis
        self.start_analysis(path)

    def show_image_preview(self, image_path):
        """Display uploaded image preview - Shows full image fit to frame"""
        try:
            # Update file info
            filename = os.path.basename(image_path)
            file_size = os.path.getsize(image_path) / 1024  # KB
            self.file_info_label.configure(
                text=f"{filename} ({file_size:.1f} KB)"
            )
            
            # Load image
            img = Image.open(image_path)
            
            # Get frame dimensions for fitting
            frame_width = 380  # Approximate width of display area
            frame_height = 280  # Approximate height of display area
            
            # Calculate new dimensions while maintaining aspect ratio
            img_ratio = img.width / img.height
            frame_ratio = frame_width / frame_height
            
            if img_ratio > frame_ratio:
                # Image is wider than frame
                new_width = frame_width
                new_height = int(frame_width / img_ratio)
            else:
                # Image is taller than frame
                new_height = frame_height
                new_width = int(frame_height * img_ratio)
            
            # Resize image to fit the frame while maintaining aspect ratio
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to CTkImage
            self.current_image = ctk.CTkImage(
                light_image=img_resized,
                dark_image=img_resized,
                size=(new_width, new_height)
            )
            
            # Update image display - set image first, then text
            self.image_display.configure(image=self.current_image)
            self.image_display.configure(text="")
            
            # Update status
            self.status_indicator.configure(
                text="✓ Image loaded successfully",
                text_color="#10b981"
            )
            
        except Exception as e:
            print(f"Error in show_image_preview: {e}")
            self.image_display.configure(
                text=f"❌ Error loading image\n{str(e)[:50]}",
                image=None
            )
            self.status_indicator.configure(
                text=f"Error loading image: {str(e)[:50]}",
                text_color="#ef4444"
            )

    def start_analysis(self, image_path):
        """Start the analysis process"""
        self.processing = True
        
        # Clear previous results
        self.clear_results()
        
        # Show analyzing message
        self.show_analyzing_message()
        
        # Update UI
        self.upload_btn.configure(state="disabled", text="Analyzing...")
        self.new_analysis_btn.configure(state="disabled")
        self.status_indicator.configure(
            text="⏳ Analyzing image with AI...",
            text_color="#f59e0b"
        )
        
        # Start analysis in separate thread
        thread = threading.Thread(target=self.analyze_image, args=(image_path,))
        thread.daemon = True
        thread.start()

    def show_analyzing_message(self):
        """Show analyzing animation"""
        self.initial_message.pack_forget()
        
        self.analyzing_frame = ctk.CTkFrame(
            self.results_container,
            fg_color="transparent"
        )
        self.analyzing_frame.pack(expand=True)
        
        # Spinner animation
        ctk.CTkLabel(
            self.analyzing_frame,
            text="⏳",
            font=("Segoe UI", 48),
            text_color="#60a5fa"
        ).pack(pady=20)
        
        ctk.CTkLabel(
            self.analyzing_frame,
            text="AI is analyzing your image...",
            font=("Segoe UI", 18, "bold"),
            text_color="#60a5fa"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            self.analyzing_frame,
            text="This may take a few seconds",
            font=("Segoe UI", 14),
            text_color="#9ca3af"
        ).pack(pady=5)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.analyzing_frame, width=300)
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0)
        self.progress_bar.start()

    def analyze_image(self, image_path):
        """Analyze the image using AI model"""
        try:
            # Simulate processing time
            import time
            for i in range(5):
                time.sleep(0.3)
                if hasattr(self, 'progress_bar'):
                    self.right_frame.after(0, self.update_progress, (i+1)/5)
            
            if self.MODEL_AVAILABLE:
                # Use actual model
                from predict import predictor
                self.prediction_data = predictor.predict_image(image_path)
                print(f"✓ Prediction: {self.prediction_data['predicted_disease']} ({self.prediction_data['confidence']:.1f}%)")
            else:
                # Simulated data for testing
                self.prediction_data = self.get_simulated_data()
                print("⚠ Using simulated predictions")
            
            # Enhance the prediction data with additional details
            self.enhance_prediction_data()
            
            # Update UI in main thread
            self.right_frame.after(0, self.display_results)
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error: {error_msg}")
            self.right_frame.after(0, self.show_error, error_msg)
    
    def enhance_prediction_data(self):
        """Add enhanced disease information to prediction data"""
        if not self.prediction_data:
            return
            
        disease_name = self.prediction_data.get("predicted_disease", "")
        enhanced_info = self.enhanced_disease_info.get(disease_name, {})
        
        # Add enhanced information to prediction data
        self.prediction_data["causes"] = enhanced_info.get("causes", ["Information not available"])
        self.prediction_data["prevention"] = enhanced_info.get("prevention", ["Information not available"])
        self.prediction_data["when_to_see_doctor"] = enhanced_info.get("when_to_see_doctor", ["Information not available"])
        self.prediction_data["complications"] = enhanced_info.get("complications", ["Information not available"])
    
    def update_progress(self, value):
        """Update progress bar"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.set(value)

    def get_simulated_data(self):
        """Generate simulated data for testing"""
        import random
        
        diseases = ["Eczema", "Melanoma", "Atopic Dermatitis", 
                   "Basal Cell Carcinoma (BCC)", "Psoriasis", "Melanocytic Nevi (NV)"]
        
        disease = random.choice(diseases)
        confidence = random.uniform(70, 95)
        
        # Disease information
        disease_info = {
            "Eczema": {
                "desc": "A condition that makes your skin red and itchy.",
                "symptoms": ["Itchy skin", "Red to brownish-gray patches", "Small, raised bumps"],
                "treatment": ["Moisturizers", "Corticosteroid creams", "Antihistamines"],
                "severity": "Low to Moderate"
            },
            "Melanoma": {
                "desc": "The most serious type of skin cancer that develops in melanocytes.",
                "symptoms": ["New spot on skin", "Changing mole", "Asymmetrical shape"],
                "treatment": ["Surgical removal", "Immunotherapy", "Radiation therapy"],
                "severity": "High"
            },
            "Atopic Dermatitis": {
                "desc": "A chronic condition that causes itchy, inflamed skin.",
                "symptoms": ["Dry skin", "Itching, especially at night", "Red to brownish-gray patches"],
                "treatment": ["Topical corticosteroids", "Moisturizers", "Antibiotics if infected"],
                "severity": "Moderate"
            },
            "Basal Cell Carcinoma (BCC)": {
                "desc": "A type of skin cancer that begins in basal cells.",
                "symptoms": ["Pearly or waxy bump", "Flat, flesh-colored scar-like lesion", "Bleeding or scabbing sore"],
                "treatment": ["Surgical excision", "Mohs surgery", "Cryotherapy"],
                "severity": "Moderate to High"
            },
            "Psoriasis": {
                "desc": "A skin disease that causes red, itchy scaly patches.",
                "symptoms": ["Red patches of skin", "Silvery scales", "Dry, cracked skin"],
                "treatment": ["Topical treatments", "Light therapy", "Systemic medications"],
                "severity": "Moderate"
            },
            "Melanocytic Nevi (NV)": {
                "desc": "Common moles that are usually harmless.",
                "symptoms": ["Round or oval shape", "Even color", "Distinct edge"],
                "treatment": ["Monitoring", "Surgical removal if suspicious"],
                "severity": "Low"
            }
        }
        
        info = disease_info.get(disease, disease_info["Eczema"])
        
        return {
            "predicted_disease": disease,
            "confidence": confidence,
            "description": info["desc"],
            "symptoms": info["symptoms"],
            "treatment": info["treatment"],
            "severity": info["severity"],
            "specialist": "Dermatologist",
            "recommendation": "Consult a dermatologist for proper diagnosis and treatment",
            "timestamp": datetime.now().strftime("%Y-%m-d %H:%M:%S"),
            "all_predictions": [
                {"disease": disease, "confidence": confidence},
                {"disease": random.choice([d for d in diseases if d != disease]), "confidence": random.uniform(10, 30)},
                {"disease": random.choice([d for d in diseases if d != disease]), "confidence": random.uniform(5, 15)}
            ]
        }

    def clear_results(self):
        """Clear previous results"""
        for widget in self.results_container.winfo_children():
            widget.destroy()

    def display_results(self):
        """Display the analysis results with HIGH CONTRAST colors and enhanced details"""
        self.processing = False
        self.upload_btn.configure(state="normal", text="📤 Upload Skin Image")
        self.new_analysis_btn.configure(state="normal")
        
        # Remove analyzing message
        if hasattr(self, 'analyzing_frame'):
            self.analyzing_frame.destroy()
        
        # Create scrollable frame for results
        self.results_scroll = ctk.CTkScrollableFrame(
            self.results_container,
            fg_color="transparent",
            scrollbar_button_color="#60a5fa",
            scrollbar_button_hover_color="#93c5fd"
        )
        self.results_scroll.pack(fill="both", expand=True)
        
        # Get data
        data = self.prediction_data
        
        # 1. MAIN RESULT CARD - HIGH CONTRAST
        result_card = ctk.CTkFrame(
            self.results_scroll,
            corner_radius=18,
            fg_color=("#1e40af", "#1e3a8a"),  # DARK BLUE background
            border_width=3,
            border_color="#3b82f6"
        )
        result_card.pack(fill="x", pady=(0, 25), padx=5)

        # Confidence indicator with color coding
        confidence = data["confidence"]
        if confidence >= self.CONFIDENCE_HIGH:
            conf_bg = "#22c55e"  # Bright green
            conf_text_color = "#ffffff"  # White text
            conf_text = "High Confidence"
        elif confidence >= self.CONFIDENCE_LOW:
            conf_bg = "#f59e0b"  # Bright amber
            conf_text_color = "#000000"  # Black text
            conf_text = "Moderate Confidence"
        else:
            conf_bg = "#ef4444"  # Bright red
            conf_text_color = "#ffffff"  # White text
            conf_text = "Low Confidence"
        
        # Result header
        header_frame = ctk.CTkFrame(result_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=20)
        
        ctk.CTkLabel(
            header_frame,
            text="📊 DIAGNOSIS RESULT",
            font=("Segoe UI", 20, "bold"),
            text_color="#ffffff"  # WHITE text on dark blue
        ).pack(side="left")
        
        # Confidence badge with high contrast - WIDER FOR BETTER TEXT DISPLAY
        conf_badge = ctk.CTkFrame(
            header_frame,
            fg_color=conf_bg,
            corner_radius=20,
            height=40
        )
        conf_badge.pack(side="right")
        conf_badge.pack_propagate(False)
        
        # Increase width to accommodate text properly
        conf_badge.configure(width=180)
        
        # Percentage label with padding
        percent_label = ctk.CTkLabel(
            conf_badge,
            text=f"{confidence:.1f}%",
            font=("Segoe UI", 18, "bold"),
            text_color=conf_text_color,
            padx=5
        )
        percent_label.pack(side="left", padx=(15, 8), pady=5)
        
        # Confidence type label with padding
        conf_type_label = ctk.CTkLabel(
            conf_badge,
            text=conf_text,
            font=("Segoe UI", 13),
            text_color=conf_text_color,
            padx=5
        )
        conf_type_label.pack(side="left", padx=(0, 15), pady=5)
        
        # Disease name - HIGH CONTRAST WHITE
        ctk.CTkLabel(
            result_card,
            text=data["predicted_disease"].upper(),
            font=("Segoe UI", 36, "bold"),
            text_color="#ffffff"  # WHITE on dark blue
        ).pack(pady=(0, 25))
        
        # Description - LIGHT GRAY for readability
        ctk.CTkLabel(
            result_card,
            text=data["description"],
            font=("Segoe UI", 16),
            text_color="#e5e7eb",  # Light gray
            wraplength=600,
            justify="center"
        ).pack(pady=(0, 30), padx=25)
        
        # 2. DETAILS SECTION - HIGH CONTRAST
        self.create_details_section(data)
        
        # 3. SYMPTOMS SECTION - HIGH CONTRAST
        self.create_section("🩺 Symptoms", data["symptoms"], 
                           bg_color="#0c4a6e",  # Dark blue
                           text_color="#e0f2fe",  # Very light blue
                           border_color="#0284c7")
        
        # 4. TREATMENT SECTION - HIGH CONTRAST
        self.create_section("💊 Recommended Treatment", data["treatment"], 
                           bg_color="#064e3b",  # Dark green
                           text_color="#d1fae5",  # Very light green
                           border_color="#10b981")
        
        # 5. CAUSES SECTION (NEW) - HIGH CONTRAST
        if data.get("causes"):
            self.create_section("🔍 Possible Causes", data["causes"], 
                               bg_color="#4c1d95",  # Dark purple
                               text_color="#f3e8ff",  # Very light purple
                               border_color="#8b5cf6")
        
        # 6. PREVENTION SECTION (NEW) - HIGH CONTRAST
        if data.get("prevention"):
            self.create_section("🛡️ Prevention Tips", data["prevention"], 
                               bg_color="#0f766e",  # Dark teal
                               text_color="#ccfbf1",  # Very light teal
                               border_color="#14b8a6")
        
        # 7. WHEN TO SEE DOCTOR SECTION (NEW) - HIGH CONTRAST
        if data.get("when_to_see_doctor"):
            self.create_section("🚨 When to See a Doctor", data["when_to_see_doctor"], 
                               bg_color="#7c2d12",  # Dark orange/brown
                               text_color="#ffedd5",  # Very light orange
                               border_color="#f97316")
        
        # 8. POSSIBLE COMPLICATIONS SECTION (NEW) - HIGH CONTRAST
        if data.get("complications"):
            self.create_section("⚠️ Possible Complications", data["complications"], 
                               bg_color="#701a75",  # Dark magenta
                               text_color="#fae8ff",  # Very light magenta
                               border_color="#c026d3")
        
        # 9. OTHER POSSIBILITIES
        if data.get("all_predictions") and len(data["all_predictions"]) > 1:
            other_preds = []
            for pred in data["all_predictions"][1:]:  # Skip first (main prediction)
                other_preds.append(f"{pred['disease']}: {pred['confidence']:.1f}%")
            
            if other_preds:
                self.create_section("📈 Other Possibilities", other_preds, 
                                   bg_color="#1e293b",  # Dark slate
                                   text_color="#f1f5f9",  # Very light slate
                                   border_color="#475569")
        
        # 10. RECOMMENDATIONS SECTION - HIGH CONTRAST
        rec_card = ctk.CTkFrame(
            self.results_scroll,
            corner_radius=18,
            fg_color=("#166534", "#14532d"),  # Dark green
            border_width=3,
            border_color="#22c55e"
        )
        rec_card.pack(fill="x", pady=15, padx=5)
        
        ctk.CTkLabel(
            rec_card,
            text="✅ RECOMMENDATION",
            font=("Segoe UI", 20, "bold"),
            text_color="#ffffff"  # WHITE on dark green
        ).pack(pady=(20, 10), padx=25, anchor="w")
        
        ctk.CTkLabel(
            rec_card,
            text=data["recommendation"],
            font=("Segoe UI", 16),
            text_color="#d1fae5",  # Light green
            wraplength=600,
            justify="left"
        ).pack(pady=(0, 20), padx=25, anchor="w")
        
        # 11. SPECIALIST INFO - HIGH CONTRAST
        spec_card = ctk.CTkFrame(
            self.results_scroll,
            corner_radius=18,
            fg_color=("#1e3a8a", "#1e40af"),  # Dark blue
            border_width=3,
            border_color="#3b82f6"
        )
        spec_card.pack(fill="x", pady=15, padx=5)
        
        ctk.CTkLabel(
            spec_card,
            text="👨‍⚕️ CONSULT SPECIALIST",
            font=("Segoe UI", 20, "bold"),
            text_color="#ffffff"  # WHITE on dark blue
        ).pack(pady=(20, 10), padx=25, anchor="w")
        
        ctk.CTkLabel(
            spec_card,
            text=f"Recommended: {data['specialist']}",
            font=("Segoe UI", 16),
            text_color="#dbeafe"  # Light blue
        ).pack(pady=(0, 20), padx=25, anchor="w")
        
        # ================== RECOMMENDED DOCTORS SECTION ==================
        doctors_section = self.create_doctors_section(data["predicted_disease"])
        if doctors_section:
            doctors_section.pack(fill="x", pady=15, padx=5)
        
        # ================== ACTION BUTTONS ==================
        action_frame = ctk.CTkFrame(self.results_scroll, fg_color="transparent")
        action_frame.pack(fill="x", pady=30)
    
        # Save Report Button
        ctk.CTkButton(
            action_frame,
            text="💾 Save Report with Image",
            width=250,
            height=50,
            corner_radius=15,
            font=("Segoe UI", 15, "bold"),
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=self.save_report
        ).pack(side="left", padx=10)
    
        # Consult Online Button
        ctk.CTkButton(
            action_frame,
            text="🩺 Find Specialist",
            width=250,
            height=50,
            corner_radius=15,
            font=("Segoe UI", 15, "bold"),
            fg_color="#10b981",
            hover_color="#059669",
            command=self.find_specialist
        ).pack(side="left", padx=10)
    
        # NEW: Chat Assistant Button (after analysis)
        chat_frame = ctk.CTkFrame(self.results_scroll, fg_color="transparent")
        chat_frame.pack(fill="x", pady=(20, 10))
    
        # Info text above the button
        ctk.CTkLabel(
            chat_frame,
            text="💬 Not satisfied with the results or have questions?",
            font=("Segoe UI", 14),
            text_color="#94a3b8",
            justify="center"
        ).pack(pady=(0, 5))
    
        ctk.CTkLabel(
            chat_frame,
            text="Chat with our Medical Assistant for more information",
            font=("Segoe UI", 12),
            text_color="#64748b",
            justify="center"
        ).pack(pady=(0, 10))
    
        ctk.CTkButton(
            chat_frame,
            text="🤖 Chat with Medical Assistant",
            width=300,
            height=45,
            corner_radius=12,
            font=("Segoe UI", 14, "bold"),
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            command=self.open_chat_assistant
        ).pack()
    
        # Update status
        self.status_indicator.configure(
            text="✓ Analysis complete - View results on the right",
            text_color="#10b981"
        )

        # Add this new method to DiagnosisView class:
    def open_chat_assistant(self):
        """Open chat assistant view"""
        # Navigate to Chat Assistant view
        self.app.navigate_to(ChatAssistantView, "Chat Assistant")
    
        # Pass the current diagnosis data to chat assistant if available
        if self.prediction_data:
            # You can pass data to chat assistant if needed
            pass

    def create_details_section(self, data):
        """Create details section with severity and timestamp - HIGH CONTRAST"""
        details_card = ctk.CTkFrame(
            self.results_scroll,
            corner_radius=18,
            fg_color=("#78350f", "#92400e"),  # Dark amber
            border_width=3,
            border_color="#f59e0b"
        )
        details_card.pack(fill="x", pady=15, padx=5)
        
        ctk.CTkLabel(
            details_card,
            text="📋 DETAILS",
            font=("Segoe UI", 20, "bold"),
            text_color="#ffffff"  # WHITE on dark amber
        ).pack(pady=(20, 15), padx=25, anchor="w")
        
        # Create grid for details
        details_grid = ctk.CTkFrame(details_card, fg_color="transparent")
        details_grid.pack(fill="x", padx=25, pady=(0, 20))
        
        # Severity
        ctk.CTkLabel(
            details_grid,
            text="Severity:",
            font=("Segoe UI", 15, "bold"),
            text_color="#fef3c7"  # Light amber
        ).grid(row=0, column=0, sticky="w", pady=8)
        ctk.CTkLabel(
            details_grid,
            text=data["severity"],
            font=("Segoe UI", 15),
            text_color="#fef3c7"  # Light amber
        ).grid(row=0, column=1, sticky="w", pady=8, padx=(15, 40))
        
        # Analysis Time
        ctk.CTkLabel(
            details_grid,
            text="Analyzed at:",
            font=("Segoe UI", 15, "bold"),
            text_color="#fef3c7"  # Light amber
        ).grid(row=0, column=2, sticky="w", pady=8)
        ctk.CTkLabel(
            details_grid,
            text=data["timestamp"],
            font=("Segoe UI", 15),
            text_color="#fef3c7"  # Light amber
        ).grid(row=0, column=3, sticky="w", pady=8, padx=15)

    def create_section(self, title, items, bg_color, text_color, border_color):
        """Create a section with list items - HIGH CONTRAST"""
        section_card = ctk.CTkFrame(
            self.results_scroll,
            corner_radius=18,
            fg_color=(bg_color, bg_color),  # Same for both modes
            border_width=3,
            border_color=border_color
        )
        section_card.pack(fill="x", pady=12, padx=5)
        
        ctk.CTkLabel(
            section_card,
            text=title.upper(),
            font=("Segoe UI", 18, "bold"),
            text_color=text_color  # High contrast text
        ).pack(pady=(18, 12), padx=25, anchor="w")
        
        # Create list items
        for item in items:
            item_frame = ctk.CTkFrame(section_card, fg_color="transparent")
            item_frame.pack(fill="x", padx=35, pady=6)
            
            ctk.CTkLabel(
                item_frame,
                text="•",
                font=("Segoe UI", 16),
                text_color=text_color  # High contrast
            ).pack(side="left", padx=(0, 12))
            
            ctk.CTkLabel(
                item_frame,
                text=item,
                font=("Segoe UI", 15),
                text_color=text_color,  # High contrast
                wraplength=550,
                justify="left"
            ).pack(side="left", fill="x", expand=True)

    def show_error(self, error_msg):
        """Display error message"""
        self.processing = False
        self.upload_btn.configure(state="normal", text="📤 Upload Skin Image")
        self.new_analysis_btn.configure(state="normal")
        
        self.clear_results()
        
        error_frame = ctk.CTkFrame(
            self.results_container,
            fg_color="transparent"
        )
        error_frame.pack(expand=True)
        
        ctk.CTkLabel(
            error_frame,
            text="❌",
            font=("Segoe UI", 48),
            text_color="#ef4444"
        ).pack(pady=20)
        
        ctk.CTkLabel(
            error_frame,
            text="ANALYSIS FAILED",
            font=("Segoe UI", 22, "bold"),
            text_color="#ef4444"  # Bright red
        ).pack(pady=10)
        
        ctk.CTkLabel(
            error_frame,
            text=error_msg[:100],
            font=("Segoe UI", 14),
            text_color="#fca5a5",  # Light red
            wraplength=400
        ).pack(pady=10)
        
        ctk.CTkButton(
            error_frame,
            text="Try Again",
            width=150,
            height=40,
            corner_radius=12,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=lambda: self.start_analysis(self.image_path)
        ).pack(pady=20)
        
        self.status_indicator.configure(
            text="❌ Analysis failed - Please try again",
            text_color="#ef4444"
        )

    def create_doctors_section(self, disease_name):
        """Create section with recommended doctors for the disease"""
        try:
            from database import Database
            db = Database()
            
            # Get doctors for this disease
            doctors = db.get_doctors_by_disease(disease_name, limit=3)
            
            if not doctors:
                return None
            
            # Create doctors section
            doctors_card = ctk.CTkFrame(
                self.results_scroll,
                corner_radius=18,
                fg_color=("#0f766e", "#0d645d"),  # Teal background
                border_width=3,
                border_color="#14b8a6"
            )
            
            ctk.CTkLabel(
                doctors_card,
                text="👨‍⚕️ RECOMMENDED SPECIALISTS",
                font=("Segoe UI", 18, "bold"),
                text_color="#ffffff"
            ).pack(pady=(18, 12), padx=25, anchor="w")
            
            # Subtitle
            ctk.CTkLabel(
                doctors_card,
                text=f"Top doctors for {disease_name}",
                font=("Segoe UI", 14),
                text_color="#ccfbf1"
            ).pack(pady=(0, 15), padx=25, anchor="w")
            
            # Create doctor cards
            for i, doctor in enumerate(doctors):
                self.create_doctor_card(doctors_card, doctor, i)
            
            return doctors_card
            
        except Exception as e:
            print(f"Error creating doctors section: {e}")
            return None
    
    def create_doctor_card(self, parent, doctor, index):
        """Create individual doctor card"""
        card_color = "#0d645d" if index % 2 == 0 else "#0b554f"
        
        doc_card = ctk.CTkFrame(
            parent,
            corner_radius=12,
            fg_color=card_color,
            border_width=1,
            border_color="#14b8a6"
        )
        doc_card.pack(fill="x", padx=25, pady=6)
        
        # Doctor info grid
        info_frame = ctk.CTkFrame(doc_card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=10)
        
        # Left column - Basic info
        left_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)
        
        # Doctor name and specialization
        ctk.CTkLabel(
            left_frame,
            text=f"👨‍⚕️ {doctor['name']}",
            font=("Segoe UI", 15, "bold"),
            text_color="#ffffff"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            left_frame,
            text=f"📚 {doctor['specialization']}",
            font=("Segoe UI", 13),
            text_color="#a7f3d0"
        ).pack(anchor="w", pady=(2, 0))
        
        # Right column - Contact and details
        right_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="y")
        
        # Hospital and city
        ctk.CTkLabel(
            right_frame,
            text=f"🏥 {doctor['hospital']}, {doctor['city']}",
            font=("Segoe UI", 12),
            text_color="#ccfbf1"
        ).pack(anchor="e")
        
        # Experience and fee
        details_text = f"📅 {doctor['experience']}y exp • 💰 {doctor['fee']}"
        ctk.CTkLabel(
            right_frame,
            text=details_text,
            font=("Segoe UI", 11),
            text_color="#a7f3d0"
        ).pack(anchor="e", pady=(2, 0))
        
        # Availability and contact
        bottom_frame = ctk.CTkFrame(doc_card, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(
            bottom_frame,
            text=f"📞 {doctor['contact']} | 📅 {doctor['availability']}",
            font=("Segoe UI", 11),
            text_color="#5eead4"
        ).pack(anchor="w")

    def save_report(self):
        """Save the diagnosis report to database and generate PDF"""
        if not self.prediction_data:
            MessageModal(self.app.root, "Error", "No analysis data to save.", False)
            return
        
        if not self.app.current_user:
            MessageModal(
                self.app.root, 
                "Login Required", 
                "Please login to save reports.", 
                False
            )
            return
        
        try:
            # Import PDF generator
            from pdf_generator import pdf_generator
            from database import Database
            
            # Get user info
            user_id = self.app.current_user["user_id"]
            username = self.app.current_user["username"]
            
            # Get doctors for this disease
            db = Database()
            disease_name = self.prediction_data.get("predicted_disease", "Unknown")
            doctors = db.get_doctors_by_disease(disease_name, limit=3)
            
            # Create report data for PDF
            report_data = {
                "report_id": "TEMP",
                "username": username,
                "disease_name": disease_name,
                "confidence": self.prediction_data.get("confidence", 0),
                "severity": self.prediction_data.get("severity", "Unknown"),
                "description": self.prediction_data.get("description", ""),
                "symptoms": self.prediction_data.get("symptoms", []),
                "treatment": self.prediction_data.get("treatment", []),
                "causes": self.prediction_data.get("causes", []),
                "prevention": self.prediction_data.get("prevention", []),
                "when_to_see_doctor": self.prediction_data.get("when_to_see_doctor", []),
                "complications": self.prediction_data.get("complications", []),
                "recommendation": self.prediction_data.get("recommendation", ""),
                "specialist": self.prediction_data.get("specialist", "Dermatologist")
            }
            
            # Step 1: Save to database first to get report ID
            success, result = db.save_report(
                user_id=user_id,
                username=username,
                prediction_data=self.prediction_data,
                image_path=self.image_path if hasattr(self, 'image_path') else ""
            )
            
            if success:
                # Update report data with actual report_id
                report_data["report_id"] = result["report_id"]
                
                # Step 2: Generate PDF with correct report ID and doctors data
                # IMPORTANT: Pass the image_path parameter
                final_pdf_path, final_pdf_filename = pdf_generator.generate_report_pdf(
                    report_data=report_data, 
                    doctors_data=doctors,  # Pass doctors as named parameter
                    output_filename=result["pdf_filename"],
                    image_path=self.image_path if hasattr(self, 'image_path') and self.image_path else None
                )
                
                # Show success message
                MessageModal(
                    self.app.root,
                    "✅ Report Saved Successfully",
                    f"✓ PDF generated with uploaded image\n✓ Report can be viewed in Reports Section\n✓ Saved as: {final_pdf_filename}",
                    True
                )
                
                # Refresh ReportsView if it's active
                if hasattr(self.app, 'active_view_name') and self.app.active_view_name == "Reports":
                    self.app.refresh_active_view()
                    
            else:
                MessageModal(
                    self.app.root,
                    "❌ Save Failed",
                    f"Error saving report:\n{result}",
                    False
                )
                
        except ImportError as e:
            MessageModal(
                self.app.root,
                "❌ PDF Generation Error",
                f"Required library missing!\n\n"
                f"Error: {str(e)}\n\n"
                "Please install required packages:\n"
                "pip install reportlab Pillow",
                False
            )
        except Exception as e:
            error_msg = str(e)
            MessageModal(
                self.app.root,
                "❌ Unexpected Error",
                f"Error saving report:\n{error_msg[:100]}...",
                False
            )
            print(f"Error in save_report: {e}")

    def find_specialist(self):
        """Open browser to find specialists"""
        if self.prediction_data:
            disease = self.prediction_data["predicted_disease"]
            search_url = f"https://www.google.com/search?q={disease.replace(' ', '+')}+dermatologist+near+me"
            webbrowser.open(search_url)



# Helper function to run the application
def create_app():
    """Create and run the application"""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("DiagnoSight AI - Skin Disease Diagnosis")
    root.geometry("1400x800")
    
    # Create app instance (simplified)
    class App:
        def __init__(self, root):
            self.root = root
    
    app = App(root)
    
    # Create diagnosis view
    diagnosis_view = DiagnosisView(root, app)
    
    root.mainloop()


import threading
import json
import requests
from enum import Enum
import os


import random
import customtkinter as ctk

class ChatAssistantView:
    def __init__(self, parent, app):
        self.app = app
        self.parent = parent
        self.conversation_state = "initial"  # Track conversation state
        self.current_disease = None
        self.user_info = {
            "age": None,
            "gender": None,
            "symptoms": [],
            "duration": None,
            "severity": None
        }

        # Main transparent frame
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.pack(fill="both", expand=True)

        # ---------- HERO HEADER ----------
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(30, 20), padx=40)

        ctk.CTkLabel(
            header_frame,
            text="🤖 Medical Diagnosis Assistant",
            font=("Segoe UI", 36, "bold"),
            text_color="#0ea5e9"
        ).pack(side="left")

        ctk.CTkLabel(
            header_frame,
            text="Rule-based medical consultation for dermatological conditions",
            font=("Segoe UI", 16),
            text_color="#78909c"
        ).pack(side="left", padx=(20, 0))

        # Clear Chat Button (top-right)
        clear_btn = ctk.CTkButton(
            header_frame,
            text="🗑️ Clear Chat",
            width=120,
            height=35,
            corner_radius=15,
            font=("Segoe UI", 12),
            fg_color="#475569",
            hover_color="#64748b",
            command=self.reset_chat
        )
        clear_btn.pack(side="right", padx=(0, 10))

        # Back to Diagnosis Button
        back_btn = ctk.CTkButton(
            header_frame,
            text="🔙 Back to Diagnosis",
            width=150,
            height=35,
            corner_radius=15,
            font=("Segoe UI", 12),
            fg_color="#0ea5e9",
            hover_color="#38bdf8",
            command=lambda: self.app.navigate_to(DiagnosisView, "Diagnosis")
        )
        back_btn.pack(side="right")

        # ---------- CHAT CONTAINER ----------
        chat_outer = ctk.CTkFrame(
            self.frame,
            corner_radius=24,
            fg_color=("#17253a", "#1e2d42"),
            border_width=2,
            border_color="#0ea5e9"
        )
        chat_outer.pack(padx=40, pady=(0, 20), fill="both", expand=True)

        # Scrollable chat area
        self.chat_container = ctk.CTkScrollableFrame(
            chat_outer,
            fg_color="transparent",
            scrollbar_button_color="#0ea5e9",
            scrollbar_button_hover_color="#38bdf8"
        )
        self.chat_container.pack(fill="both", expand=True, padx=20, pady=20)

        # ---------- INITIAL WELCOME ----------
        self.add_bot_message(self.get_welcome_message())

        # ---------- INPUT AREA ----------
        input_outer = ctk.CTkFrame(
            self.frame,
            fg_color=("#17253a", "#1e2d42"),
            corner_radius=24,
            border_width=2,
            border_color="#0ea5e9"
        )
        input_outer.pack(padx=40, pady=(0, 40), fill="x")

        input_frame = ctk.CTkFrame(input_outer, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=20)

        self.user_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your message or select an option...",
            height=56,
            font=("Segoe UI", 15),
            corner_radius=20,
            fg_color="#0f1f38",
            border_color="#0ea5e9",
            border_width=2,
            text_color="#e6f7fa"
        )
        self.user_input.pack(side="left", fill="x", expand=True, padx=(0, 15))

        self.send_btn = ctk.CTkButton(
            input_frame,
            text="Send →",
            width=140,
            height=56,
            corner_radius=20,
            font=("Segoe UI Semibold", 15),
            fg_color="#0ea5e9",
            hover_color="#38bdf8",
            command=self.send_message
        )
        self.send_btn.pack(side="right")

        # Enter key support
        self.user_input.bind("<Return>", lambda e: self.send_message())

        # ---------- QUICK ACTION BUTTONS ----------
        self.create_quick_buttons()

    def create_quick_buttons(self):
        """Create quick action buttons for common queries"""
        button_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        button_frame.pack(padx=40, pady=(0, 20), fill="x")

        buttons = [
            ("🏥 Main Diseases", lambda: self.show_disease_menu()),
            ("🤒 Describe Symptoms", lambda: self.prompt_for_symptoms()),
            ("🩺 Quick Diagnosis", lambda: self.quick_diagnosis()),
            ("📋 View Options", lambda: self.show_options_menu()),
            ("❓ Help", lambda: self.show_help()),
            ("🔄 Reset Chat", lambda: self.reset_chat())
        ]

        for i, (text, command) in enumerate(buttons):
            btn = ctk.CTkButton(
                button_frame,
                text=text,
                height=40,
                corner_radius=15,
                font=("Segoe UI", 12),
                fg_color="#1e2d42",
                hover_color="#2d3b53",
                border_color="#0ea5e9",
                border_width=1,
                command=command
            )
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
        
        # Configure equal column weights
        for i in range(len(buttons)):
            button_frame.grid_columnconfigure(i, weight=1)

    # ================== RULE-BASED RESPONSE SYSTEM ==================
    
    def get_welcome_message(self):
        """Return a random welcome message"""
        welcomes = [
            "👋 Welcome! I'm your AI Medical Assistant specializing in dermatological conditions.\n\nI can help you understand symptoms, provide information about skin conditions, and guide you through self-assessment for:\n• Eczema/Atopic Dermatitis\n• Melanoma\n• Basal Cell Carcinoma\n• Melanocytic Nevi (Moles)\n• Psoriasis\n• Seborrheic Keratosis\n\nHow can I assist you today?",
            
            "🩺 Hello! I'm here to provide information about common skin conditions.\n\nPlease remember: I'm an AI assistant for educational purposes only. Always consult a healthcare professional for medical advice.\n\nYou can ask about symptoms, get information about specific conditions, or describe what you're experiencing.",
            
            "🌟 Welcome to Medical Chat Assistant!\n\nI specialize in dermatology and can provide information about various skin conditions including eczema, melanoma, psoriasis, and more.\n\nType 'help' to see all available options or describe your symptoms to begin.",
            
            "💫 Hello there! I'm your dermatology information assistant.\n\nI can help you understand skin conditions, recognize symptoms, and provide general guidance.\n\nWhat would you like to know about today?",
            
            "👨‍⚕️ Welcome! I'm designed to provide educational information about dermatological conditions.\n\nYou can:\n1. Describe your symptoms\n2. Ask about specific diseases\n3. Get self-care tips\n4. Learn about prevention\n\nHow may I help you?"
        ]
        return random.choice(welcomes)

    def send_message(self):
        """Process user input and generate rule-based response"""
        text = self.user_input.get().strip()
        if not text:
            return

        self.user_input.delete(0, "end")
        self.add_user_message(text)
        
        # Disable input during processing
        self.user_input.configure(state="disabled")
        self.send_btn.configure(state="disabled", text="Processing...")
        
        # Process after delay
        self.frame.after(800, lambda: self.process_message(text))

    def process_message(self, text):
        """Main message processing logic"""
        response = self.generate_response(text.lower())
        self.add_bot_message(response)
        
        # Re-enable input
        self.user_input.configure(state="normal")
        self.send_btn.configure(state="normal", text="Send →")

    def generate_response(self, text):
        """Generate rule-based response based on input"""
        # General greetings
        if any(word in text for word in ["hello", "hi", "hey", "greetings"]):
            return random.choice([
                "Hello! How can I assist you with dermatological concerns today?",
                "Hi there! Ready to discuss skin health?",
                "Greetings! I'm here to help with skin condition information."
            ])
        
        # Help request
        if "help" in text:
            return self.show_help()
        
        # Disease-specific queries
        disease_responses = self.get_disease_response(text)
        if disease_responses:
            return disease_responses
        
        # Symptom analysis
        if any(word in text for word in ["symptom", "feel", "experience", "itch", "rash", "pain", "burn", "spot"]):
            return self.analyze_symptoms(text)
        
        # Treatment questions
        if any(word in text for word in ["treatment", "cure", "medicine", "cream", "ointment", "therapy"]):
            return self.get_treatment_info(text)
        
        # Prevention questions
        if any(word in text for word in ["prevent", "avoid", "stop", "protection"]):
            return self.get_prevention_info(text)
        
        # About the assistant
        if any(word in text for word in ["who are you", "what are you", "purpose", "function"]):
            return "I'm a rule-based medical assistant specializing in dermatology. I provide educational information about skin conditions based on established medical knowledge. I cannot replace a doctor's diagnosis."
        
        # Thank you responses
        if any(word in text for word in ["thank", "thanks", "appreciate"]):
            return random.choice([
                "You're welcome! I'm glad I could help. Is there anything else you'd like to know?",
                "My pleasure! Feel free to ask more questions.",
                "You're welcome! Stay informed about your skin health."
            ])
        
        # Goodbye
        if any(word in text for word in ["bye", "goodbye", "exit", "quit"]):
            return "Thank you for chatting! Remember to consult a healthcare professional for any medical concerns. Have a great day!"
        
        # Default response with suggestions
        return self.get_random_suggestion(text)

    def get_disease_response(self, text):
        """Generate disease-specific responses"""
        diseases = {
            "eczema": {
                "name": "Eczema/Atopic Dermatitis",
                "symptoms": ["itching", "redness", "dry skin", "scaling", "inflammation", "cracking"],
                "common_areas": ["hands", "inner elbows", "back of knees", "face"],
                "triggers": ["stress", "allergens", "dry weather", "irritants"],
                "description": "A chronic condition causing inflamed, itchy, and cracked skin."
            },
            "melanoma": {
                "name": "Melanoma",
                "symptoms": ["changing mole", "asymmetrical shape", "irregular borders", "color variation", "diameter >6mm", "evolving"],
                "warning_signs": ["ABCDE rule: Asymmetry, Border, Color, Diameter, Evolution"],
                "risk_factors": ["sun exposure", "fair skin", "family history", "many moles"],
                "description": "The most serious type of skin cancer that develops in melanocytes."
            },
            "basal cell carcinoma": {
                "name": "Basal Cell Carcinoma",
                "symptoms": ["pearly bump", "pink growth", "bleeding sore", "scar-like area"],
                "common_locations": ["sun-exposed areas", "face", "ears", "neck"],
                "characteristics": ["slow-growing", "rarely spreads", "most common skin cancer"],
                "description": "A type of skin cancer that begins in basal cells."
            },
            "psoriasis": {
                "name": "Psoriasis",
                "symptoms": ["red patches", "silvery scales", "dry skin", "itching", "burning", "thickened nails"],
                "types": ["plaque", "guttate", "inverse", "pustular", "erythrodermic"],
                "triggers": ["stress", "infection", "cold weather", "medications"],
                "description": "An autoimmune condition causing rapid skin cell buildup."
            },
            "seborrheic keratosis": {
                "name": "Seborrheic Keratosis",
                "symptoms": ["waxy bump", "stuck-on appearance", "brown/black color", "multiple lesions"],
                "characteristics": ["benign", "non-cancerous", "common in older adults", "cosmetic concern"],
                "appearance": ["waxy", "scaly", "slightly raised", "varied colors"],
                "description": "Common noncancerous skin growths in older adults."
            },
            "mole": {
                "name": "Melanocytic Nevi (Moles)",
                "characteristics": ["round/oval", "uniform color", "clear borders", "<6mm diameter"],
                "types": ["congenital", "acquired", "atypical"],
                "monitoring": ["regular checks", "ABCDE assessment", "photographic tracking"],
                "description": "Common skin growths that develop when pigment cells grow in clusters."
            }
        }
        
        for disease_key, info in diseases.items():
            if disease_key in text or info["name"].lower() in text:
                response = f"**{info['name']}**\n\n"
                response += f"{info['description']}\n\n"
                response += f"**Common Symptoms:** {', '.join(info['symptoms'][:4])}\n"
                if 'common_areas' in info:
                    response += f"**Common Areas:** {', '.join(info['common_areas'])}\n"
                response += f"\n**Key Information:**\n"
                for key, value in info.items():
                    if key not in ['name', 'description', 'symptoms', 'common_areas']:
                        if isinstance(value, list):
                            response += f"• {key.title()}: {', '.join(value[:3])}\n"
                        else:
                            response += f"• {key.title()}: {value}\n"
                
                response += "\n⚠️ **Note:** This is informational only. Consult a dermatologist for proper diagnosis."
                return response
        
        return None

    def analyze_symptoms(self, text):
        """Analyze user-described symptoms"""
        symptom_keywords = {
            "itch": "Itching could indicate eczema, allergies, or dry skin.",
            "rash": "Rashes can be caused by eczema, psoriasis, contact dermatitis, or infections.",
            "red": "Redness may suggest inflammation, eczema, psoriasis, or allergic reactions.",
            "bump": "Bumps could be moles, skin tags, basal cell carcinoma, or cysts.",
            "scale": "Scaling often occurs in psoriasis, eczema, or fungal infections.",
            "pain": "Painful lesions should be evaluated by a doctor immediately.",
            "bleed": "Bleeding moles or sores require medical attention.",
            "change": "Changing moles should be checked for melanoma risk.",
            "dry": "Dry skin is common in eczema, especially in cold weather.",
            "flake": "Flaking can indicate seborrheic dermatitis or psoriasis."
        }
        
        detected_symptoms = []
        advice = []
        
        for keyword, message in symptom_keywords.items():
            if keyword in text:
                detected_symptoms.append(keyword)
                advice.append(message)
        
        if detected_symptoms:
            response = f"Based on your description of {', '.join(detected_symptoms)}:\n\n"
            response += "\n".join(advice[:3])
            response += "\n\n**Recommendations:**\n"
            response += "1. Keep a symptom diary\n"
            response += "2. Avoid scratching or irritating the area\n"
            response += "3. Use gentle, fragrance-free skincare products\n"
            response += "4. Schedule a dermatology appointment if symptoms persist\n"
            response += "\nWould you like information about any specific condition?"
        else:
            response = "I understand you're describing symptoms. Could you provide more details about:\n• Location of the issue\n• Duration of symptoms\n• Any triggers or patterns\n• Previous skin conditions"
        
        return response

    def get_treatment_info(self, text):
        """Provide treatment information"""
        treatments = {
            "eczema": "Moisturizers, topical corticosteroids, antihistamines, avoiding triggers.",
            "melanoma": "Surgical excision, Mohs surgery, immunotherapy, targeted therapy.",
            "basal": "Surgical removal, Mohs surgery, cryotherapy, topical treatments.",
            "psoriasis": "Topical treatments, phototherapy, systemic medications, biologics.",
            "keratosis": "Cryotherapy, curettage, laser therapy, electrocautery.",
            "mole": "Observation, surgical removal if suspicious, cosmetic removal.",
            "general": "Always consult a dermatologist for personalized treatment plans."
        }
        
        for key, treatment in treatments.items():
            if key in text:
                return f"**Treatment options may include:**\n\n{treatment}\n\n⚠️ **Important:** Treatment must be prescribed by a qualified dermatologist based on your specific case."
        
        return "Treatment depends on the specific diagnosis. Could you specify which condition you're asking about?"

    def get_prevention_info(self, text):
        """Provide prevention information"""
        prevention_tips = [
            "**Sun Protection:** Use SPF 30+ sunscreen daily, wear protective clothing, avoid peak sun hours.",
            "**Skin Checks:** Perform monthly self-exams, note any changes in moles or spots.",
            "**Healthy Habits:** Stay hydrated, eat antioxidant-rich foods, avoid smoking.",
            "**Skincare:** Use gentle products, moisturize regularly, avoid harsh chemicals.",
            "**Professional Care:** Get annual skin checks, especially if high-risk.",
            "**Early Detection:** Know the ABCDEs of melanoma and act on changes promptly."
        ]
        
        return "**Skin Cancer Prevention Tips:**\n\n" + "\n\n".join(random.sample(prevention_tips, 3)) + "\n\nRegular dermatologist visits are crucial for prevention."

    def get_random_suggestion(self, text):
        """Provide random helpful suggestions when query is not recognized"""
        suggestions = [
            "I can help you with information about specific skin conditions. Try asking about:\n• Eczema symptoms and treatment\n• How to check moles for melanoma\n• Differences between psoriasis and eczema\n• When to see a dermatologist",
            
            "You might find these topics helpful:\n• The ABCDE rule for melanoma detection\n• Daily skincare routines for sensitive skin\n• Common triggers for eczema flare-ups\n• Prevention tips for skin cancer",
            
            "Consider exploring:\n1. Self-examination techniques\n2. Understanding different types of skin lesions\n3. When to seek medical attention\n4. Lifestyle factors affecting skin health",
            
            "I specialize in:\n✅ Disease information\n✅ Symptom guidance\n✅ Prevention tips\n✅ General dermatology education\n\nWhat would you like to know more about?",
            
            "Here are some useful queries:\n\"Tell me about melanoma warning signs\"\n\"What does eczema look like?\"\n\"How often should I check my moles?\"\n\"What's the difference between BCC and melanoma?\""
        ]
        
        return random.choice(suggestions)

    def show_disease_menu(self):
        """Display disease selection menu"""
        self.add_user_message("Show me main diseases")
        response = "**🏥 Main Dermatological Conditions:**\n\n"
        diseases = [
            "1. **Eczema/Atopic Dermatitis** - Chronic itchy, inflamed skin",
            "2. **Melanoma** - Serious skin cancer from pigment cells",
            "3. **Basal Cell Carcinoma** - Most common skin cancer type",
            "4. **Melanocytic Nevi** - Common moles (benign)",
            "5. **Psoriasis** - Autoimmune condition with scaly patches",
            "6. **Seborrheic Keratosis** - Benign waxy growths in adults"
        ]
        response += "\n\n".join(diseases)
        response += "\n\n**Ask about any disease by name or number!**"
        self.add_bot_message(response)

    def prompt_for_symptoms(self):
        """Prompt user to describe symptoms"""
        self.add_user_message("I want to describe symptoms")
        response = "**Please describe your symptoms in detail:**\n\n"
        response += "• What does the skin look like? (red, scaly, bumpy, etc.)\n"
        response += "• Where is it located on your body?\n"
        response += "• How long have you had it?\n"
        response += "• What makes it better or worse?\n"
        response += "• Any itching, pain, or bleeding?\n\n"
        response += "**Example:** \"I have itchy red patches on my elbows for 2 weeks\""
        self.add_bot_message(response)

    def quick_diagnosis(self):
        """Provide quick self-assessment guidance"""
        self.add_user_message("Quick diagnosis")
        response = "**Quick Self-Assessment Guide:**\n\n"
        response += "🔴 **URGENT - See doctor immediately if:**\n"
        response += "• New/changing mole (ABCDE rule)\n"
        response += "• Sore that doesn't heal\n"
        response += "• Sudden widespread rash with fever\n\n"
        
        response += "🟡 **Schedule appointment if:**\n"
        response += "• Persistent itchy rash >2 weeks\n"
        response += "• Suspicious skin growth\n"
        response += "• Worsening skin condition\n\n"
        
        response += "🟢 **Self-care for:**\n"
        response += "• Mild dry skin\n"
        response += "• Occasional irritation\n"
        response += "• Known eczema flare-ups\n\n"
        
        response += "⚠️ **Remember:** I provide guidance only. See a dermatologist for diagnosis."
        self.add_bot_message(response)

    def show_options_menu(self):
        """Display all available options"""
        self.add_user_message("Show options")
        response = "**📋 Available Options:**\n\n"
        
        categories = [
            "**DIAGNOSIS INFO:**",
            "• Describe symptoms for analysis",
            "• Get disease-specific information",
            "• Learn about warning signs",
            "• Understand risk factors",
            "",
            "**TREATMENT GUIDANCE:**",
            "• General treatment approaches",
            "• Self-care recommendations",
            "• When to seek medical help",
            "• Prevention strategies",
            "",
            "**EDUCATION:**",
            "• ABCDE rule for melanoma",
            "• Difference between skin conditions",
            "• Skin self-examination guide",
            "• Sun protection tips",
            "",
            "**TOOLS:**",
            "• Quick symptom checker",
            "• Disease comparison",
            "• FAQ about skin health",
            "• Preparation for doctor visits"
        ]
        
        response += "\n".join(categories)
        response += "\n\n**Just type what you need help with!**"
        self.add_bot_message(response)

    def show_help(self):
        """Display help information"""
        response = "**❓ How to Use This Assistant:**\n\n"
        response += "**1. Ask About Specific Conditions:**\n"
        response += "• \"Tell me about melanoma\"\n• \"What is eczema?\"\n• \"Psoriasis symptoms\"\n\n"
        
        response += "**2. Describe Symptoms:**\n"
        response += "• \"I have an itchy red rash\"\n• \"My mole changed color\"\n• \"Dry scaly patches on elbows\"\n\n"
        
        response += "**3. Get Practical Advice:**\n"
        response += "• \"How to check moles?\"\n• \"Prevent skin cancer\"\n• \"Eczema home care\"\n\n"
        
        response += "**4. Quick Commands:**\n"
        response += "• Click any quick button above\n• Type 'options' for menu\n• Type 'reset' to start over\n\n"
        
        response += "**⚠️ Important:** I provide educational information only.\nAlways consult healthcare professionals for medical advice."
        return response

    def reset_chat(self):
        """Reset the chat conversation"""
        # Clear chat container
        for widget in self.chat_container.winfo_children():
            widget.destroy()
        
        # Reset state
        self.conversation_state = "initial"
        self.current_disease = None
        self.user_info = {
            "age": None,
            "gender": None,
            "symptoms": [],
            "duration": None,
            "severity": None
        }
        
        # Add new welcome message
        self.add_bot_message(self.get_welcome_message())

    # ================== MESSAGE DISPLAY FUNCTIONS ==================
    def add_user_message(self, text):
        """Display user message"""
        bubble_frame = ctk.CTkFrame(self.chat_container, fg_color="transparent")
        bubble_frame.pack(anchor="e", pady=10, padx=20)

        bubble = ctk.CTkFrame(
            bubble_frame,
            fg_color="#0ea5e9",
            corner_radius=24,
            border_width=1,
            border_color="#38bdf8"
        )
        bubble.pack(anchor="e")

        ctk.CTkLabel(
            bubble,
            text=text,
            wraplength=500,
            justify="right",
            text_color="#020817",
            font=("Segoe UI", 15),
            padx=20,
            pady=14
        ).pack()

    def add_bot_message(self, text):
        """Display bot message"""
        bubble_frame = ctk.CTkFrame(self.chat_container, fg_color="transparent")
        bubble_frame.pack(anchor="w", pady=10, padx=20)

        bubble = ctk.CTkFrame(
            bubble_frame,
            fg_color="#1e2d42",
            corner_radius=24,
            border_width=2,
            border_color="#0ea5e9"
        )
        bubble.pack(anchor="w")

        ctk.CTkLabel(
            bubble,
            text=text,
            wraplength=500,
            justify="left",
            text_color="#e6f7fa",
            font=("Segoe UI", 15),
            padx=20,
            pady=14
        ).pack()
        
        # Auto-scroll to bottom
        self.chat_container._parent_canvas.yview_moveto(1.0)

import customtkinter as ctk
from database import Database


class WebInsightsView:
    def __init__(self, parent, app):
        self.app = app
        self.db = Database()  # Create database instance directly

        # Main background - deeper dark for depth
        self.frame = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=0)
        self.frame.pack(fill="both", expand=True)

        # ---------- TITLE SECTION ----------
        self.title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.title_frame.pack(fill="x", padx=30, pady=(30, 10))
        
        ctk.CTkLabel(
            self.title_frame,
            text="Doctor Recommendations",
            font=("Segoe UI Bold", 28),
            text_color="#f8fafc"
        ).pack(side="left")

        # Subtitle with count
        self.subtitle_label = ctk.CTkLabel(
            self.title_frame,
            text="Loading doctors...",
            font=("Segoe UI", 14),
            text_color="#94a3b8"
        )
        self.subtitle_label.pack(side="right", padx=10)

        # ---------- TABLE CONTAINER ----------
        self.table_container = ctk.CTkFrame(
            self.frame,
            fg_color="#1e293b",
            corner_radius=16,
            border_width=1,
            border_color="#334155"
        )
        self.table_container.pack(fill="both", expand=True, padx=25, pady=(10, 25))

        # ---------- SCROLLABLE AREA ----------
        self.scroll = ctk.CTkScrollableFrame(
            self.table_container,
            fg_color="transparent",
            scrollbar_button_color="#475569",
            scrollbar_button_hover_color="#94a3b8"
        )
        self.scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Create table header immediately
        self.create_table_header()
        self.load_doctors()

    def create_table_header(self):
        # Header with a distinct darker background
        header = ctk.CTkFrame(self.scroll, fg_color="#0f172a", height=45, corner_radius=8)
        header.pack(fill="x", pady=(5, 10), padx=5)
        header.pack_propagate(False)

        # Use a grid inside the header frame
        for i in range(9):
            header.grid_columnconfigure(i, weight=1)

        headers = [
            "Doctor Name", "Specialization", "Disease",
            "Hospital", "City", "Exp",
            "Contact", "Fee", "Availability"
        ]
        
        # Fixed widths in pixels for perfect alignment
        widths = [200, 160, 140, 200, 120, 80, 140, 100, 130]

        for i, (text, w) in enumerate(zip(headers, widths)):
            lbl = ctk.CTkLabel(
                header,
                text=text.upper(),
                width=w,
                font=("Segoe UI Bold", 11),
                text_color="#94a3b8",
                anchor="w"
            )
            lbl.grid(row=0, column=i, padx=12, pady=10, sticky="w")

    def load_doctors(self):
        try:
            doctors = self.db.get_all_doctors()
            
            if not doctors:
                self.show_empty_state()
                self.subtitle_label.configure(text="No doctors found in database")
                return

            # Update subtitle with count
            self.subtitle_label.configure(text=f"Found {len(doctors)} doctors")
            
            for doc in doctors:
                self.create_doctor_row(doc)
                
        except Exception as e:
            self.show_error_state(str(e))
            self.subtitle_label.configure(text="Database error")

    def show_empty_state(self):
        # Clear any existing content except header
        for widget in self.scroll.winfo_children()[1:]:  # Keep header
            widget.destroy()
        
        empty_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        empty_frame.pack(fill="both", expand=True, pady=100)

        ctk.CTkLabel(
            empty_frame,
            text="👨‍⚕️",
            font=("Segoe UI", 80)
        ).pack(pady=(0, 20))

        ctk.CTkLabel(
            empty_frame,
            text="No Doctor Records Found",
            font=("Segoe UI Semibold", 24),
            text_color="#94a3b8"
        ).pack()

        ctk.CTkLabel(
            empty_frame,
            text="The doctors database is currently empty.\nPlease check your database connection.",
            font=("Segoe UI", 16),
            text_color="#64748b",
            justify="center"
        ).pack(pady=(20, 0))

    def show_error_state(self, error_msg):
        # Clear any existing content except header
        for widget in self.scroll.winfo_children()[1:]:  # Keep header
            widget.destroy()
        
        error_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        error_frame.pack(fill="both", expand=True, pady=100)

        ctk.CTkLabel(
            error_frame,
            text="⚠️",
            font=("Segoe UI", 80)
        ).pack(pady=(0, 20))

        ctk.CTkLabel(
            error_frame,
            text="Database Connection Error",
            font=("Segoe UI Semibold", 24),
            text_color="#ef4444"
        ).pack()

        ctk.CTkLabel(
            error_frame,
            text=f"Error: {error_msg[:100]}...",
            font=("Segoe UI", 14),
            text_color="#f87171",
            justify="center"
        ).pack(pady=(20, 10))

        ctk.CTkButton(
            error_frame,
            text="Retry",
            width=200,
            height=40,
            fg_color="#0ea5e9",
            hover_color="#38bdf8",
            command=self.refresh_data
        ).pack(pady=20)

    def refresh_data(self):
        # Clear current content except header
        for widget in self.scroll.winfo_children()[1:]:  # Keep header
            widget.destroy()
        
        # Reload data
        self.load_doctors()

    def create_doctor_row(self, doc):
        # Row Container
        row = ctk.CTkFrame(
            self.scroll,
            fg_color="#334155",
            height=50,
            corner_radius=10
        )
        row.pack(fill="x", pady=4, padx=5)
        row.pack_propagate(False)

        # Use grid inside row frame
        for i in range(9):
            row.grid_columnconfigure(i, weight=1)

        # Hover Effects
        row.bind("<Enter>", lambda e, r=row: r.configure(fg_color="#475569"))
        row.bind("<Leave>", lambda e, r=row: r.configure(fg_color="#334155"))

        values = [
            doc["name"] if doc["name"] else "N/A",
            doc["specialization"] if doc["specialization"] else "N/A",
            doc["disease"] if doc["disease"] else "N/A",
            doc["hospital"] if doc["hospital"] else "N/A",
            doc["city"] if doc["city"] else "N/A",
            f'{doc["experience"]}y' if doc["experience"] else "N/A",
            doc["contact"] if doc["contact"] else "N/A",
            f'Rs {doc["fee"]}' if doc["fee"] else "Rs N/A",
            doc["availability"] if doc["availability"] else "N/A"
        ]
        
        # Same fixed widths as header
        widths = [200, 160, 140, 200, 120, 80, 140, 100, 130]

        for i, (val, w) in enumerate(zip(values, widths)):
            # Color logic: Make the Name and Fee stand out
            t_color = "#ffffff" if i == 0 else "#cbd5e1"
            f_style = ("Segoe UI Semibold", 13) if i == 0 else ("Segoe UI", 12)
            
            lbl = ctk.CTkLabel(
                row,
                text=val,
                width=w,
                font=f_style,
                text_color=t_color,
                anchor="w"
            )
            lbl.grid(row=0, column=i, padx=12, pady=10, sticky="w")
            
            # Ensure clicking the label doesn't break hover
            lbl.bind("<Enter>", lambda e, r=row: r.configure(fg_color="#475569"))
            lbl.bind("<Leave>", lambda e, r=row: r.configure(fg_color="#334155"))         
                        
class ReportsView:
    def __init__(self, parent, app):
        self.app = app
        self.parent = parent
        self.current_user = app.current_user
        
        # Main frame
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.pack(fill="both", expand=True, padx=40, pady=30)

        # ---------- HEADER ----------
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(
            header_frame,
            text="📋 Medical Reports",
            font=("Segoe UI", 36, "bold"),
            text_color="#0ea5e9"
        ).pack(side="left")
        
        # Reports count badge
        self.reports_count_label = ctk.CTkLabel(
            header_frame,
            text="Loading...",
            font=("Segoe UI", 14),
            text_color="#94a3b8"
        )
        self.reports_count_label.pack(side="right", padx=(0, 20))
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            width=100,
            height=35,
            corner_radius=10,
            font=("Segoe UI", 12),
            fg_color="#475569",
            hover_color="#64748b",
            command=self.load_reports
        )
        refresh_btn.pack(side="right")
        
        # Subtitle
        subtitle = "View and manage your AI diagnosis reports"
        if not self.current_user:
            subtitle = "Please login to view your saved reports"
        
        ctk.CTkLabel(
            self.frame,
            text=subtitle,
            font=("Segoe UI", 16),
            text_color="#b0bec5"
        ).pack(anchor="w", pady=(0, 30))
        
        # ---------- REPORTS CONTAINER ----------
        self.reports_container = ctk.CTkScrollableFrame(
            self.frame,
            fg_color="transparent",
            scrollbar_button_color="#0ea5e9",
            scrollbar_button_hover_color="#38bdf8"
        )
        self.reports_container.pack(fill="both", expand=True)
        
        # Load reports or show login prompt
        if self.current_user:
            self.load_reports()
        else:
            self.show_login_prompt()

    def show_login_prompt(self):
        """Show login prompt for guest users"""
        prompt_frame = ctk.CTkFrame(self.reports_container, fg_color="transparent")
        prompt_frame.pack(fill="both", expand=True, pady=100)
        
        ctk.CTkLabel(
            prompt_frame,
            text="🔒",
            font=("Segoe UI", 80),
            text_color="#94a3b8"
        ).pack(pady=(0, 30))
        
        ctk.CTkLabel(
            prompt_frame,
            text="Login Required",
            font=("Segoe UI Semibold", 28),
            text_color="#94a3b8"
        ).pack()
        
        ctk.CTkLabel(
            prompt_frame,
            text="You need to be logged in to view your saved reports.\n"
                 "All your diagnosis reports will be saved securely and\n"
                 "you can access them anytime.",
            font=("Segoe UI", 16),
            text_color="#64748b",
            justify="center"
        ).pack(pady=(20, 40))
        
        ctk.CTkButton(
            prompt_frame,
            text="👤 Login Now",
            width=200,
            height=50,
            corner_radius=15,
            font=("Segoe UI Semibold", 16),
            fg_color="#0ea5e9",
            hover_color="#38bdf8",
            command=lambda: LoginWindow(self.app.root, self.app.on_user_login)
        ).pack()

    def load_reports(self):
        """Load reports from database"""
        if not self.current_user:
            return
        
        # Clear existing content
        for widget in self.reports_container.winfo_children():
            widget.destroy()
        
        try:
            from database import Database
            db = Database()
            success, reports = db.get_user_reports(self.current_user["user_id"])
            
            if not success:
                self.show_error_state(reports)
                self.reports_count_label.configure(text="Error loading reports")
                return
            
            # Update count
            count = len(reports)
            self.reports_count_label.configure(
                text=f"{count} report{'s' if count != 1 else ''}"
            )
            
            if count == 0:
                self.show_empty_state()
                return
            
            # Create reports table header
            self.create_table_header()
            
            # Add each report as a row
            for i, report in enumerate(reports):
                self.create_report_row(report, i % 2 == 0)
                
        except Exception as e:
            self.show_error_state(str(e))
            self.reports_count_label.configure(text="Error")

    def create_table_header(self):
        """Create table header for reports"""
        header_frame = ctk.CTkFrame(
            self.reports_container,
            fg_color="#1e293b",
            corner_radius=10,
            height=50
        )
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Use grid layout for header
        header_frame.grid_columnconfigure(0, weight=1, minsize=80)   # ID
        header_frame.grid_columnconfigure(1, weight=2, minsize=200)  # Disease
        header_frame.grid_columnconfigure(2, weight=1, minsize=100)  # Confidence
        header_frame.grid_columnconfigure(3, weight=1, minsize=100)  # Severity
        header_frame.grid_columnconfigure(4, weight=2, minsize=180)  # Date
        header_frame.grid_columnconfigure(5, weight=1, minsize=120)  # Actions
        
        headers = ["Report ID", "Disease", "Confidence", "Severity", "Date", "Actions"]
        
        for col, text in enumerate(headers):
            ctk.CTkLabel(
                header_frame,
                text=text,
                font=("Segoe UI Bold", 13),
                text_color="#94a3b8"
            ).grid(row=0, column=col, padx=15, pady=15, sticky="w")

    def create_report_row(self, report, is_even):
        """Create a table row for a report"""
        row_color = "#1e293b" if is_even else "#0f172a"
        
        row_frame = ctk.CTkFrame(
            self.reports_container,
            fg_color=row_color,
            corner_radius=8,
            height=60
        )
        row_frame.pack(fill="x", pady=4)
        row_frame.pack_propagate(False)
        
        # Configure grid columns (same as header)
        row_frame.grid_columnconfigure(0, weight=1, minsize=80)   # ID
        row_frame.grid_columnconfigure(1, weight=2, minsize=200)  # Disease
        row_frame.grid_columnconfigure(2, weight=1, minsize=100)  # Confidence
        row_frame.grid_columnconfigure(3, weight=1, minsize=100)  # Severity
        row_frame.grid_columnconfigure(4, weight=2, minsize=180)  # Date
        row_frame.grid_columnconfigure(5, weight=1, minsize=120)  # Actions
        
        # Report ID
        ctk.CTkLabel(
            row_frame,
            text=f"#{report['report_id']}",
            font=("Segoe UI Semibold", 13),
            text_color="#0ea5e9"
        ).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # Disease name
        ctk.CTkLabel(
            row_frame,
            text=report['disease_name'],
            font=("Segoe UI", 13),
            text_color="#ffffff"
        ).grid(row=0, column=1, padx=15, pady=15, sticky="w")
        
        # Confidence with color coding
        confidence = report['confidence']
        if confidence >= 75:
            conf_color = "#22c55e"
        elif confidence >= 50:
            conf_color = "#f59e0b"
        else:
            conf_color = "#ef4444"
        
        ctk.CTkLabel(
            row_frame,
            text=f"{confidence:.1f}%",
            font=("Segoe UI Semibold", 13),
            text_color=conf_color
        ).grid(row=0, column=2, padx=15, pady=15, sticky="w")
        
        # Severity
        severity_color = {
            "Low": "#22c55e",
            "Moderate": "#f59e0b",
            "High": "#ef4444"
        }.get(report['severity'].split()[0].lower(), "#94a3b8")
        
        ctk.CTkLabel(
            row_frame,
            text=report['severity'],
            font=("Segoe UI", 12),
            text_color=severity_color
        ).grid(row=0, column=3, padx=15, pady=15, sticky="w")
        
        # Date
        date_str = report['analysis_date']
        if len(date_str) > 10:
            date_str = date_str[:10]  # Show only date part
        
        ctk.CTkLabel(
            row_frame,
            text=date_str,
            font=("Segoe UI", 12),
            text_color="#94a3b8"
        ).grid(row=0, column=4, padx=15, pady=15, sticky="w")
        
        # Action buttons frame
        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=5, padx=15, pady=15, sticky="e")
        
        # View button
        ctk.CTkButton(
            action_frame,
            text="👁️ View",
            width=70,
            height=32,
            corner_radius=8,
            font=("Segoe UI", 11),
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=lambda r=report: self.view_report_details(r['report_id'])
        ).pack(side="left", padx=(0, 5))
        
        # Download button
        ctk.CTkButton(
            action_frame,
            text="📥 PDF",
            width=70,
            height=32,
            corner_radius=8,
            font=("Segoe UI", 11),
            fg_color="#10b981",
            hover_color="#059669",
            command=lambda r=report: self.download_pdf(r['report_id'], r.get('pdf_filename', ''))
        ).pack(side="left", padx=(0, 5))
        
        # Delete button
        ctk.CTkButton(
            action_frame,
            text="🗑️",
            width=40,
            height=32,
            corner_radius=8,
            font=("Segoe UI", 14),
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=lambda r=report: self.delete_report(r['report_id'])
        ).pack(side="left")

    def show_empty_state(self):
        """Show empty state when no reports"""
        empty_frame = ctk.CTkFrame(self.reports_container, fg_color="transparent")
        empty_frame.pack(fill="both", expand=True, pady=100)
        
        ctk.CTkLabel(
            empty_frame,
            text="📄",
            font=("Segoe UI", 80),
            text_color="#94a3b8"
        ).pack(pady=(0, 20))
        
        ctk.CTkLabel(
            empty_frame,
            text="No Reports Yet",
            font=("Segoe UI Semibold", 28),
            text_color="#94a3b8"
        ).pack()
        
        ctk.CTkLabel(
            empty_frame,
            text="You haven't saved any diagnosis reports yet.\n"
                 "Go to the Diagnosis section, upload an image,\n"
                 "and save your first report!",
            font=("Segoe UI", 16),
            text_color="#64748b",
            justify="center"
        ).pack(pady=(20, 40))
        
        ctk.CTkButton(
            empty_frame,
            text="🔍 Go to Diagnosis",
            width=200,
            height=50,
            corner_radius=15,
            font=("Segoe UI Semibold", 16),
            fg_color="#0ea5e9",
            hover_color="#38bdf8",
            command=lambda: self.app.navigate_to(DiagnosisView, "Diagnosis")
        ).pack()

    def show_error_state(self, error_msg):
        """Show error state"""
        error_frame = ctk.CTkFrame(self.reports_container, fg_color="transparent")
        error_frame.pack(fill="both", expand=True, pady=100)
        
        ctk.CTkLabel(
            error_frame,
            text="⚠️",
            font=("Segoe UI", 80),
            text_color="#ef4444"
        ).pack(pady=(0, 20))
        
        ctk.CTkLabel(
            error_frame,
            text="Failed to Load Reports",
            font=("Segoe UI Semibold", 28),
            text_color="#ef4444"
        ).pack()
        
        ctk.CTkLabel(
            error_frame,
            text=f"Error: {error_msg[:100]}...",
            font=("Segoe UI", 14),
            text_color="#f87171",
            justify="center"
        ).pack(pady=(20, 10))
        
        ctk.CTkButton(
            error_frame,
            text="🔄 Retry",
            width=150,
            height=45,
            corner_radius=12,
            font=("Segoe UI Semibold", 14),
            fg_color="#0ea5e9",
            hover_color="#38bdf8",
            command=self.load_reports
        ).pack(pady=20)

    def view_report_details(self, report_id):
        """View detailed report in a modal"""
        try:
            from database import Database
            db = Database()
            success, report = db.get_report_details(report_id)
            
            if not success:
                MessageModal(self.app.root, "Error", report, False)
                return
            
            # Create modal for detailed view
            modal = BaseModal(self.app.root, 800, 700)
            modal.win.configure(fg_color="#121212")
            
            # Main content frame
            content_frame = ctk.CTkFrame(
                modal.win,
                corner_radius=20,
                fg_color="#1e1e1e",
                border_width=1,
                border_color="#333333"
            )
            content_frame.pack(padx=30, pady=30, fill="both", expand=True)
            
            # Scrollable content
            scroll_frame = ctk.CTkScrollableFrame(
                content_frame,
                fg_color="transparent"
            )
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Header
            ctk.CTkLabel(
                scroll_frame,
                text=f"Report #{report_id}",
                font=("Segoe UI", 28, "bold"),
                text_color="#00c2cb"
            ).pack(anchor="w", pady=(0, 10))
            
            # Diagnosis card
            diag_card = ctk.CTkFrame(
                scroll_frame,
                corner_radius=15,
                fg_color="#252525",
                border_width=2,
                border_color="#00c2cb"
            )
            diag_card.pack(fill="x", pady=(0, 20))
            
            # Confidence badge
            confidence = report.get("confidence", 0)
            if confidence >= 75:
                conf_color = "#22c55e"
                conf_text = "High Confidence"
            elif confidence >= 50:
                conf_color = "#f59e0b"
                conf_text = "Moderate Confidence"
            else:
                conf_color = "#ef4444"
                conf_text = "Low Confidence"
            
            ctk.CTkLabel(
                diag_card,
                text=f"{confidence:.1f}% ({conf_text})",
                font=("Segoe UI", 16, "bold"),
                text_color=conf_color,
                fg_color="#1a1a1a",
                corner_radius=20,
                padx=20,
                pady=8
            ).pack(anchor="e", padx=20, pady=(15, 5))
            
            ctk.CTkLabel(
                diag_card,
                text=report.get("disease_name", "Unknown").upper(),
                font=("Segoe UI", 32, "bold"),
                text_color="#ffffff"
            ).pack(pady=(0, 10), padx=20, anchor="w")
            
            ctk.CTkLabel(
                diag_card,
                text=report.get("description", ""),
                font=("Segoe UI", 14),
                text_color="#b0b0b0",
                wraplength=700,
                justify="left"
            ).pack(pady=(0, 20), padx=20, anchor="w")
            
            # Details grid
            details_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            details_frame.pack(fill="x", pady=(0, 20))
            
            # Left column
            left_col = ctk.CTkFrame(details_frame, fg_color="transparent")
            left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
            # Right column
            right_col = ctk.CTkFrame(details_frame, fg_color="transparent")
            right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))
            
            # Create detail sections
            sections = {
                "Severity": report.get("severity", "Unknown"),
                "Specialist": report.get("specialist", "Dermatologist"),
                "Analysis Date": report.get("analysis_date", ""),
                "Image": report.get("image_filename", "No image")
            }
            
            for i, (label, value) in enumerate(sections.items()):
                col = left_col if i % 2 == 0 else right_col
                self.create_detail_item(col, label, value)
            
            # Create list sections
            list_sections = [
                ("Symptoms", report.get("symptoms", []), "#0c4a6e"),
                ("Treatment", report.get("treatment", []), "#064e3b"),
                ("Causes", report.get("causes", []), "#4c1d95"),
                ("Prevention", report.get("prevention", []), "#0f766e"),
                ("When to See Doctor", report.get("when_to_see_doctor", []), "#7c2d12"),
                ("Complications", report.get("complications", []), "#701a75")
            ]
            
            for title, items, color in list_sections:
                if items:
                    self.create_list_section(scroll_frame, title, items, color)
            
            # Recommendation
            rec_frame = ctk.CTkFrame(
                scroll_frame,
                corner_radius=15,
                fg_color="#166534",
                border_width=2,
                border_color="#22c55e"
            )
            rec_frame.pack(fill="x", pady=15)
            
            ctk.CTkLabel(
                rec_frame,
                text="✅ RECOMMENDATION",
                font=("Segoe UI", 16, "bold"),
                text_color="#ffffff"
            ).pack(anchor="w", padx=20, pady=(15, 5))
            
            ctk.CTkLabel(
                rec_frame,
                text=report.get("recommendation", ""),
                font=("Segoe UI", 14),
                text_color="#d1fae5",
                wraplength=700,
                justify="left"
            ).pack(anchor="w", padx=20, pady=(0, 15))
            
            # Action buttons
            action_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            action_frame.pack(fill="x", pady=30)
            
            ctk.CTkButton(
                action_frame,
                text="📥 Download PDF",
                width=180,
                height=45,
                corner_radius=12,
                font=("Segoe UI Semibold", 14),
                fg_color="#10b981",
                hover_color="#059669",
                command=lambda: self.download_pdf(report_id, report.get('pdf_filename', ''))
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                action_frame,
                text="🗑️ Delete Report",
                width=180,
                height=45,
                corner_radius=12,
                font=("Segoe UI Semibold", 14),
                fg_color="#ef4444",
                hover_color="#dc2626",
                command=lambda: self.delete_report(report_id)
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                action_frame,
                text="✕ Close",
                width=120,
                height=45,
                corner_radius=12,
                font=("Segoe UI Semibold", 14),
                fg_color="#475569",
                hover_color="#64748b",
                command=modal.win.destroy
            ).pack(side="right", padx=5)
            
        except Exception as e:
            MessageModal(self.app.root, "Error", f"Failed to load report: {str(e)[:100]}", False)

    def create_detail_item(self, parent, label, value):
        """Create a detail item in the grid"""
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            item_frame,
            text=f"{label}:",
            font=("Segoe UI", 13, "bold"),
            text_color="#94a3b8"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            item_frame,
            text=value,
            font=("Segoe UI", 14),
            text_color="#ffffff"
        ).pack(anchor="w", pady=(2, 0))

    def create_list_section(self, parent, title, items, bg_color):
        """Create a list section"""
        if not items:
            return
        
        section_card = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=bg_color,
            border_width=2,
            border_color=self.adjust_color(bg_color, 30)
        )
        section_card.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            section_card,
            text=title.upper(),
            font=("Segoe UI", 14, "bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        for item in items:
            item_frame = ctk.CTkFrame(section_card, fg_color="transparent")
            item_frame.pack(fill="x", padx=35, pady=4)
            
            ctk.CTkLabel(
                item_frame,
                text="•",
                font=("Segoe UI", 14),
                text_color="#ffffff"
            ).pack(side="left", padx=(0, 10))
            
            ctk.CTkLabel(
                item_frame,
                text=item,
                font=("Segoe UI", 13),
                text_color="#ffffff",
                wraplength=600,
                justify="left"
            ).pack(side="left", fill="x", expand=True)

    def adjust_color(self, hex_color, percent):
        """Adjust color brightness"""
        import colorsys
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        hls = colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        new_l = max(0, min(1, hls[1] + percent/100))
        new_rgb = colorsys.hls_to_rgb(hls[0], new_l, hls[2])
        return f'#{int(new_rgb[0]*255):02x}{int(new_rgb[1]*255):02x}{int(new_rgb[2]*255):02x}'

    def download_pdf(self, report_id, pdf_filename):
        """Download PDF report"""
        try:
            from database import Database
            import os
            
            db = Database()
            success, report = db.get_report_details(report_id)
            
            if not success:
                MessageModal(self.app.root, "Error", "Report not found", False)
                return
            
            # Find PDF file
            pdf_path = os.path.join(db.reports_dir, pdf_filename)
            
            if not os.path.exists(pdf_path):
                # Try to generate PDF on the fly
                from pdf_generator import pdf_generator
                pdf_path, _ = pdf_generator.generate_report_pdf(report)
            
            # Open file dialog for saving
            from tkinter import filedialog
            save_path = filedialog.asksaveasfilename(
                title="Save PDF Report",
                defaultextension=".pdf",
                initialfile=f"diagnosis_report_{report_id}.pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            
            if save_path:
                import shutil
                shutil.copy2(pdf_path, save_path)
                MessageModal(
                    self.app.root,
                    "Download Complete",
                    f"✅ PDF saved to:\n{save_path}",
                    True
                )
                
        except Exception as e:
            MessageModal(
                self.app.root,
                "Download Failed",
                f"❌ Error downloading PDF:\n{str(e)[:100]}",
                False
            )

    def delete_report(self, report_id):
        """Delete a report with confirmation"""
        def confirm_delete():
            try:
                from database import Database
                db = Database()
                success, message = db.delete_report(report_id)
                
                if success:
                    MessageModal(
                        self.app.root,
                        "Report Deleted",
                        f"✅ Report #{report_id} has been deleted.",
                        True
                    )
                    # Reload reports
                    self.load_reports()
                else:
                    MessageModal(self.app.root, "Delete Failed", message, False)
                
                confirm_modal.win.destroy()
            except Exception as e:
                MessageModal(
                    self.app.root,
                    "Error",
                    f"Failed to delete report: {str(e)}",
                    False
                )
        
        # Create confirmation modal
        confirm_modal = BaseModal(self.app.root, 400, 200)
        confirm_modal.win.configure(fg_color="#121212")
        
        card = ctk.CTkFrame(
            confirm_modal.win,
            corner_radius=20,
            fg_color="#1e1e1e",
            border_width=1,
            border_color="#333333"
        )
        card.pack(padx=30, pady=30, fill="both", expand=True)
        
        ctk.CTkLabel(
            card,
            text="🗑️ Delete Report",
            font=("Segoe UI", 22, "bold"),
            text_color="#ef4444"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            card,
            text=f"Are you sure you want to delete Report #{report_id}?\n\nThis action cannot be undone.",
            font=("Segoe UI", 14),
            text_color="#b0b0b0",
            justify="center"
        ).pack(pady=(0, 30))
        
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40)
        
        ctk.CTkButton(
            btn_frame,
            text="Delete",
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=confirm_delete
        ).pack(side="left", padx=10, expand=True)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color="#475569",
            hover_color="#64748b",
            command=confirm_modal.win.destroy
        ).pack(side="right", padx=10, expand=True)


class SettingsView:
    def __init__(self, parent, app):
        self.app = app
        self.parent = parent

        # Main container with scrollbar
        self.main_scroll = ctk.CTkScrollableFrame(
            parent, 
            fg_color="transparent",
            scrollbar_button_color="#0ea5e9",
            scrollbar_button_hover_color="#38bdf8"
        )
        self.main_scroll.pack(fill="both", expand=True)

        self.frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.frame.pack(fill="both", expand=True, padx=40, pady=30)

        # Title
        ctk.CTkLabel(
            self.frame,
            text="Settings",
            font=("Segoe UI", 40, "bold"),
            text_color="#0ea5e9"
        ).pack(anchor="w", pady=(20, 10))

        # Status
        status_text = f"Logged in as: {app.current_user['username']}" if app.current_user else "Guest Mode"
        ctk.CTkLabel(
            self.frame,
            text=status_text,
            font=("Segoe UI", 16),
            text_color="#b0bec5"
        ).pack(anchor="w", pady=(0, 40))

        # Main container
        sections_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        sections_frame.pack(fill="both", expand=True)

        # ================== ACCOUNT SETTINGS ==================
        account_card = ctk.CTkFrame(
            sections_frame,
            corner_radius=20,
            fg_color=("#17253a", "#1e2d42"),
            border_width=2,
            border_color="#0ea5e9"
        )
        account_card.pack(fill="x", pady=15)

        # Account title
        ctk.CTkLabel(
            account_card,
            text="Account Settings",
            font=("Segoe UI Semibold", 22),
            text_color="#0ea5e9"
        ).pack(anchor="w", padx=30, pady=(25, 20))

        # Account info
        account_info = [
            ("Username", app.current_user["username"] if app.current_user else "Guest"),
            ("Email", app.current_user["email"] if app.current_user else "Not logged in"),
            ("User ID", str(app.current_user["user_id"]) if app.current_user else "-"),
        ]

        for label, value in account_info:
            row = ctk.CTkFrame(account_card, fg_color="transparent")
            row.pack(fill="x", padx=30, pady=8)

            ctk.CTkLabel(
                row,
                text=f"{label}:",
                font=("Segoe UI", 14),
                text_color="#94a3b8",
                width=140,
                anchor="w"
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=value,
                font=("Segoe UI", 15, "bold"),
                text_color="#e6f7fa",
                anchor="w"
            ).pack(side="left")

        # Account buttons
        account_buttons_frame = ctk.CTkFrame(account_card, fg_color="transparent")
        account_buttons_frame.pack(fill="x", padx=30, pady=(20, 30))

        # Edit Profile button
        ctk.CTkButton(
            account_buttons_frame,
            text="✏️ Edit Profile",
            width=200,
            height=45,
            corner_radius=15,
            font=("Segoe UI Semibold", 14),
            fg_color="#0ea5e9",
            hover_color="#38bdf8",
            command=self.open_edit_profile_popup
        ).pack(side="left", padx=(0, 15))

        # Change Password button
        ctk.CTkButton(
            account_buttons_frame,
            text="🔐 Change Password",
            width=200,
            height=45,
            corner_radius=15,
            font=("Segoe UI Semibold", 14),
            fg_color="#10b981",
            hover_color="#34d399",
            command=self.open_change_password_popup
        ).pack(side="left")

        # ================== DANGER ZONE ==================
        danger_card = ctk.CTkFrame(
            sections_frame,
            corner_radius=20,
            fg_color=("#17253a", "#1e2d42"),
            border_width=2,
            border_color="#ef4444"
        )
        danger_card.pack(fill="x", pady=15)

        # Danger zone title
        ctk.CTkLabel(
            danger_card,
            text="⚠️ Danger Zone",
            font=("Segoe UI Semibold", 22),
            text_color="#ef4444"
        ).pack(anchor="w", padx=30, pady=(25, 20))

        # Danger zone info
        danger_info = [
            ("Account Status", "Active" if app.current_user else "Guest"),
            ("Warning", "These actions cannot be undone"),
        ]

        for label, value in danger_info:
            row = ctk.CTkFrame(danger_card, fg_color="transparent")
            row.pack(fill="x", padx=30, pady=8)

            ctk.CTkLabel(
                row,
                text=f"{label}:",
                font=("Segoe UI", 14),
                text_color="#94a3b8",
                width=140,
                anchor="w"
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=value,
                font=("Segoe UI", 15, "bold"),
                text_color="#fca5a5" if label == "Warning" else "#e6f7fa",
                anchor="w"
            ).pack(side="left")

        # Danger zone buttons
        danger_buttons_frame = ctk.CTkFrame(danger_card, fg_color="transparent")
        danger_buttons_frame.pack(fill="x", padx=30, pady=(20, 30))

        # Logout button
        ctk.CTkButton(
            danger_buttons_frame,
            text="🚪 Logout",
            width=180,
            height=45,
            corner_radius=15,
            font=("Segoe UI Semibold", 14),
            fg_color="#f59e0b",
            hover_color="#d97706",
            command=self.logout
        ).pack(side="left", padx=(0, 15))

        # Delete Account button
        ctk.CTkButton(
            danger_buttons_frame,
            text="🗑️ Delete Account",
            width=180,
            height=45,
            corner_radius=15,
            font=("Segoe UI Semibold", 14),
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self.delete_account
        ).pack(side="left")

    # =====================================================
    #                EDIT PROFILE
    # =====================================================
    def open_edit_profile_popup(self):
        """Edit username only (email cannot be changed for security)"""
        if not self.app.current_user:
            MessageModal(self.app.root, "Error", "You must be logged in to edit your profile.", False)
            return

        modal = BaseModal(self.app.root, 500, 420)
        modal.win.configure(fg_color="#121212")

        # Close button (X) in top-right
        close_btn = ctk.CTkButton(
            modal.win,
            text="✕",
            width=40,
            height=40,
            corner_radius=20,
            font=("Segoe UI Bold", 18),
            fg_color="transparent",
            hover_color="#333333",
            text_color="#aaaaaa",
            command=modal.win.destroy
        )
        close_btn.place(x=440, y=10)

        card = ctk.CTkFrame(
            modal.win,
            corner_radius=20,
            fg_color="#1e1e1e",
            border_width=1,
            border_color="#333333"
        )
        card.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(
            card,
            text="Edit Profile",
            font=("Segoe UI", 28, "bold"),
            text_color="#00c2cb"
        ).pack(pady=(20, 15))

        # Current info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkLabel(
            info_frame,
            text=f"Current: {self.app.current_user['username']}",
            font=("Segoe UI", 14),
            text_color="#94a3b8"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text=f"Email: {self.app.current_user['email']}",
            font=("Segoe UI", 12),
            text_color="#64748b"
        ).pack(anchor="w", pady=(5, 0))

        # Current password (for verification)
        current_pw = ctk.CTkEntry(
            card,
            placeholder_text="Current Password (for verification)",
            show="•",
            height=45,
            font=("Segoe UI", 14),
            fg_color="#252525",
            border_color="#00c2cb",
            border_width=2
        )
        current_pw.pack(pady=15, padx=30, fill="x")

        # New username
        new_username = ctk.CTkEntry(
            card,
            placeholder_text="New Username (3-20 characters)",
            height=45,
            font=("Segoe UI", 14),
            fg_color="#252525",
            border_color="#00c2cb",
            border_width=2
        )
        new_username.pack(pady=15, padx=30, fill="x")

        def save_username():
            password = current_pw.get().strip()
            username = new_username.get().strip()

            if not password:
                MessageModal(self.app.root, "Error", "Please enter your current password.", False)
                return
            
            if not username:
                MessageModal(self.app.root, "Error", "Please enter a new username.", False)
                return
            
            if len(username) < 3 or len(username) > 20:
                MessageModal(self.app.root, "Error", "Username must be 3-20 characters.", False)
                return
            
            # Verify password first
            from database import Database
            db = Database()
            success, result = db.verify_user(self.app.current_user["email"], password)
            
            if not success:
                MessageModal(self.app.root, "Error", "Incorrect password. Please try again.", False)
                return
            
            # Update username
            success, message = db.update_username(self.app.current_user["user_id"], username)
            
            if success:
                # Update app state
                self.app.current_user["username"] = username
                MessageModal(self.app.root, "Success", f"Username updated to: {username}", True)
                modal.win.destroy()
                # Refresh settings view
                self.app.navigate_to(SettingsView, "Settings")
            else:
                MessageModal(self.app.root, "Error", message, False)

        # Button frame
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="Update Username",
            height=45,
            font=("Segoe UI Semibold", 15),
            fg_color="#00c2cb",
            hover_color="#00a5ad",
            command=save_username
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            height=45,
            font=("Segoe UI Semibold", 15),
            fg_color="#475569",
            hover_color="#64748b",
            command=modal.win.destroy
        ).pack(side="right", fill="x", expand=True)

    # =====================================================
    #                CHANGE PASSWORD
    # =====================================================
    def open_change_password_popup(self):
        """Change password popup"""
        if not self.app.current_user:
            MessageModal(self.app.root, "Error", "You must be logged in to change password.", False)
            return

        modal = BaseModal(self.app.root, 500, 520)
        modal.win.configure(fg_color="#121212")

        # Close button (X) in top-right
        close_btn = ctk.CTkButton(
            modal.win,
            text="✕",
            width=40,
            height=40,
            corner_radius=20,
            font=("Segoe UI Bold", 18),
            fg_color="transparent",
            hover_color="#333333",
            text_color="#aaaaaa",
            command=modal.win.destroy
        )
        close_btn.place(x=440, y=10)

        card = ctk.CTkFrame(
            modal.win,
            corner_radius=20,
            fg_color="#1e1e1e",
            border_width=1,
            border_color="#333333"
        )
        card.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(
            card,
            text="Change Password",
            font=("Segoe UI", 28, "bold"),
            text_color="#00c2cb"
        ).pack(pady=(20, 25))

        # Current password
        current_pw = ctk.CTkEntry(
            card,
            placeholder_text="Current Password",
            show="•",
            height=45,
            font=("Segoe UI", 14),
            fg_color="#252525",
            border_color="#00c2cb",
            border_width=2
        )
        current_pw.pack(pady=10, padx=30, fill="x")

        # New password
        new_pw = ctk.CTkEntry(
            card,
            placeholder_text="New Password (min 8 characters)",
            show="•",
            height=45,
            font=("Segoe UI", 14),
            fg_color="#252525",
            border_color="#00c2cb",
            border_width=2
        )
        new_pw.pack(pady=10, padx=30, fill="x")

        # Confirm password
        confirm_pw = ctk.CTkEntry(
            card,
            placeholder_text="Confirm New Password",
            show="•",
            height=45,
            font=("Segoe UI", 14),
            fg_color="#252525",
            border_color="#00c2cb",
            border_width=2
        )
        confirm_pw.pack(pady=10, padx=30, fill="x")

        # Password requirements
        requirements = ctk.CTkFrame(card, fg_color="transparent")
        requirements.pack(fill="x", padx=30, pady=(10, 20))
        
        ctk.CTkLabel(
            requirements,
            text="Password Requirements:",
            font=("Segoe UI", 12, "bold"),
            text_color="#94a3b8"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            requirements,
            text="• Minimum 8 characters\n• Include letters and numbers\n• Avoid common passwords",
            font=("Segoe UI", 11),
            text_color="#64748b",
            justify="left"
        ).pack(anchor="w", pady=(5, 0))

        def update_password():
            current = current_pw.get().strip()
            new = new_pw.get().strip()
            confirm = confirm_pw.get().strip()

            # Validation
            if not current or not new or not confirm:
                MessageModal(self.app.root, "Error", "All fields are required.", False)
                return
            
            if new != confirm:
                MessageModal(self.app.root, "Error", "New passwords do not match.", False)
                return
            
            if len(new) < 8:
                MessageModal(self.app.root, "Error", "Password must be at least 8 characters.", False)
                return
            
            # Verify current password
            from database import Database
            db = Database()
            success, result = db.verify_user(self.app.current_user["email"], current)
            
            if not success:
                MessageModal(self.app.root, "Error", "Current password is incorrect.", False)
                return
            
            # Update password
            success, message = db.update_password(self.app.current_user["user_id"], new)
            
            if success:
                MessageModal(self.app.root, "Success", "Password updated successfully!", True)
                modal.win.destroy()
            else:
                MessageModal(self.app.root, "Error", message, False)

        # Button frame
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="Update Password",
            height=45,
            font=("Segoe UI Semibold", 15),
            fg_color="#00c2cb",
            hover_color="#00a5ad",
            command=update_password
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            height=45,
            font=("Segoe UI Semibold", 15),
            fg_color="#475569",
            hover_color="#64748b",
            command=modal.win.destroy
        ).pack(side="right", fill="x", expand=True)

    # =====================================================
    #                DELETE ACCOUNT
    # =====================================================
    def delete_account(self):
        """Delete account with confirmation"""
        if not self.app.current_user:
            MessageModal(self.app.root, "Error", "You must be logged in to delete your account.", False)
            return

        # First confirmation
        modal = BaseModal(self.app.root, 500, 350)
        modal.win.configure(fg_color="#121212")

        # Close button (X) in top-right
        close_btn = ctk.CTkButton(
            modal.win,
            text="✕",
            width=40,
            height=40,
            corner_radius=20,
            font=("Segoe UI Bold", 18),
            fg_color="transparent",
            hover_color="#333333",
            text_color="#aaaaaa",
            command=modal.win.destroy
        )
        close_btn.place(x=440, y=10)

        card = ctk.CTkFrame(
            modal.win,
            corner_radius=20,
            fg_color="#1e1e1e",
            border_width=1,
            border_color="#ef4444"
        )
        card.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(
            card,
            text="⚠️ DELETE ACCOUNT",
            font=("Segoe UI", 26, "bold"),
            text_color="#ef4444"
        ).pack(pady=(20, 15))

        # Warning message
        warning_text = "This will permanently:\n• Delete your account\n• Remove all saved reports\n• Erase all your data\n\nThis cannot be undone!"
        ctk.CTkLabel(
            card,
            text=warning_text,
            font=("Segoe UI", 14),
            text_color="#fca5a5",
            justify="center"
        ).pack(pady=(0, 25), padx=20)

        def proceed_to_password():
            modal.win.destroy()
            self.verify_password_for_deletion()
        
        # Button frame
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Continue to Password",
            height=45,
            font=("Segoe UI Semibold", 15),
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=proceed_to_password
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            height=45,
            font=("Segoe UI Semibold", 15),
            fg_color="#475569",
            hover_color="#64748b",
            command=modal.win.destroy
        ).pack(side="right", fill="x", expand=True)

    def verify_password_for_deletion(self):
        """Password verification for account deletion"""
        modal = BaseModal(self.app.root, 500, 320)
        modal.win.configure(fg_color="#121212")

        # Close button (X) in top-right
        close_btn = ctk.CTkButton(
            modal.win,
            text="✕",
            width=40,
            height=40,
            corner_radius=20,
            font=("Segoe UI Bold", 18),
            fg_color="transparent",
            hover_color="#333333",
            text_color="#aaaaaa",
            command=modal.win.destroy
        )
        close_btn.place(x=440, y=10)

        card = ctk.CTkFrame(
            modal.win,
            corner_radius=20,
            fg_color="#1e1e1e",
            border_width=1,
            border_color="#ef4444"
        )
        card.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(
            card,
            text="Confirm Password",
            font=("Segoe UI", 24, "bold"),
            text_color="#ef4444"
        ).pack(pady=(20, 15))

        ctk.CTkLabel(
            card,
            text="Enter your password to confirm deletion",
            font=("Segoe UI", 14),
            text_color="#fca5a5",
            justify="center"
        ).pack(pady=(0, 20))

        # Password entry
        password_entry = ctk.CTkEntry(
            card,
            placeholder_text="Enter your password",
            show="•",
            height=45,
            font=("Segoe UI", 14),
            fg_color="#252525",
            border_color="#ef4444",
            border_width=2
        )
        password_entry.pack(pady=15, padx=30, fill="x")

        def verify_and_delete():
            password = password_entry.get().strip()
            
            if not password:
                MessageModal(self.app.root, "Error", "Please enter your password.", False)
                return
            
            # Verify password
            from database import Database
            db = Database()
            success, result = db.verify_user(self.app.current_user["email"], password)
            
            if not success:
                MessageModal(self.app.root, "Error", "Incorrect password.", False)
                return
            
            # Delete account
            success, message = db.delete_account(self.app.current_user["user_id"])
            if success:
                MessageModal(self.app.root, "Account Deleted", "Your account has been permanently deleted.", True)
                modal.win.destroy()
                # Logout user
                self.app.logout()
            else:
                MessageModal(self.app.root, "Error", message, False)

        # Button frame
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=15)
        
        ctk.CTkButton(
            btn_frame,
            text="Delete Account",
            height=45,
            font=("Segoe UI Semibold", 15),
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=verify_and_delete
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            height=45,
            font=("Segoe UI Semibold", 15),
            fg_color="#475569",
            hover_color="#64748b",
            command=modal.win.destroy
        ).pack(side="right", fill="x", expand=True)

    # =====================================================
    #                LOGOUT
    # =====================================================
    def logout(self):
        """Logout user"""
        if not self.app.current_user:
            MessageModal(self.app.root, "Already Logged Out", "You are already in guest mode.", True)
            return
        
        modal = BaseModal(self.app.root, 450, 220)
        modal.win.configure(fg_color="#121212")

        # Close button (X) in top-right
        close_btn = ctk.CTkButton(
            modal.win,
            text="✕",
            width=40,
            height=40,
            corner_radius=20,
            font=("Segoe UI Bold", 18),
            fg_color="transparent",
            hover_color="#333333",
            text_color="#aaaaaa",
            command=modal.win.destroy
        )
        close_btn.place(x=390, y=10)

        card = ctk.CTkFrame(
            modal.win,
            corner_radius=20,
            fg_color="#1e1e1e",
            border_width=1,
            border_color="#333333"
        )
        card.pack(padx=30, pady=30, fill="both", expand=True)
        
        ctk.CTkLabel(
            card,
            text="Logout Confirmation",
            font=("Segoe UI", 22, "bold"),
            text_color="#f59e0b"
        ).pack(pady=(10, 15))
        
        ctk.CTkLabel(
            card,
            text="Are you sure you want to logout?",
            font=("Segoe UI", 14),
            text_color="#94a3b8",
            justify="center"
        ).pack(pady=(0, 20))
        
        def confirm_logout():
            self.app.logout()
            modal.win.destroy()
            MessageModal(self.app.root, "Logged Out", "You have been successfully logged out.", True)
        
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)
        
        ctk.CTkButton(
            btn_frame,
            text="Logout",
            height=40,
            font=("Segoe UI Semibold", 14),
            fg_color="#f59e0b",
            hover_color="#d97706",
            command=confirm_logout
        ).pack(side="left", padx=5, expand=True)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            height=40,
            font=("Segoe UI Semibold", 14),
            fg_color="#475569",
            hover_color="#64748b",
            command=modal.win.destroy
        ).pack(side="right", padx=5, expand=True)
        
                
if __name__ == "__main__":
    SplashScreen(on_finish_callback=launch_main_app)