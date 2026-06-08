# AddTask: Calendar Integration & Local Scheduling Design

**Date:** 2026-06-08
**Status:** Approved (revised — local-only, no cloud sync)

---

## Problem

1. **Morning briefing says TASKS.md is missing.** The remote CCR agent runs in Anthropic's cloud and cannot read local files. Tasks are personal and should stay local.

2. **No calendar integration.** Tasks with time/date information require a separate manual step.

3. **Formatting bug.** The task insertion Python script omits a blank line between the last task in a section and the next `##` header.

4. **TASKS.md path has spaces.** `/Users/syaz/Documents/Claude/Claude-Cowork/ABOUT ME/TASKS.md` — can cause edge-case shell issues.

---

## Solution Overview

### Fix 1 — Local Scheduling (replaces remote CCR)

- Disable the existing remote routine (`trig_01PXYsANDHpXUkTUp4n2cREf`)
- Create a **local Claude Code cron job** (`CronCreate`) that runs the morning briefing at 8am SGT
- The local job uses the SKILL.md prompt with `source ~/.daily-claude && cat "$TASKS_FILE"` — full local filesystem access
- TASKS.md never leaves the machine

### Fix 2 — Migrate TASKS.md to clean path

- New path: `~/Documents/tasks.md`
- Migrate existing tasks from current path
- Update `~/.daily-claude`: `TASKS_FILE=/Users/syaz/Documents/tasks.md`

### Fix 3 — Calendar NLP Integration

After a task is added, "Add to Calendar?" appears. If Yes:
1. Parse task text for date/time hints (NLP pre-fill)
2. "When?" dialog (pre-filled with hints, e.g. `tomorrow 2pm`)
3. "Where?" dialog (skippable)
4. Confirmation dialog showing parsed event details
5. AppleScript creates event in Calendar.app → syncs to Google Calendar

### Fix 4 — Insertion Formatting Bug

Normalize blank lines around inserted tasks: strip trailing blanks, add exactly one blank before and after new task.

---

## Config File Format (`~/.daily-claude`)

```
TASKS_FILE=/Users/syaz/Documents/tasks.md
```

Simple — no repo paths, no cloud config.

---

## NLP Date/Time Parser

Input: free text from "When?" dialog (e.g. `tomorrow 2pm`, `Monday at 3:30pm`, `June 10 9am`)

Parses:
- **Relative dates:** `today`, `tomorrow`
- **Day names:** `monday`–`sunday` (and 3-letter abbreviations) → next occurrence
- **Absolute dates:** `June 10`, `10 June`, `10/6`, `10-6` (dd/mm, Singapore locale)
- **Times:** `2pm`, `14:00`, `9:30am` → 24h hour + minute
- **Default:** tomorrow at 9:00am if nothing detected

Output: macOS AppleScript date string (`Saturday, June 7, 2026 at 2:00:00 PM`) for start and end (default duration: 1 hour).

---

## Calendar.app AppleScript

```applescript
tell application "Calendar"
    set startDate to date "..."
    set endDate to date "..."
    set targetCal to first calendar whose name is not "Birthdays"
    tell targetCal
        make new event with properties {
            summary: "Task title",
            start date: startDate,
            end date: endDate,
            location: "Location or empty"
        }
    end tell
    reload calendars
end tell
```

Event title = full task text. Location = empty string if user skips "Where?".

---

## AddTask Flow (Updated)

```
Launch
 ├─ No ~/.daily-claude → first-run setup (pick folder only — no repo needed)
 ├─ TASKS_FILE missing → "Reset Config?" dialog
 └─ Config OK → continue

Pick category → Enter task text → Insert into TASKS.md (fixed formatting)
        ↓
"Add to Calendar?" → Yes / No
        ↓ Yes
Parse task text for date/time hints
"When?" dialog (pre-filled)
"Where?" dialog (skippable)
Parse → Confirmation dialog
        ↓ Create ✓
AppleScript → Calendar.app
Notification: "Event created ✓"
```

---

## Morning Briefing — Local Cron

The briefing runs as a local Claude Code cron job at 8:00am SGT (`0 0 * * *` UTC).
Prompt sources from `skills/morning-briefing/SKILL.md` — the skill already handles local file discovery via `source ~/.daily-claude`.

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Python NLP parse fails | Default to tomorrow 9am; user edits in dialog |
| Calendar.app not accessible | Dialog: "Couldn't create event. Open Calendar.app and try again." |
| User cancels any dialog | Exit cleanly; task already saved |
| TASKS_FILE not set | Show error; offer Reset Config |

---

## Files Changed

- `AddTask.app/Contents/MacOS/AddTask` — main script (calendar + formatting fix)
- `~/.daily-claude` — updated path
- `~/Documents/tasks.md` — new TASKS.md location (migrated)
