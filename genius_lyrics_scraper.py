"""
Professional Genius Lyrics Scraper GUI
Enhanced with modern UI/UX components using CustomTkinter.
"""

from pydoc import text
import customtkinter as ctk
import threading
import queue
from tkinter import messagebox
import pyperclip
import os
from datetime import datetime
from genius_scraper import GeniusScraper, GeniusScraperError
from genius_scraper_db import LyricsDatabase

from main_queue import message

# --- Constants & Theme ---
APP_NAME = "LyricsFusion PRO"
ACCENT_COLOR = "#00d4ff"  # Neon Cyan
BG_COLOR = "#0f0f12"     # Deep Dark
SIDEBAR_COLOR = "#16161a"
CARD_COLOR = "#1e1e24"
TEXT_COLOR = "#e0e0e0"
SUCCESS_COLOR = "#2ecc71"
ERROR_COLOR = "#e74c3c"

class SidebarButton(ctk.CTkButton):
    def __init__(self, master, text, command, image=None, **kwargs):
        super().__init__(
            master, 
            text=text, 
            command=command, 
            anchor="w", 
            height=45,
            fg_color="transparent",
            text_color=TEXT_COLOR,
            hover_color=CARD_COLOR,
            font=("Inter", 13, "bold"),
            **kwargs
        )

class SongCard(ctk.CTkFrame):
    def __init__(self, master, data, on_view, on_delete, **kwargs):
        super().__init__(master, fg_color=CARD_COLOR, corner_radius=10, **kwargs)
        
        self.data = data
        
        # Song Info
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        ctk.CTkLabel(
            info_frame, 
            text=data['song_title'], 
            font=("Inter", 14, "bold"),
            text_color=ACCENT_COLOR,
            anchor="w"
        ).pack(fill="x")
        
        ctk.CTkLabel(
            info_frame, 
            text=data['artist'], 
            font=("Inter", 12),
            text_color=TEXT_COLOR,
            anchor="w"
        ).pack(fill="x")
        
        # Date
        ctk.CTkLabel(
            self, 
            text=data['scraped_at'][:10], 
            font=("Inter", 10),
            text_color="#666"
        ).pack(side="left", padx=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="VIEW", 
            width=60, 
            height=28,
            fg_color=ACCENT_COLOR,
            text_color="#000",
            hover_color="#00a8cc",
            font=("Inter", 10, "bold"),
            command=lambda: on_view(data)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="DEL", 
            width=50, 
            height=28,
            fg_color="#333",
            hover_color=ERROR_COLOR,
            font=("Inter", 10, "bold"),
            command=lambda: on_delete(data)
        ).pack(side="left", padx=5)

