# ACP-001 — Governance Automation Adoption

        Version: 1.0.0

        Status:
        Approved

        Type:
        Architecture Change Proposal

        ------------------------------------------------------------------------------

        ## Purpose

        Approve adoption of Repository Context Resolution and Governance
        Enforcement as deterministic repository-owned change-process
        automation.

        ------------------------------------------------------------------------------

        ## Governing Boundaries

        Repository Context Resolution resolves applicable repository context
        before repository changes begin.

        Governance Enforcement checks deterministic, machine-verifiable
        governance requirements before governed changes are committed.

        Neither capability evaluates architectural quality or replaces human
        judgment.

        ------------------------------------------------------------------------------

        ## Scope

        - `docs/ACP-001-GOVERNANCE-AUTOMATION-ADOPTION.md`
- `docs/REPOSITORY-CHANGE-WORKFLOW.md`
- `.governance/`
- `.githooks/`
- `.github/workflows/`
- `scripts/governance/`
- `scripts/platform/`
- `tests/governance/`

        ------------------------------------------------------------------------------

        ## Approval

        This proposal records the governance architecture approved by the
        governing Systems Architect Discipline session.

        Approved implementation includes:

        - Repository Context Resolution;
        - Governance Enforcement;
        - executable governance policy;
        - proposal scope validation;
        - pre-commit integration;
        - blocking CI integration;
        - deterministic tests;
        - repository change workflow documentation.

        ------------------------------------------------------------------------------

        ## Constraint

        Normative governance remains authoritative.

        Executable policy represents only the machine-verifiable subset.

        Generated repository context is derived state and is not authoritative.
