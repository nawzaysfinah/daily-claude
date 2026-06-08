# AddTask Calendar Integration & Local Scheduling — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix TASKS.md formatting bug, migrate to a clean local path, add Google Calendar NLP integration in AddTask, and switch the morning briefing from remote CCR to a local Claude Code cron job.

**Architecture:** Single bash script (`AddTask.app/Contents/MacOS/AddTask`) with embedded Python heredocs for text processing. NLP logic is also extracted to `scripts/parse_when.py` for testability. Calendar.app events are created via AppleScript. Morning briefing runs as a local `CronCreate` job inside Claude Code.

**Tech Stack:** Bash, Python 3 (stdlib only), AppleScript/osascript, Calendar.app, Claude Code CronCreate

---

## File Map

| Action | File | Responsibility |
|---|---|---|
| Modify | `AddTask.app/Contents/MacOS/AddTask` | Main app script — fix formatting, add calendar flow |
| Create | `scripts/parse_when.py` | Standalone NLP date/time parser (testable) |
| Create | `tests/test_parse_when.py` | Pytest tests for the NLP parser |
| Create | `TASKS.md` | Repo-level placeholder (points to local path, not pushed with real tasks) |
| Modify | `~/.daily-claude` | Update TASKS_FILE to `~/Documents/tasks.md` |
| Disable | Remote routine `trig_01PXYsANDHpXUkTUp4n2cREf` | Stop cloud agent from running |

---

## Task 1: Fix Python Insertion Formatting Bug

**Files:**
- Modify: `AddTask.app/Contents/MacOS/AddTask` (PYEOF heredoc, lines ~100–145)

The current Python inserts tasks at the bottom of a section but omits the blank line between the last task and the next `##` header. Fix: strip trailing blanks from the accumulated section, then insert one blank before and after the new task line.

- [ ] **Step 1: Open the file and locate the PYEOF block**

```bash
grep -n 'in_section\|result.append\|PYEOF' AddTask.app/Contents/MacOS/AddTask | head -30
```

- [ ] **Step 2: Replace the Python insertion block**

In `AddTask.app/Contents/MacOS/AddTask`, replace everything between `python3 - "$TASKS_FILE" "$SECTION" "$TASK" << 'PYEOF'` and `PYEOF` with:

```python
import sys

tasks_file = sys.argv[1]
section = sys.argv[2]
task = sys.argv[3]
new_line = f"- [ ] {task}"

with open(tasks_file, 'r') as f:
    lines = f.readlines()

inserted = False
result = []
i = 0
in_section = False

while i < len(lines):
    line = lines[i]
    stripped = line.strip()

    if stripped == section:
        in_section = True
        result.append(line)
        i += 1
        continue

    if in_section and (stripped.startswith('## ') or stripped.startswith('---')):
        # End of section — normalize and insert task at bottom
        # Strip trailing blank lines accumulated in this section
        while result and result[-1].strip() == '':
            result.pop()
        result.append('\n')            # one blank line before task
        result.append(new_line + '\n')
        result.append('\n')            # one blank line after task
        inserted = True
        in_section = False

    result.append(line)
    i += 1

# Section was the last block in the file (no trailing ## or ---)
if in_section and not inserted:
    while result and result[-1].strip() == '':
        result.pop()
    result.append('\n')
    result.append(new_line + '\n')
    result.append('\n')
    inserted = True

# Section header not found — append a new section
if not inserted:
    result.append(f'\n{section}\n\n{new_line}\n\n')

with open(tasks_file, 'w') as f:
    f.writelines(result)
```

- [ ] **Step 3: Manually test the formatting**

Create a temporary test file and run the script directly:

```bash
cat > /tmp/test_tasks.md << 'EOF'
# Tasks

## 🔴 Today

- [ ] Existing task

## 🟡 This Week


## 🟢 Backlog


---
_Created: 2026-06-08_
EOF

python3 - /tmp/test_tasks.md "## 🔴 Today" "New task" << 'PYEOF'
# (paste the Python block from Step 2 here)
PYEOF

cat /tmp/test_tasks.md
```

Expected output — blank line between new task and `## 🟡 This Week`:

```markdown
## 🔴 Today

- [ ] Existing task

- [ ] New task

## 🟡 This Week
```

