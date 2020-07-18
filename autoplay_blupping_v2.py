from selenium import webdriver
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from pprint import pprint
import time
import random
import math

blupping_horse_id = 64218662
sire_horse_id = 64191267

wait_time = 0.5

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
        "submit": "walk-foret-submit",
        "form": "walk-tab-balade-foret"
    },
    "mountain": {
        "button": "boutonBalade-montagne",
        "slider": "walkmontagneSlider",
        "submit": "walk-montagne-submit",
        "form": "walk-tab-balade-montagne"
    }
}

compete = False

driver = webdriver.Chrome(executable_path=r"C:\Users\killa\Downloads\chromedriver_win32\chromedriver.exe")


def click_element_by_id(element_id, iteration=1):
    element_exists = True
    try:
        driver.find_element_by_id(element_id).click()
    except selenium.common.exceptions.StaleElementReferenceException as e:
        print(e)
        if iteration > 3:
            return False
        else:
            return click_element_by_id(element_id, iteration+1)
    except selenium.common.exceptions.NoSuchElementException as e:
        print(e)
        element_exists = False
    finally:
        return element_exists


def login(url):
    driver.get(url)

    time.sleep(wait_time)

    driver.find_element_by_class_name("as-oil__btn-optin").click()
    time.sleep(wait_time)
    driver.find_element_by_id("login").send_keys("")
    driver.find_element_by_id("password").send_keys("")
    driver.find_element_by_id("password").send_keys(Keys.ENTER)


def get_blup():
    time.sleep(wait_time)
    try:
        genetic_blup = driver.find_element_by_id("genetic-body-content").find_element_by_class_name("nowrap").text
    except selenium.common.exceptions.NoSuchElementException:
        genetic_blup = None
    genetic_blup = int(genetic_blup) if genetic_blup else -100
    return genetic_blup


def get_age():
    raw_age = driver.find_element_by_id("characteristics-body-content") \
        .find_elements_by_class_name("last")[0].text.split(": ")[1]
    age = 0
    print("raw_age", raw_age)
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
    print("age", age)
    return age


def get_energy():
    time.sleep(wait_time)
    energy = None
    try:
        energy = int(driver.find_element_by_id("energie").text)
    except selenium.common.exceptions.NoSuchElementException as e:
        energy = None
        print(e)
    finally:
        return energy


def get_time():
    raw_time = driver.find_element_by_class_name("hour").text
    hour, minute = raw_time.split(":")
    hour = int(hour)
    minute = int(minute)
    horse_time = hour + (minute/60)
    print("time", horse_time)
    return horse_time


def board_at_equestrian_center():
    time.sleep(wait_time)
    click_element_by_id("fourrageCheckbox")
    time.sleep(wait_time)

    click_element_by_id("avoineCheckbox")
    time.sleep(wait_time)

    click_element_by_id("carotteCheckbox")
    time.sleep(wait_time)

    click_element_by_id("mashCheckbox")
    time.sleep(wait_time)

    driver.find_element_by_class_name("button-style-0").click()
    time.sleep(wait_time)

    buttons = driver.find_element_by_id("table-0").find_elements_by_tag_name("button")

    for button in buttons:
        if "disabled" not in button.get_attribute("class"):
            button.click()
            break
    time.sleep(wait_time)

    alert = driver.switch_to.alert
    alert.accept()

    time.sleep(wait_time)


def put_to_bed(age_up):
    click_element_by_id("boutonCoucher")
    time.sleep(wait_time)
    if age_up:
        click_element_by_id("boutonVieillir")
        time.sleep(wait_time)
        driver.find_element_by_id("age").find_element_by_class_name("button-text-0").click()
        time.sleep(wait_time)


