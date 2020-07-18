from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from pprint import pprint
import time

driver = webdriver.Chrome(executable_path=r"C:\Users\killa\Downloads\chromedriver_win32\chromedriver.exe")

driver.get("https://www.howrse.com/elevage/chevaux/")

update = []

driver.find_element_by_id("login").send_keys("")
driver.find_element_by_id("password").send_keys("")
driver.find_element_by_id("password").send_keys(Keys.ENTER)

time.sleep(1)

horses = [horse.text for horse in driver.find_elements_by_class_name("horsename")]


for horse_name in horses:
    # Set up report
    report = {}

    # Get horse's name
    print(horse_name)
    report.setdefault("name", horse_name)

    time.sleep(1)

    horse = None
    for link in driver.find_elements_by_tag_name("a"):
        if link.text == horse_name:
            horse = link

    # Go to this horse
    horse.click()

    # Wait for page to load
    time.sleep(1)

    # # Get the horse's states
    # report.setdefault("characteristics", {})
    # characteristics = driver.find_element_by_id("characteristics-body-content")
    # for characteristic in \
    #         characteristics.find_elements_by_class_name("first") + \
    #         characteristics.find_elements_by_class_name("last"):
    #
    #     if characteristic.text:
    #         label, value = characteristic.text.split(": ")
    #         report["characteristics"].setdefault(label, value)
    #
    # # Get the horse's genetics
    # report.setdefault("genetic", {}).setdefault("potential", {})
    # genetics = driver.find_element_by_id("genetic-body-content")
    # for index, genetic_potential in enumerate(genetics.find_elements_by_tag_name("tr")):
    #
    #     cells = [cell.get_attribute("innerHTML") for cell in genetic_potential.find_elements_by_tag_name("td")]
    #
    #     if "" == cells[0]:
    #         continue
    #
    #     if "potential" in cells[0]:
    #         total = cells[2]
    #         label_1, value_1 = total.split(": ")
    #         report["genetic"]["potential"].setdefault(label_1.split(">")[1], value_1.split("<")[0])
    #     elif "BLUP" in cells[0]:
    #         label_1 = "BLUP"
    #         value_1 = genetic_potential.find_elements_by_tag_name("td")[-1].get_attribute("innerHTML").split(">")[1].split("<")[0]
    #         report["genetic"]["potential"].setdefault(label_1, value_1)
    #     else:
    #         label_1, value_1, label_2, value_2 = [cell.split(">")[1].split("<")[0] for cell in cells if "span" in cell]
    #         report["genetic"]["potential"].setdefault(label_1, value_1)
    #         report["genetic"]["potential"].setdefault(label_2, value_2)
    #
    # report["genetic"].setdefault("excellence", {})
    # excellence = driver.find_element_by_id("excellence")
    # for index, excellency in enumerate(excellence.find_elements_by_tag_name("tr")):
    #     if "horse" in excellency.find_elements_by_tag_name("td")[0].get_attribute("innerHTML"):
    #         cell = excellency.find_elements_by_tag_name("td")[0].get_attribute("innerHTML")
    #         report["genetic"]["excellence"].setdefault("Total",
    #                                                    cell.split(">")[1].split("<")[0] + " stars")
    #     else:
    #         label, value = excellency.find_elements_by_tag_name("td")[1].get_attribute("data-tooltip").split(": ")
    #         report["genetic"]["excellence"].setdefault(label, value)

    report.setdefault("maintenance", {})
    # Feed the horse
    if driver.find_element_by_id("boutonAllaiter"):
        print("Bottle Feed")
        # report["maintenance"].setdefault("feed", "Bottle Feed")
        # driver.find_element_by_id("boutonAllaiter").click()
    elif driver.find_element_by_id("boutonNourrir"):
        print("Feed")
        # report["maintenance"].setdefault("feed", "Fodder Feed")
        driver.find_element_by_id("boutonNourrir").click()
        fodder_quantity = driver.find_element_by_class_name("section-fourrage-target")
        oats_quantity = driver.find_element_by_class_name("section-avoine-target")
    else:
        print("No Button")
        # report["maintenance"].setdefault("feed", False)

    # Water the horse
    if driver.find_element_by_id("boutonBoire"):
        print("Water")
        # driver.find_element_by_id("boutonBoire").click()
        # report["maintenance"].setdefault("Water", True)
    else:
        print("No Button")
        # report["maintenance"].setdefault("Water", False)
    driver.back()
    time.sleep(3)
    update.append(report)

pprint(update)
# driver.close()
