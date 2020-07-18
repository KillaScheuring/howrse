from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from pprint import pprint
import time

driver = webdriver.Chrome(executable_path=r"C:\Users\killa\Downloads\chromedriver_win32\chromedriver.exe")

driver.get("https://www.howrse.com/currencies/videos")

update = []
driver.find_element_by_class_name("as-oil__btn-optin").click()
time.sleep(1)
driver.find_element_by_id("login").send_keys("")
driver.find_element_by_id("password").send_keys("")
driver.find_element_by_id("password").send_keys(Keys.ENTER)

time.sleep(4)
for _ in range(0, 1000):
    if driver.find_element_by_class_name("btn__label__text"):
        driver.find_element_by_class_name("btn__label__text").click()

    time.sleep(40)
    if driver.find_element_by_class_name("videoAdUiSkipButtonExperimentalText"):
        driver.find_element_by_class_name("videoAdUiSkipButtonExperimentalText").click()
    else:
        time.sleep(60)
    time.sleep(10)

    winnings_section = driver.find_elements_by_class_name("text--secondary")[-1]
    update.append(winnings_section)

    driver.find_element_by_class_name("popupview__close").click()
    if len(update) > 300:
        break

pprint(update)

