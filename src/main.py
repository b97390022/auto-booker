from src.booker import BadmintonBooker
import schedule
from pytz import timezone
import time
from loguru import logger
import os


def prerequisite(booker: BadmintonBooker):
    logger.info(f"Running prerequisite.")
    booker.login()


def main(booker: BadmintonBooker, job_number: int, **kwargs):
    tic = time.perf_counter()
    booker.main(job_number, **kwargs)
    toc = time.perf_counter()
    logger.info(f"Total Jobs finished in {toc - tic:0.4f} seconds.")


if __name__ == "__main__":
    if (job_number := os.environ.get("job_number", 10)) == "":
        job_number = 10
    if (job_days := os.environ.get("job_days", +13)) == "":
        job_days = +13
    if (court_name := os.environ.get("court_name", "E")) == "":
        court_name = "E"

    booker = BadmintonBooker()
    logger.info("Starting schedule jobs...")
    logger.info(
        f"schedule with arguments: job_number: {job_number}, job_days: {job_days}, court_name: {court_name}"
    )
    schedule.every().day.at("23:50:00", timezone("Asia/Taipei")).do(
        prerequisite, booker=booker
    )
    schedule.every().day.at("00:00:00", timezone("Asia/Taipei")).do(
        main,
        booker=booker,
        job_number=job_number,
        court_name=court_name,
        book_date_days=job_days,
    )

    while True:
        schedule.run_pending()
        time.sleep(1)
