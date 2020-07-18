from selenium import webdriver
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from pprint import pprint
import time
import random
import math
import dotenv

# The ids to look up the horses
dame_horse_id = 64218662
sire_horse_id = 64191267

# The time the system waits for the site to load
wait_time = 0.5

types_of_training = [
    "Endurance",
    "Vitesse",
    "Dressage",
    "Galop",
    "Trot",
    "Saut"
]

ride_types = ["foret", "montagne"]

mission_types = [
    "Equus",
    "Montagne",
    "Foret",
    "Plage"
]

competitions = [("cso", 17), ("dressage", 25), ("galop", 14), ("trot", 14), ("cross", 17)]

play_button_id = "Jouer"

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
            return click_element_by_id(element_id, iteration + 1)
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
    driver.find_element_by_id("login").send_keys(dotenv.dotenv_values().get("USERNAME"))
    driver.find_element_by_id("password").send_keys(dotenv.dotenv_values().get("PASSWORD"))
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
        age = months / 12
    elif "year" in raw_age:
        if "month" in raw_age:
            years, _, months, _ = raw_age.split(" ")
            years = int(years)
            months = int(months)
        else:
            years = raw_age.split(" ")[0]
            years = int(years)
            months = 0
        age = years + (months / 12)
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
    horse_time = hour + (minute / 60)
    print("time", horse_time)
    return horse_time


def board_at_equestrian_center():
    # Wait for the page to load
    time.sleep(wait_time)

    # Mark hay true
    click_element_by_id("fourrageCheckbox")
    time.sleep(wait_time)

    # Mark oats true
    click_element_by_id("avoineCheckbox")
    time.sleep(wait_time)

    # Mark carrots true
    click_element_by_id("carotteCheckbox")
    time.sleep(wait_time)

    # Mark mash true
    click_element_by_id("mashCheckbox")
    time.sleep(wait_time)

    # Search
    driver.find_element_by_class_name("button-style-0").click()
    time.sleep(wait_time)

    # Get all buttons
    buttons = driver.find_element_by_id("table-0").find_elements_by_tag_name("button")

    # Select first available button
    for button in buttons:
        if "disabled" not in button.get_attribute("class"):
            button.click()
            break

    # Wait for page to load
    time.sleep(wait_time)

    # Accept the confirmation
    alert = driver.switch_to.alert
    alert.accept()

    # Wait for the page to load
    time.sleep(wait_time)


def put_to_bed(age_up):
    time.sleep(wait_time)
    # Click sleep button
    click_element_by_id("boutonCoucher")

    time.sleep(wait_time)

    if age_up:
        # Click age up
        click_element_by_id("boutonVieillir")

        time.sleep(wait_time)

        # Confirm age up
        driver.find_element_by_id("age").find_element_by_class_name("button-text-0").click()

        time.sleep(wait_time)


def care_for(mash):
    """
    Run through all of the motions for a horse
    :param bool mash: Whether the horse should be fed energy mash
    """

    time.sleep(wait_time)
    try:
        driver.find_element_by_id("cheval-inscription").find_element_by_tag_name("a").click()
    except selenium.common.exceptions.WebDriverException as e:
        print(e)
    else:
        board_at_equestrian_center()

    # Stroke horse
    click_element_by_id("boutonCaresser")
    time.sleep(wait_time)

    # Give water
    click_element_by_id("boutonBoire")
    time.sleep(wait_time)

    # Feed carrot
    click_element_by_id("boutonCarotte")
    time.sleep(wait_time)

    # Groom
    click_element_by_id("boutonPanser")
    time.sleep(wait_time)

    if mash:
        # Give energy mash
        click_element_by_id("boutonMash")
        time.sleep(wait_time)

    # Get age
    age = get_age()

    time.sleep(wait_time)

    # If age is less than 6 months
    if age < 0.5:
        # Nurse
        click_element_by_id("boutonAllaiter")
    else:
        # Click feed button
        click_element_by_id("boutonNourrir")

        time.sleep(wait_time)

        # Get the hay amount
        hay_amount = int(driver.find_element_by_class_name("section-fourrage-target").text)
        # Get the slider
        hay_slider = driver.find_element_by_id("haySlider")
        # Click the amount of hay being fed
        hay_slider.find_elements_by_class_name("slider-number")[hay_amount].click()

        time.sleep(wait_time)

        # Check if the horse is old enough to eat oats
        if age >= 1.5:
            # Get the oats amount
            oat_amount = int(driver.find_element_by_class_name("section-avoine-target").text)
            # Get the slider
            oat_slider = driver.find_element_by_id("oatsSlider")
            # Click the amount of oat being fed
            oat_slider.find_elements_by_class_name("slider-number")[oat_amount].click()

            time.sleep(wait_time)
        # Submit the feed
        click_element_by_id("feed-button")

        time.sleep(wait_time)


