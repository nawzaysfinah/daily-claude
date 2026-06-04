# daily-claude 🌅

> An agentic daily briefing system — Claude reads your tasks, pulls news and weather, checks your calendar, and delivers a morning report. Every day. Automatically.

![Platform](https://img.shields.io/badge/platform-macOS-lightgrey?logo=apple)
![Claude](https://img.shields.io/badge/Claude-Cowork-orange?logo=anthropic)
![Shell](https://img.shields.io/badge/shell-bash-4EAA25?logo=gnubash&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

---

## The Idea

Most productivity systems fail because they require you to *work the system*. You have to open the app, review the list, decide what matters.

daily-claude flips this: the agent does the review and delivers a single, opinionated briefing to you. You start the day informed and focused without touching a dashboard.

It's also a practical example of a **context-aggregating agent** — a pattern that's increasingly common in production AI systems. The morning briefing prompt is designed to pull structured context from multiple sources (file, web, calendar API), reason over it, and produce a single coherent output under a token budget.

---

## What It Delivers Each Morning

```
📋 Tasks       — open to-dos from TASKS.md, surfaced by priority
📰 News        — 5 headlines relevant to your work/interests
🌤️  Weather     — today's forecast for your location
📅 Calendar    — today's events from Google Calendar (optional)
```

All in one message, under 300 words, formatted for scanning.

---

## System Architecture

```
                    ┌─────────────────────────────────┐
                    │        Claude Cowork Agent       │
                    │                                  │
  8:00am cron ─────►│  1. Read TASKS.md               │
                    │  2. WebSearch (news headlines)   │
                    │  3. WebSearch (weather)          │
                    │  4. Google Calendar MCP          │
                    │  5. Synthesise → briefing        │
                    └──────────────┬──────────────────┘
                                   │
                             Morning briefing
                             delivered in chat
                                   
  ┌────────────────────────────────────────────────────┐
  │               Add Task (macOS .app)                │
  │                                                    │
  │   Global hotkey / dock click                       │
  │        └─► Category picker (Today/Week/Backlog)    │
  │              └─► Task input                        │
  │                    └─► Appends to TASKS.md         │
  │                          └─► macOS notification    │
  └────────────────────────────────────────────────────┘
```

Two components, one shared file (`TASKS.md`) as the interface between them.

---

## Context Engineering Notes

The morning briefing is a practical example of **context window management for agents**:

**Structured input, not freeform.** `TASKS.md` uses a consistent format (`- [ ]` / `- [x]`, three priority sections) so the agent can parse it reliably without needing to infer structure from messy text.

**Token budget constraint.** The briefing prompt caps output at 300 words. This forces the agent to prioritise — a longer unconstrained output would be less useful than a tighter curated one.

**Multi-source aggregation.** Rather than separate calls for tasks / news / weather, everything is synthesised in one prompt. This gives Claude the full context to make connections (e.g. "you have an outdoor meeting at 2pm and rain is forecast").

**Persistent memory via flat file.** `TASKS.md` acts as durable agent memory across sessions. This sidesteps the need for a database or external state store for a personal productivity agent.

---

## Quick Install (macOS)

```bash
curl -fsSL https://raw.githubusercontent.com/nawzaysfinah/daily-claude/main/setup.sh | bash
```

This downloads and installs the Add Task app to your Desktop and clears macOS security quarantine.

---

## Manual Install

1. Download this repo: **Code → Download ZIP**
2. Unzip and drag `AddTask.app` to your Desktop or Applications
3. Right-click → **Open** the first time (one-time macOS security step)

---

## Setting Up the Morning Briefing

The briefing runs as a scheduled task inside **[Claude Cowork](https://claude.ai)** (Anthropic's desktop app).

**Step 1 — Install Claude Cowork** and sign in at [claude.ai](https://claude.ai).

**Step 2 — Schedule the briefing.** Open Cowork and paste:

```
Schedule a daily morning briefing at 8am. Each morning:
1. Read my TASKS.md and surface open tasks by priority section
2. Search for today's top 5 news headlines
3. Check the weather for my location
4. List my Google Calendar events for today

Format with clear sections. Keep it under 300 words. Lead with anything time-sensitive.
```

**Step 3 — Connect Google Calendar** (optional) — Cowork will prompt you on first run.

**Step 4 — Point Claude to your TASKS.md** — the Add Task app asks on first launch; pick any folder. Cowork reads it from there each morning.

---

## TASKS.md Format

```markdown
# Tasks

## 🔴 Today
- [ ] Review PR from Amir
- [ ] Send invoice to client

## 🟡 This Week
- [ ] Finish slide deck for Thursday
- [ ] Book dentist appointment

## 🟢 Backlog
- [ ] Learn Blender
- [ ] Clean up Notion workspace
```

`- [ ]` = open (agent reads) · `- [x]` = done (agent skips)

The Add Task app inserts into the correct section automatically — no manual editing needed.

---

## Add Task App

A minimal native macOS app built as a Python-backed `.app` bundle.

**First launch:** prompts for your TASKS.md location, saves config to `~/.daily-claude`.

**Every launch:** two-step popup — pick category → type task → done. Appends to TASKS.md and fires a macOS notification.

**To reconfigure:**
```bash
rm ~/.daily-claude  # then relaunch
```

---

## Requirements

- macOS 12 Monterey or later
- Python 3 (pre-installed on macOS 12+)
- [Claude Cowork](https://claude.ai) for the morning briefing

---

## Uninstall

```bash
rm -rf ~/Desktop/"Add Task.app"
rm ~/.daily-claude
# optionally: rm ~/path/to/TASKS.md
```

---

## What's Next

- [ ] Menu bar app version
- [ ] Windows / Linux support
- [ ] Sync TASKS.md to iCloud / Notion
- [ ] Weekly review agent (Sundays)
- [ ] Due dates and reminders

---

## Related Projects

- [`build-llm-apps`](https://github.com/nawzaysfinah/build-llm-apps) — beginner guide to LLM apps including agentic patterns
- [`pdf-knowledge-graph-pipeline`](https://github.com/nawzaysfinah/pdf-knowledge-graph-pipeline) — more complex multi-stage agentic pipeline

---

*Built by [Syaz](https://syaz.super.site) — AI Lecturer @ ITE College West, Singapore*
