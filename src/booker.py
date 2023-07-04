from abc import ABC, abstractmethod
import asyncio
import base64
from collections.abc import Callable
import datetime
import requests
import functools
from src.config import config
from src.captcha import Captcha
from src.locator import Locator
from src.selenium_service import SeleniumService
from selenium.webdriver.common.by import By
from loguru import logger
from pydantic import HttpUrl
from pytz import timezone
from typing import Any
import threading


class BookingThread(threading.Thread):
    def __init__(self, num, job: Callable, **kwargs):
        threading.Thread.__init__(self)
        self.num = num
        self.job = job
        self.kwargs = kwargs

    def run(self):
        logger.info(f"start job with num: {self.num}")
        asyncio.run(self.job(self.num, **self.kwargs))
        logger.info(f"finish job with num: {self.num}")


class BookerBase(ABC):
    @abstractmethod
    def main(self):
        return NotImplemented


class Booker(BookerBase):
    def __init__(self) -> None:
        self.login_url: HttpUrl = (
            "https://scr.cyc.org.tw/tp02.aspx?module=login_page&files=login"
        )
        self.url: HttpUrl = "https://scr.cyc.org.tw/tp02.aspx"
        self.cookies: list = []
        # selenium service
        self.selenium_service = SeleniumService()
        # captcha
        self.captcha_worker: Captcha = Captcha()
        self.captcha_image_file_name: str = "captcha_login.png"
        # locators
        self.username_locator = Locator(By.ID, "ContentPlaceHolder1_loginid")
        self.password_locator = Locator(By.ID, "loginpw")
        self.captcha_locator = Locator(By.ID, "ContentPlaceHolder1_Captcha_text")
        self.captcha_image_locator = Locator(
            By.XPATH, "//*[@id='ContentPlaceHolder1_CaptchaImage']"
        )
        self.login_locator = Locator(By.ID, "login_but")

    def save_captcha_image(self, img_base64: Any):
        with open(self.captcha_image_file_name, "wb") as image:
            image.write(base64.b64decode(img_base64))

    def register_cookies(self, cookies):
        logger.info(f"register new cookies: {cookies}")
        self.cookies = cookies

    @logger.catch
    def login(self):
        # goto login page
        self.selenium_service.get(self.login_url)
        # below is trying to close all the alert window
        self.selenium_service.close_all_alert_window()

        base64_image = self.selenium_service.get_base64_image(
            self.captcha_image_locator
        )

        self.save_captcha_image(base64_image)  # save image to file
        captcha_text = self.captcha_worker.solve_captcha(
            self.captcha_image_file_name
        )  # solve captcha

        if captcha_text:
            username = self.selenium_service.get_element(self.username_locator)
            password = self.selenium_service.get_element(self.password_locator)
            captcha = self.selenium_service.get_element(self.captcha_locator)
            login = self.selenium_service.get_element(self.login_locator)

            self.selenium_service.input_value(
                username, config.username.get_secret_value()
            )
            self.selenium_service.input_value(
                password, config.password.get_secret_value()
            )
            self.selenium_service.input_value(captcha, captcha_text)

            self.selenium_service.click(login)

        self.register_cookies(self.selenium_service.get_cookies())


class BadmintonBooker(Booker):
    def __init__(self) -> None:
        super().__init__()
        self.pt = "1"
        self.court_map: dict = {
            "A": "83",
            "B": "84",
            "C": "85",
            "D": "86",
            "E": "87",
            "F": "88",
        }

    async def async_get(
        self,
        loop,
        url: str,
        headers: dict = {},
        params: dict = {},
        cookies: list = [],
    ):
        with requests.Session() as session:
            # try to set cookies
            for cookie in cookies:
                session.cookies.set(cookie["name"], cookie["value"])
            r = await loop.run_in_executor(
                None,
                functools.partial(session.get, url=url, headers=headers, params=params),
            )
            return r

    async def book_badminton_court(
        self,
        num: int,
        job_days: int,
        court_name: str,
        book_time: str,
    ):
        now = datetime.datetime.now(timezone("Asia/Taipei"))
        book_date = (now + datetime.timedelta(days=job_days)).strftime("%Y/%m/%d")

        loop = asyncio.get_event_loop()
        tasks = []
        tasks.append(
            loop.create_task(
                self.async_get(
                    loop=loop,
                    url=self.url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                        "Host": "scr.cyc.org.tw",
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                    },
                    params={
                        "module": "net_booking",
                        "files": "booking_place",
                        "StepFlag": "25",
                        "QPid": self.court_map.get(court_name),
                        "QTime": book_time,
                        "PT": self.pt,
                        "D": book_date,
                    },
                    cookies=self.cookies,
                )
            )
        )
        results = await asyncio.gather(*tasks)
        logger.info(f"job: {num} with status {[r.status_code for r in results]}")

    def main(self, job_number: int, **kwargs):
        threads = []
        for i in range(job_number):
            thread = BookingThread(i, self.book_badminton_court, **kwargs)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
        logger.info(f"All jobs are finished.")
