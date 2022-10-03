#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © Vivian Sedov
#
# File Name: PythonAuto.py
__author__ = "Vivian Sedov"
__email__ = "viv.sv@hotmail.com"

import json
import logging
import os
import time
import warnings
from collections import defaultdict
from shutil import which

import psutil
from icecream import ic
from rich.logging import RichHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

warnings.filterwarnings("ignore", category=DeprecationWarning)

FIREFOXPATH = which("firefox")
CHROMEPATH = which("chrome") or which("chromium")
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)()

FORMAT = "%(message)s"
logging.basicConfig(level="INFO",
                    format=FORMAT,
                    datefmt="[%X]",
                    handlers=[RichHandler()])

__import__("dotenv").load_dotenv()


def init_webdriver():
    """Simple Function to initialize and configure Webdriver"""
    # if FIREFOXPATH is not None:
    logging.info(FIREFOXPATH)
    from selenium.webdriver.firefox.options import Options
    options = Options()
    options.binary = FIREFOXPATH
    options.add_argument("-headless")
    return webdriver.Firefox(options=options, log_path="geckodriver.log")

    # from selenium.webdriver.chrome.options import Options
    # opts = Options()
    # opts.binary_location = "/usr/bin/chromium"
    # driver = webdriver.Chrome(chrome_options=opts)
    # return driver
    #


