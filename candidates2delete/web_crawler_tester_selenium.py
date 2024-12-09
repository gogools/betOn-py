import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# preparing options to avoid opening the browser
options = Options()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')  # Last I checked this was necessary.

with webdriver.Firefox(options=options) as driver:

    wait = WebDriverWait(driver, 2)

    url = 'https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League'
    driver.get(url)
    time.sleep(3)
    source = driver.page_source
    soup = BeautifulSoup(source, 'html.parser')
    # print(soup.prettify())

    title = soup.title.text  # Access the <title> element's text content
    print(title.strip())

    links = [a.get("href") for a in soup.find_all("a")]
    print(f"\npage links: \n{links}")

    # here we tell to soup to get the link with the body content "Fixtures"
    # and then we get the link
    link_page_element = soup.find("a", string="Fixtures")
    print(f"\npage element with 'Fixtures' as a string: \n{link_page_element.get("href")}")

    fixture_links = [a.get("href") for a in soup.findAll("a", string="Fixtures")]
    print(f"\npage link elements with 'Fixtures' as a string: \n{fixture_links}")

    # here we tell to the browser to click on the link with title "View next week"
    # and then we get the link
    print("\nClicking few elements:\n")
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[title='View next week']"))).click()
        print("a[title='View next week'] -> clicked \n")

        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Team Statistics']"))).click()
        print("//a[text()='Team Statistics'] -> clicked \n")

    except NoSuchElementException:
        print(f"\nElement not found: {NoSuchElementException.args[0]}")

# here we are goig to consume data from an API using requests
# import requests
#
# url = "https://api.github.com/users/andrewbeattycourseware/followers"
# response = requests.get(url)
# data = response.json()
