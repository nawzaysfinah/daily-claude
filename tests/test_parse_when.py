"""Tests for the parse_when NLP date/time parser."""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "parse_when.py"
REF_DATE = "2026-06-08"  # Monday


def run(when_str):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), when_str, REF_DATE],
        capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    start = list(map(int, lines[0].split()))
    end   = list(map(int, lines[1].split()))
    human = lines[2]
    return start, end, human


def test_tomorrow_2pm():
    start, end, human = run("tomorrow 2pm")
    assert start == [2026, 6, 9, 14, 0]
    assert end   == [2026, 6, 9, 15, 0]
    assert "2:00pm" in human or "2pm" in human.lower()


def test_today_9am():
    start, end, _ = run("today 9am")
    assert start[:3] == [2026, 6, 8]
    assert start[3] == 9


def test_monday_next_week():
    # ref is Monday 2026-06-08; next Monday = 2026-06-15
    start, _, _ = run("Monday 10am")
    assert start[:3] == [2026, 6, 15]
    assert start[3] == 10


def test_tuesday():
    # ref Monday; next Tuesday = 2026-06-09
    start, _, _ = run("tuesday 3pm")
    assert start[:3] == [2026, 6, 9]
    assert start[3] == 15


def test_june_10():
    start, _, _ = run("June 10 9am")
    assert start[:3] == [2026, 6, 10]
    assert start[3] == 9


def test_dd_slash_mm():
    # 15/6 = 15 June (dd/mm, Singapore locale)
    start, _, _ = run("15/6 2pm")
    assert start[:3] == [2026, 6, 15]


def test_24h_time():
    start, _, _ = run("tomorrow 14:30")
    assert start[3:5] == [14, 30]


def test_no_date_defaults_to_tomorrow_9am():
    start, _, _ = run("no date here")
    assert start[:3] == [2026, 6, 9]
    assert start[3] == 9


def test_duration_is_one_hour():
    start, end, _ = run("tomorrow 2pm")
    assert end[3] - start[3] == 1
    assert end[4] == start[4]
