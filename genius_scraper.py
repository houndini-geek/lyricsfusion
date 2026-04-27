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
    
    def _queue_handler(self,msg:str):
       
        message.put(msg) #type: ignore


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
        return self._match.match(str1,str2,score=80) #type: ignore
    
    def _matchArtistName(self,str1,str2):#type: ignore
        return self._match.match(str1,str2,score=80)#type: ignore


    def _build_genius_url(self, artist: str, song_title: str) -> str:
        """Build Genius URL from artist and song title."""
        import urllib.parse
        #print("Step 1")
        #print("Build Genius URL from artist and song title.")
        self._queue_handler(msg='Build Genius URL from artist and song title.')
        # Genius URL format: genius.com/Artist-Song-lyrics
        query = f"{artist} {song_title}"
        encoded_query = urllib.parse.quote(query)
       # https://genius.com/search?q=plaboi%20carti%20evil%20jordan
        url : str = f"https://genius.com/search?q={encoded_query}"
        return url

    def _search_genius(self, artist: str, song_title: str) -> str | None:
        """
        Search Genius and return the actual URL of the first result if found.
        """
        try:
            url = self._build_genius_url(artist, song_title)
            self._queue_handler(url)
            #print(f"Open browser: {url}")
            self._queue_handler(msg=f"Open browser: {url}")

            self.driver.maximize_window()#type: ignore
            
            #print("Calling driver.get(url)...")
            self._queue_handler(msg="Calling driver.get(url)...")
            try:
                self.driver.get(url)#type: ignore
            except TimeoutException:
                #print("driver.get(url) timed out (page load timeout)!")
                self._queue_handler(msg="driver.get(url) timed out (page load timeout)!")

                return None
            
            #print("Waiting for page to load...")
            self._queue_handler(msg="Waiting for page to load...")
            time.sleep(2) # Give it a moment to render dynamic content
            
            #print(f"Browser opened: {self.driver.title}")
            self._queue_handler(msg=f"Browser opened: {self.driver.title}")#type: ignore


            #print("Waiting for 'Show more song' button...")
            self._queue_handler(msg="Waiting for 'Show more song' button...")

            try:
                showMoreButton = self.wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/routable-page/ng-outlet/search-results-page/div/div[2]/div[1]/div[2]/search-result-section/div/a')))
                showMoreButton.click()
                #print("'Show more button clicked!'")
                self._queue_handler(msg="'Show more button clicked!'")

            except (TimeoutException, NoSuchElementException):
                artist_clean = artist.lower().replace(" ",'-')
                title_clean = song_title.lower().replace(" ",'-')
                direcURL = f"https://genius.com/{artist_clean}-{title_clean}-lyrics"
                self._queue_handler(msg="Couldn't found the 'Show more button'")

                #print("Couldn't found the 'Show more button'")
                #print(f"Try with direct URL: {direcURL}")
                self._queue_handler(msg=f"Try with direct URL: {direcURL}")
                
                return direcURL
            # Try to find the result cards
            time.sleep(2)
            try:
                #print("Searching for 'search-result-paginated-section'")
                self._queue_handler(msg="Searching for 'search-result-paginated-section'")

                search_result = self.driver.find_element(By.TAG_NAME, 'search-result-paginated-section')#type: ignore
                if search_result:
                   # print("'search-result-paginated-section' Found!")
                    self._queue_handler(msg="'search-result-paginated-section' Found!")

                    #print("Checking for mini-song-card")
                    self._queue_handler(msg="Checking for mini-song-card")

                    mini_card_songs = search_result.find_elements(By.TAG_NAME,'mini-song-card')
                    #print(f"mini-song-card found: {len(mini_card_songs)}")
                    self._queue_handler(msg=f"mini-song-card found: {len(mini_card_songs)}")

                    if mini_card_songs:
                        for card in mini_card_songs:
                            try:
                                #print("Checking for mini_card-title AND mini_card-subtitle")
                                self._queue_handler(msg="Checking for mini_card-title AND mini_card-subtitle")

                                title = card.find_element(By.CLASS_NAME,'mini_card-title').text.strip().lower()
                                subtitle = card.find_element(By.CLASS_NAME,'mini_card-subtitle').text.strip().lower()
                                #print("Checking for MATCH")
                                self._queue_handler(msg="Checking for MATCH")

                                if self._matchTitle(str1=title,str2=song_title) and self._matchArtistName(str1=subtitle,str2=artist): #type: ignore
                                    #print(f"match found for : {song_title} : {artist}")
                                    self._queue_handler(msg=f"match found for : {song_title} : {artist}")

                                    card_url = card.find_element(By.TAG_NAME,'a').get_attribute('href')#type: ignore
                                    return card_url
                            except NoSuchElementException:
                                print("mini_card-title AND mini_card-subtitle not found - page has changed")
                                self._queue_handler(msg="mini_card-title AND mini_card-subtitle not found - page has changed")
                                return None
                else:
                    print("Search result paginated section NOT FOUND!")
                    self._queue_handler(msg="Search result paginated section NOT FOUND!")

                    return None
            except Exception as e :
                raise GeniusScraperError(f"Error searching Genius: {e}")

        except Exception as e:
            raise GeniusScraperError(f"Error searching Genius: {e}")
          

    def _extract_lyrics(self) -> str | None:
        """Extract lyrics from the current page."""
        try:
            
            # Wait for lyrics containers to load
            # The class name often contains 'Lyrics__Container'
            #print("Looking for the lyrics container")
            try:
               # print("Waiting for data-lyrics-container")
                self._queue_handler(msg="Waiting for data-lyrics-container")

                # Modern Genius uses data-lyrics-container attribute
                containers = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-lyrics-container='true']"))
                )
                #print("Container found")
                self._queue_handler(msg="Container found")

            except TimeoutException:
                # Fallback to old class-based selector if needed
                print("Data attribute not found, trying class-based selector...")
                self._queue_handler(msg="Data attribute not found, trying class-based selector...")

                containers = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='Lyrics__Container']") #type: ignore

            if containers:
                #print(f"Found {len(containers)} lyrics containers.")
                self._queue_handler(msg=f"Found {len(containers)} lyrics containers.")

                lyrics_text = []
                self._queue_handler(msg='Lyrics extraction started...')

                for container in containers:
                    # Get text with line breaks preserved
                    # We can use get_attribute('innerText') or execute script to preserve formatting
                    text = self.driver.execute_script("return arguments[0].innerText;", container)#type: ignore
                    if text:
                        lyrics_text.append(text.strip())#type: ignore
                
                self._queue_handler(msg='Lyrics extracted')
                full_lyrics = '\n\n'.join(lyrics_text).strip()#type: ignore
                return full_lyrics if full_lyrics else None
            else:
                #print("Lyrics containers NOT FOUND")
                self._queue_handler(msg="Lyrics containers NOT FOUND")
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
            #print(f"Starting scraping for {artist} - {song_title}...")
            self._queue_handler(msg=f"Starting scraping for {artist} - {song_title}...")
            song_url = self._search_genius(artist, song_title)
            
            if not song_url:
                #print("Song URL not found during search.")
                self._queue_handler(msg="Song URL not found during search.")
                return None
            #print(f"Navigating to song page: {song_url}")
            self._queue_handler(msg=f"Navigating to song page: {song_url}")

            self.driver.get(song_url) #type: ignore
            
            lyrics = self._extract_lyrics()
            
            if not lyrics:
               #print("Failed to extract lyrics.")
               self._queue_handler(msg="Failed to extract lyrics.")

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
                #print("Operation terminated")
                self._queue_handler(msg="Operation terminated")
            except:
                pass
        self.driver = None

    def __del__(self):
        """Ensure driver is closed on object destruction."""
        self.close()


# if __name__ == "__main__":
#     app = GeniusScraper()
#     lyrics = app.scrape(artist='playboi carti', song_title='just better')
#     print(lyrics)

