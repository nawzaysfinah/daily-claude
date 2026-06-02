# daily-claude 🌅

**Your AI-powered morning OS — built on Claude Cowork.**

daily-claude gives you a frictionless daily system: a one-click app to capture tasks anywhere, and an automated morning briefing from Claude that reads your to-do list, pulls today's news, checks the weather, and shows your calendar — every morning, automatically.

---

## What it does

Every morning, Claude runs a briefing that covers:

- ✅ **Tasks** — your open to-dos from `TASKS.md`, sorted by priority
- 📰 **Top news** — 5 headlines from today
- 🌤️ **Weather** — for your location
- 📅 **Calendar** — today's events from Google Calendar (optional)

Capture tasks instantly with the **Add Task** desktop app — a native macOS popup that drops tasks directly into your `TASKS.md` in the right section.

---

## Quick install (macOS)

```bash
curl -fsSL https://raw.githubusercontent.com/nawzaysfinah/daily-claude/main/setup.sh | bash
```

That's it. The installer:
- Downloads and installs the **Add Task** app to your Desktop
- Clears the macOS security quarantine so it opens immediately
- Prints next steps for Claude Cowork setup

---

## Manual install

1. Download this repo as a ZIP → click **Code → Download ZIP**
2. Unzip it
3. Drag `AddTask.app` to your Desktop (or Applications)
4. Right-click → **Open** the first time (macOS security step, one-time only)

---

## Setting up the morning briefing

daily-claude's briefing runs inside **[Claude Cowork](https://claude.ai)** — Anthropic's desktop app.

**Step 1 — Install Claude Cowork**
Download it from [claude.ai](https://claude.ai) and sign in.

**Step 2 — Set up a scheduled task**
Open Claude Cowork and say:

> "Schedule a daily morning briefing at 8am using the skill file in this repo"

Or paste this prompt directly:

```
Schedule a daily morning briefing at 8am. Each morning, read my TASKS.md, 
search for today's top news headlines, check the weather for my location, 
and list my Google Calendar events for the day. Format it with clear sections 
and keep it under 300 words.
```

**Step 3 — Connect your calendars (optional)**
In Claude Cowork, connect Google Calendar when prompted. Claude will automatically pull today's events into the briefing.

**Step 4 — Point Claude to your TASKS.md**
When you first open Add Task, it will ask where to store your `TASKS.md`. Pick any folder — Claude Cowork reads it from there each morning.

---

## How TASKS.md works

```markdown
# Tasks

## 🔴 Today
- [ ] Review pull request from Amir
- [ ] Send invoice to client

## 🟡 This Week
- [ ] Finish slide deck for Thursday
- [ ] Book dentist appointment

## 🟢 Backlog
- [ ] Learn Blender
- [ ] Clean up Notion workspace
```

- `- [ ]` = open task (Claude reads these)
- `- [x]` = done (Claude skips these)

The Add Task app inserts into the right section automatically.

---

## Add Task app — how it works

**First launch:** picks a folder for your `TASKS.md` and saves a config at `~/.daily-claude`.

**Every launch after:** shows a two-step popup:

1. Pick a category — Today / This Week / Backlog
2. Type your task

Done. The task is appended to `TASKS.md` and a macOS notification confirms it.

**To reconfigure** (change where TASKS.md lives):
```bash
rm ~/.daily-claude
```
Then relaunch the app.

---

## Uninstall

```bash
# Remove the app
rm -rf ~/Desktop/"Add Task.app"

# Remove config
rm ~/.daily-claude

# Optionally remove your TASKS.md
# (keep it if you want your task history)
```

---

## Requirements

- macOS 12 Monterey or later
- [Claude Cowork](https://claude.ai) (free or paid) for the morning briefing
- Python 3 (pre-installed on macOS 12+)

---

## Contributing

PRs welcome. Ideas for next features:
- [ ] Windows / Linux support
- [ ] Menu bar app version
- [ ] Sync TASKS.md to iCloud / Notion
- [ ] Weekly review prompt
- [ ] Due dates and reminders

---

## License

MIT — use it, fork it, build on it.

---

Made with ☕ and Claude.
