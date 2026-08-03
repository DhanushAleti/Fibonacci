# GitHub Labels

**Status:** Draft
**Last Updated:** 2026-08-03

## Purpose

Recommended label set for the `project-phi` GitHub repository, to keep issues and pull requests consistently categorized as the project grows.

## Recommended Labels

| Label | Color (Hex) | Description |
|---|---|---|
| `bug` | `#d73a4a` | Something isn't working as intended |
| `feature` | `#0e8a16` | New feature or capability request |
| `enhancement` | `#a2eeef` | Improvement to existing functionality |
| `research` | `#5319e7` | Research task, investigation, or spike |
| `documentation` | `#0075ca` | Documentation additions or corrections |
| `architecture` | `#1d76db` | System, AI, API, backend, frontend, or data architecture |
| `backend` | `#c5def5` | Backend service code |
| `frontend` | `#bfd4f2` | Frontend application code |
| `ai` | `#7057ff` | AI/ML model, agent, or prompt work |
| `math` | `#b60205` | Quantitative or mathematical modeling |
| `performance` | `#fbca04` | Performance, latency, or resource usage |
| `security` | `#e11d21` | Security vulnerability or hardening |
| `good first issue` | `#7057ff` | Good for newcomers |
| `help wanted` | `#008672` | Extra attention or contributors wanted |
| `blocked` | `#000000` | Blocked on another issue, decision, or dependency |
| `question` | `#d876e3` | Further information is requested |

## Usage Notes

- Apply exactly one primary type label (`bug`, `feature`, `enhancement`, `research`, `documentation`) per issue where possible.
- `architecture`, `backend`, `frontend`, `ai`, `math`, `performance`, and `security` are area labels and can be combined with a type label.
- Use `blocked` alongside a comment explaining what it's blocked on.
- Create labels via GitHub repository Settings → Labels, or with the [GitHub CLI](https://cli.github.com/):

```bash
gh label create "bug" --color d73a4a --description "Something isn't working as intended"
```

## TODO

- [ ] Create these labels on the `DhanushAleti/project-phi` GitHub repository
- [ ] Review label set with team once contributors are added
- [ ] Remove unused default GitHub labels (e.g. `wontfix`, `duplicate`) if not adopted
