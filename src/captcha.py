from abc import ABC, abstractmethod
import pathlib
import requests
from src.config import config
import time
from loguru import logger


class CaptchaBase(ABC):
    @abstractmethod
    def solve_captcha(self):
        return NotImplemented


class Captcha(CaptchaBase):
    def __init__(self) -> None:
        self.captcha_key: str = config.captcha_key.get_secret_value()

    def solve_captcha(self, image_file_name: str):
        image_path = pathlib.Path(image_file_name).resolve()
        with open(image_path, "rb") as image:
            file = {"file": image}

            data = {"key": self.captcha_key, "method": "post"}

            response = requests.post(
                "http://2captcha.com/in.php", files=file, data=data
            )

            if response.ok and response.text.find("OK") > -1:
                captcha_id = response.text.split("|")[1]  # get captcha_id

                for _ in range(10):
                    response = requests.get(
                        f"http://2captcha.com/res.php?key={self.captcha_key}&action=get&id={captcha_id}"
                    )

                    if response.text.find("CAPCHA_NOT_READY") > -1:  # 尚未辨識完成
                        time.sleep(3)
                    elif response.text.find("OK") > -1:
                        return response.text.split("|")[1]  # 擷取辨識結果
                return None

            else:
                logger.error(
                    "Error occurred while submitting the image for processing."
                )
                return None
