"""
Genius.com lyrics scraper using Selenium.
Handles web scraping and parsing of lyrics from Genius.
"""

from operator import sub #type: ignore
from typing import Any


import time
from turtle import title #type: ignore
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from main_queue import message #type: ignore

from utils import SettingsManager

from stringmatch import Match


class GeniusScraperError(Exception):
    """Custom exception for scraper errors."""
    pass


class GeniusScraper:
    def __init__(self):
        """Initialize Selenium WebDriver with headless Chrome."""
        self.driver = None
        self._init_driver()
        self.wait = WebDriverWait[Any](self.driver,5)
        self._match = Match()
        self.selectors = SettingsManager()
        self.load_selectors()

     
  
        

    def _queue_handler(self,msg:str):
       
        message.put(msg) #type: ignore

    def load_selectors(self):
        return self.selectors.load_selectors()


    def _init_driver(self):
        """Initialize Chrome WebDriver with headless options."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        # Use a more complete and realistic User-Agent
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Set page load strategy to 'eager' to not wait for all subresources (like ads/trackers)
        chrome_options.page_load_strategy = 'eager'
        
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            # Increase timeout to 30 seconds as Genius can be slow
            self.driver.set_page_load_timeout(30)
        except Exception as e:
            raise GeniusScraperError(f"Failed to initialize Chrome WebDriver: {e}")


    def _matchTitle(self,str1,str2): #type: ignore
        return self._match.match(str1,str2,score=50) #type: ignore
    
    def _matchArtistName(self,str1,str2):#type: ignore
        return self._match.match(str1,str2,score=50)#type: ignore


    def _build_genius_url(self, artist: str, song_title: str) -> str:
        """Build Genius URL from artist and song title."""
        import urllib.parse
        self._queue_handler(msg='Constructing search query and routing...')
        query = f"{artist} {song_title}"
        encoded_query = urllib.parse.quote(query)
        url : str = f"https://genius.com/search?q={encoded_query}"
        return url

    def _search_genius(self, artist: str, song_title: str) -> str | None:
        """
        Search Genius and return the actual URL of the first result if found.
        """
        try:
            url = self._build_genius_url(artist, song_title)
            self._queue_handler(msg="Establishing secure connection to Genius...")

            self.driver.maximize_window()#type: ignore
            
            self._queue_handler(msg="Synchronizing with server response...")
            try:
                self.driver.get(url)#type: ignore
            except TimeoutException:
                self._queue_handler(msg="Connection timed out. Retrying protocol...")
                return None
            
            self._queue_handler(msg="Decoding page layout and scripts...")
            time.sleep(2) # Give it a moment to render dynamic content
            
            self._queue_handler(msg="Portal established: Accessing song database.")


            self._queue_handler(msg="Searching for extended track results...")

            try:
                showMore = self.load_selectors()['selectors']['showmorebutton']['selector']
              
                showMoreButton = self.wait.until(
                    EC.visibility_of_element_located(
                        (By.CLASS_NAME,
                        showMore)))
                showMoreButton.click()
                self._queue_handler(msg="Expanding result list...")

            except (TimeoutException, NoSuchElementException):
                self._queue_handler(msg="Element not found - page may have changed / Check for updates > settings > check for updates")
                return None


            # Try to find the result cards
            time.sleep(2)
            try:
                searchresultpaginated = self.load_selectors()['selectors']['searchresultpaginated']['selector']
                
                self._queue_handler(msg="Scanning metadata containers...")

                search_result = self.driver.find_element(By.TAG_NAME,  searchresultpaginated)#type: ignore
                if search_result:
                    minisongcard = self.load_selectors()['selectors']['minisongcard']['selector']

                    self._queue_handler(msg="Track section identified.")

                    self._queue_handler(msg="Filtering potential matches...")
                    time.sleep(4)
                    mini_card_songs = search_result.find_elements(By.TAG_NAME, minisongcard)
                    if  not mini_card_songs:
                        self._queue_handler(msg="No matching track cards detected in this section.")
                        return None


                    for card in mini_card_songs:
                            try:
                                minicardtitle = self.load_selectors()['selectors']['minicardtitle']['selector']
                                minicardsubtitle = self.load_selectors()['selectors']['minicardsubtitle']['selector']

                                self._queue_handler(msg="Verifying track signatures and artist metadata...")

                                title = card.find_element(By.CLASS_NAME,minicardtitle).text.strip().lower()
                                subtitle = card.find_element(By.CLASS_NAME,minicardsubtitle).text.strip().lower()
                                self._queue_handler(msg="Calculating similarity scores...")

                                if self._matchTitle(str1=title,str2=song_title) and self._matchArtistName(str1=subtitle,str2=artist): #type: ignore
                                    self._queue_handler(msg=f"Verification successful: Match confirmed.")

                                    card_url = card.find_element(By.TAG_NAME,'a').get_attribute('href')#type: ignore
                                    return card_url
                                else:
                                    return None

                            except NoSuchElementException:
                                self._queue_handler(msg="Dynamic layout shift detected. Verification failed.")
                                return None
                else:
                    self._queue_handler(msg="Critical metadata section missing from page.")
                    return None
            except Exception as e :
                raise GeniusScraperError(f"Error searching Genius: {e}")

        except Exception as e:
            raise GeniusScraperError(f"Error searching Genius: {e}")
          

    def _extract_lyrics(self) -> str | None:
        """Extract lyrics from the current page."""
        try:
            try:
                datalyricscontainer = self.load_selectors()['selectors']['datalyricscontainer']['selector']
                datalyricscontainerfallback = self.load_selectors()['selectors']['datalyricscontainerfallback']['selector']

                self._queue_handler(msg="Searching for lyrical data stream...")

                # Modern Genius uses data-lyrics-container attribute
                containers = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, datalyricscontainer))
                )
                self._queue_handler(msg="Lyrics container localized.")

            except TimeoutException:
                self._queue_handler(msg="Primary selector failed. Initiating legacy fallback...")
                containers = self.driver.find_elements(By.CSS_SELECTOR, datalyricscontainerfallback) #type: ignore

            if containers:
                self._queue_handler(msg=f"Detected {len(containers)} lyrical segments. Beginning extraction...")

                lyrics_text = []
                for container in containers:
                    text = self.driver.execute_script("return arguments[0].innerText;", container)#type: ignore
                    if text:
                        lyrics_text.append(text.strip())#type: ignore
                
                self._queue_handler(msg="Text buffer populated successfully.")
                full_lyrics = '\n\n'.join(lyrics_text).strip()#type: ignore
                return full_lyrics if full_lyrics else None
            else:
                self._queue_handler(msg="Error: Lyrics container not present on page.")
                return None

        except Exception as e:
            raise GeniusScraperError(f"Error extracting lyrics: {e}")

    def scrape(self, artist: str, song_title: str) -> dict | None:#type: ignore
      
        """
        Scrape lyrics from Genius for a given artist and song.
        
        Returns:
            dict with 'lyrics' and 'url' keys, or None if not found
        """
        if not artist.strip() or not song_title.strip():
            raise GeniusScraperError("Artist and song title cannot be empty")
        
        try:
            self._queue_handler(msg=f"Initializing request: {artist} - {song_title}...")
            song_url = self._search_genius(artist, song_title)
            
            if not song_url:
               # self._queue_handler(msg="Track not found in Genius repository.")
                return None

            self._queue_handler(msg="Accessing confirmed song page...")
            self.driver.get(song_url) #type: ignore
            
            lyrics = self._extract_lyrics()
            
            if not lyrics:
               self._queue_handler(msg="Failed to retrieve content from containers.")
               return None
            else:
                return {
                    'lyrics': lyrics,
                    'url': song_url
                } #type: ignore
        except GeniusScraperError:
            raise
        except Exception as e:
            raise GeniusScraperError(f"Unexpected error during scraping: {e}")

    def close(self):
        """Close the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                self._queue_handler(msg="Secure session terminated.")
            except:
                pass
        self.driver = None

    def __del__(self):
        """Ensure driver is closed on object destruction."""
        self.close()


if __name__ == "__main__":
    app = GeniusScraper()
    lyrics = app.scrape(artist='playboi carti', song_title='different day')
    print(lyrics)

