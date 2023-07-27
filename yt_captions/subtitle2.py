# deprecated

import sys
import time
import urllib.request

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class YoutubeSubtitlesScraper:
    def __init__(self, start_url):
        self.driver = webdriver.Chrome(service=Service("D:/Python/chromedriver.exe"))
        self.wait = WebDriverWait(self.driver, 10)
        self.start_url = start_url
        self.videos = None
        self.index = 0

    def __enter__(self):
        self.driver.get(self.start_url)
        self.display_all_videos()
        # self.videos = [(video.text, video.get_attribute("snap"))
        #                for video in self.driver.find_elements(By.CSS_SELECTOR, "#video-title")]
        self.videos = [(video.text, video.get_attribute("href"))
                       for video in self.driver.find_elements(By.CLASS_NAME, "yt-uix-tile-link")]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index == len(self.videos):
            raise StopIteration
        filename, link = self.videos[self.index]
        print(f"filename, {filename}, link: {link}")
        self.index += 1
        if link:
            self.driver.get(link)
        self.enable_subtitles()
        link = self.get_subtitles_link()
        content = self.scrape_subtitles(link) if link else "No Closed Captions"
        return filename, link, content

    def display_all_videos(self):
        """ Clicks on "Load More" button to display all users videos """
        while True:
            try:
                element = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "yt-uix-load-more")))
                element.click()
            except TimeoutException:
                break

    def enable_subtitles(self):
        """ Clicks on CC(Closed Caption) button in Youtube video """
        show_subtitles_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ytp-subtitles-button")))
        show_subtitles_button.click()

    def get_subtitles_link(self):
        """ Find string in performance timings that contains the substring 'srv3' which is the subtitle link. """
        time.sleep(1)
        timings = self.driver.execute_script("return window.performance.getEntries()")

        for timing in timings:
            for value in timing.values():
                if 'srv3' in str(value):
                    return value
        return ""

    def scrape_subtitles(self, subtitle_link):
        """ HTML parses subtitles """
        response = urllib.request.urlopen(subtitle_link)
        soup = BeautifulSoup(response, "lxml")
        return soup.get_text(strip=True)


def create_file(filename, link, subtitles):
    """ Create file for the subtitles """
    title = "".join(c for c in filename if c.isalpha() or c.isdigit() or c == " ").rstrip()
    print(title)
    with open(f"{title}.txt", "w") as file:
        file.write(f"LINK: {link}\n")
        file.write(subtitles)


def main():
    start_url = sys.argv[1]
    print("Starting program...")
    with YoutubeSubtitlesScraper(start_url) as scraper:
        print(scraper.videos)
        print("within scraper...")
        for filename, link, content in scraper:
            print(filename, link, content)
            pass
            # try:
            #     create_file(filename, link, content)
            #     print("successfully finish it")
            # except Exception as e:
            #     print(f"Error occurred: {str(e)}")
        print("end for-loop")


if __name__ == '__main__':
    main()