def do_mission(full_day):
    time.sleep(wait_time)

    max_allowed_time = 24 if full_day else 22
    min_allowed_energy = 0 if full_day else 20

    current_energy = get_energy()
    current_time = get_time()

    if current_energy - 30 > min_allowed_energy\
        and current_time + 2 < max_allowed_time:
        for mission in mission_types:
            if click_element_by_id("boutonMission%s" % mission):
                break
    time.sleep(wait_time)


def compete_till_tired(rotate, full_day, training_horse=dame_horse_id):
    """
    Loop through competitions until the horse runs out of energy or time
    :param bool rotate: Whether or not to rotate through competition types
    :param bool full_day: Used to determine how long the horse can compete and how much energy it needs left
    :param int training_horse: The id of the horse to compete
    """

    time.sleep(wait_time)

    # Initial index at 1
    competition_index = 1

    # Get the current energy and the current time
    current_energy = get_energy()
    current_time = get_time()

    # Figure out the time and energy limits
    time_limit = 24 if full_day else 22
    energy_limit = 0 if full_day else 20

    while current_energy - competitions[competition_index][1] > energy_limit \
            and current_time + 2 < time_limit:
        driver.get("https://www.howrse.com/elevage/competition/inscription?cheval=%s&competition=%s" %
                   (training_horse, competitions[competition_index][0]))

        time.sleep(wait_time)

        try:
            driver.find_element_by_class_name("button-text-0").click()
        except selenium.common.exceptions.WebDriverException:
            print("can't click")
        finally:
            driver.get("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % training_horse)

        time.sleep(wait_time)

        current_energy = get_energy()

        current_time = get_time()

        if rotate:
            competition_index += 1
            if competition_index == len(competitions):
                competition_index = 0


def train_till_tired(full_day, training_horse=dame_horse_id):
    """
    Train the horse until energy is too low or they run out of time in the day
    :param bool full_day: Used to determine energy and time required at bed time
    :param int training_horse: The id of the horse being trained
    """

    # Get current stats
    current_energy = get_energy()
    current_time = get_time()
    current_age = get_age()

    # Determine the minimum required end of the day
    max_time_allowed = 24 if full_day else 22  # This is different if they have achilles heel
    min_energy_allowed = 0 if full_day else 20  # This is different if they have achilles heel

    cared_for = False

    # Check age
    if current_age < 0.67:
        # Too young to train
        print("still a baby")
    elif current_age < 1.5:
        # Old enough to go for rides, but can play

        # click to open the play button
        click_element_by_id(play_button_id)

        time.sleep(wait_time)

        # Get the play slider
        play_slider = driver.find_element_by_id("centerPlaySlider")
        # Click the first one to get the energy requirement
        play_slider.find_elements_by_tag_name("li")[1].click()
        # Get the min energy requirement
        min_energy_needed = math.ceil(float(driver.find_element_by_id("formCenterPlayEnergy").text) * -1)

        # Calculate the allowed energy and time for future calculations
        available_energy = current_energy - min_energy_needed
        available_time = min((max_time_allowed - current_time)*2, 20)
        if available_energy > min_energy_allowed \
                and current_time + 0.5 < max_time_allowed:

            time.sleep(wait_time)

            # Calculate the amount of time the horse can play
            playing_time = math.floor((current_energy - min_energy_allowed) / min_energy_needed)
            playing_time = min(playing_time, available_time)

            play_slider.find_elements_by_tag_name("li")[playing_time].click()

            time.sleep(wait_time)

            if not click_element_by_id("formCenterPlaySubmit"):
                driver.find_element_by_id("care-tab-play").find_element_by_tag_name("a").click()
            time.sleep(wait_time)
        else:
            driver.find_element_by_id("care-tab-play").find_element_by_tag_name("a").click()
    elif current_age < 2:

        # Old enough to go on rides
        # Open the forest ride
        if not click_element_by_id("boutonBalade-%s" % ride_types[0]):
            do_mission(full_day)
            return
        slider = driver.find_element_by_id("walk%sSlider" % ride_types[0])
        # Click the first one to get the energy requirement
        slider.find_elements_by_tag_name("li")[1].click()

        time.sleep(wait_time)

        # Get the min energy requirement
        min_energy_needed = math.ceil(float(driver.find_element_by_id("walk-%s-energie" % ride_types[0]).text))

        # Calculate the allowed energy and time for future calculations
        available_energy = current_energy - min_energy_needed
        available_time = min((max_time_allowed - current_time)*2, 20)

        if current_energy - available_energy > min_energy_allowed \
                and current_time + 0.5 <= max_time_allowed:

            time.sleep(wait_time)

            # Calculate the amount of time the horse can play
            ride_time = math.floor((current_energy - min_energy_allowed) / min_energy_needed)
            ride_time = min(ride_time, available_time)

            slider.find_elements_by_tag_name("li")[ride_time].click()

            time.sleep(wait_time)

            if not click_element_by_id("walk-%s-submit" % ride_types[0]):
                driver.find_element_by_id("walk-tab-balade-%s" % ride_types[0]).find_element_by_tag_name("a").click()
        else:
            driver.find_element_by_id("walk-tab-balade-%s" % ride_types[0]).find_element_by_tag_name("a").click()
        time.sleep(wait_time)
    else:
        # Open the forest ride
        if not click_element_by_id("boutonBalade-%s" % ride_types[0]):
            do_mission(full_day)
            return

        slider = driver.find_element_by_id("walk%sSlider" % ride_types[0])
        # Click the first one to get the energy requirement
        slider.find_elements_by_tag_name("li")[1].click()

        time.sleep(wait_time)

        # Get the min energy requirement
        min_energy_needed = math.ceil(float(driver.find_element_by_id("walk-%s-energie" % ride_types[0]).text))

        # Close ride tab
        click_element_by_id("walk-tab-balade-%s" % ride_types[0])

        # Calculate the allowed energy and time for future calculations
        available_energy = current_energy - min_energy_needed
        available_time = min((max_time_allowed - current_time)*2, 20)
        # Current ride type
        ride_index = 0
        # Current training type
        training_type = "training"
        # Loop till no energy or time
        while available_energy > min_energy_allowed \
                and current_time + 0.5 <= max_time_allowed:

            time.sleep(wait_time)

            # Check for training type
            if training_type == "training" \
                    and current_energy - 50 > min_energy_allowed \
                    and current_time + 3 <= max_time_allowed:

                # Check all training buttons
                for actual_training_type in types_of_training:
                    if click_element_by_id("entrainement%s" % actual_training_type):
                        break
                    elif actual_training_type == types_of_training[-1]:
                        training_type = "rides"
            elif training_type == "rides" or \
                    (available_energy > min_energy_allowed
                     and current_time + 0.5 < max_time_allowed
                     and training_type != "competitions"):

                # Get the ride slider
                slider = driver.find_element_by_id("walk%sSlider" % ride_types[ride_index][0])

                time.sleep(wait_time)

                # Calculate the amount of time the horse can play
                ride_time = math.floor((current_energy - min_energy_allowed) / min_energy_needed)
                ride_time = min(ride_time, available_time)

                # Click the first one to get the energy requirement
                slider.find_elements_by_tag_name("li")[ride_time].click()
                time.sleep(wait_time)
                slider = driver.find_element_by_id("walk%sSlider" % ride_types[ride_index])

                time.sleep(wait_time)

                # Check if riding helps
                slider.find_elements_by_tag_name("li")[ride_time].click()

                form = driver.find_element_by_id("walk-tab-balade-%s" % ride_types[ride_index])

                no_display = 0
                for list_item in form.find_elements_by_class_name("gain-balade"):
                    if list_item.get_attribute("style"):
                        no_display += 1
                if len(form.find_elements_by_class_name("gain-balade")) - 1 != no_display:
                    click_element_by_id("walk-%s-submit" % ride_types[ride_index])
                    time.sleep(wait_time)
                else:
                    if ride_index == 1:
                        training_type = "competitions"
                    else:
                        ride_index = 1
                    form.find_element_by_class_name("tab-action").click()
                    time.sleep(wait_time)

                click_element_by_id("walk-%s-submit" % ride_types[ride_index])

                time.sleep(wait_time)
            else:
                compete_till_tired(True, full_day, training_horse)
                time.sleep(wait_time)
            current_energy = get_energy()
            current_time = get_time()
            time.sleep(wait_time)

            # Open the forest ride
            if not click_element_by_id("boutonBalade-%s" % ride_types[0]):
                do_mission(full_day)
                return

            slider = driver.find_element_by_id("walk%sSlider" % ride_types[0])
            # Click the first one to get the energy requirement
            slider.find_elements_by_tag_name("li")[1].click()

            time.sleep(wait_time)

            # Get the min energy requirement
            min_energy_needed = math.ceil(float(driver.find_element_by_id("walk-%s-energie" % ride_types[0]).text))

            # Close ride tab
            click_element_by_id("walk-tab-balade-%s" % ride_types[0])

            # Calculate the allowed energy and time for future calculations
            available_energy = current_energy - min_energy_needed
            available_time = min((max_time_allowed - current_time) * 2, 20)

            if available_energy <= min_energy_allowed \
                    and current_time + 0.5 > max_time_allowed:
                if not cared_for:
                    care_for(training_type != "competitions")
                    cared_for = True
        time.sleep(wait_time)


def run_cover_mare():
    time.sleep(wait_time)

    # Go to the sire's page
    driver.get("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % sire_horse_id)

    current_energy = get_energy()
    current_time = get_time()

    available_energy = current_energy - 25

    if current_energy > available_energy and current_time < 21.5:
        driver.find_element_by_id("reproduction-tab-0").find_elements_by_class_name("tab-action")[1].click()
        click_element_by_id("formMalePublicTypeMoi")
        time.sleep(wait_time)
        click_element_by_id("boutonMaleReproduction")
    else:
        care_for(True)
        if current_energy > available_energy and current_time < 21.5:
            driver.find_element_by_id("reproduction-tab-0").find_elements_by_class_name("tab-action")[1].click()
            click_element_by_id("formMalePublicTypeMoi")
            time.sleep(wait_time)
            click_element_by_id("boutonMaleReproduction")
        else:
            put_to_bed(True)
            run_cover_mare()
    time.sleep(wait_time)


def run_birth():
    time.sleep(wait_time * 2)
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
    driver.get("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % dame_horse_id)


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
            reproduction_bottom.find_element_by_class_name("item-relative").click()
        except selenium.common.exceptions.ElementNotInteractableException as e:
            print(e)
            time.sleep(wait_time)
            return
        else:
            time.sleep(wait_time)
            click_element_by_id("boutonDoReproduction")
            time.sleep(wait_time)
            return


def blup(cover, train):
    genetic_blup = get_blup()
    print("genetic_blup", genetic_blup)

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
login("https://www.howrse.com/elevage/chevaux/cheval?id=%s" % dame_horse_id)
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
