# GitHub Milestones

**Status:** Draft
**Last Updated:** 2026-08-03

## Purpose

Recommended milestone plan for the `project-phi` GitHub repository. These map to the phase structure implied by the existing `docs/` sections and are intended as a starting point for planning — not a committed schedule. Refine and reorder with the team before creating them on GitHub.

## Recommended Milestones

### Phase A — AIOS Foundation

**Status:** Complete (v0.1.0)

Establish the repository, the AI Operating System (AIOS) documentation structure, and skeletons for the PRD, architecture documents, playbooks, templates, workflows, and standards.

### Phase B — Requirements & Architecture Finalization

Move the PRD (`docs/02-project/PHI_PRD.md`) and architecture documents (`docs/03-architecture/`) from drafted skeletons to reviewed, stakeholder-approved content. Record key decisions in `docs/18-decisions/` as ADRs.

### Phase C — Data Foundation

Define and document real data sources, ingestion pipelines, storage, and governance per `docs/09-data/` and `docs/03-architecture/DATA_ARCHITECTURE.md`, ahead of any backend work depending on it.

### Phase D — Backend Core

Implement the core backend services and API layer described in `docs/03-architecture/BACKEND_ARCHITECTURE.md` and `docs/03-architecture/API_ARCHITECTURE.md`. Populate the `backend/` directory.

### Phase E — AI / Model Layer

Implement the AI and model components described in `docs/03-architecture/AI_ARCHITECTURE.md`, operationalizing the role playbooks in `docs/01-ai-playbooks/`. Populate the `models/` directory.

### Phase F — Frontend & User Experience

Implement the frontend application described in `docs/03-architecture/FRONTEND_ARCHITECTURE.md`, integrating with the backend/API layer. Populate the `frontend/` directory.

### Phase G — Testing & Quality Assurance

Build out unit, integration, and end-to-end test suites per `docs/11-testing/`. Populate the `tests/` directory and establish coverage expectations.

### Phase H — Security & Compliance

Implement and document security controls, threat modeling, and secrets management per `docs/12-security/`.

### Phase I — DevOps & Release Engineering

Stand up CI/CD, deployment, and observability workflows per `docs/13-devops/` and `docs/16-workflows/DEPLOYMENT_WORKFLOW.md`. Populate `.github/` with real workflow configuration.

### Phase J — Public / Beta Release

Stabilization pass across all layers, documentation completeness review, and the first tagged public or beta release, following `docs/16-workflows/RELEASE_WORKFLOW.md`.

## Usage Notes

- Create milestones via GitHub repository Issues → Milestones, or with the [GitHub CLI](https://cli.github.com/):

```bash
gh api repos/DhanushAleti/project-phi/milestones -f title="Phase B — Requirements & Architecture Finalization"
```

- Milestones are intentionally sequential at this stage; revisit ordering once real scope and staffing are known.
- Each milestone should get a due date and description once the team commits to a plan — none are set here to avoid inventing a timeline.

## TODO

- [ ] Review and reorder phases with the team
- [ ] Create these milestones on the `DhanushAleti/project-phi` GitHub repository
- [ ] Attach due dates once scope and staffing are confirmed
