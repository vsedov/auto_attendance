#!/usr/bin/python

import json

import CONFIG
from logs import Log
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


class Timetable:

    timetable = []

    def __init__(self) -> None:
        Log.log("starting timetable updater")
        options = Options()
        options.headless = True
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Firefox(
            options=options, executable_path="/usr/bin/geckodriver"
        )
        self.get_timetable()

    def wait_for_element(self, id):
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, id)))

    def get_timetable(self) -> None:
        Log.log("opening login page")
        self.driver.get(CONFIG.url)

        # Wait for login page
        self.wait_for_element("tUserName")

        # Login
        Log.log("entering login details")
        self.driver.find_element(By.ID, "tUserName").send_keys(CONFIG.username)
        self.driver.find_element(By.ID, "tPassword").send_keys(CONFIG.password)
        self.driver.find_element(By.ID, "bLogin").click()

        # Wait for options page
        self.wait_for_element("LinkBtn_studentMyTimetable")

        # Select 'My Timetable'
        self.driver.find_element(By.ID, "LinkBtn_studentMyTimetable").click()

        # Wait for page to load
        self.wait_for_element("lbWeeks")

        # Select current week
        Log.log("selecting current week")
        week_list = Select(self.driver.find_element(By.ID, "lbWeeks"))
        week_list.select_by_index(3)

        # Load timetable page
        Log.log("loading timetable page")
        self.driver.find_element(By.ID, "bGetTimetable").click()

        # Wait for page to load
        self.wait_for_element("form1")

        # Get all timetable information
        table = self.driver.find_element(By.XPATH, "/html/body/table[2]/tbody")
        self.save_timetable(table)
        self.driver.quit()

    def save_timetable(self, table) -> None:
        Log.log("running save timetable")
        for i, tr in enumerate(table.find_elements(By.XPATH, "./*")[1:]):
            offset = 0
            self.timetable.append([])
            for td in tr.find_elements(By.XPATH, "./*")[2 if i == 0 else 1 :]:
                colspan = td.get_attribute("colspan")
                if colspan:
                    self.timetable[i].append([offset, td.text])
                    offset = offset + (30 * int(colspan))
                else:
                    offset = offset + 30

        with open("current_week.json", "w") as f:
            Log.log("saving timetable")
            json.dump(self.timetable, f)


Timetable()