class LyricsScraperPRO(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1100x750")
        self.configure(fg_color=BG_COLOR)
        
        # Set Icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "lyricsfusion.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass
        
        # Initialize Core
        self.db = LyricsDatabase()
        self.scraper = None
        self.current_lyrics_data = None
        
        # UI State
        self.current_frame = None
        
        # Setup Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._build_sidebar()
        self._build_main_container()
        
        # Default View
        self.show_search_view()
        
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=SIDEBAR_COLOR, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)
        
        # Logo
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="LYRICS\nFUSION", 
            font=("Inter", 24, "bold"),
            text_color=ACCENT_COLOR
        )
        self.logo_label.grid(row=0, column=0, pady=30)
        
        # Nav Buttons
        self.btn_search = SidebarButton(self.sidebar, "Search Scraper", self.show_search_view)
        self.btn_search.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        self.btn_history = SidebarButton(self.sidebar, "My Library", self.show_history_view)
        self.btn_history.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.btn_stats = SidebarButton(self.sidebar, "Statistics", self.show_stats_view)
        self.btn_stats.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        
        # Appearance Mode
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar, text="Appearance Mode:", font=("Inter", 11), text_color="#666")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0), sticky="w")
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar, values=["Dark", "Light", "System"],
            command=self.change_appearance_mode,
            fg_color=CARD_COLOR, button_color="#333", button_hover_color="#444"
        )
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20))

    def _build_main_container(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
    def clear_main_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def _show_feedback(self):
        """Poll the message queue for updates from the scraper thread."""
        try:
            while True:
                msg = message.get_nowait()
                self._update_status(msg, ACCENT_COLOR)
                message.task_done()
        except queue.Empty:
            pass
        except Exception:
            pass
        
        if hasattr(self, "_is_scraping") and self._is_scraping:
            self.after(100, self._show_feedback)


    def show_search_view(self):
        self.clear_main_container()
        self.btn_search.configure(fg_color=CARD_COLOR)
        self.btn_history.configure(fg_color="transparent")
        self.btn_stats.configure(fg_color="transparent")
        
        # Header

    
        header = ctk.CTkLabel(self.main_container, text="Scrape New Lyrics", font=("Inter", 24, "bold"), text_color=TEXT_COLOR)
        header.pack(anchor="w", pady=(0, 20))
        
        
        # Input Section
        input_frame = ctk.CTkFrame(self.main_container, fg_color=CARD_COLOR, corner_radius=15)
        input_frame.pack(fill="x", pady=20)
        
        inner_input = ctk.CTkFrame(input_frame, fg_color="transparent")
        inner_input.pack(padx=30)
        
        # Artist Entry
        artist_frame = ctk.CTkFrame(inner_input, fg_color="transparent")
        artist_frame.grid(row=0, column=0, padx=10)
        ctk.CTkLabel(artist_frame, text="ARTIST NAME", font=("Inter", 10, "bold"), text_color="#666").pack(anchor="w")
        self.artist_entry = ctk.CTkEntry(artist_frame, placeholder_text="e.g. The Weeknd", width=300, height=40, border_color="#333")
        self.artist_entry.pack(pady=5)
        
        # Song Entry
        song_frame = ctk.CTkFrame(inner_input, fg_color="transparent")
        song_frame.grid(row=0, column=1, padx=10)
        ctk.CTkLabel(song_frame, text="SONG TITLE", font=("Inter", 10, "bold"), text_color="#666").pack(anchor="w")
        self.song_entry = ctk.CTkEntry(song_frame, placeholder_text="e.g. Blinding Lights", width=300, height=40, border_color="#333")
        self.song_entry.pack(pady=5)
        
        # Scrape Button
        self.scrape_btn = ctk.CTkButton(
            inner_input, 
            text="START SCRAPING", 
            width=150, 
            height=40, 
            fg_color=ACCENT_COLOR, 
            text_color="#000",
            hover_color="#00a8cc",
            font=("Inter", 12, "bold"),
            command=self._start_scrape
        )
        self.scrape_btn.grid(row=0, column=2, padx=10, pady=(18, 0))
        
        # Progress & Status
        self.status_bar = ctk.CTkFrame(self.main_container, fg_color="transparent", height=40)
        self.status_bar.pack(fill="x", pady=10)
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready to find some magic...", font=("Inter", 12), text_color="#666")
        self.status_label.pack(side="left")
        
        self.progress_bar = ctk.CTkProgressBar(self.status_bar, width=200, height=8, progress_color=ACCENT_COLOR)
        self.progress_bar.set(0)
        
        # Lyrics Display
        self.lyrics_container = ctk.CTkFrame(self.main_container, fg_color=CARD_COLOR, corner_radius=15)
        self.lyrics_container.pack(fill="both", expand=True, pady=10)
        
        self.lyrics_textbox = ctk.CTkTextbox(
            self.lyrics_container, 
            fg_color="transparent", 
            text_color=TEXT_COLOR,
            font=("Inter", 15),
            padx=25,
            pady=25,
            undo=True
        )
        self.lyrics_textbox.pack(fill="both", expand=True)
        self.lyrics_textbox.configure(state="disabled")
        
        # Action Bar (Inside lyrics container at bottom)
        self.action_bar = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.action_bar.pack(fill="x", pady=(0, 10))
        
        self.save_btn = ctk.CTkButton(self.action_bar, text="Save to Library", fg_color=SUCCESS_COLOR, width=120, height=35, font=("Inter", 11, "bold"), command=self._save_lyrics)
        self.save_btn.pack(side="right", padx=5)
        
        self.copy_btn = ctk.CTkButton(self.action_bar, text="Copy to Clipboard", fg_color="#333", width=120, height=35, font=("Inter", 11, "bold"), command=self._copy_lyrics)
        self.copy_btn.pack(side="right", padx=5)

    def show_history_view(self):
        self.clear_main_container()
        self.btn_search.configure(fg_color="transparent")
        self.btn_history.configure(fg_color=CARD_COLOR)
        self.btn_stats.configure(fg_color="transparent")
        
        # Header
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="My Library", font=("Inter", 24, "bold"), text_color=TEXT_COLOR).pack(side="left")
        
        # Search Library
        self.history_search = ctk.CTkEntry(header_frame, placeholder_text="Search artist or song...", width=300, height=35, border_color="#333")
        self.history_search.pack(side="right")
        self.history_search.bind("<KeyRelease>", self._filter_history)
        
        # History List
        self.history_scroll = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent", label_text="")
        self.history_scroll.pack(fill="both", expand=True)
        
        self._refresh_history()

    def show_stats_view(self):
        self.clear_main_container()
        self.btn_search.configure(fg_color="transparent")
        self.btn_history.configure(fg_color="transparent")
        self.btn_stats.configure(fg_color=CARD_COLOR)
        
        header = ctk.CTkLabel(self.main_container, text="Statistics", font=("Inter", 24, "bold"), text_color=TEXT_COLOR)
        header.pack(anchor="w", pady=(0, 20))
        
        stats = self.db.get_all_lyrics()
        count = len(stats)
        
        # Stats Card
        stats_frame = ctk.CTkFrame(self.main_container, fg_color=CARD_COLOR, corner_radius=15, height=200)
        stats_frame.pack(fill="x")
        
        ctk.CTkLabel(stats_frame, text="Total Songs Scraped", font=("Inter", 14), text_color="#666").pack(pady=(30, 0))
        ctk.CTkLabel(stats_frame, text=str(count), font=("Inter", 64, "bold"), text_color=ACCENT_COLOR).pack(pady=(0, 30))
        
        if count > 0:
            latest = stats[0]
            ctk.CTkLabel(self.main_container, text="Last Activity", font=("Inter", 14, "bold"), text_color="#666").pack(anchor="w", pady=(30, 10))
            
            activity_card = SongCard(self.main_container, latest, self._view_lyrics_from_history, self._delete_from_history)
            activity_card.pack(fill="x")

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
            self._update_status("Please enter artist and song!", ERROR_COLOR)
            return

        self._is_scraping = True
        self.scrape_btn.configure(state="disabled")
        self.progress_bar.pack(side="right", padx=10)
        self.progress_bar.start()
        self._update_status("Connecting to Genius...", ACCENT_COLOR)
       
        # Start feedback polling
        self._show_feedback()
        
        thread = threading.Thread(target=self._scrape_worker, args=(artist, song))
        thread.daemon = True
        thread.start()
       
       


    def _scrape_worker(self, artist, song):
        try:
            if not self.scraper:
                self.scraper = GeniusScraper()

            result = self.scraper.scrape(artist, song)
            
            if result:
                self.after(0, lambda: self._display_lyrics(result, artist, song))
                self.after(0, lambda: self._update_status(f"Found: {artist} - {song}", SUCCESS_COLOR))
            else:
                self.after(0, lambda: self._update_status("No lyrics found.", ERROR_COLOR))
                
        except Exception as e:
            self.after(0, lambda: self._update_status(f"Error: {str(e)}", ERROR_COLOR))
        finally:
            self.after(0, self._stop_loading)
            if self.scraper:
                try:
                    self.scraper.close()
                except:
                    pass
                self.scraper = None
            

    def _display_lyrics(self, result, artist, song):
        self.current_lyrics_data = {
            'artist': artist,
            'song': song,
            'lyrics': result['lyrics'],
            'url': result['url']
        }
        self.lyrics_textbox.configure(state="normal")
        self.lyrics_textbox.delete("1.0", "end")
        self.lyrics_textbox.insert("end", result['lyrics'])
        self.lyrics_textbox.configure(state="normal")

    def _save_lyrics(self):
        if not self.current_lyrics_data:
            self._update_status("Nothing to save!", ERROR_COLOR)
            return
            
        data = self.current_lyrics_data
        success = self.db.save_lyrics(data['artist'], data['song'], data['lyrics'], data['url'])
        
        if success:
            self._update_status("Successfully saved to library!", SUCCESS_COLOR)
            messagebox.showinfo("Saved", f"'{data['song']}' has been added to your library.")
        else:
            self._update_status("Already in library.", "#888")

    def _copy_lyrics(self):
        content = self.lyrics_textbox.get("1.0", "end-1c")
        if content:
            pyperclip.copy(content)
            self._update_status("Copied to clipboard!", SUCCESS_COLOR)

    def _refresh_history(self, filter_text=""):
        for widget in self.history_scroll.winfo_children():
            widget.destroy()
            
        songs = self.db.get_all_lyrics()
        if filter_text:
            songs = [s for s in songs if filter_text.lower() in s['artist'].lower() or filter_text.lower() in s['song_title'].lower()]
            
        if not songs:
            ctk.CTkLabel(self.history_scroll, text="No songs found in your library.", font=("Inter", 13), text_color="#666").pack(pady=40)
            return
            
        for song in songs:
            card = SongCard(self.history_scroll, song, self._view_lyrics_from_history, self._delete_from_history)
            card.pack(fill="x", pady=5, padx=5)

    def _filter_history(self, event=None):
        query = self.history_search.get()
        self._refresh_history(query)

    def _view_lyrics_from_history(self, song_data):
        # Create a popup window for viewing lyrics
        view_win = ctk.CTkToplevel(self)
        view_win.title(f"{song_data['artist']} - {song_data['song_title']}")
        view_win.geometry("600x700")
        view_win.configure(fg_color=BG_COLOR)
        view_win.attributes("-topmost", True)
        
        header = ctk.CTkFrame(view_win, fg_color=SIDEBAR_COLOR, height=80, corner_radius=0)
        header.pack(fill="x")
        
        ctk.CTkLabel(header, text=song_data['song_title'], font=("Inter", 18, "bold"), text_color=ACCENT_COLOR).pack(pady=(15, 0))
        ctk.CTkLabel(header, text=song_data['artist'], font=("Inter", 14), text_color=TEXT_COLOR).pack()
        
        txt = ctk.CTkTextbox(view_win, fg_color="transparent", text_color=TEXT_COLOR, font=("Inter", 13), padx=20, pady=20)
        txt.pack(fill="both", expand=True)
        txt.insert("end", song_data['lyrics'])
        txt.configure(state="disabled")
        
        ctk.CTkButton(view_win, text="COPY", fg_color="#333", height=35, command=lambda: pyperclip.copy(song_data['lyrics'])).pack(fill="x", padx=20, pady=20)

    def _delete_from_history(self, song_data):
        if messagebox.askyesno("Confirm Delete", f"Remove '{song_data['song_title']}' from your library?"):
            if self.db.delete_lyrics(song_data['artist'], song_data['song_title']):
                self._refresh_history(self.history_search.get())
                self._update_status("Deleted from library.", ERROR_COLOR)

    def _stop_loading(self):
        self._is_scraping = False
        self.scrape_btn.configure(state="normal")
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def on_closing(self):
        if self.scraper:
            self.scraper.close()
        self.db.close()
        self.destroy()

if __name__ == "__main__":
    app = LyricsScraperPRO()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
