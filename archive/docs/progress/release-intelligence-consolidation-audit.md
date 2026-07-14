# Release Intelligence Consolidation Audit

## Objective

Identify repeated verification infrastructure before performing behavior-preserving refactoring.

## Inventory

- Connector modules: 48
- API modules: 24
- Schema modules: 24
- Test modules: 29
- Files using SHA-256: 16
- Files defining or using canonical JSON: 10
- Verification classes: 59
- Issue classes: 7
- Summary classes: 24

## Repeated Verification Properties

### `accepted` — 11 implementations

- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `blocked` — 3 implementations

- `app/connectors/repository/repository_release_audit_ledger_progression_gate.py`
- `app/connectors/repository/repository_release_readiness.py`
- `app/connectors/repository/repository_snapshot_gate.py`

### `critical_issue_count` — 7 implementations

- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `error_issue_count` — 7 implementations

- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `evidence_count` — 3 implementations

- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_certification.py`
- `app/connectors/repository/repository_release_evidence_package.py`

### `exit_code` — 5 implementations

- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_ledger_progression_gate.py`
- `app/connectors/repository/repository_release_audit_report.py`
- `app/connectors/repository/repository_release_readiness.py`
- `app/connectors/repository/repository_snapshot_gate.py`

### `is_healthy` — 4 implementations

- `app/connectors/repository/repository_intelligence_dashboard.py`
- `app/connectors/repository/repository_intelligence_report.py`
- `app/connectors/repository/repository_intelligence_snapshot.py`
- `app/connectors/repository/repository_snapshot_baseline.py`

### `issue_codes` — 7 implementations

- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `issue_count` — 9 implementations

- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `metric_count` — 3 implementations

- `app/connectors/repository/repository_intelligence_dashboard.py`
- `app/connectors/repository/repository_intelligence_snapshot.py`
- `app/connectors/repository/repository_snapshot_baseline.py`

### `metric_names` — 3 implementations

- `app/connectors/repository/repository_intelligence_dashboard.py`
- `app/connectors/repository/repository_intelligence_snapshot.py`
- `app/connectors/repository/repository_snapshot_baseline.py`

### `passed` — 4 implementations

- `app/connectors/repository/repository_release_audit_ledger_progression_gate.py`
- `app/connectors/repository/repository_release_audit_report.py`
- `app/connectors/repository/repository_snapshot_gate.py`
- `app/connectors/repository/repository_snapshot_policy.py`

### `rejected` — 10 implementations

- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_evidence_package.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `status` — 16 implementations

- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger.py`
- `app/connectors/repository/repository_release_audit_ledger_progression_gate.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_comparison.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`
- `app/connectors/repository/repository_release_readiness.py`
- `app/connectors/repository/repository_snapshot_gate.py`

### `valid` — 8 implementations

- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `warning_issue_count` — 7 implementations

- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

## Repeated Functions

### `_is_sha256` — 7 implementations

- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `_normalize_evidence` — 3 implementations

- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `accepted` — 11 implementations

- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `as_json` — 7 implementations

- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_ledger.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_report.py`
- `app/connectors/repository/repository_release_certification.py`
- `app/connectors/repository/repository_release_evidence_package.py`

### `as_markdown` — 5 implementations

