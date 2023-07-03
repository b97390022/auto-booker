from src.config import config
from src.locator import Locator
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import sys
from typing import Any


class SeleniumService:
    def __init__(self) -> None:
        self._init_chrome_options()
        self._driver = webdriver.Chrome(
            options=self.chrome_options,
            service=ChromeService(ChromeDriverManager().install()),
        )
        self.default_timeout: int = 60

    def _init_chrome_options(self):
        self.chrome_options = Options()
        for argument in config.chrome_arguments:
            self.chrome_options.add_argument(argument)
            if (
                sys.platform.startswith("linux")
                and "--headless" not in config.chrome_arguments
            ):
                self.chrome_options.add_argument("--headless")

            self.chrome_options.add_experimental_option(
                "excludeSwitches", config.chrome_excludeSwitches
            )
            self.chrome_options.add_experimental_option("prefs", config.chrome_prefs)

    @property
    def driver(self):
        return self._driver

    def get(self, url: str):
        self.driver.get(url)

    def get_cookies(self):
        return self.driver.get_cookies()

    def click(self, element: WebElement):
        element.click()

    def close_all_alert_window(self):
        try:
            while self.driver.switch_to.alert:
                self.driver.switch_to.alert.dismiss()
        except:
            pass

    def element_exists(self, locator: Locator, timeout: int) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                expected_conditions.presence_of_element_located(
                    (locator.by, locator.value)
                )
            )
            return True
        except TimeoutException:
            return False

    def get_element(self, locator: Locator, timeout: int | None = None):
        if not timeout:
            timeout = self.default_timeout
        if not self.element_exists(locator, timeout):
            raise NoSuchElementException(f"Could not find element {locator}")
        return self.driver.find_element(locator.by, locator.value)

    def get_base64_image(self, locator: Locator):
        return self.driver.execute_script(
            """
                var ele = arguments[0];
                var cnv = document.createElement('canvas');
                cnv.width = ele.width; cnv.height = ele.height;
                cnv.getContext('2d').drawImage(ele, 0, 0);
                return cnv.toDataURL('image/jpeg').substring(22);    
            """,
            self.get_element(locator),
        )

    def input_value(self, element: WebElement, value: Any):
        element.send_keys(value)