- [ ] **Step 4: Commit**

```bash
git add AddTask.app/Contents/MacOS/AddTask
git commit -m "fix: normalize blank lines around inserted tasks"
```

---

## Task 2: Create NLP Parser as Standalone Script

**Files:**
- Create: `scripts/parse_when.py`
- Create: `tests/test_parse_when.py`

This makes the NLP logic testable independently of the bash app.

- [ ] **Step 1: Create `scripts/` directory**

```bash
mkdir -p scripts tests
```

- [ ] **Step 2: Write the failing tests first**

Create `tests/test_parse_when.py`:

```python
"""Tests for the parse_when NLP date/time parser."""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "parse_when.py"
REF_DATE = "2026-06-08"  # Monday


def run(when_str):
    """Run parse_when.py and return (y, m, d, h, min, y2, m2, d2, h2, min2, human)."""
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
    # 15/6 = 15 June (dd/mm, Singapore)
    start, _, _ = run("15/6 2pm")
    assert start[:3] == [2026, 6, 15]


def test_24h_time():
    start, _, _ = run("tomorrow 14:30")
    assert start[3:5] == [14, 30]


def test_no_date_defaults_to_tomorrow_9am():
    start, _, _ = run("no date here")
    tomorrow = [2026, 6, 9]
    assert start[:3] == tomorrow
    assert start[3] == 9


def test_duration_is_one_hour():
    start, end, _ = run("tomorrow 2pm")
    assert end[3] - start[3] == 1
    assert end[4] == start[4]
```

- [ ] **Step 3: Run tests — expect all to fail (ImportError/FileNotFoundError)**

```bash
cd /Users/syaz/Documents/work/repos/daily-claude
python3 -m pytest tests/test_parse_when.py -v 2>&1 | head -30
```

Expected: `ERROR` — `scripts/parse_when.py` doesn't exist yet.

- [ ] **Step 4: Create `scripts/parse_when.py`**

```python
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


def parse_when(when_str: str, ref: datetime) -> tuple[datetime, datetime, str]:
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
        # Day-of-week (short or full)
        days_map = {
            'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6,
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6,
        }
        for key, dow in days_map.items():
            if re.search(r'\b' + key + r'\b', ws):
                diff = (dow - ref.weekday()) % 7 or 7  # always next occurrence
                event_date = ref + timedelta(days=diff)
                break

    if not event_date:
        # Month name + day (e.g. "June 10", "10 June", "Jun 10")
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
```

- [ ] **Step 5: Run tests — expect them to pass**

```bash
python3 -m pytest tests/test_parse_when.py -v
```

Expected:

```
tests/test_parse_when.py::test_tomorrow_2pm PASSED
tests/test_parse_when.py::test_today_9am PASSED
tests/test_parse_when.py::test_monday_next_week PASSED
tests/test_parse_when.py::test_tuesday PASSED
tests/test_parse_when.py::test_june_10 PASSED
tests/test_parse_when.py::test_dd_slash_mm PASSED
tests/test_parse_when.py::test_24h_time PASSED
tests/test_parse_when.py::test_no_date_defaults_to_tomorrow_9am PASSED
tests/test_parse_when.py::test_duration_is_one_hour PASSED

9 passed in 0.XXs
```

Fix any failures before continuing.

- [ ] **Step 6: Commit**

```bash
git add scripts/parse_when.py tests/test_parse_when.py
git commit -m "feat: add NLP date/time parser with tests"
```

---

## Task 3: Migrate TASKS.md to `~/Documents/tasks.md`

**Files:**
- Modify: `~/.daily-claude`
- Create: `~/Documents/tasks.md` (migrated content)

- [ ] **Step 1: Copy existing TASKS.md to new path**

```bash
cp "/Users/syaz/Documents/Claude/Claude-Cowork/ABOUT ME/TASKS.md" \
   "$HOME/Documents/tasks.md"
```

- [ ] **Step 2: Verify the copy looks right**

```bash
cat ~/Documents/tasks.md
```

Expected: same content as the original file.

- [ ] **Step 3: Update `~/.daily-claude`**

```bash
echo "TASKS_FILE=$HOME/Documents/tasks.md" > ~/.daily-claude
```

- [ ] **Step 4: Verify config**

```bash
cat ~/.daily-claude
```

