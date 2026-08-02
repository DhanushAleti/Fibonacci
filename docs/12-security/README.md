# 12 · Security

**Status:** Draft
**Last Updated:** 2026-08-02

## Purpose

Document security policies, threat models, and audit findings for Project PHI.

## Scope

Covers security posture and process documentation. Does not cover credentials or secrets, which must never be committed to this repo.

## What Belongs Here

- Security policies and guidelines
- Threat models
- Audit and review findings

## Naming Convention

Use kebab-case markdown files, e.g. `threat-model.md`.

## Example Files

- `security-policy.md`
- `threat-model.md`

## Best Practices

- Never store secrets, keys, or credentials in this folder
- Review security docs whenever auth, payments, or user data handling changes
- Escalate CRITICAL findings immediately per security review protocol

## TODO

- [ ] Fill in real purpose statement once scope is confirmed
- [ ] Add first real document to this folder
- [ ] Review naming convention with team
