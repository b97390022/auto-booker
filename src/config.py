import json
from pathlib import Path
from pydantic import BaseModel, SecretStr, ValidationError

from loguru import logger

config = None
values = None


@logger.catch
def load_values():
    global values
    config_file_path = Path("config.json").resolve()
    with open(config_file_path) as f:
        values = json.load(f)


load_values()


class Config(BaseModel):
    """Simple singleton class for managing and accessing configs"""

    username: SecretStr
    password: SecretStr
    captcha_key: SecretStr
    chrome_arguments: list[str] = []
    chrome_excludeSwitches: list[str] = []
    chrome_prefs: dict[str, str] = []


config: Config = Config.model_validate(values)

if __name__ == "__main__":
    print(config.username)