- `app/connectors/repository/repository_intelligence_report.py`
- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_ledger.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_report.py`

### `blocked` — 3 implementations

- `app/connectors/repository/repository_release_audit_ledger_progression_gate.py`
- `app/connectors/repository/repository_release_readiness.py`
- `app/connectors/repository/repository_snapshot_gate.py`

### `build` — 35 implementations

- `app/connectors/repository/repository_intelligence_dashboard.py`
- `app/connectors/repository/repository_intelligence_dashboard_summary.py`
- `app/connectors/repository/repository_intelligence_report.py`
- `app/connectors/repository/repository_intelligence_report_summary.py`
- `app/connectors/repository/repository_intelligence_snapshot.py`
- `app/connectors/repository/repository_intelligence_snapshot_summary.py`
- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_attestation_summary.py`
- `app/connectors/repository/repository_release_attestation_verification_summary.py`
- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_bundle_summary.py`
- `app/connectors/repository/repository_release_audit_bundle_verification_summary.py`
- `app/connectors/repository/repository_release_audit_ledger.py`
- `app/connectors/repository/repository_release_audit_ledger_progression_gate_summary.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_comparison.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_comparison_summary.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_summary.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification_summary.py`
- `app/connectors/repository/repository_release_audit_ledger_summary.py`
- `app/connectors/repository/repository_release_audit_ledger_verification_summary.py`
- `app/connectors/repository/repository_release_audit_report.py`
- `app/connectors/repository/repository_release_audit_report_summary.py`
- `app/connectors/repository/repository_release_audit_report_verification_summary.py`
- `app/connectors/repository/repository_release_certificate_verification_summary.py`
- `app/connectors/repository/repository_release_certification.py`
- `app/connectors/repository/repository_release_certification_summary.py`
- `app/connectors/repository/repository_release_evidence_package.py`
- `app/connectors/repository/repository_release_evidence_package_summary.py`
- `app/connectors/repository/repository_release_evidence_package_verification_summary.py`
- `app/connectors/repository/repository_release_readiness_summary.py`
- `app/connectors/repository/repository_snapshot_baseline.py`
- `app/connectors/repository/repository_snapshot_comparison_summary.py`
- `app/connectors/repository/repository_snapshot_gate_summary.py`
- `app/connectors/repository/repository_snapshot_policy_summary.py`

### `canonical_json` — 9 implementations

- `app/connectors/repository/repository_intelligence_snapshot.py`
- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_ledger.py`
- `app/connectors/repository/repository_release_audit_ledger.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_report.py`
- `app/connectors/repository/repository_release_certification.py`
- `app/connectors/repository/repository_release_evidence_package.py`

### `canonical_payload` — 9 implementations

- `app/connectors/repository/repository_intelligence_snapshot.py`
- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_ledger.py`
- `app/connectors/repository/repository_release_audit_ledger.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_report.py`
- `app/connectors/repository/repository_release_certification.py`
- `app/connectors/repository/repository_release_evidence_package.py`

### `critical_issue_count` — 7 implementations

- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `error_issue_count` — 7 implementations

- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `evaluate` — 4 implementations

- `app/connectors/repository/repository_release_audit_ledger_progression_gate.py`
- `app/connectors/repository/repository_release_readiness.py`
- `app/connectors/repository/repository_snapshot_gate.py`
- `app/connectors/repository/repository_snapshot_policy.py`

### `evidence_count` — 3 implementations

- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_certification.py`
- `app/connectors/repository/repository_release_evidence_package.py`

### `exit_code` — 5 implementations

- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_ledger_progression_gate.py`
- `app/connectors/repository/repository_release_audit_report.py`
- `app/connectors/repository/repository_release_readiness.py`
- `app/connectors/repository/repository_snapshot_gate.py`

### `is_healthy` — 4 implementations

- `app/connectors/repository/repository_intelligence_dashboard.py`
- `app/connectors/repository/repository_intelligence_report.py`
- `app/connectors/repository/repository_intelligence_snapshot.py`
- `app/connectors/repository/repository_snapshot_baseline.py`

### `issue_codes` — 7 implementations

- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `issue_count` — 9 implementations

- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `metric_count` — 3 implementations

- `app/connectors/repository/repository_intelligence_dashboard.py`
- `app/connectors/repository/repository_intelligence_snapshot.py`
- `app/connectors/repository/repository_snapshot_baseline.py`

### `metric_names` — 3 implementations

- `app/connectors/repository/repository_intelligence_dashboard.py`
- `app/connectors/repository/repository_intelligence_snapshot.py`
- `app/connectors/repository/repository_snapshot_baseline.py`

### `metric_value` — 3 implementations

- `app/connectors/repository/repository_intelligence_dashboard.py`
- `app/connectors/repository/repository_intelligence_snapshot.py`
- `app/connectors/repository/repository_snapshot_baseline.py`

### `passed` — 4 implementations

- `app/connectors/repository/repository_release_audit_ledger_progression_gate.py`
- `app/connectors/repository/repository_release_audit_report.py`
- `app/connectors/repository/repository_snapshot_gate.py`
- `app/connectors/repository/repository_snapshot_policy.py`

### `rejected` — 10 implementations

- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_evidence_package.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `status` — 16 implementations

- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger.py`
- `app/connectors/repository/repository_release_audit_ledger_progression_gate.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_comparison.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`
- `app/connectors/repository/repository_release_readiness.py`
- `app/connectors/repository/repository_snapshot_gate.py`

