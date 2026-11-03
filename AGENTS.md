# Forgejo API and pull-request requirement

## Forgejo API and pull-request procedure

Before creating, listing, updating, merging, or commenting on a Forgejo pull request, read the canonical machine-readable contract at `../mwg-ops-manual/100-Release-Management/forgejo-api-contract.json` (or the corresponding checked-out operations-manual path on another host).

A valid saved Forgejo browser session and a shell API credential are separate. Do not treat an unavailable `FORGEJO_TOKEN` variable as proof a saved credential is missing, expose a credential, or ask the operator to recreate one before the contract's authenticated-user preflight has identified the configured credential source. If the saved browser session works and API preflight does not, use the browser session for the requested interactive action.

Confirm repository, base branch, head branch, and comparison before preparing a pull request. Creating a pull request, comment, assignment, merge, close, or any other remote state change requires explicit owner approval immediately before that final action.
