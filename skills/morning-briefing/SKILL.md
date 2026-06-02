# Morning Briefing Skill

This is the Claude Cowork scheduled skill for **daily-claude**.

## What this skill does

Runs automatically each morning and delivers a concise briefing covering:

1. **Tasks / To-dos** — Reads the user's `TASKS.md` file. Lists open tasks (`- [ ]`), highlighting anything in the Today section.

2. **Top News** — Web searches for 3–5 top headlines from today. One sentence each.

3. **Weather** — Searches for today's weather for the user's location.

4. **Calendar Events** — If Google Calendar is connected, lists today's meetings and events.

## Instructions

You are running the user's daily morning briefing. Deliver a concise, friendly summary covering these four areas:

1. **Tasks / To-dos** — Read the user's TASKS.md file (check the workspace folder or `~/.daily-claude` config for the path). List open tasks (`- [ ]`), highlighting the Today section first.

2. **Top News** — Use web search to find 3–5 top news headlines from today. Keep each to one sentence.

3. **Weather** — Use web search to find today's weather forecast for the user's location. If location is unknown, note it.

4. **Calendar Events** — If Google Calendar is connected, list today's meetings and events. If not connected, skip and note it.

Format the output with clear emoji headers for each section. Keep the whole briefing scannable and under 300 words. End with a short motivating sentence for the day.

## Setup in Claude Cowork

Ask Claude: "Schedule a daily morning briefing at 8am" and attach this file, or paste the instructions above into the scheduled task prompt.
