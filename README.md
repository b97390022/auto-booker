# auto-booker

auto-booker a Python package to automatically book the court.

[![Docker Build](https://github.com/b97390022/auto-booker/actions/workflows/basic.yml/badge.svg)](https://github.com/b97390022/auto-booker/actions/workflows/basic.yml)

## Create Confin.json
Please place the config.json file into the auto-booker root folder and replace the corresponding values.

```json
{
  "username": "運動中心-使用者名稱",
  "password": "運動中心-使用者密碼",
  "captcha_key": "2captcha_key",
  "chrome_arguments": [
      "--no-sandbox",
      "--disable-web-security",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      "--disable-extensions",
      "--disable-popup-blocking",
      "--start-maximized",
      "--lang=en-US",
      "--window-size=1920,1080",
      "--disable-notifications",
      "--headless"
    ],
  "chrome_excludeSwitches": [
    "enable-logging"
  ],
  "chrome_prefs": {}
}
```

## Usage

```bash
git clone https://github.com/b97390022/auto-booker.git
cd auto-booker

docker compose up -d
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)