# Documentation Workflow

## Goal

Every meaningful project change must be reflected in the documentation.

The idea is simple:

- if we change behavior, we update docs
- if we add a feature, we update docs
- if we remove something, we update docs

This keeps the project understandable over time.

## Rule to Follow for Every Update

For each technical change, check these files:

1. `README.md`
2. `docs/PROJECT_OVERVIEW.md`
3. `docs/TECHNICAL_DOCUMENTATION.md`
4. `docs/ROADMAP.md`
5. `docs/DEMO_SCRIPT.md`

Update only the files that are impacted.

## Quick Decision Guide

### Update `README.md` when:

- installation changes
- launch commands change
- required tools change
- the main project description changes

### Update `docs/PROJECT_OVERVIEW.md` when:

- the product scope changes
- a new major capability appears
- the user flow changes

### Update `docs/TECHNICAL_DOCUMENTATION.md` when:

- architecture changes
- a new module is added
- an agent changes behavior
- the data model changes

### Update `docs/ROADMAP.md` when:

- priorities change
- a milestone is completed
- a new next step becomes important

### Update `docs/DEMO_SCRIPT.md` when:

- demo scenarios change
- new important questions should be showcased

## Lightweight Checklist Before Closing a Task

- Code updated
- Tests updated if needed
- Relevant docs updated
- Launch instructions still valid
- Example questions still valid

## Commit Habit

When possible, keep documentation updates in the same commit as the code change.

That makes the project history much easier to understand.
