# Orchestrator Handbook

Operational guide for coordination, decision logging, and execution sequencing.

---

## Core Responsibilities

1. Maintain consistency across `RULES`, `DECISIONS`, task briefs, and changelog.
2. Break business feedback into implementable task briefs.
3. Resolve cross-agent conflicts.
4. Gate completion on acceptance criteria + tests + documentation.

---

## Daily Operating Loop

1. Review active task briefs in `docs/tasks/`.
2. Review latest decisions and locked rules.
3. Validate branch/workspace state.
4. Issue or refine implementation tasks.
5. Review deliverables and test evidence.
6. Update documentation and changelog.

---

## Decision Protocol

When a blocker appears:
1. Check `RULES_OF_ENGAGEMENT.md`.
2. Check `DECISIONS.md`.
3. If unresolved, collect options with tradeoffs.
4. Request owner decision.
5. Log decision before implementation starts.

---

## Documentation Governance

For any material change:
- update task brief,
- update changelog,
- update decisions,
- update rules (only with explicit approval),
- update migration log (if schema changes).

Historical status/task files remain archival context.

---

## Escalation Conditions

Stop and escalate if:
- data-loss risk,
- unresolved RBAC conflict,
- locked-rule contradiction,
- migration inconsistency,
- API contract ambiguity that blocks frontend/backend synchronization.

---

Last Updated: 2026-02-17
