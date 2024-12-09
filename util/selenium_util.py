import re
import time
from operator import truediv

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from .util_msg import msg, err


def click_select_option(driver, select_id: str, option_text: str, wait4it: bool = False, wait4it_time: int = 3) -> None:
    """
        This function clicks on a select option
    """
    if wait4it:
        try:
            WebDriverWait(driver, wait4it_time).until(
                lambda d: d.find_element(By.XPATH, f"//select[@id='{select_id}']"))
        except TimeoutException:
            err(f"[Waiting for select.id: {select_id} caused timeout]")

    select = driver.find_element(By.XPATH, f"//select[@id='{select_id}']")
    for option in Select(select).options:
        if bool(re.match(option_text, option.text)):
            option.click()
            break


def click_element_xpath(driver, xpath: str, wait4it: bool = False, wait4it_time: int = 3, wait_after: int = 0) -> None:
    """
        This function clicks on an element by xpath
    """
    if wait4it:
        try:
            WebDriverWait(driver, wait4it_time).until(lambda d: d.find_element(By.XPATH, xpath))
        except TimeoutException:
            err(f"[Waiting for xpath: {xpath} caused timeout]")

    driver.find_element(By.XPATH, xpath).click()

    if wait_after > 0:
        time.sleep(wait_after)


def click_element_xpath_by_script(driver, xpath: str, wait_after: int = 0, wait4it: bool = False, wait4it_time: int = 3) -> None:
    """
        This function clicks on an element by xpath
    """
    if wait4it:
        try:
            WebDriverWait(driver, wait4it_time).until(lambda d: d.find_element(By.XPATH, xpath))
        except TimeoutException:
            err(f"[Waiting for xpath: {xpath} caused timeout]")

    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, xpath))

    if wait_after > 0:
        time.sleep(wait_after)


def click_and_wait(driver, xpath: str, xpath_2_wait: str) -> None:
    """
        This function clicks on an element by xpath and wait till xpath_2_wait element changes
    """
    wait_4_html = driver.find_element(By.XPATH, xpath_2_wait).get_attribute("outerHTML")

    try:
        WebDriverWait(driver, 2).until(lambda d: d.find_element(By.XPATH, xpath))
    except TimeoutException:
        err(f"[Click and wait: {xpath} not found]")

    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, xpath))

    WebDriverWait(driver, 7).until(lambda d: check_for_changes(d, wait_4_html, xpath_2_wait), "Waiting for changes caused timeout")


def click_and_wait_inner(driver,  we: WebElement, xpath_2_click: str, xpath_2_wait: str) -> None:
    """
        This function clicks on an inner element by xpath and wait till xpath_2_wait element changes
    """
    wait_4_html = we.find_element(By.XPATH, xpath_2_wait).get_attribute("outerHTML")

    try:
        WebDriverWait(driver, 2).until(EC.visibility_of(we))
    except TimeoutException:
        err(f"[Waiting for web element: {we} caused timeout]")

    driver.execute_script("arguments[0].click();", we.find_element(By.XPATH, xpath_2_click))

    WebDriverWait(we if we is not None else driver, 7).until(lambda d: check_for_changes(d, wait_4_html, xpath_2_wait), "Waiting for changes caused timeout")


def click_element_by_script(driver, we: WebElement, wait_after: int = 0, wait4it: bool = False, wait4it_time: int = 3) -> None:
    """
        This function clicks on an element by xpath
    """
    if wait4it:
        try:
            WebDriverWait(driver, wait4it_time).until(EC.visibility_of(we))
        except TimeoutException:
            err(f"[Waiting for web element: {we} caused timeout]")

    driver.execute_script("arguments[0].click();", we)

    if wait_after > 0:
        time.sleep(wait_after)


def click_element_by_script_wait_4_element(driver, we: WebElement, xpath_2_wait) -> None:
    """
        This function clicks on an element by xpath
    """
    wait_4_html = driver.find_element(By.XPATH, xpath_2_wait).get_attribute("outerHTML")

    try:
        WebDriverWait(driver, 2).until(EC.visibility_of(we))
    except TimeoutException:
        err(f"[Waiting for web element: {we} caused timeout]")

    driver.execute_script("arguments[0].click();", we)

    WebDriverWait(driver, 7).until(lambda d: check_for_changes(d, wait_4_html, xpath_2_wait), "Waiting for changes caused timeout")


def wait_til_filled(driver, xpath: str, wait4it_time: int = 3) -> bool:
    """
        This function waits until an element gets filled
    """
    try:
        WebDriverWait(driver, wait4it_time).until(lambda d: len(d.find_element(By.XPATH, xpath).text) > 0)
        msg(f"[xpath: {xpath} got filled]")
        return True
    except TimeoutException:
        err(f"[Waiting for xpath: {xpath} to get filled caused timeout]")

    raise Exception(f"<EXC---[Waiting for xpath: {xpath} to get filled caused timeout]--->")


def build_url(current_url, href: str) -> str:
    return current_url.split("/")[0] + "//" + current_url.split("/")[2] + href


def check_for_changes(driver, initial_html: str, xpath_2_wait: str) -> bool:
    current_html = driver.find_element(By.XPATH, xpath_2_wait).get_attribute("outerHTML")
    if initial_html != current_html:
        return True
    return False


def click_select(select_element: WebElement, option_text: str) -> bool:
    select_obj = Select(select_element)

    # Get all options
    options = select_obj.options

    # Find the option with the desired text
    for option in options:
        if option.text == option_text:
            option.click()
            return True

    return False


#get selected option text
def get_select_current_text(select_element: WebElement) -> str:
    select_obj = Select(select_element)
    return select_obj.first_selected_option.text


def get_select_by_index_text(select_element: WebElement, index: int) -> str:
    select_obj = Select(select_element)
    return select_obj.options[index].text if len(select_obj.options) > index else ""