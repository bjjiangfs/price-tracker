import datetime

SEC_PER_HOUR = 60 * 60


def epoch_to_date_hour(epoch_time):
    mytimestamp = datetime.datetime.fromtimestamp(epoch_time)
    return mytimestamp.strftime("%Y-%m-%d-%H")


def epoch_hours_ago(epoch_time, hours=24):
    return epoch_time - hours * SEC_PER_HOUR


def epoch_to_datetime(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time)