def care_for(mash):
    try:
        driver.find_element_by_id("cheval-inscription").find_element_by_tag_name("a").click()
        needs_new_home = True
    except selenium.common.exceptions.WebDriverException:
        needs_new_home = False

    if needs_new_home:
        board_at_equestrian_center()

    click_element_by_id("boutonCaresser")
    time.sleep(wait_time)

    click_element_by_id("boutonBoire")
    time.sleep(wait_time)

    click_element_by_id("boutonCarotte")
    time.sleep(wait_time)

    click_element_by_id("boutonPanser")
    time.sleep(wait_time)

    if mash:
        click_element_by_id("boutonMash")
        time.sleep(wait_time)

    age = get_age()

    if age < 0.5:
        click_element_by_id("boutonAllaiter")
    else:
        time.sleep(wait_time)
        click_element_by_id("boutonNourrir")

        time.sleep(wait_time)

        hay_amount = int(driver.find_element_by_class_name("section-fourrage-target").text)
        hay_slider = driver.find_element_by_id("haySlider")
        hay_slider.find_elements_by_class_name("slider-number")[hay_amount].click()

        time.sleep(wait_time)

        if age >= 1.5:
            oat_amount = int(driver.find_element_by_class_name("section-avoine-target").text)
            oat_slider = driver.find_element_by_id("oatsSlider")
            oat_slider.find_elements_by_class_name("slider-number")[oat_amount].click()

        time.sleep(wait_time)
        click_element_by_id("feed-button")
        time.sleep(wait_time)


