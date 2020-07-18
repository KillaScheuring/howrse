from selenium import webdriver
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from pprint import pprint
import time
import random

driver = webdriver.Chrome(executable_path=r"C:\Users\killa\Downloads\chromedriver_win32\chromedriver.exe")

driver.get("https://www.howrse.com/elevage/chevaux/")

update = []
nada = []
index = 0
driver.find_element_by_class_name("as-oil__btn-optin").click()
time.sleep(2)
driver.find_element_by_id("login").send_keys("")
driver.find_element_by_id("password").send_keys("")
driver.find_element_by_id("password").send_keys(Keys.ENTER)

time.sleep(1)

for refresh in range(0, 1000):
    time.sleep(3)
    links = driver.find_elements_by_tag_name("a")
    try:
        driver.find_element_by_id("Ufo_0").click()
        index += 1
        time.sleep(2)
    except selenium.common.exceptions.NoSuchElementException:
        nada.append("nope")

    links[0].click()

    if index > 100:
        break
    continue

print(index)
