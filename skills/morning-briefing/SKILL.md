# Morning Briefing Skill

This is the Claude Cowork scheduled skill for **daily-claude**.

## What this skill does

Runs automatically each morning and delivers a concise briefing covering:

1. **Tasks / To-dos** — Reads the user's `TASKS.md` file. Lists open tasks (`- [ ]`), highlighting anything in the Today section.
2. **Top News** — Web searches for 3–5 top headlines from today. One sentence each.
3. **Weather** — Searches for today's weather for the user's location.
4. **Calendar Events** — If Google Calendar is connected, lists today's meetings and events.

---

## Instructions

You are running the user's daily morning briefing. Follow each step in order.

### Step 1 — Find and read TASKS.md

Run this bash command to find the tasks file path:

```bash
bash -c 'source ~/.daily-claude 2>/dev/null && echo "$TASKS_FILE"'
```

- If the command returns a path (e.g. `/Users/syaz/Documents/TASKS.md`), use the Read tool to read that file.
- If the command returns nothing or errors, tell the user: "I couldn't find your TASKS.md. Open the Add Task app once to configure the path, or run `cat ~/.daily-claude` to check your config."
- If the file exists but is empty or has no open tasks, note "No open tasks today — clear slate! 🎉"

List open tasks (`- [ ]`) grouped by section. Show **🔴 Today** first, then **🟡 This Week**, then **🟢 Backlog**. Skip completed tasks (`- [x]`).

### Step 2 — Top News

Use web search to find 3–5 top news headlines from today. Keep each to one sentence.

### Step 3 — Weather

Use web search to find today's weather forecast for the user's location (Singapore by default). If location is unknown, note it.

### Step 4 — Calendar Events

If Google Calendar is connected, list today's meetings and events. If not connected, skip this section silently.

---

## Output Format

Format with clear emoji headers. Keep the whole briefing scannable and under 300 words. End with a short motivating sentence for the day.

```
📋 Tasks
...

📰 News
...

🌤️ Weather
...

📅 Calendar
...
```

---

## Setup in Claude Cowork

Ask Claude: "Schedule a daily morning briefing at 8am" and attach this file, or paste the instructions above into the scheduled task prompt.
