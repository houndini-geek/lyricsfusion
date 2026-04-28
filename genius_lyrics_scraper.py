import customtkinter as ctk
import threading
import queue
from tkinter import messagebox
import pyperclip
import os
import webbrowser

# Assuming your backend files remain the same
from genius_scraper import GeniusScraper
from genius_scraper_db import LyricsDatabase
from main_queue import message 
from utils import SettingsManager

# --- Trending UI Palette (Tailwind Inspired) ---
APP_NAME = "LyricsFusion PRO"
BG_APP = "#09090b"        # Zinc 950 (Deepest background)
BG_SURFACE = "#18181b"    # Zinc 900 (Main floating card)
BG_ELEVATED = "#27272a"   # Zinc 800 (Inputs, secondary cards)
ACCENT_COLOR = "#7c3aed"  # Vibrant Tech Violet
ACCENT_HOVER = "#6d28d9"  # Deep Violet
TEXT_PRIMARY = "#f4f4f5"  # Zinc 50
TEXT_MUTED = "#a1a1aa"    # Zinc 400
SUCCESS_COLOR = "#10b981" # Emerald 500
ERROR_COLOR = "#ef4444"   # Red 500
BORDER_COLOR = "#3f3f46"  # Zinc 700

class SidebarButton(ctk.CTkButton):
    def __init__(self, master, text, command, **kwargs):
        super().__init__(
            master, 
            text=text, 
            command=command, 
            anchor="w", 
            height=45,
            corner_radius=10,
            fg_color="transparent",
            text_color=TEXT_MUTED,
            hover_color=BG_ELEVATED,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            **kwargs
        )

class SongCard(ctk.CTkFrame):
    def __init__(self, master, data, on_view, on_delete, **kwargs): 
        super().__init__(master, fg_color=BG_ELEVATED, corner_radius=12, border_width=1, border_color=BORDER_COLOR, **kwargs)
        
        self.data = data
        
        # Info Container
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=20, pady=15)
        
        ctk.CTkLabel(
            info_frame, 
            text=data.get('song_title', 'Unknown'), 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        ).pack(fill="x")
        
        ctk.CTkLabel(
            info_frame, 
            text=data.get('artist', 'Unknown'), 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", pady=(2, 0))
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="right", padx=20)
        
        # Web Link Button
        if data.get('genius_url'):
            ctk.CTkButton(
                btn_frame, text="🌐", width=35, height=32, corner_radius=8,
                fg_color=BG_SURFACE, hover_color=BORDER_COLOR,
                command=lambda: webbrowser.open(data['genius_url'])
            ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame, text="View", width=70, height=32, corner_radius=8,
            fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: on_view(data)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame, text="Drop", width=70, height=32, corner_radius=8,
            fg_color="transparent", border_width=1, border_color=ERROR_COLOR, text_color=ERROR_COLOR, hover_color="#451a1e",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: on_delete(data)
        ).pack(side="left", padx=2)