Expected:
```
TASKS_FILE=/Users/syaz/Documents/tasks.md
```

- [ ] **Step 5: Test that SKILL.md path resolution works**

```bash
bash -c 'source ~/.daily-claude 2>/dev/null && echo "$TASKS_FILE" && cat "$TASKS_FILE" | head -5'
```

Expected: prints the path and the first 5 lines of tasks.md.

---

## Task 4: Disable Remote CCR Routine

The remote routine can't read local files. Disable it — the local cron (Task 6) replaces it.

- [ ] **Step 1: Disable via RemoteTrigger**

In Claude Code, run this tool call:

```
RemoteTrigger action=update trigger_id=trig_01PXYsANDHpXUkTUp4n2cREf body={"enabled": false}
```

- [ ] **Step 2: Verify it's disabled**

```
RemoteTrigger action=get trigger_id=trig_01PXYsANDHpXUkTUp4n2cREf
```

Expected: `"enabled": false` in the response.

---

## Task 5: Add Calendar Flow to AddTask

**Files:**
- Modify: `AddTask.app/Contents/MacOS/AddTask`

Adds the "Add to Calendar?" prompt, NLP hint extraction, "When?"/"Where?" dialogs, confirmation, and AppleScript event creation — all after the existing task insertion block.

- [ ] **Step 1: Locate where to insert the calendar block**

The calendar section goes immediately after this line:

```bash
osascript -e "display notification \"Added to $CATEGORY\" with title \"$TASK\""
```

- [ ] **Step 2: Add the SCRIPTS_DIR resolver after `source "$CONFIG_FILE"`**

In AddTask, after the line `source "$CONFIG_FILE"`, add:

```bash
# Resolve scripts directory relative to this .app bundle
SCRIPTS_DIR="$(dirname "$(dirname "$(dirname "$0")")")/scripts"
```

This resolves from `.../AddTask.app/Contents/MacOS/AddTask` → `.../AddTask.app/` → `.../daily-claude/scripts/`.

> **Note:** This path is valid when the app is run from the repo directory. If the app is on the Desktop (installed via setup.sh), this path won't exist. The calendar flow gracefully skips if `parse_when.py` is not found — see Step 3.

- [ ] **Step 3: Append the calendar block to the end of AddTask**

Replace the final notification line:

```bash
osascript -e "display notification \"Added to $CATEGORY: $TASK\" with title \"Task added ✓\""
```

with:

