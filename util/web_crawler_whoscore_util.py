from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# noinspection SpellCheckingInspection
def close_whoscore_cover_div(driver: webdriver) -> None:
    # If a div that covers the whole screen appears, close it
    try:
        wait = WebDriverWait(driver, 3)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.webpush-swal2-close[aria-label='Close "
                                                                      "this dialog']")))

        button = driver.find_element(By.CSS_SELECTOR, "button.webpush-swal2-close[aria-label='Close this dialog']")
        button.click()
    except (NoSuchElementException, TimeoutException):
        print("<EXC---[No webpush-swal2-close button found, no cover DIV appeared]--->")
