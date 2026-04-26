# LyricsFusion PRO

A professional, high-performance lyrics scraping and management suite built with Python. 

**LyricsFusion PRO** provides a modern, intuitive interface for fetching, storing, and organizing song lyrics from Genius.com. Built with **CustomTkinter** for a sleek aesthetic and **Selenium** for robust web automation.

## 🚀 Key Features

- **PRO Dashboard**: Modern sidebar navigation with a high-end dark theme.
- **Intelligent Scraper**: Headless Selenium-based engine for reliable data extraction.
- **My Library**: Advanced card-based management system for your saved lyrics.
- **Real-time Filtering**: Instantly search through your collection by artist or song title.
- **Statistics View**: Track your scraping activity and library size.
- **Threading Engine**: Asynchronous operations ensure the UI remains buttery smooth.
- **Cross-Platform**: Designed to work seamlessly on Windows, macOS, and Linux.

## 📦 Prerequisites

- **Python 3.8+**
- **Google Chrome** (Required for the Selenium engine)
- **Active Internet Connection**

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/LyricsFusion.git
cd LyricsFusion
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup ChromeDriver (Recommended)
We recommend installing `webdriver-manager` to handle driver updates automatically:
```bash
pip install webdriver-manager
```

## 🎮 Usage

Launch the application using:
```bash
python genius_lyrics_scraper.py
```

### Workflow:
1. **Search**: Enter the artist and song title in the "Search Scraper" tab.
2. **Scrape**: Hit "START SCRAPING" and watch the progress bar.
3. **Library**: Save your favorite lyrics to your local library.
4. **Manage**: Use the "My Library" tab to view, copy, or delete saved songs.
5. **Analyze**: Check the "Statistics" tab to see your collection's growth.

## 📂 Project Architecture

```text
├── genius_lyrics_scraper.py    # Main PRO UI (CustomTkinter)
├── genius_scraper.py            # Selenium Scraper Core
├── genius_scraper_db.py         # SQLite3 Database Controller
├── requirements.txt             # Project Dependencies
└── lyrics.db                    # Persistent Local Storage
```

## ⚙️ Configuration & Customization

The UI supports several appearance modes (Dark, Light, System) which can be toggled from the sidebar. The theme colors can be easily modified in the `Constants` section of `genius_lyrics_scraper.py`.

## 🛡️ Troubleshooting

- **No Lyrics Found**: Ensure the spelling matches Genius.com exactly.
- **WebDriver Error**: If not using `webdriver-manager`, ensure your `chromedriver.exe` matches your Chrome version and is in the system PATH.
- **UI Scaling**: If the window looks blurry on Windows, ensure your high-DPI settings are configured for Python.

## ⚖️ Legal & Compliance

This tool is intended for personal and educational use. Please respect Genius.com's Terms of Service and avoid aggressive scraping that could strain their servers.

---
**LyricsFusion PRO** - *Your Personal Lyrics Archive*
