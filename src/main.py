import argparse
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
    parser = argparse.ArgumentParser(description="Docker Example")

    parser.add_argument(
        "--job_number", type=int, help="執行的任務數量", required=False, default=10
    )
    parser.add_argument(
        "--job_days", type=int, help="預計要預約的日期相對於排程日", required=False, default=+13
    )

    args = parser.parse_args()

    booker = BadmintonBooker()
    schedule.every().day.at("23:50:00", timezone("Asia/Taipei")).do(
        prerequisite, booker=booker
    )
    schedule.every().day.at("00:00:00", timezone("Asia/Taipei")).do(
        main,
        booker=booker,
        job_number=args.job_number,
        court_name="E",
        book_date_days=args.job_days,
    )
    schedule.every().day.at("00:00:00", timezone("Asia/Taipei")).do(
        main,
        booker=booker,
        job_number=args.job_number,
        court_name="F",
        book_date_days=args.job_days,
    )

    while True:
        schedule.run_pending()
        time.sleep(1)