### `valid` — 8 implementations

- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `verify_json` — 7 implementations

- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `verify_payload` — 7 implementations

- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

### `warning_issue_count` — 7 implementations

- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`

## SHA-256 Implementations

- `app/connectors/repository/repository_intelligence_snapshot.py`
- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_attestation_verification.py`
- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `app/connectors/repository/repository_release_audit_ledger.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `app/connectors/repository/repository_release_audit_report.py`
- `app/connectors/repository/repository_release_audit_report_verification.py`
- `app/connectors/repository/repository_release_certificate_verification.py`
- `app/connectors/repository/repository_release_certification.py`
- `app/connectors/repository/repository_release_evidence_package.py`
- `app/connectors/repository/repository_release_evidence_package_verification.py`
- `app/connectors/repository/repository_snapshot_baseline.py`

## Canonical JSON Implementations

- `app/connectors/repository/repository_intelligence_snapshot.py`
- `app/connectors/repository/repository_release_attestation.py`
- `app/connectors/repository/repository_release_audit_bundle.py`
- `app/connectors/repository/repository_release_audit_ledger.py`
- `app/connectors/repository/repository_release_audit_ledger_snapshot.py`
- `app/connectors/repository/repository_release_audit_report.py`
- `app/connectors/repository/repository_release_certification.py`
- `app/connectors/repository/repository_release_evidence_package.py`
- `app/api/repository_intelligence_snapshot.py`
- `app/schemas/repository_intelligence_snapshot.py`

## Verification Classes

- `RepositoryReleaseAttestationVerification` — `app/connectors/repository/repository_release_attestation_verification.py`
- `RepositoryReleaseAttestationVerificationIssue` — `app/connectors/repository/repository_release_attestation_verification.py`
- `RepositoryReleaseAttestationVerificationIssueResponse` — `app/schemas/repository_release_attestation_verification.py`
- `RepositoryReleaseAttestationVerificationRequest` — `app/schemas/repository_release_attestation_verification.py`
- `RepositoryReleaseAttestationVerificationResponse` — `app/schemas/repository_release_attestation_verification.py`
- `RepositoryReleaseAttestationVerificationSummary` — `app/connectors/repository/repository_release_attestation_verification_summary.py`
- `RepositoryReleaseAttestationVerificationSummaryBuilder` — `app/connectors/repository/repository_release_attestation_verification_summary.py`
- `RepositoryReleaseAttestationVerificationSummaryResponse` — `app/schemas/repository_release_attestation_verification.py`
- `RepositoryReleaseAuditBundleVerification` — `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `RepositoryReleaseAuditBundleVerificationIssue` — `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `RepositoryReleaseAuditBundleVerificationIssueResponse` — `app/schemas/repository_release_audit_bundle_verification.py`
- `RepositoryReleaseAuditBundleVerificationRequest` — `app/schemas/repository_release_audit_bundle_verification.py`
- `RepositoryReleaseAuditBundleVerificationResponse` — `app/schemas/repository_release_audit_bundle_verification.py`
- `RepositoryReleaseAuditBundleVerificationSummary` — `app/connectors/repository/repository_release_audit_bundle_verification_summary.py`
- `RepositoryReleaseAuditBundleVerificationSummaryBuilder` — `app/connectors/repository/repository_release_audit_bundle_verification_summary.py`
- `RepositoryReleaseAuditBundleVerificationSummaryResponse` — `app/schemas/repository_release_audit_bundle_verification.py`
- `RepositoryReleaseAuditLedgerDocumentVerification` — `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `RepositoryReleaseAuditLedgerSnapshotVerification` — `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `RepositoryReleaseAuditLedgerSnapshotVerificationIssue` — `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `RepositoryReleaseAuditLedgerSnapshotVerificationIssueResponse` — `app/schemas/repository_release_audit_ledger_snapshot_verification.py`
- `RepositoryReleaseAuditLedgerSnapshotVerificationRequest` — `app/schemas/repository_release_audit_ledger_snapshot_verification.py`
- `RepositoryReleaseAuditLedgerSnapshotVerificationResponse` — `app/schemas/repository_release_audit_ledger_snapshot_verification.py`
- `RepositoryReleaseAuditLedgerSnapshotVerificationSummary` — `app/connectors/repository/repository_release_audit_ledger_snapshot_verification_summary.py`
- `RepositoryReleaseAuditLedgerSnapshotVerificationSummaryBuilder` — `app/connectors/repository/repository_release_audit_ledger_snapshot_verification_summary.py`
- `RepositoryReleaseAuditLedgerSnapshotVerificationSummaryResponse` — `app/schemas/repository_release_audit_ledger_snapshot_verification.py`
- `RepositoryReleaseAuditLedgerVerification` — `app/connectors/repository/repository_release_audit_ledger.py`
- `RepositoryReleaseAuditLedgerVerificationIssue` — `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `RepositoryReleaseAuditLedgerVerificationIssueResponse` — `app/schemas/repository_release_audit_ledger_verification.py`
- `RepositoryReleaseAuditLedgerVerificationRequest` — `app/schemas/repository_release_audit_ledger_verification.py`
- `RepositoryReleaseAuditLedgerVerificationResponse` — `app/schemas/repository_release_audit_ledger.py`
- `RepositoryReleaseAuditLedgerVerificationResponse` — `app/schemas/repository_release_audit_ledger_verification.py`
- `RepositoryReleaseAuditLedgerVerificationSummary` — `app/connectors/repository/repository_release_audit_ledger_verification_summary.py`
- `RepositoryReleaseAuditLedgerVerificationSummaryBuilder` — `app/connectors/repository/repository_release_audit_ledger_verification_summary.py`
- `RepositoryReleaseAuditLedgerVerificationSummaryResponse` — `app/schemas/repository_release_audit_ledger_verification.py`
- `RepositoryReleaseAuditReportVerification` — `app/connectors/repository/repository_release_audit_report_verification.py`
- `RepositoryReleaseAuditReportVerificationIssue` — `app/connectors/repository/repository_release_audit_report_verification.py`
- `RepositoryReleaseAuditReportVerificationIssueResponse` — `app/schemas/repository_release_audit_report_verification.py`
- `RepositoryReleaseAuditReportVerificationRequest` — `app/schemas/repository_release_audit_report_verification.py`
- `RepositoryReleaseAuditReportVerificationResponse` — `app/schemas/repository_release_audit_report_verification.py`
- `RepositoryReleaseAuditReportVerificationSummary` — `app/connectors/repository/repository_release_audit_report_verification_summary.py`
- `RepositoryReleaseAuditReportVerificationSummaryBuilder` — `app/connectors/repository/repository_release_audit_report_verification_summary.py`
- `RepositoryReleaseAuditReportVerificationSummaryResponse` — `app/schemas/repository_release_audit_report_verification.py`
- `RepositoryReleaseCertificateVerification` — `app/connectors/repository/repository_release_certificate_verification.py`
- `RepositoryReleaseCertificateVerificationIssue` — `app/connectors/repository/repository_release_certificate_verification.py`
- `RepositoryReleaseCertificateVerificationIssueResponse` — `app/schemas/repository_release_certificate_verification.py`
- `RepositoryReleaseCertificateVerificationRequest` — `app/schemas/repository_release_certificate_verification.py`
- `RepositoryReleaseCertificateVerificationResponse` — `app/schemas/repository_release_certificate_verification.py`
- `RepositoryReleaseCertificateVerificationSummary` — `app/connectors/repository/repository_release_certificate_verification_summary.py`
- `RepositoryReleaseCertificateVerificationSummaryBuilder` — `app/connectors/repository/repository_release_certificate_verification_summary.py`
- `RepositoryReleaseCertificateVerificationSummaryResponse` — `app/schemas/repository_release_certificate_verification.py`
- `RepositoryReleaseEvidencePackageVerification` — `app/connectors/repository/repository_release_evidence_package_verification.py`
- `RepositoryReleaseEvidencePackageVerificationIssue` — `app/connectors/repository/repository_release_evidence_package_verification.py`
- `RepositoryReleaseEvidencePackageVerificationIssueResponse` — `app/schemas/repository_release_evidence_package_verification.py`
- `RepositoryReleaseEvidencePackageVerificationRequest` — `app/schemas/repository_release_evidence_package_verification.py`
- `RepositoryReleaseEvidencePackageVerificationResponse` — `app/schemas/repository_release_evidence_package_verification.py`
- `RepositoryReleaseEvidencePackageVerificationSummary` — `app/connectors/repository/repository_release_evidence_package_verification_summary.py`
- `RepositoryReleaseEvidencePackageVerificationSummaryBuilder` — `app/connectors/repository/repository_release_evidence_package_verification_summary.py`
- `RepositoryReleaseEvidencePackageVerificationSummaryResponse` — `app/schemas/repository_release_evidence_package_verification.py`
- `RepositorySnapshotBaselineVerification` — `app/connectors/repository/repository_snapshot_baseline.py`

## Issue Classes

- `RepositoryReleaseAttestationVerificationIssue` — `app/connectors/repository/repository_release_attestation_verification.py`
- `RepositoryReleaseAuditBundleVerificationIssue` — `app/connectors/repository/repository_release_audit_bundle_verification.py`
- `RepositoryReleaseAuditLedgerSnapshotVerificationIssue` — `app/connectors/repository/repository_release_audit_ledger_snapshot_verification.py`
- `RepositoryReleaseAuditLedgerVerificationIssue` — `app/connectors/repository/repository_release_audit_ledger_verification.py`
- `RepositoryReleaseAuditReportVerificationIssue` — `app/connectors/repository/repository_release_audit_report_verification.py`
- `RepositoryReleaseCertificateVerificationIssue` — `app/connectors/repository/repository_release_certificate_verification.py`
- `RepositoryReleaseEvidencePackageVerificationIssue` — `app/connectors/repository/repository_release_evidence_package_verification.py`

## Highest-Use Repository Imports

- `app.connectors.repository.repository_snapshot_baseline` — 16 imports
- `app.connectors.repository.repository_snapshot_policy` — 14 imports
- `app.connectors.repository.repository_intelligence_dashboard` — 5 imports
- `app.connectors.repository.repository_intelligence_snapshot` — 5 imports
- `app.connectors.repository.repository_release_certification` — 5 imports
- `app.connectors.repository.repository_release_audit_ledger` — 5 imports
- `app.connectors.repository.repository_release_certificate_verification` — 4 imports
- `app.connectors.repository.repository_release_attestation` — 4 imports
- `app.connectors.repository.repository_release_audit_report` — 4 imports
- `app.connectors.repository.repository_release_evidence_package` — 4 imports
- `app.connectors.repository.repository_release_evidence_package_verification` — 4 imports
- `app.connectors.repository.repository_intelligence_report` — 3 imports
- `app.connectors.repository.repository_release_attestation_verification` — 3 imports
- `app.connectors.repository.repository_release_audit_report_verification` — 3 imports
- `app.connectors.repository.repository_release_audit_bundle` — 3 imports
- `app.connectors.repository.repository_release_audit_bundle_verification` — 3 imports
- `app.connectors.repository.repository_release_audit_ledger_snapshot_comparison` — 3 imports
- `app.connectors.repository.repository_release_audit_ledger_verification` — 3 imports
- `app.connectors.repository.repository_release_audit_ledger_snapshot_verification` — 3 imports
- `app.connectors.repository.repository_release_audit_ledger_snapshot` — 3 imports
- `app.connectors.repository.repository_release_readiness` — 3 imports
- `app.connectors.repository.repository_snapshot_gate` — 3 imports
- `app.connectors.repository.repository_architecture_report` — 2 imports
- `app.connectors.repository.repository_knowledge_graph` — 2 imports
- `app.connectors.repository.repository_summary` — 2 imports
- `app.connectors.repository.repository_release_audit_ledger_progression_gate` — 2 imports
- `app.connectors.repository.repository_snapshot_comparison` — 2 imports
- `app.connectors.repository.repository_search_index` — 1 imports
- `app.connectors.repository.repository_intelligence_dashboard_summary` — 1 imports
- `app.connectors.repository.repository_intelligence_report_summary` — 1 imports

## Recommended Consolidation Boundary

The first refactoring sprint should introduce only:

1. A shared canonical JSON serializer.
2. A shared SHA-256 digest helper.
3. A shared SHA-256 format validator.
4. A shared verification issue base model.

Do not consolidate endpoint-specific behavior, public response schemas, status names, or API routes during the first refactoring sprint.

## Required Safety Rule

Refactoring must preserve every existing public API and keep the complete test suite green.
