"""
This file should not include any other or django related files.

use:
 from datetime import datetime, timezone
 now = datetime.now(timezone.utc)
"""

from datetime import datetime, date, timedelta, timezone
from dateutil import parser


class DateUtils(object):
    def get_iso_today():
        return date.today().isoformat()

    def get_datetime_now_utc():
        return datetime.now(timezone.utc)

    def get_datetime_now_iso():
        now = DateUtils.get_datetime_now_utc()
        return now.isoformat()

    def to_utc_date(input_date):
        input_date = input_date.replace(tzinfo=timezone.utc)
        return input_date

    def get_day_diff(time_input):
        current_time = DateUtils.get_datetime_now_utc()
        time_diff = current_time - time_input
        days_diff = time_diff.days
        return days_diff

    def get_local_time(utc_time, time_zone):
        """
        Time zone is a string
        @returns string
        """
        from pytz import timezone

        if not utc_time:
            return ""

        tzn = timezone(time_zone)
        local_time = utc_time.astimezone(tzn)

        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_local_time_object(utc_time, time_zone):
        """
        Time zone is a string
        @returns datetime object
        """
        from pytz import timezone

        if not utc_time:
            return ""

        tzn = timezone(time_zone)
        local_time = utc_time.astimezone(tzn)

        return local_time

    def get_date_yesterday():
        current_date = date.today()
        prev_day = current_date - timedelta(days=1)

        return prev_day

    def get_date_today():
        return date.today()

    def get_date_tommorow():
        current_date = date.today()
        next_day = current_date + timedelta(days=1)

        return next_day

    def get_datetime_file_name():
        return datetime.today().strftime("%Y-%m-%d_%H-%M-%S")

    def get_date_file_name():
        return DateUtils.format_date(datetime.today())

    def get_dir4date(date):
        return date.strftime("%Y-%m-%d")

    def get_date_tuple(date):
        return [date.strftime("%Y"), date.strftime("%m"), date.strftime("%d")]

    def get_iso_datetime(timestamp):
        date = parser.parse(timestamp)
        date = date.isoformat()
        return date

    def parse_datetime(timestamp):
        date = parser.parse(timestamp)
        return date

    def get_datetime_year(datetime):
        return datetime.strftime("%Y")

    def get_datetime_month(datetime):
        return datetime.strftime("%m")

    def get_range4day(date_iso):
        current_date = date.fromisoformat(date_iso)
        next_day = current_date + timedelta(days=1)

        return (current_date, next_day)

    def get_range_today():
        current_date = date.today()
        return DateUtils.get_range4day(current_date.isoformat())

    def is_month_changed():
        yesterday = DateUtils.get_date_yesterday()
        today = DateUtils.get_date_today()

        y_m = DateUtils.get_datetime_month(yesterday)
        t_m = DateUtils.get_datetime_month(today)

        if y_m != t_m:
            return True

        return False

    def get_days_before(number_of_days=7):
        return date.today() - timedelta(days=number_of_days)

    def get_days_before_dt(number_of_days=7):
        return DateUtils.get_datetime_now_utc() - timedelta(days=number_of_days)

    def get_days_range(number_of_days=7):
        date_stop = date.today() + timedelta(days=1)
        date_start = date.today() - timedelta(days=number_of_days)
        return [date_start, date_stop]

    def get_days_range_dt(number_of_days=7):
        date_stop = DateUtils.get_datetime_now_utc() + timedelta(days=1)
        date_start = DateUtils.get_datetime_now_utc() - timedelta(days=number_of_days)
        return [date_start, date_stop]

    def from_string(string_input, string_format="%Y-%m-%dT%H:%M:%SZ"):
        """
        TODO - remove this, we have already parse_datetime?
        """
        return datetime.strptime(string_input, string_format)

    def get_display_date(date_input):
        if date_input:
            return date_input.strftime("%Y-%m-%d %H:%M:%S")