def compete_till_tired(rotate, full_day, training_horse=blupping_horse_id):
    competitions = ["cso", "dressage", "galop", "trot", "cross"]
    competition_index = 1
    energy = int(driver.find_element_by_id("energie").text)
    horse_time = int(driver.find_element_by_class_name("hour").text.split(":")[0])

    time_limit = 22 if full_day else 20
    energy_limit = 20 if full_day else 40

    while energy >= energy_limit and horse_time <= time_limit:
        print("index", competition_index)
        driver.get("https://www.howrse.com/elevage/competition/inscription?cheval=%s&competition=%s" %
                   (training_horse, competitions[competition_index]))
        time.sleep(wait_time)
        try:
            driver.find_element_by_class_name("button-text-0").click()
        except selenium.common.exceptions.WebDriverException:
            print("can't click")
            driver.get("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % training_horse)
            return
        time.sleep(wait_time)
        try:
            energy = int(driver.find_element_by_id("energie").text)
        except selenium.common.exceptions.NoSuchElementException:
            energy = 0
            print("can't find energy")
            continue
        horse_time = int(driver.find_element_by_class_name("hour").text.split(":")[0])
        if rotate:
            competition_index += 1
            if competition_index == len(competitions):
                competition_index = 0


def train_till_tired(full_day, training_horse=blupping_horse_id):
    energy = int(driver.find_element_by_id("energie").text)
    horse_time = get_time()
    age = get_age()
    
    max_time = 24 if full_day else 22
    min_remaining_energy = 0 if full_day else 20

    if age < 0.67:
        print("still a baby")
    elif age < 1.5:
        while energy - 5 > min_remaining_energy and max_time - 0.5 > horse_time:
            time.sleep(wait_time)
            playing_time = math.floor((energy - min_remaining_energy) / 6)
            playing_time = min(playing_time, 20)
            click_element_by_id("boutonJouer")
            time.sleep(wait_time)
            play_slider = driver.find_element_by_id("centerPlaySlider")
            play_slider.find_elements_by_tag_name("li")[playing_time].click()
            time.sleep(wait_time)
            click_element_by_id("formCenterPlaySubmit")
            time.sleep(wait_time)
            energy = int(driver.find_element_by_id("energie").text)
            horse_time = get_time()
    elif age < 2:
        min_energy_required = 9
        min_time_required = 0.5
        while energy - min_remaining_energy >= min_energy_required and max_time - min_time_required > horse_time:
            time.sleep(wait_time)
            riding_time = round((energy - min_remaining_energy) / min_energy_required)
            print("riding_time", riding_time)
            driver.find_element_by_id(rides["forest"]["button"]).click()
            time.sleep(wait_time)
            forest_slider = driver.find_element_by_id(rides["forest"]["slider"])
            forest_slider.find_elements_by_tag_name("li")[riding_time].click()
            time.sleep(wait_time)
            click_element_by_id(rides["forest"]["submit"])
            time.sleep(wait_time)
            energy = int(driver.find_element_by_id("energie").text)
            horse_time = get_time()
    else:
        min_energy_required = 45
        min_time_required = 3
        switch_to_rides = False
        ride_type = "forest"
        switch_to_competitions = False
        while energy - min_remaining_energy >= min_energy_required and max_time - min_time_required > horse_time:
            time.sleep(wait_time)
            if not switch_to_rides:
                min_energy_required = 50
                min_time_required = 3
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
                    elif training_type == types_of_training[-1]:
                        switch_to_rides = True
            elif not switch_to_competitions:
                min_energy_required = 9
                min_time_required = 0.5
                time.sleep(wait_time)
                riding_time = math.floor((energy - min_remaining_energy) / min_energy_required)
                form = driver.find_element_by_id(rides[ride_type]["form"])
                try:
                    click_element_by_id(rides[ride_type]["button"])
                    baby = False
                except selenium.common.exceptions.ElementNotInteractableException as e:
                    baby = True
                    print(e)

                if baby:
                    click_element_by_id("boutonMissionEquus")
                    return
                time.sleep(wait_time)
                slider = driver.find_element_by_id(rides[ride_type]["slider"])

                time.sleep(wait_time)

                # Check if riding helps
                slider.find_elements_by_tag_name("li")[riding_time].click()
                time.sleep(wait_time)
                no_display = 0
                for list_item in form.find_elements_by_class_name("gain-balade"):
                    if list_item.get_attribute("style"):
                        no_display += 1
                if len(form.find_elements_by_class_name("gain-balade")) - 1 != no_display:
                    driver.find_element_by_id(rides[ride_type]["submit"]).click()
                    time.sleep(wait_time)
                else:
                    try:
                        driver.find_element_by_id("walk-tab-balade-foret").find_element_by_class_name("tab-action").click()
                    except selenium.common.exceptions.ElementNotInteractableException:
                        print("can't click training")
                    print(ride_type)
                    if ride_type == "mountain":
                        switch_to_competitions = True
                    else:
                        try:
                            form.find_element_by_class_name("tab-action").click()
                        except selenium.common.exceptions.ElementNotInteractableException:
                            print("can't click training")
                        time.sleep(wait_time)
                        ride_type = "mountain"
            else:
                min_energy_required = 45
                min_time_required = 0.5
                compete_till_tired(True, full_day, training_horse)
                return
            energy = int(driver.find_element_by_id("energie").text)
            horse_time = get_time()
            time.sleep(wait_time)
        while energy - min_remaining_energy >= 9 and horse_time <= max_time - 0.5 and (not switch_to_rides):
            print("trigger spill over ride")
            min_energy_required = 9
            time.sleep(wait_time)
            riding_time = math.floor((energy - min_remaining_energy) / min_energy_required)
            form = driver.find_element_by_id(rides[ride_type]["form"])
            time.sleep(wait_time)
            try:
                driver.find_element_by_id(rides[ride_type]["button"]).click()
            except selenium.common.exceptions.ElementNotInteractableException as e:
                print(e)
            time.sleep(wait_time)
            slider = driver.find_element_by_id(rides[ride_type]["slider"])

            # Check if riding helps
            try:
                slider.find_elements_by_tag_name("li")[riding_time].click()
            except selenium.common.exceptions.ElementNotInteractableException as e:
                print(e)
                break

            time.sleep(wait_time)
            no_display = 0
            for list_item in form.find_elements_by_class_name("gain-balade"):
                if list_item.get_attribute("style"):
                    no_display += 1
            if len(form.find_elements_by_class_name("gain-balade"))-1 != no_display:
                driver.find_element_by_id(rides[ride_type]["submit"]).click()
                time.sleep(wait_time)
            else:
                if ride_type == "mountain":
                    break
                else:
                    ride_type = "mountain"
                form.find_element_by_class_name("tab-action").click()
                time.sleep(wait_time)
            energy = int(driver.find_element_by_id("energie").text)
            horse_time = get_time()
        if energy - min_remaining_energy >= 30 and horse_time <= max_time - 2:
            time.sleep(wait_time)
            click_element_by_id("boutonMissionEquus")
            time.sleep(wait_time)

        time.sleep(wait_time)


def run_cover_mare():
    time.sleep(wait_time)
    driver.get("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % sire_horse_id)
    try:
        energy = int(driver.find_element_by_id("energie").text)
    except selenium.common.exceptions.NoSuchElementException:
        energy = 30
    horse_time = int(driver.find_element_by_class_name("hour").text.split(":")[0])

    if energy > 40 and horse_time < 20:
        driver.find_element_by_id("reproduction-tab-0").find_elements_by_class_name("tab-action")[1].click()
        click_element_by_id("formMalePublicTypeMoi")
        time.sleep(wait_time)
        click_element_by_id("boutonMaleReproduction")
    else:
        care_for(True)
        if energy > 40 and horse_time < 20:
            driver.find_element_by_id("reproduction-tab-0").find_elements_by_class_name("tab-action")[1].click()
            click_element_by_id("formMalePublicTypeMoi")
            time.sleep(wait_time)
            click_element_by_id("boutonMaleReproduction")
        else:
            put_to_bed(True)
            run_cover_mare()
    time.sleep(wait_time)
    driver.get("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % blupping_horse_id)


def run_birth():
    time.sleep(wait_time*2)
    driver.find_element_by_id("poulain-1").send_keys("temp")
    driver.find_element_by_id("poulain-1").send_keys(Keys.ENTER)
    time.sleep(wait_time)
    gender = driver.find_element_by_id("characteristics-body-content") \
        .find_elements_by_class_name("first")[2].text.split(": ")[1]
    click_element_by_id("tab-genetics-title")
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

    time.sleep(wait_time)

    care_for(False)

    put_to_bed(False)

    time.sleep(wait_time)

    run_cover_mare()
    time.sleep(wait_time)
    driver.get("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % blupping_horse_id)


def check_reproduction(cover):
    time.sleep(wait_time)
    print("Checking for birth...")

    birth = click_element_by_id("boutonVeterinaire")

    if birth:
        print("Birthing foal...")
        run_birth()

    if cover:
        print("Checking for cover offer...")
        reproduction_bottom = driver.find_element_by_id("reproduction-bottom")
        try:
            time.sleep(wait_time)
            reproduction_bottom.find_element_by_class_name("item-relative").click()
            time.sleep(wait_time)
            click_element_by_id("boutonDoReproduction")
            time.sleep(wait_time)
        except selenium.common.exceptions.WebDriverException as e:
            print(e)

    time.sleep(wait_time)


def blup(cover, train):
    genetic_blup = get_blup()
    print(genetic_blup)

    age = get_age()

    while age < 30:
        if cover:
            print("Will cover this horse...")
            check_reproduction(True)

        if train:
            train_till_tired(True)
        else:
            compete_till_tired(True, True)

        time.sleep(wait_time)

        care_for(train)

        time.sleep(wait_time)

        if train:
            train_till_tired(True)
        else:
            compete_till_tired(True, True)

        time.sleep(wait_time)

        put_to_bed(True)


def cycle_through_horses(starter_id):
    login("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % starter_id)
    time.sleep(wait_time)
    current_horse_id = 0
    while int(current_horse_id) != starter_id:
        check_reproduction(False)
        train_till_tired(False, starter_id if current_horse_id == 0 else current_horse_id)
        care_for(True)
        train_till_tired(False, starter_id if current_horse_id == 0 else current_horse_id)
        time.sleep(wait_time)
        put_to_bed(False)
        time.sleep(wait_time)
        click_element_by_id("nav-next")
        time.sleep(wait_time)
        horse_name = driver.find_elements_by_class_name("horse-name")[-1]
        horse_name.click()
        time.sleep(wait_time)
        current_horse_id = driver.current_url.split("=")[1]
        print(current_horse_id)


# cycle_through_horses(64049762)
login("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % blupping_horse_id)
# login("https://www.howrse.com/elevage/chevaux/choisirNoms?jument=64123625")

time.sleep(wait_time)

# run_cover_mare()
# time.sleep(wait_time)
# driver.get("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % blupping_horse_id)

blup(True, False)
# run_birth()
# while True:
#     train_till_tired("mountain", True)
#     time.sleep(wait_time)
#     care_for(True)
#     time.sleep(wait_time)
#     train_till_tired("mountain", True)
#     put_to_bed(True)
