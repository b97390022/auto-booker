import datetime
from src.booker import BadmintonBooker
import schedule
from pytz import timezone
import time
from loguru import logger


def prerequisite(booker: BadmintonBooker):
    logger.info(f"Running prerequisite.")
    booker.login()


def main(booker: BadmintonBooker, job_number: int, **kwargs):
    tic = time.perf_counter()
    booker.main(job_number, **kwargs)
    toc = time.perf_counter()
    logger.info(f"Total Jobs finished in {toc - tic:0.4f} seconds.")


if __name__ == "__main__":
    booker = BadmintonBooker()
    schedule.every().day.at("23:50:00", timezone("Asia/Taipei")).do(
        prerequisite, booker=booker
    )
    schedule.every().day.at("00:00:00", timezone("Asia/Taipei")).do(
        main, booker=booker, job_number=5, court_name="C", book_date_days=+13
    )

    while True:
        schedule.run_pending()
        time.sleep(1)