class LyricsScraperPRO(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1200x800")
        self.configure(fg_color=BG_APP) 
        ctk.set_appearance_mode("dark")

        # Set Icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "lyricsfusion.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)# type: ignore
        except Exception:
            pass
        
        # Initialize Settings
        self.settings = SettingsManager.load_settings()
        
        # Initialize Core with settings
        db_path = self.settings.get("db_path", "lyrics.db")
        self.db = LyricsDatabase(db_path)
        self.scraper = None
        self.current_lyrics_data = None
        
        # Settings State
        self.auto_save_var = ctk.BooleanVar(value=self.settings.get("auto_save", False))
        self.high_fidelity_var = ctk.BooleanVar(value=self.settings.get("high_fidelity", True))
        self.db_path_var = ctk.StringVar(value=os.path.abspath(db_path))
        
        # Add traces to save on change
        self.auto_save_var.trace_add("write", lambda *args: self._save_app_settings())
        self.high_fidelity_var.trace_add("write", lambda *args: self._save_app_settings())

        # Layout Config
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._build_sidebar()
        self._build_main_container()
        
        self.show_search_view()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=260, fg_color=BG_APP, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=20)
        self.sidebar.grid_rowconfigure(5, weight=1)
        
        # Sleek App Identity
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, pady=(20, 40), padx=20, sticky="w")
        
        ctk.CTkLabel(brand_frame, text="LYRICS", font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(brand_frame, text="FUSION", font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"), text_color=ACCENT_COLOR).pack(anchor="w", pady=(0, 0))
        
        # Navigation
        self.btn_search = SidebarButton(self.sidebar, text="✦  Scrape Studio", command=self.show_search_view)
        self.btn_search.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        
        self.btn_history = SidebarButton(self.sidebar, text="📚  My Library", command=self.show_history_view)
        self.btn_history.grid(row=2, column=0, sticky="ew", padx=15, pady=5)
        
        self.btn_stats = SidebarButton(self.sidebar, text="📊  Insights", command=self.show_stats_view)
        self.btn_stats.grid(row=3, column=0, sticky="ew", padx=15, pady=5)

        self.btn_setting = SidebarButton(self.sidebar, text="⚙️ Settings", command=self.show_settings_view)
        self.btn_setting.grid(row=4,column=0,sticky="ew", padx=15, pady=5)

    def _build_main_container(self):
        # The Floating Surface
        self.main_container = ctk.CTkFrame(self, fg_color=BG_SURFACE, corner_radius=20, border_width=1, border_color=BORDER_COLOR)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        
    def clear_main_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def _reset_sidebar_buttons(self):
        # FIX: Added self.btn_setting to the reset list to prevent it staying highlighted
        self.btn_search.configure(fg_color="transparent", text_color=TEXT_MUTED)
        self.btn_history.configure(fg_color="transparent", text_color=TEXT_MUTED)
        self.btn_stats.configure(fg_color="transparent", text_color=TEXT_MUTED)
        self.btn_setting.configure(fg_color="transparent", text_color=TEXT_MUTED)

    def show_search_view(self):
        self.clear_main_container()
        self._reset_sidebar_buttons()
        self.btn_search.configure(fg_color=BG_ELEVATED, text_color=TEXT_PRIMARY)
       
        
        self.main_container.grid_rowconfigure(3, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 20))
        ctk.CTkLabel(header_frame, text="Scrape Studio", font=ctk.CTkFont(size=28, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(header_frame, text="Locate and extract high-fidelity lyrics directly from the source.", font=ctk.CTkFont(size=14), text_color=TEXT_MUTED).pack(anchor="w")

        # Input Card
        input_card = ctk.CTkFrame(self.main_container, fg_color=BG_ELEVATED, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        input_card.grid(row=1, column=0, sticky="ew", padx=40, pady=10)
        
        input_inner = ctk.CTkFrame(input_card, fg_color="transparent")
        input_inner.pack(pady=25, padx=25, fill="x")
        input_inner.grid_columnconfigure((0, 1), weight=1)

        # Artist Entry
        artist_frame = ctk.CTkFrame(input_inner, fg_color="transparent")
        artist_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(artist_frame, text="Artist", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 5))
        self.artist_entry = ctk.CTkEntry(artist_frame, placeholder_text="e.g. The Weeknd", height=45, corner_radius=8, border_color=BORDER_COLOR, fg_color=BG_SURFACE)
        self.artist_entry.pack(fill="x")

        # Song Entry
        song_frame = ctk.CTkFrame(input_inner, fg_color="transparent")
        song_frame.grid(row=0, column=1, sticky="ew", padx=(10, 20))
        ctk.CTkLabel(song_frame, text="Track Title", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 5))
        self.song_entry = ctk.CTkEntry(song_frame, placeholder_text="e.g. Starboy", height=45, corner_radius=8, border_color=BORDER_COLOR, fg_color=BG_SURFACE)
        self.song_entry.pack(fill="x")

        # Action Button
        self.scrape_btn = ctk.CTkButton(
            input_inner, text="Extract Lyrics", height=45, width=160, corner_radius=8,
            fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, font=ctk.CTkFont(size=14, weight="bold"),
            command=self._start_scrape
        )
     
        self.cancel_btn = ctk.CTkButton(
            input_inner, text="Cancel", height=45, width=160, corner_radius=8,
            fg_color=ERROR_COLOR,  font=ctk.CTkFont(size=14, weight="bold"),
            command=self._cancel_scrape
        )

        self.scrape_btn.grid(row=0, column=2, sticky="s")
      

        # Status Tracker
        self.status_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(10, 0))
        self.status_label = ctk.CTkLabel(self.status_frame, text="System Idle", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.status_label.pack(side="left")
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, width=150, height=4, progress_color=ACCENT_COLOR, fg_color=BORDER_COLOR)
        self.progress_bar.set(0)

        # Output Terminal / Editor
        editor_frame = ctk.CTkFrame(self.main_container, fg_color=BG_ELEVATED, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        editor_frame.grid(row=3, column=0, sticky="nsew", padx=40, pady=(20, 40))
        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)

        self.lyrics_textbox = ctk.CTkTextbox(
            editor_frame, fg_color="transparent", text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Consolas", size=15), wrap="word", padx=30, pady=30
        )
        self.lyrics_textbox.grid(row=0, column=0, sticky="nsew")
        
        # Tool Bar
        toolbar = ctk.CTkFrame(editor_frame, fg_color="transparent", height=60)
        toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkButton(toolbar, text="Copy to Clipboard", fg_color="transparent", border_width=1, border_color=BORDER_COLOR, text_color=TEXT_PRIMARY, hover_color=BG_SURFACE, height=35, command=self._copy_lyrics).pack(side="right", padx=5)
        ctk.CTkButton(toolbar, text="Save to Library", fg_color=SUCCESS_COLOR, hover_color="#059669", height=35, font=ctk.CTkFont(weight="bold"), command=self._save_lyrics).pack(side="right", padx=5)

    def show_history_view(self):
        self.clear_main_container()
        self._reset_sidebar_buttons()
        self.btn_history.configure(fg_color=BG_ELEVATED, text_color=TEXT_PRIMARY)
        
        self.main_container.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 20))
        
        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="My Library", font=ctk.CTkFont(size=28, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        
        # Track counter label
        self.library_subtitle = ctk.CTkLabel(title_box, text="Manage your saved extractions.", font=ctk.CTkFont(size=14), text_color=TEXT_MUTED)
        self.library_subtitle.pack(anchor="w")

        self.history_search = ctk.CTkEntry(header_frame, placeholder_text="Search tracks...", width=250, height=40, corner_radius=8, fg_color=BG_ELEVATED, border_color=BORDER_COLOR)
        self.history_search.pack(side="right", pady=10)
        self.history_search.bind("<KeyRelease>", self._filter_history)

        # Scrollable Grid
        self.history_scroll = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent",height=500)
        self.history_scroll.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 40))
        
        self._refresh_history()

    def show_stats_view(self):
        self.clear_main_container()
        self._reset_sidebar_buttons()
        self.btn_stats.configure(fg_color=BG_ELEVATED, text_color=TEXT_PRIMARY)
        
        # Header
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 20))
        ctk.CTkLabel(header_frame, text="Insights", font=ctk.CTkFont(size=28, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")

        stats = self.db.get_all_lyrics()
        count = len(stats)
        unique_artists = len(set(s['artist'] for s in stats))

        # Metric Card Grid
        metrics_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        metrics_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=10)
        metrics_frame.grid_columnconfigure((0, 1), weight=1)

        # Card 1: Total Tracks
        card1 = ctk.CTkFrame(metrics_frame, fg_color=BG_ELEVATED, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        card1.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(card1, text="TOTAL TRACKS SECURED", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).pack(pady=(20, 5))
        ctk.CTkLabel(card1, text=f"{count:02d}", font=ctk.CTkFont(size=48, weight="bold"), text_color=ACCENT_COLOR).pack(pady=(0, 20))

        # Card 2: Unique Artists
        card2 = ctk.CTkFrame(metrics_frame, fg_color=BG_ELEVATED, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        card2.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(card2, text="UNIQUE ARTISTS", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).pack(pady=(20, 5))
        ctk.CTkLabel(card2, text=f"{unique_artists:02d}", font=ctk.CTkFont(size=48, weight="bold"), text_color=SUCCESS_COLOR).pack(pady=(0, 20))

        # Recent Activity section
        ctk.CTkLabel(self.main_container, text="RECENT ACTIVITY", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).grid(row=2, column=0, sticky="w", padx=45, pady=(20, 10))
        
        recent_scroll = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent", height=300)
        recent_scroll.grid(row=3, column=0, sticky="nsew", padx=30, pady=(0, 40))
        
        if not stats:
            ctk.CTkLabel(recent_scroll, text="No secure activity yet.", text_color=TEXT_MUTED).pack(pady=20)
        else:
            # Show last 5 tracks
            for song in stats[:5]: 
                row = ctk.CTkFrame(recent_scroll, fg_color=BG_SURFACE, height=45, corner_radius=8)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=f"✦ {song['artist']} - {song['song_title']}", font=ctk.CTkFont(size=13), text_color=TEXT_PRIMARY).pack(side="left", padx=15, pady=10)
                ctk.CTkLabel(row, text=song.get('scraped_at', ''), font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(side="right", padx=15)

    def show_settings_view(self):
        self.clear_main_container()
        self._reset_sidebar_buttons()
        self.btn_setting.configure(fg_color=BG_ELEVATED, text_color=TEXT_PRIMARY)
        
        # Enable scrolling for settings
        scroll_container = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent",height=700)
        scroll_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.main_container.grid_rowconfigure(0, weight=1)
        scroll_container.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 20))
        ctk.CTkLabel(header_frame, text="Settings", font=ctk.CTkFont(size=28, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(header_frame, text="Configure your workspace and database preferences.", font=ctk.CTkFont(size=14), text_color=TEXT_MUTED).pack(anchor="w")

        # Database Configuration Card
        db_card = ctk.CTkFrame(scroll_container, fg_color=BG_ELEVATED, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        db_card.grid(row=1, column=0, sticky="ew", padx=40, pady=10)
        
        ctk.CTkLabel(db_card, text="DATABASE CONFIGURATION", font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT_COLOR).pack(anchor="w", padx=25, pady=(25, 15))
        
        db_path_frame = ctk.CTkFrame(db_card, fg_color="transparent")
        db_path_frame.pack(fill="x", padx=25, pady=(0, 25))
        
        path_entry = ctk.CTkEntry(db_path_frame, textvariable=self.db_path_var, height=40, border_color=BORDER_COLOR, fg_color=BG_SURFACE, state="readonly")
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(db_path_frame, text="Change Path", width=120, height=40, fg_color="transparent", border_width=1, border_color=BORDER_COLOR, hover_color=BG_SURFACE, command=self._change_db_path).pack(side="right")

        # Preferences Card
        pref_card = ctk.CTkFrame(scroll_container, fg_color=BG_ELEVATED, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        pref_card.grid(row=2, column=0, sticky="ew", padx=40, pady=10)
        
        ctk.CTkLabel(pref_card, text="APP PREFERENCES", font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT_COLOR).pack(anchor="w", padx=25, pady=(25, 15))
        
        # Toggle Switches
        ctk.CTkSwitch(pref_card, text="Auto-save to Library", variable=self.auto_save_var, progress_color=ACCENT_COLOR, font=ctk.CTkFont(size=14)).pack(anchor="w", padx=25, pady=10)
        ctk.CTkSwitch(pref_card, text="High Fidelity Extraction", variable=self.high_fidelity_var, progress_color=ACCENT_COLOR, font=ctk.CTkFont(size=14)).pack(anchor="w", padx=25, pady=10)

        # Maintenance & Updates
        maint_card = ctk.CTkFrame(scroll_container, fg_color=BG_ELEVATED, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        maint_card.grid(row=3, column=0, sticky="ew", padx=40, pady=10)
        
        ctk.CTkLabel(maint_card, text="MAINTENANCE", font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT_COLOR).pack(anchor="w", padx=25, pady=(25, 15))
        
        btn_container = ctk.CTkFrame(maint_card, fg_color="transparent")
        btn_container.pack(fill="x", padx=25, pady=(0, 25))
        
        ctk.CTkButton(btn_container, text="Check for Updates", height=40, fg_color=BG_SURFACE, border_width=1, border_color=BORDER_COLOR, command=self._check_updates).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_container, text="Wipe Library", height=40, fg_color="transparent", border_width=1, border_color=ERROR_COLOR, text_color=ERROR_COLOR, hover_color="#451a1e", command=self._wipe_library).pack(side="left")

        # About Section
        ctk.CTkLabel(scroll_container, text=f"{APP_NAME} v1.2.0\nBuilt for High Performance Lyrics Sync", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).grid(row=4, column=0, pady=40)

    def _change_db_path(self):
        from tkinter import filedialog
        new_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite Database", "*.db")], initialfile="lyrics.db")
        if new_path:
            self.db.close()
            self.db = LyricsDatabase(new_path)
            self.db_path_var.set(os.path.abspath(new_path))
            self._save_app_settings()
            messagebox.showinfo("Database Updated", f"Active database switched to:\n{new_path}")

    def _save_app_settings(self):
        # Save relative path if it's in the current directory, else absolute
        current_dir = os.getcwd()
        full_path = self.db_path_var.get()
        
        if full_path.startswith(current_dir):
            db_path = os.path.relpath(full_path, current_dir)
        else:
            db_path = full_path

        settings = {
            "db_path": db_path,
            "auto_save": self.auto_save_var.get(),
            "high_fidelity": self.high_fidelity_var.get()
        }
        SettingsManager.save_settings(settings)

    def _check_updates(self):
        messagebox.showinfo("Updater", "You are running the latest version of LyricsFusion PRO (v1.2.0).")

    def _wipe_library(self):
        if messagebox.askyesno("Confirm Wipe", "Are you sure you want to permanently delete ALL saved lyrics?"):
            # Minimal implementation to clear DB
            self.db.cursor.execute("DELETE FROM lyrics")
            self.db.connection.commit()
            messagebox.showinfo("Library Wiped", "All stored data has been removed.")
            
            # Auto-refresh UI if currently in library or stats
            if hasattr(self, "history_scroll") and self.history_scroll.winfo_exists():
                self._refresh_history()
            elif hasattr(self, "btn_stats") and self.btn_stats.cget("fg_color") == BG_ELEVATED:
                self.show_stats_view()

    def _show_feedback(self):

        """Poll the message queue for updates from the scraper thread."""

        try:

            while True:

                msg = message.get_nowait()# type: ignore

                self._update_status(msg, ACCENT_COLOR)# type: ignore

                message.task_done()

        except queue.Empty:

            pass

        except Exception:

            pass

       

        if hasattr(self, "_is_scraping") and self._is_scraping:

            self.after(100, self._show_feedback)




    # --- Utility Methods ---
    def _update_status(self, text, color):
        try:
            if hasattr(self, "status_label") and self.status_label.winfo_exists():
                self.status_label.configure(text=text, text_color=color)
        except Exception:
            pass

    def _start_scrape(self):
        artist = self.artist_entry.get().strip()
        song = self.song_entry.get().strip()
        
        if not artist or not song:
            self._update_status("Requires both artist and track title.", ERROR_COLOR)
            return
            
        self._is_scraping = True
        
        # UI Toggle: Switch Scrape for Cancel
        self.scrape_btn.grid_forget()
        self.cancel_btn.grid(row=0, column=2, sticky="s")
    
        self.progress_bar.pack(side="right", padx=10)
        self.progress_bar.start()
        self._update_status("Connecting to Genius API routing...", ACCENT_COLOR)
        
        thread = threading.Thread(target=self._scrape_worker, args=(artist, song), daemon=True)
        thread.start()

         # Start feedback polling
        self._show_feedback()

    def _scrape_worker(self, artist, song):
        try:
            if not self.scraper:
                self.scraper = GeniusScraper()
            result = self.scraper.scrape(artist, song)
            
            if result:
                self.after(0, lambda: self._display_lyrics(result, artist, song))
                self.after(0, lambda: self._update_status(f"Extraction successful: {artist} - {song}", SUCCESS_COLOR))
            else:
                self.after(0, lambda: self._update_status("Data not found in repository.", ERROR_COLOR))
        except Exception:
            # This will catch errors when the driver is closed via _cancel_scrape
            if not self._is_scraping:
                self.after(0, lambda: self._update_status("Extraction canceled by user.", TEXT_MUTED))
            else:
                self.after(0, lambda: self._update_status("Connection interrupted.", ERROR_COLOR))
        finally:
            self.after(0, self._stop_loading)

    def _cancel_scrape(self):
        """Terminate the scraping process and reset UI."""
        self._is_scraping = False
        if self.scraper:
            # Closing the driver will cause the worker thread to throw an exception
            # which is handled in _scrape_worker's try-except-finally
            self.scraper.close()
            self.scraper = None 
        
        # _stop_loading will be called by the thread's finally block, 
        # but we call it here for immediate UI response if needed.
        self._stop_loading()

    def _display_lyrics(self, result, artist, song):
        try:
            lyrics = result['lyrics']
            
            # High Fidelity Extraction Logic: Clean up text artifacts and headers
            if self.high_fidelity_var.get():
                import re
                
                # 1. Remove specific Genius page artifacts at the top
                # Patterns: "X Contributors", "Translations", "Song Title Lyrics"
                lyrics = re.sub(r'^\d+\s+Contributors.*?\n', '', lyrics, flags=re.IGNORECASE)
                lyrics = re.sub(r'^Translations.*?\n', '', lyrics, flags=re.IGNORECASE)
                lyrics = re.sub(r'^.*?Lyrics\n', '', lyrics, flags=re.IGNORECASE)
                
                # 2. Remove the "You can’t judge something..." intro snippets if they got caught
                lyrics = re.sub(r'^“.*?” was surprise-released.*?\n', '', lyrics, flags=re.IGNORECASE | re.DOTALL)
                
                # 3. Remove structural tags like [Verse], [Chorus], etc.
                lyrics = re.sub(r'\[.*?\]', '', lyrics)
                
                # 4. Final Cleanup: Remove extra whitespace left behind
                lyrics = re.sub(r'\n{3,}', '\n\n', lyrics).strip()

            self.current_lyrics_data = {'artist': artist, 'song': song, 'lyrics': lyrics, 'url': result['url']}
            
            if hasattr(self, "lyrics_textbox") and self.lyrics_textbox.winfo_exists():
                self.lyrics_textbox.configure(state="normal")
                self.lyrics_textbox.delete("1.0", "end")
                self.lyrics_textbox.insert("end", lyrics)
            
            # Auto-save logic
            if self.auto_save_var.get():
                self._save_lyrics()
        except Exception:
            pass

    def _stop_loading(self):
        try:
            if hasattr(self, "scrape_btn") and self.scrape_btn.winfo_exists():
                self.scrape_btn.configure(state="normal", text="Extract Lyrics")
                self.scrape_btn.grid(row=0, column=2, sticky="s")
            
            if hasattr(self, "cancel_btn") and self.cancel_btn.winfo_exists():
                self.cancel_btn.grid_forget()
            
            if hasattr(self, "progress_bar") and self.progress_bar.winfo_exists():
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
        except Exception:
            pass

    def _save_lyrics(self):
        if not self.current_lyrics_data:
            self._update_status("Buffer empty.", ERROR_COLOR)
            return
        data = self.current_lyrics_data
        success = self.db.save_lyrics(data['artist'], data['song'], data['lyrics'], data['url'])
        if success:
            self._update_status("Archived successfully.", SUCCESS_COLOR)
        else:
            self._update_status("Duplicate detected in archive.", TEXT_MUTED)

    def _copy_lyrics(self):
        if hasattr(self, "lyrics_textbox") and self.lyrics_textbox.winfo_exists():
            content = self.lyrics_textbox.get("1.0", "end-1c")
            if content:
                pyperclip.copy(content)
                self._update_status("Copied to clipboard.", SUCCESS_COLOR)

    def _refresh_history(self, filter_text=""):
        try:
            for widget in self.history_scroll.winfo_children():
                widget.destroy()
                
            songs = self.db.get_all_lyrics()
            
            # Update count in subtitle
            if hasattr(self, "library_subtitle") and self.library_subtitle.winfo_exists():
                count = len(songs)
                self.library_subtitle.configure(text=f"Manage {count} saved extraction{'s' if count != 1 else ''}.")
            
            if filter_text:
                songs = [s for s in songs if filter_text.lower() in s['artist'].lower() or filter_text.lower() in s['song_title'].lower()]
                
            if not songs:
                ctk.CTkLabel(self.history_scroll, text="Your library is currently empty.", text_color=TEXT_MUTED).pack(pady=40)
                return
                
            for song in songs:
                card = SongCard(self.history_scroll, song, self._view_lyrics_from_history, self._delete_from_history)
                card.pack(fill="x", pady=(0, 10), padx=10)
        except Exception:
            pass

    def _filter_history(self, event=None):
        self._refresh_history(self.history_search.get())

    def _view_lyrics_from_history(self, song_data):
        view_win = ctk.CTkToplevel(self)
        view_win.title(f"{song_data['artist']} - {song_data['song_title']}")
        view_win.geometry("700x800")
        view_win.configure(fg_color=BG_APP)
        view_win.attributes("-topmost", True)
        
        header = ctk.CTkFrame(view_win, fg_color=BG_SURFACE, corner_radius=0, height=120)
        header.pack(fill="x")
        
        ctk.CTkLabel(header, text=song_data['song_title'], font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_PRIMARY).pack(pady=(25, 0))
        ctk.CTkLabel(header, text=song_data['artist'], font=ctk.CTkFont(size=14), text_color=ACCENT_COLOR).pack()
        
        # Action Toolbar in View Window
        view_toolbar = ctk.CTkFrame(header, fg_color="transparent")
        view_toolbar.pack(pady=10)
        
        ctk.CTkButton(view_toolbar, text="📋 Copy", width=80, height=28, fg_color=BG_ELEVATED, command=lambda: pyperclip.copy(song_data['lyrics'])).pack(side="left", padx=5)
        if song_data.get('genius_url'):
            ctk.CTkButton(view_toolbar, text="🌐 Open", width=80, height=28, fg_color=BG_ELEVATED, command=lambda: webbrowser.open(song_data['genius_url'])).pack(side="left", padx=5)
        
        txt = ctk.CTkTextbox(view_win, fg_color=BG_ELEVATED, text_color=TEXT_PRIMARY, font=ctk.CTkFont(family="Consolas", size=15), wrap="word", padx=30, pady=30, corner_radius=12)
        txt.pack(fill="both", expand=True, padx=20, pady=20)
        txt.insert("end", song_data['lyrics'])
        txt.configure(state="disabled")

    def _delete_from_history(self, song_data):
        if messagebox.askyesno("Confirm Drop", f"Permanently remove '{song_data['song_title']}'?"):
            if self.db.delete_lyrics(song_data['artist'], song_data['song_title']):
                self._refresh_history(self.history_search.get())

if __name__ == "__main__":
    app = LyricsScraperPRO()
    app.mainloop()