```bash
osascript -e "display notification \"Added to $CATEGORY\" with title \"$TASK ✓\""

# ── Optional: Add to Google Calendar ───────────────────────────────────────────
# Require parse_when.py to be available (installed app won't have it unless repo is present)
if [ ! -f "$SCRIPTS_DIR/parse_when.py" ]; then
  exit 0
fi

CAL_CHOICE=$(osascript -e 'choose from list {"Yes", "No"} with title "Add to Calendar?" with prompt "'"$TASK"'" default items {"No"}' 2>/dev/null)

if [ "$CAL_CHOICE" != "Yes" ]; then
  exit 0
fi

# NLP pre-fill: extract any time/day hint visible in the task text itself
HINT=$(python3 "$SCRIPTS_DIR/parse_when.py" "$TASK" "$(date '+%Y-%m-%d')" 2>/dev/null | tail -1)
# HINT is the human string, e.g. "tue jun 9 · 2:00pm" — not useful as a pre-fill
# Instead, pull out just the raw time/day fragment from the task for the dialog default
RAW_HINT=$(python3 - "$TASK" << 'HINTEOF'
import sys, re
task = sys.argv[1]
fragments = []
t = re.search(r'\b\d{1,2}(?::\d{2})?\s*(?:am|pm)\b', task, re.IGNORECASE)
if t: fragments.append(t.group(0).strip())
d = re.search(r'\b(?:today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)\b', task, re.IGNORECASE)
if d: fragments.append(d.group(0).strip())
print(' '.join(fragments))
HINTEOF
)

WHEN=$(osascript -e "display dialog \"When is this event?\\n\\nExamples: \\\"tomorrow 2pm\\\", \\\"Monday 3pm\\\", \\\"June 10 9am\\\"\" with title \"Add to Calendar\" default answer \"$RAW_HINT\" buttons {\"Cancel\", \"Next →\"} default button \"Next →\"" -e 'text returned of result' 2>/dev/null)

if [ -z "$WHEN" ]; then
  exit 0
fi

WHERE=$(osascript -e 'display dialog "Location? (leave blank to skip)" with title "Add to Calendar" default answer "" buttons {"Skip", "Done ✓"} default button "Done ✓"' -e 'text returned of result' 2>/dev/null)

# Parse date/time into numeric fields for AppleScript
PARSED=$(python3 "$SCRIPTS_DIR/parse_when.py" "$WHEN" "$(date '+%Y-%m-%d')" 2>/dev/null)

if [ -z "$PARSED" ]; then
  osascript -e 'display dialog "Couldn'\''t parse the date/time. Event not created." with title "Calendar Error" buttons {"OK"}' 2>/dev/null
  exit 0
fi

S_YEAR=$(echo "$PARSED" | sed -n '1p' | awk '{print $1}')
S_MON=$(echo  "$PARSED" | sed -n '1p' | awk '{print $2}')
S_DAY=$(echo  "$PARSED" | sed -n '1p' | awk '{print $3}')
S_HOUR=$(echo "$PARSED" | sed -n '1p' | awk '{print $4}')
S_MIN=$(echo  "$PARSED" | sed -n '1p' | awk '{print $5}')

E_YEAR=$(echo "$PARSED" | sed -n '2p' | awk '{print $1}')
E_MON=$(echo  "$PARSED" | sed -n '2p' | awk '{print $2}')
E_DAY=$(echo  "$PARSED" | sed -n '2p' | awk '{print $3}')
E_HOUR=$(echo "$PARSED" | sed -n '2p' | awk '{print $4}')
E_MIN=$(echo  "$PARSED" | sed -n '2p' | awk '{print $5}')

HUMAN_TIME=$(echo "$PARSED" | sed -n '3p')

# Confirm
CONFIRM=$(osascript -e "display dialog \"Create calendar event?\\n\\n📅 $TASK\\n🕐 $HUMAN_TIME\\n📍 ${WHERE:-(no location)}\" with title \"Add to Calendar\" buttons {\"Cancel\", \"Create ✓\"} default button \"Create ✓\"" -e 'button returned of result' 2>/dev/null)

if [ "$CONFIRM" != "Create ✓" ]; then
  exit 0
fi

# Sanitise strings for AppleScript (replace " with ')
AS_TITLE="${TASK//\"/\'}"
AS_LOCATION="${WHERE//\"/\'}"

osascript << ASEOF
tell application "Calendar"
    -- Build start date numerically (locale-safe)
    set startDate to current date
    set year of startDate to $S_YEAR
    set month of startDate to $S_MON
    set day of startDate to $S_DAY
    set hours of startDate to $S_HOUR
    set minutes of startDate to $S_MIN
    set seconds of startDate to 0

    -- Build end date numerically
    set endDate to current date
    set year of endDate to $E_YEAR
    set month of endDate to $E_MON
    set day of endDate to $E_DAY
    set hours of endDate to $E_HOUR
    set minutes of endDate to $E_MIN
    set seconds of endDate to 0

    -- Find first non-system calendar
    set targetCal to missing value
    repeat with c in every calendar
        set cName to name of c
        if cName is not "Birthdays" and cName is not "Siri Suggestions" and cName is not "Holidays in Singapore" then
            set targetCal to c
            exit repeat
        end if
    end repeat
    if targetCal is missing value then
        set targetCal to first calendar
    end if

    tell targetCal
        make new event with properties {summary:"$AS_TITLE", start date:startDate, end date:endDate, location:"$AS_LOCATION"}
    end tell
    reload calendars
end tell
ASEOF

AS_STATUS=$?
if [ $AS_STATUS -eq 0 ]; then
  osascript -e "display notification \"$HUMAN_TIME\" with title \"Event created: $TASK\""
else
  osascript -e 'display dialog "Calendar event failed. Make sure Calendar.app is open and has permission." with title "Calendar Error" buttons {"OK"}' 2>/dev/null
fi
```

- [ ] **Step 6: Manual smoke test**

Run AddTask from the repo directly to avoid the Desktop copy:

