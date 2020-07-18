from selenium import webdriver
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from pprint import pprint
import time
import random
import math

blupping_horse_id = 64123625
# blupping_horse_id = 64066576
sire_horse_id = 64124325

types_of_training = [
    "entrainementEndurance",
    "entrainementVitesse",
    "entrainementDressage",
    "entrainementGalop",
    "entrainementTrot",
    "entrainementSaut"
]

rides = {
    "forest": {
        "button": "boutonBalade-foret",
        "slider": "walkforetSlider",
        "submit": "walk-foret-submit"
    },
    "mountain": {
        "button": "boutonBalade-montagne",
        "slider": "walkmontagneSlider",
        "submit": "walk-montagne-submit"
    }
}

driver = webdriver.Chrome(executable_path=r"C:\Users\killa\Downloads\chromedriver_win32\chromedriver.exe")


def login(url):
    driver.get(url)

    driver.find_element_by_class_name("as-oil__btn-optin").click()
    time.sleep(2)
    driver.find_element_by_id("login").send_keys("Older_Sister")
    driver.find_element_by_id("password").send_keys("floweryard")
    driver.find_element_by_id("password").send_keys(Keys.ENTER)


def get_blup():
    time.sleep(1)
    genetic_blup = driver.find_element_by_id("genetic-body-content").find_element_by_class_name("nowrap").text
    genetic_blup = int(genetic_blup) if genetic_blup else -100
    return genetic_blup


def get_age():
    raw_age = driver.find_element_by_id("characteristics-body-content") \
        .find_elements_by_class_name("last")[0].text.split(": ")[1]
    age = 0
    if raw_age == "a few hours":
        age = 0
    elif "year" not in raw_age:
        months = int(raw_age.split(" ")[0])
        age = months/12
    elif "year" in raw_age:
        if "month" in raw_age:
            years, _, months, _ = raw_age.split(" ")
            years = int(years)
            months = int(months)
        else:
            years = raw_age.split(" ")[0]
            years = int(years)
            months = 0
        age = years + (months/12)

    return age


def board_at_equestrian_center():
    time.sleep(2)
    driver.find_element_by_id("fourrageCheckbox").click()
    time.sleep(1)

    driver.find_element_by_id("avoineCheckbox").click()
    time.sleep(1)

    driver.find_element_by_id("carotteCheckbox").click()
    time.sleep(1)

    driver.find_element_by_id("mashCheckbox").click()
    time.sleep(1)

    driver.find_element_by_class_name("button-style-0").click()
    time.sleep(1)

    buttons = driver.find_element_by_id("table-0").find_elements_by_tag_name("button")

    for button in buttons:
        if "disabled" not in button.get_attribute("class"):
            button.click()
            break
    time.sleep(1)

    alert = driver.switch_to.alert
    alert.accept()

    time.sleep(2)


def put_to_bed(age_up):
    driver.find_element_by_id("boutonCoucher").click()
    time.sleep(1)

    if age_up:
        driver.find_element_by_id("boutonVieillir").click()
        time.sleep(1)
        driver.find_element_by_id("age").find_element_by_class_name("button-text-0").click()
        time.sleep(2)


def care_for(mash):
    try:
        driver.find_element_by_id("cheval-inscription").find_element_by_tag_name("a").click()
        needs_new_home = True
    except selenium.common.exceptions.WebDriverException:
        needs_new_home = False

    if needs_new_home:
        board_at_equestrian_center()

    driver.find_element_by_id("boutonCaresser").click()
    time.sleep(1)

    driver.find_element_by_id("boutonBoire").click()
    time.sleep(1)

    driver.find_element_by_id("boutonCarotte").click()
    time.sleep(1)

    driver.find_element_by_id("boutonPanser").click()
    time.sleep(1)

    if mash:
        driver.find_element_by_id("boutonMash").click()
        time.sleep(1)

    age = get_age()

    print(age)

    if age < 0.5:
        driver.find_element_by_id("boutonAllaiter").click()
    else:
        driver.find_element_by_id("boutonNourrir").click()
        time.sleep(1)
        oats = True
        if "year" not in age:
            hay_amount = 4
            oats = False
        elif int(age.split(" ")[0]) <= 2:
            hay_amount = 6
        else:
            hay_amount = 8
        hay_slider = driver.find_element_by_id("haySlider")
        hay_slider.find_elements_by_class_name("slider-number")[hay_amount].click()
        if oats:
            oat_slider = driver.find_element_by_id("oatsSlider")
            oat_slider.find_elements_by_class_name("slider-number")[5].click()
        driver.find_element_by_id("feed-button").click()
        time.sleep(1)


