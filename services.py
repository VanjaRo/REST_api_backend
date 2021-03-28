from marshmallow import ValidationError
import re
# Validation


# Length validation
def validate_length(value):
    if len(value) < 1:
        raise ValidationError('Quantity must be greater than 0.')


# Hours and minutes to seconds
def hours_to_seconds(hours):
    hours = re.split('-', hours)
    for i in range(len(hours)):
        seconds = sum(x * int(t)
                      for x, t in zip([3600, 60], hours[i].split(":")))
        hours[i] = seconds
    return str(hours[0]) + '-' + str(hours[1])


def seconds_to_hours(seconds):
    seconds = re.split('-', seconds)
    for i in range(len(seconds)):
        hours = str(int(seconds[i]) // (60*60))
        if len(hours) == 1:
            hours = '0' + hours
        minutes = str((int(seconds[i]) % (60*60) // 60))
        if len(minutes) == 1:
            minutes = '0' + minutes
        seconds[i] = hours + ':' + minutes
    return seconds[0] + '-' + seconds[1]


# Checking if the time periods are overlapping
def order_in_working_hours(working_hours, delivery_hours):
    for work_shift in working_hours:
        work_shift = re.split('-', work_shift)
        for order_shift in delivery_hours:
            order_shift = re.split('-', order_shift)
            if not (work_shift[0] > order_shift[1] or work_shift[1] < order_shift[0]):
                return True
    return False


# Checking if the two time stamps have the common period
def time_within_period(moment_1, moment_2, periods):
    for period in periods:
        period = list(map(int, re.split('-', period)))
        if moment_1 > period[0] and moment_1 < period[1] and moment_2 > period[0] and moment_2 < period[1]:
            return True


# RFC 3339 time to seconds
def rfc_to_seconds(time):
    time = re.split('T', time)[1][:-1]
    time = re.split('\.', time)[0]
    seconds = sum(x * int(t)
                  for x, t in zip([3600, 60], time.split(":")))
    return seconds


# Mapping for convenient calculations
courier_type_mapping = {
    # "type" : (max_weight, salary_coefficient)
    'foot': (10, 2),
    'bike': (15, 5),
    'car': (50, 9)
}


# Rating and earnings calculation algorithm (same region)
if __name__ == '__main__':
    print(seconds_to_hours('41700-50700'))
