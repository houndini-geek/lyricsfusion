# LyricsFusion PRO: Professional Genius Lyrics Scraper & Manager

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**LyricsFusion PRO** is a high-performance **Genius lyrics downloader** and management suite. It combines the power of **Selenium web scraping** with a modern **CustomTkinter GUI** to provide the ultimate desktop experience for music enthusiasts and researchers.

## 🚀 Key Features

- **Advanced Lyrics Scraper**: Robust Selenium-based engine specifically optimized for Genius.com.
- **Modern UI/UX**: Professional dark-themed dashboard built with CustomTkinter.
- **Persistent Library**: Automatically saves scraped lyrics to a local SQLite database (`lyrics.db`).
- **Smart Matching**: Uses `stringmatch` algorithms to find the correct song even with typos.
- **Asynchronous Operations**: Fully threaded execution ensures the GUI never freezes during scraping.
- **Portable**: Can be compiled into a standalone Windows executable.

## 📦 Search Keywords
*Genius Scraper, Lyrics Downloader, Python Scraper, CustomTkinter App, Selenium Automation, Music Metadata, Lyrics Archive, Desktop Lyrics App.*

## 🛠️ Quick Start

### Prerequisites
- **Google Chrome**: The engine uses headless Chrome for scraping.
- **Python 3.8+**

### Installation
1. **Clone the Repo**
   ```bash
   git clone https://github.com/houndini-geek/lyricsfusion.git
   cd lyricsfusion
   ```
2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the App**
   ```bash
   python genius_lyrics_scraper.py
   ```

## 📂 Project Structure
- `genius_lyrics_scraper.py`: The main Graphical User Interface.
- `genius_scraper.py`: Core Selenium scraping logic.
- `genius_scraper_db.py`: Database management (SQLite).
- `main_queue.py`: Thread-safe communication for real-time feedback.

---
### 🏷️ GitHub Topics (Add these to your repo settings!)
To make this project even more visible, go to your GitHub repository settings and add these topics:
`python`, `selenium`, `lyrics-scraper`, `genius-api`, `customtkinter`, `web-scraping`, `desktop-application`, `sqlite`, `music-tools`.
