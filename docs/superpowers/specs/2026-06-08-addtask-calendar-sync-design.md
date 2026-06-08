# AddTask: Calendar Integration & Repo Sync Design

**Date:** 2026-06-08
**Status:** Approved

---

## Problem

1. **Morning briefing says TASKS.md is missing.** The remote Claude CoWork agent checks out the git repo and reads `TASKS.md` from the repo root. The user's actual `TASKS.md` lives at a local path (`~/Documents/Claude/Claude-Cowork/ABOUT ME/TASKS.md`) that the cloud agent cannot access.

2. **No calendar integration.** Tasks with time/date information require a separate manual step to create a calendar event.

3. **Formatting bug.** The task insertion Python script omits a blank line between the last task in a section and the next `##` header.

---

## Solution Overview

### Fix 1 — Repo Sync

After every task write, AddTask:
1. Copies `TASKS.md` to `$REPO_DIR/TASKS.md` (repo root)
2. Runs `git commit && git push` in the background (non-blocking)

`REPO_DIR` is stored in `~/.daily-claude`. Existing users without `REPO_DIR` get a one-time prompt to pick the repo folder.

The morning briefing agent reads `TASKS.md` from the repo root — always up to date.

### Fix 2 — Calendar NLP Integration

After a task is added, a "Add to Calendar?" prompt appears. If the user says Yes:
1. Python parses the task text for date/time hints (NLP pre-fill)
2. A "When?" dialog appears, pre-filled with any detected time
3. A "Where?" dialog appears (skippable)
4. A confirmation dialog shows the parsed event details
5. AppleScript creates the event in Calendar.app → syncs to Google Calendar

### Fix 3 — Insertion Formatting

The Python insertion script is updated to normalize blank lines around tasks: strip trailing blanks from the section, add exactly one blank before and after the new task.

---

## Config File Format (`~/.daily-claude`)

```
TASKS_FILE=/path/to/TASKS.md
REPO_DIR=/path/to/daily-claude-repo
```

`REPO_DIR` is optional — sync is skipped if absent or if the directory has no `.git`.

---

## NLP Date/Time Parser

Input: free text from "When?" dialog (e.g. `tomorrow 2pm`, `Monday at 3:30pm`, `June 10 9am`)

Parses:
- **Relative dates:** `today`, `tomorrow`
- **Day names:** `monday`–`sunday` (and 3-letter abbreviations) → next occurrence
- **Absolute dates:** `June 10`, `10 June`, `10/6`, `10-6` (dd/mm, Singapore locale)
- **Times:** `2pm`, `14:00`, `9:30am` → 24h hour + minute
- **Default:** tomorrow at 9:00am if nothing is detected

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

The event title is the full task text (without the `- [ ]` prefix). Location is empty if the user skips the "Where?" dialog.

---

## AddTask Flow (Updated)

```
Launch
 ├─ No ~/.daily-claude → first-run setup (pick folder + pick repo)
 ├─ TASKS_FILE missing → "Reset Config?" dialog
 └─ Config OK → continue

Pick category → Enter task text → Insert into TASKS.md
 ↓
Sync to repo (background git commit + push)
 ↓
"Add to Calendar?" → Yes / No
 ↓ Yes
Parse task text for date/time hints
"When?" dialog (pre-filled with hints)
"Where?" dialog (skippable)
Parse → Confirmation dialog
 ↓ Create ✓
AppleScript → Calendar.app
Notification: "Event created ✓"
```

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| `REPO_DIR` not set | Sync step silently skipped |
| `REPO_DIR` has no `.git` | Sync step silently skipped |
| Git push fails (offline) | Silently ignored; local TASKS.md is still written |
| Python NLP parse fails | Default to tomorrow 9am; user edits in dialog |
| Calendar.app not accessible | Show error: "Couldn't create calendar event. Open Calendar.app and try again." |
| User cancels at any dialog | Exit cleanly; task already saved |

---

## Files Changed

- `AddTask.app/Contents/MacOS/AddTask` — main script
- `~/.daily-claude` — config format extended with `REPO_DIR`
- `TASKS.md` (repo root) — created/synced by AddTask going forward