```bash
bash /Users/syaz/Documents/work/repos/daily-claude/AddTask.app/Contents/MacOS/AddTask
```

Walk through:
1. Pick "🔴 Today"
2. Type: `Meeting with team tomorrow 3pm`
3. Check TASKS.md — task should appear with proper blank lines
4. Click "Yes" in the calendar prompt
5. "When?" should pre-fill with `tomorrow 3pm`
6. Click "Next →", skip location, confirm
7. Open Calendar.app — event should appear on tomorrow at 3pm

- [ ] **Step 7: Commit**

```bash
git add AddTask.app/Contents/MacOS/AddTask
git commit -m "feat: add Google Calendar NLP integration to AddTask"
```

---

## Task 6: Set Up Local Morning Briefing Cron

Replace the disabled remote routine with a local Claude Code cron job. This runs inside Claude Code and has full access to local files.

- [ ] **Step 1: Load CronCreate tool via ToolSearch**

```
ToolSearch query="select:CronCreate"
```

- [ ] **Step 2: Create the local cron**

```
CronCreate schedule="0 0 * * *" prompt="Run the daily morning briefing using the skill at /Users/syaz/Documents/work/repos/daily-claude/skills/morning-briefing/SKILL.md. The skill will source ~/.daily-claude to find the TASKS.md path."
```

(8am SGT = 00:00 UTC)

- [ ] **Step 3: Verify with CronList**

```
ToolSearch query="select:CronList"
CronList
```

Confirm the new job appears with schedule `0 0 * * *`.

---

## Task 7: Update setup.sh to Download `scripts/parse_when.py`

So that users who install via `curl | bash` also get the calendar NLP feature.

**Files:**
- Modify: `setup.sh`

- [ ] **Step 1: Add download step after AddTask.app install**

In `setup.sh`, after the `cp -r "$TMP_DIR/$APP_NAME" "$APP_DEST"` block, add:

```bash
# ── Download parse_when.py ────────────────────────────────────────────────────
echo "→  Downloading NLP parser..."
SCRIPTS_DEST="$INSTALL_DIR/daily-claude-scripts"
mkdir -p "$SCRIPTS_DEST"

curl -fsSL "$RAW_URL/scripts/parse_when.py" \
  -o "$SCRIPTS_DEST/parse_when.py"

echo "✓  NLP parser installed"
```

- [ ] **Step 2: Update SCRIPTS_DIR resolution in AddTask**

Since installed users have the app at `~/Desktop/Add Task.app` and scripts at `~/Desktop/daily-claude-scripts/`, update the `SCRIPTS_DIR` resolver in AddTask to try both locations:

```bash
# Resolve scripts directory — try repo-relative first, then Desktop fallback
BUNDLE_PARENT="$(dirname "$(dirname "$(dirname "$0")")")"
if [ -f "$BUNDLE_PARENT/scripts/parse_when.py" ]; then
  SCRIPTS_DIR="$BUNDLE_PARENT/scripts"
elif [ -f "$HOME/Desktop/daily-claude-scripts/parse_when.py" ]; then
  SCRIPTS_DIR="$HOME/Desktop/daily-claude-scripts"
else
  SCRIPTS_DIR=""
fi
```

- [ ] **Step 3: Commit**

```bash
git add setup.sh AddTask.app/Contents/MacOS/AddTask
git commit -m "feat: include parse_when.py in setup.sh install"
```

---

## Task 8: Final Integration Commit and Push

- [ ] **Step 1: Run all tests one final time**

```bash
python3 -m pytest tests/test_parse_when.py -v
```

All 9 tests should pass.

- [ ] **Step 2: Push to GitHub**

```bash
git push origin main
```

- [ ] **Step 3: Verify morning briefing skill path**

```bash
bash -c 'source ~/.daily-claude && cat "$TASKS_FILE"'
```

Should print your tasks from `~/Documents/tasks.md`.

- [ ] **Step 4: Done**

Summary of what changed:
- TASKS.md migrated to `~/Documents/tasks.md` — clean, no spaces, stays local
- Remote CCR routine disabled — tasks never leave the machine
- Local Claude Code cron runs the briefing at 8am SGT with full file access
- AddTask now creates Google Calendar events via NLP + Calendar.app
- Formatting bug fixed — proper blank lines around all inserted tasks
