from datetime import datetime, timedelta
import sys

from icalendar import Calendar


def data_for_vevent(ev):
    start_date, end_date = [ev[which].dt.replace(tzinfo=None) + timedelta(hours=-9) for which in ('DTSTART', 'DTEND')]

    # TODO: convert to PT

    return (start_date.date(), str(ev['SUMMARY']), start_date, end_date)


def main(argv):
    # TODO: specify filename?
    cal_str = open('ical.ics').read()
    cal = Calendar.from_string(cal_str)

    vevents = (ev for ev in cal.walk() if ev.name == 'VEVENT')
    event_datas = (data_for_vevent(ev) for ev in vevents)

    ordered_event_data = sorted(event_datas, key=lambda d: d[0])
    for data in ordered_event_data:
        print str(data)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
