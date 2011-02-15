from datetime import datetime, timedelta
from pprint import pformat
import sys

from icalendar import Calendar


def future_events_for_vevents(events):
    now = datetime.utcnow() + timedelta(hours=-9)
    today = now.date()
    for event in events:
        if event['DTSTART'].dt.date() < today:
            continue
        yield event


def data_for_vevent(ev):
    start_date, end_date = [ev[which].dt.replace(tzinfo=None) + timedelta(hours=-9)
        for which in ('DTSTART', 'DTEND')]

    return (start_date.date(), str(ev['SUMMARY']), start_date, end_date)


def main(argv):
    # TODO: specify filename?
    cal_str = open('ical.ics').read()
    cal = Calendar.from_string(cal_str)

    vevents = (ev for ev in cal.walk() if ev.name == 'VEVENT')
    future_vevents = future_events_for_vevents(vevents)
    event_datas = (data_for_vevent(ev) for ev in future_vevents)

    ordered_event_data = sorted(event_datas, key=lambda d: d[0])

    with open('giants_schedule.py', 'w') as outfile:
        outfile.write('import datetime\n\n\n')
        outfile.write('schedule = ')
        outfile.write(pformat(tuple(ordered_event_data)))

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