class Attendance:

    def __init__(self, live_check: bool = True):
        self.current_information = defaultdict(list)
        self.driver = init_webdriver()
        logging.info(ic.format("Initializing, succesful get of dirver"))

        self.user_name = os.getenv("EMAIL")
        self.password = os.getenv("PASS")

        self.is_active = False
        self.live_check_bool = live_check
        self.timed_check = not self.live_check

    def login_path(self) -> None:
        """Login Path to register user with email and password"""
        # self.driver.get("www.google.com")

        self.driver.get("http://lum-prod.ec.royalholloway.ac.uk")
        time.sleep(2)
        self.wait_for_element("userNameInput")
        username = self.driver.find_element(By.ID, "userNameInput")
        password = self.driver.find_element(By.ID, "passwordInput")
        logging.info(
            ic.format("Logging in with username: {}".format(self.user_name)))
        username.send_keys(self.user_name)
        logging.info(ic.format("Logging in with password"))
        password.send_keys(self.password)
        loginbtn = self.driver.find_element(By.ID, "submitButton")
        loginbtn.click()
        self.driver.get(
            "https://generalssb-prod.ec.royalholloway.ac.uk/BannerExtensibility/customPage/page/RHUL_Attendance_Student"
        )
        logging.info(ic.format("Logged in"))
        self.is_active = True

    def reset_driver(self) -> None:
        logging.info(ic.format("Resetting driver"))
        self.driver.close()
        self.driver = webdriver.Firefox()
        self.is_active = False

    def get_attandance_info(self) -> None:
        logging.info(ic.format("Getting and saving attandance info"))

        pattern = "pbid-htmlTwoWeekSchedule-td-displayTwoWeekSchedule{0}-{1}"

        self.wait_for_element(
            "pbid-htmlTwoWeekSchedule-td-displayTwoWeekScheduleDate-1")

        def parser(type: str, index: int) -> str:
            return pattern.format(type, index)

        try:
            for i in range(0, 22):
                date = self.driver.find_element(By.ID, parser("Date", i)).text
                lesson = {
                    "start":
                    self.driver.find_element(By.ID, parser("Time", i)).text,
                    "attendance":
                    self.driver.find_element(By.ID, parser("Attendance",
                                                           i)).text,
                    "Lesson":
                    self.driver.find_element(By.ID, parser("Course", i)).text,
                }
                if date not in self.current_information:
                    self.current_information[date] = []

                self.current_information[date].append(lesson)
        except Exception as e:
            logging.error(ic.format("error is {}".format(e)))
            pass

        # This is just for a back up just in case
        with open("attendance.json", "+w") as f:
            f.write(
                json.dumps({**self.current_information},
                           indent=4,
                           sort_keys=True))
            logging.info(ic.format("Saved attandance info"))

    def time_out_recovery(self) -> None:
        """Time out recovery if occours"""
        self.driver.get("https://adfs.rhul.ac.uk/adfs/ls/")
        logging.info("Recovering from time out")
        time.sleep(1)

    def wait_for_element(self, id: str) -> None:
        """Wait for element to be visible

        Parameters
        ----------
        id : str
            id of the element to wait for
        """
        logging.info(ic.format("Waiting for element to be visible", id))
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, id)))
        except Exception as e:
            logging.info(self.driver)
            logging.error(ic.format("error is {}".format(e)))
            logging.info(ic.format("Element not found", id))
            self.wait_for_element(id)

    def is_in_time_period(self, start_time: time, end_time: time,
                          now_time: time) -> bool:
        if start_time < end_time:
            return now_time >= start_time and now_time <= end_time
        else:
            # Over midnight:
            return now_time >= start_time or now_time <= end_time

    def current_date(self) -> str:
        """Current Date

        Returns
        -------
        str
            Formated for the webpage
        """
        return time.strftime("%d:%m:%Y").replace(":", "/")

    def check_live_pop_up(self) -> bool:
        self.wait_for_element(
            "pbid-htmlTwoWeekSchedule-td-displayTwoWeekScheduleDate-1")
        # Extra wait if needed
        logging.info(ic.format("Checking live pop sleeping for 5 seconds"))
        time.sleep(5)
        logging.info(ic.format("Checking live pop up, sleep succeeded"))

        pop_up_button = [
            '//*[@id="pbid-buttonFoundHappeningNowButtonsTwoHere"]',
            '//*[@id="pbid-buttonFoundHappeningNowButtonsTwoInPerson"]',
            '//*[@id="pbid-buttonFoundHappeningNowButtonsHere"]',
            '//*[@id="pbid-LiteralFoundHappeningNowButtonsTwoHere"]',
        ]
        # '//*[@id="pbid-buttonManualAttendance"]',
        for i in range(len(pop_up_button)):
            try:
                click = self.driver.find_element(By.XPATH, pop_up_button[i])
                if not click.is_displayed():
                    continue
                self.driver.execute_script("arguments[0].click();", click)
                logging.info(
                    ic.format("Clicked Live Pop up : {}".format(
                        pop_up_button[i])))
                return True
            except:
                logging.info(ic.format("No pop up found"))
                continue

        logging.info(ic.format("No pop up found"))
        return False

    def time_date_check(self):
        logging.info(ic.format("Checking time and date"))
        current_day_info = self.current_information[self.current_date()]
        lesson_times = current_day_info["time"]
        for timed_val in lesson_times:
            # format is 1300 - 1400 need to extract
            timed_list = timed_val.split("-")
            start_time = time(timed_list[0][:2], timed_list[0][2:])

            end_time = time(timed_list[1][:2], timed_list[1][2:])

            current_24_time = time(time.strftime("%H:%M"))

            if self.is_in_time_period(start_time, end_time, current_24_time):
                self.check_live_pop_up()

    def live_check(self) -> None:
        """ Live check, this is a program that will not sleep and would continue """
        while True and self.is_active:
            if self.driver.current_url == "https://generalssb-prod.ec.royalholloway.ac.uk/BannerExtensibility/ssb/logout/timeoutPage":
                self.time_out_recovery()

            elif self.live_check_bool():
                self.check_live_pop_up()

            elif self.timed_check():
                try:
                    self.time_date_check(self)
                except KeyError as error:
                    logging.debug(ic.format(error))
                    pass

    def __del__(self):
        """ Kill all firefox instance """
        logging.info(ic.format("Closing Driver"))
        self.driver.close()

        logging.info(ic.format("Killing all firefox instance"))
        for proc in psutil.process_iter():
            if proc.name() == "firefox.exe":
                proc.kill()  # kill the process
        logging.info(ic.format("Firefox killed"))

        logging.info(
            ("----------------------------------------------------\n"
             "|   Date: {}                                         \n"
             "|   Day: {}                                         \n"
             "|   Time: {}                                        \n"
             "| ---------------End of Program---------------------\n").format(
                 time.strftime("%d:%m:%Y"), time.strftime("%A"),
                 time.strftime("%H:%M:%S")))  # noqa

    def __call__(self):
        self.login_path()
        self.check_live_pop_up()
        self.get_attandance_info()


def main() -> None:
    """Main Function"""
    at = Attendance()
    return at()


if __name__ == "__main__":
    main()
