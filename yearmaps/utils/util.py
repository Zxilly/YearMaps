from datetime import date


def date_encode():
    return date.today().strftime("%Y%m%d")


def date_decode(date_str: str):
    return date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:]))
