# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from datetime import timedelta

from odoo.fields import datetime


def generate_date(date_domain_fields):
    series = date_domain_fields
    return eval("date_series_" + series.split("_")[0])(series.split("_")[1])


def date_series_last(date_selection):
    filter_date_value = {}
    date_filter_options = {
        "day": 0,
        "week": 7,
        "month": 30,
        "quarter": 90,
        "year": 365,
    }
    filter_date_value["selected_end_date"] = datetime.strptime(
        datetime.now().strftime("%Y-%m-%d 23:59:59"), "%Y-%m-%d %H:%M:%S"
    )
    filter_date_value["selected_start_date"] = datetime.strptime(
        (datetime.now() - timedelta(days=date_filter_options[date_selection])).strftime(
            "%Y-%m-%d 00:00:00"
        ),
        "%Y-%m-%d %H:%M:%S",
    )
    return filter_date_value


def date_series_this(date_selection):
    return eval("get_date_range_from_" + date_selection)("current")


def date_series_lastp(date_selection):
    return eval("get_date_range_from_" + date_selection)("previous")


def date_series_next(date_selection):
    return eval("get_date_range_from_" + date_selection)("next")


def get_date_range_from_day(date_state):
    filter_date_value = {}

    date = datetime.now()

    if date_state == "previous":
        date = date - timedelta(days=1)
    elif date_state == "next":
        date = date + timedelta(days=1)

    filter_date_value["selected_start_date"] = datetime(date.year, date.month, date.day)
    filter_date_value["selected_end_date"] = datetime(
        date.year, date.month, date.day
    ) + timedelta(days=1, seconds=-1)
    return filter_date_value


def get_date_range_from_week(date_state):
    filter_date_value = {}

    date = datetime.now()

    if date_state == "previous":
        date = date - timedelta(days=7)
    elif date_state == "next":
        date = date + timedelta(days=7)

    date_iso = date.isocalendar()
    year = date_iso[0]
    week_no = date_iso[1]

    filter_date_value["selected_start_date"] = datetime.strptime(
        "%s-W%s-1" % (year, week_no - 1), "%Y-W%W-%w"
    )
    filter_date_value["selected_end_date"] = filter_date_value[
        "selected_start_date"
    ] + timedelta(days=6, hours=23, minutes=59, seconds=59, milliseconds=59)
    return filter_date_value


def get_date_range_from_month(date_state):
    filter_date_value = {}

    date = datetime.now()
    year = date.year
    month = date.month

    if date_state == "previous":
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    elif date_state == "next":
        month += 1
        if month == 13:
            month = 1
            year += 1

    end_year = year
    end_month = month
    if month == 12:
        end_year += 1
        end_month = 1
    else:
        end_month += 1

    filter_date_value["selected_start_date"] = datetime(year, month, 1)
    filter_date_value["selected_end_date"] = datetime(
        end_year, end_month, 1
    ) - timedelta(seconds=1)
    return filter_date_value


def get_date_range_from_quarter(date_state):
    filter_date_value = {}

    date = datetime.now()
    year = date.year
    quarter = int((date.month - 1) / 3) + 1

    if date_state == "previous":
        quarter -= 1
        if quarter == 0:
            quarter = 4
            year -= 1
    elif date_state == "next":
        quarter += 1
        if quarter == 5:
            quarter = 1
            year += 1

    filter_date_value["selected_start_date"] = datetime(year, 3 * quarter - 2, 1)

    month = 3 * quarter
    remaining = int(month / 12)
    filter_date_value["selected_end_date"] = datetime(
        year + remaining, month % 12 + 1, 1
    ) - timedelta(seconds=1)

    return filter_date_value


def get_date_range_from_year(date_state):
    filter_date_value = {}

    date = datetime.now()
    year = date.year

    if date_state == "previous":
        year -= 1
    elif date_state == "next":
        year += 1

    filter_date_value["selected_start_date"] = datetime(year, 1, 1)
    filter_date_value["selected_end_date"] = datetime(year + 1, 1, 1) - timedelta(
        seconds=1
    )

    return filter_date_value