def compete_till_tired(rotate, fullday):
    competitions = ["cso", "dressage", "galop", "trot", "cross"]
    competition_index = 0
    energy = int(driver.find_element_by_id("energie").text)
    horse_time = int(driver.find_element_by_class_name("hour").text.split(":")[0])

    time_limit = 22 if fullday else 20
    energy_limit = 20 if fullday else 40

    while energy >= energy_limit and horse_time < time_limit:
        driver.get("https://www.howrse.com/elevage/competition/inscription?cheval=%s&competition=%s" %
                   (blupping_horse_id, competitions[competition_index]))
        time.sleep(2)
        try:
            driver.find_element_by_class_name("button-text-0").click()
        except selenium.common.exceptions.WebDriverException:
            print("can't click")
            driver.get("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % blupping_horse_id)
            return
        time.sleep(2)
        energy = int(driver.find_element_by_id("energie").text)
        horse_time = int(driver.find_element_by_class_name("hour").text.split(":")[0])
        if rotate:
            competition_index += 1
            if competition_index == len(competitions):
                competition_index = 0


def train_till_tired(type_of_training, fullday):
    energy = int(driver.find_element_by_id("energie").text)
    raw_time = driver.find_element_by_class_name("hour").text
    # horse_time = int(raw_time.split(":")[0]) + (0.5 if int(raw_time.split(":")[1]))
    horse_time = int(raw_time.split(":")[0])

    if type_of_training == "forest" or type_of_training == "mountain":
        min_energy_required = 9
        min_time_required = 1
        while energy >= min_energy_required and horse_time <= 24 - min_time_required:
            time.sleep(1)
            riding_time = math.floor(energy / min_energy_required)
            driver.find_element_by_id(rides[type_of_training]["button"]).click()
            time.sleep(1)
            forest_slider = driver.find_element_by_id(rides[type_of_training]["slider"])
            forest_slider.find_elements_by_tag_name("li")[riding_time].click()
            time.sleep(0.5)
            driver.find_element_by_id(rides[type_of_training]["submit"]).click()
            time.sleep(1)
            energy = int(driver.find_element_by_id("energie").text)
            horse_time = int(raw_time.split(":")[0])
    elif type_of_training == "training":
        min_energy_required = 45
        min_time_required = 3
        while energy >= min_energy_required and horse_time <= 24 - min_time_required:
            time.sleep(1)
            for training_type in types_of_training:
                try:
                    training_button = driver.find_element_by_id(training_type)
                    not_finished = True
                except selenium.common.exceptions.NoSuchElementException or selenium.common.exceptions.StaleElementReferenceException:
                    training_button = None
                    not_finished = False
                if not_finished:
                    training_button.click()
                    break
            energy = int(driver.find_element_by_id("energie").text)
            horse_time = int(raw_time.split(":")[0])
    elif type_of_training == "play":
        min_energy_required = 8
        min_time_required = 1
    else:
        compete_till_tired(True, fullday)
        return


def run_cover_mare():
    time.sleep(2)
    driver.get("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % sire_horse_id)
    energy = int(driver.find_element_by_id("energie").text)
    horse_time = int(driver.find_element_by_class_name("hour").text.split(":")[0])

    if energy > 40 and horse_time < 20:
        driver.find_element_by_id("reproduction-tab-0").find_elements_by_class_name("tab-action")[1].click()
        driver.find_element_by_id("formMalePublicTypeMoi").click()
        time.sleep(1)
        driver.find_element_by_id("boutonMaleReproduction").click()
    else:
        care_for(True)
        if energy > 40 and horse_time < 20:
            driver.find_element_by_id("reproduction-tab-0").find_elements_by_class_name("tab-action")[1].click()
            driver.find_element_by_id("formMalePublicTypeMoi").click()
            time.sleep(1)
            driver.find_element_by_id("boutonMaleReproduction").click()
        else:
            put_to_bed(True)
            run_cover_mare()
    time.sleep(1)
    driver.get("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % blupping_horse_id)


def run_birth():
    time.sleep(2)
    driver.find_element_by_id("poulain-1").send_keys("temp")
    driver.find_element_by_id("poulain-1").send_keys(Keys.ENTER)
    time.sleep(1)
    gender = driver.find_element_by_id("characteristics-body-content") \
        .find_elements_by_class_name("first")[2].text.split(": ")[1]
    driver.find_element_by_id("tab-genetics-title").click()
    genetic_potential = driver.find_element_by_id("genetic-body-content") \
        .find_element_by_class_name("last").text.split(": ")[1]

    new_name = "%s %s" % (gender[0], genetic_potential)

    driver.find_element_by_class_name("button-align-14").click()
    driver.find_element_by_class_name("options-menu").find_element_by_tag_name("li").click()
    driver.find_element_by_id("horseNameName").clear()
    driver.find_element_by_id("horseNameName").send_keys(new_name)
    breeding_farms = driver.find_element_by_id("horseNameElevage")
    breeding_farms.click()
    breeding_farms.find_element_by_tag_name("option").click()
    driver.find_element_by_id("horseNameName").send_keys(Keys.ENTER)

    print()
    print(new_name)
    print()

    time.sleep(1)

    care_for(False)

    put_to_bed(False)

    time.sleep(1)

    run_cover_mare()
    time.sleep(1)
    driver.get("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % blupping_horse_id)


def check_reproduction(cover):
    time.sleep(1)
    print("Checking for birth...")
    try:
        driver.find_element_by_id("boutonVeterinaire").click()
        birth = True
    except selenium.common.exceptions.WebDriverException:
        birth = False

    if birth:
        print("Birthing foal...")
        run_birth()

    if cover:
        print("Checking for cover offer...")
        reproduction_bottom = driver.find_element_by_id("reproduction-bottom")
        try:
            time.sleep(1)
            reproduction_bottom.find_element_by_class_name("item-relative").click()
            time.sleep(1)
            driver.find_element_by_id("boutonDoReproduction").click()
            time.sleep(1)
            ready_to_cover = True
        except selenium.common.exceptions.WebDriverException as e:
            print(e)
            ready_to_cover = False
        if ready_to_cover:
            print("Running cover...")
            time.sleep(2)
            run_cover_mare()
            time.sleep(1)


def blup(cover):
    genetic_blup = get_blup()
    print(genetic_blup)

    age = get_age()

    while age < 30:
        if cover:
            print("Will cover this horse...")
            check_reproduction(True)

        compete_till_tired(False, True)

        care_for(False)

        compete_till_tired(False, True)

        driver.find_element_by_id("boutonCoucher").click()
        time.sleep(1)
        driver.find_element_by_id("boutonVieillir").click()
        time.sleep(1)
        driver.find_element_by_id("age").find_element_by_class_name("button-text-0").click()
        time.sleep(2)


def cycle_through_horses(starter_id):
    login("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % starter_id)
    time.sleep(1)
    current_horse_id = 0
    while int(current_horse_id) != starter_id:
        check_reproduction(False)
        # care_for()
        time.sleep(1)
        driver.find_element_by_id("nav-next").click()
        time.sleep(1)
        horse_name = driver.find_elements_by_class_name("horse-name")[-1]
        horse_name.click()
        time.sleep(1)
        current_horse_id = driver.current_url.split("=")[1]


# cycle_through_horses(63821317)
login("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % blupping_horse_id)
# login("https://www.howrse.com/elevage/chevaux/choisirNoms?jument=64123625")

time.sleep(1)

# run_cover_mare()
# time.sleep(1)
# driver.get("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % blupping_horse_id)

blup(True)
# run_birth()
# while True:
#     train_till_tired("mountain", True)
#     time.sleep(1)
#     care_for(True)
#     time.sleep(1)
#     train_till_tired("mountain", True)
#     put_to_bed(True)
