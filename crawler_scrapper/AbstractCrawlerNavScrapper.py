import os
import re
import time
from abc import ABC, abstractmethod
from enum import Enum

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

# mine
from util import exc, msg, err, show_table


class AbstractCrawlerNavScrapper(ABC):
    driver = None
    soup = None
    REGEX = None
    base_url = None

    class Browser(Enum):
        CHROME = 'Chrome'
        FIREFOX = 'Firefox'
        SAFARI = 'Safari'

    def __init__(self, hide_browser: bool = True, browser: Browser = Browser.CHROME):

        options = None

        if browser == self.Browser.CHROME:
            options = webdriver.ChromeOptions()
        elif browser == self.Browser.FIREFOX:
            options = webdriver.FirefoxOptions()
        elif browser == self.Browser.SAFARI:
            options = webdriver.SafariOptions()

        if hide_browser:
            user_data_dir = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Google", "Chrome",
                                         "Default")

            options.add_argument("--user-data-dir=" + user_data_dir)
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')  # Last I checked this was necessary.
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/108.0.0.0 Safari/537.36")

        if browser == self.Browser.CHROME:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) # webdriver.Chrome(options=options)
        elif browser == self.Browser.FIREFOX:
            self.driver = webdriver.Firefox(options=options)
        elif browser == self.Browser.SAFARI:
            self.driver = webdriver.Safari(options=options)

        msg(f"Driver initialized: {browser}")
        WebDriverWait(self.driver, 7).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.driver.implicitly_wait(7)


    @abstractmethod
    def _navigate(self):
        pass

    @abstractmethod
    def _scrap(self) -> dict:
        pass

    @abstractmethod
    def _validate_required_fields(self) -> bool:
        pass

    def scrap(self, url: str = None) -> dict:

        url = url if url is not None else self.base_url
        msg(f"Waiting for page to load. Url: {url}")
        start_time = time.time()
        self.driver.get(url)
        msg(f"Page loaded. Took: {time.time() - start_time} seconds")

        if not self._validate_required_fields():
            err("Required fields are not valid")
            return dict()

        try:
            if not re.match(rf"{self.base_url}{self.REGEX}", self.driver.current_url):
                self._navigate()

            mined_stuff = self.do_some_extra_stuff(self._scrap())

            return mined_stuff

        except Exception as e:
            exc(e, "An error occurred while navigating or scraping.")
            return dict()
        finally:
            self.driver.quit()
            msg("scraping done")

    def crawl(self) -> dict:
        pass

    def do_some_extra_stuff(self, mined_stuff: dict) -> dict:
        msg(f"Doing some extra stuff in {self.driver.current_url}")
        return mined_stuff

    def scrap_and_print(self, url: str = None) -> dict:
        data = self.scrap(url if url is not None else self.base_url)
        show_table(data)
        return data
