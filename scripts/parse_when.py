#!/usr/bin/env python3
"""
parse_when.py — NLP date/time parser for AddTask calendar integration.

Usage: python3 parse_when.py "<when_string>" "<YYYY-MM-DD ref_date>"

Outputs three lines:
  YEAR MONTH DAY HOUR MINUTE       (start — space-separated integers)
  YEAR MONTH DAY HOUR MINUTE       (end = start + 1 hour)
  human-readable string            (e.g. "tue jun 9 · 2:00pm")
"""
import sys
import re
from datetime import datetime, timedelta


def parse_when(when_str: str, ref: datetime) -> tuple:
    ws = when_str.lower().strip()

    # ── Time ──────────────────────────────────────────────────────────────────
    hour, minute = 9, 0  # default

    tm = re.search(r'\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b', ws)
    if tm:
        h = int(tm.group(1))
        m = int(tm.group(2) or 0)
        p = tm.group(3)
        if p == 'pm' and h != 12:
            h += 12
        elif p == 'am' and h == 12:
            h = 0
        hour, minute = h, m
    else:
        tm2 = re.search(r'\b(\d{1,2}):(\d{2})\b', ws)
        if tm2:
            hour, minute = int(tm2.group(1)), int(tm2.group(2))

    # ── Date ──────────────────────────────────────────────────────────────────
    event_date = None

    if 'today' in ws:
        event_date = ref
    elif 'tomorrow' in ws:
        event_date = ref + timedelta(days=1)
    else:
        days_map = {
            'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6,
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6,
        }
        for key, dow in days_map.items():
            if re.search(r'\b' + key + r'\b', ws):
                diff = (dow - ref.weekday()) % 7 or 7
                event_date = ref + timedelta(days=diff)
                break

    if not event_date:
        months = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10,
            'november': 11, 'december': 12,
        }
        for mname, mnum in months.items():
            m1 = re.search(r'\b' + mname + r'\w*\s+(\d{1,2})\b', ws)
            m2 = re.search(r'\b(\d{1,2})\s+' + mname + r'\w*\b', ws)
            day = None
            if m1:
                day = int(m1.group(1))
            elif m2:
                day = int(m2.group(1))
            if day:
                yr = ref.year
                try:
                    d = datetime(yr, mnum, day)
                    if d.date() < ref.date():
                        d = datetime(yr + 1, mnum, day)
                    event_date = d
                except ValueError:
                    pass
                break

    if not event_date:
        # dd/mm or dd-mm (Singapore locale)
        dm = re.search(r'\b(\d{1,2})[/\-](\d{1,2})\b', ws)
        if dm:
            try:
                d = datetime(ref.year, int(dm.group(2)), int(dm.group(1)))
                if d.date() < ref.date():
                    d = datetime(ref.year + 1, int(dm.group(2)), int(dm.group(1)))
                event_date = d
            except ValueError:
                pass

    if not event_date:
        event_date = ref + timedelta(days=1)  # default: tomorrow

    start = event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    end = start + timedelta(hours=1)

    human = start.strftime('%a %b %-d · %-I:%M%p').lower()

    return start, end, human


def main():
    when_str = sys.argv[1]
    ref_date = datetime.strptime(sys.argv[2], '%Y-%m-%d')

    start, end, human = parse_when(when_str, ref_date)

    def fmt(dt):
        return f"{dt.year} {dt.month} {dt.day} {dt.hour} {dt.minute}"

    print(fmt(start))
    print(fmt(end))
    print(human)


if __name__ == '__main__':
    main()
