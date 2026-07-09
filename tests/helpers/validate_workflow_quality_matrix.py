#!/usr/bin/env python3
"""Validate workflow-quality matrix structure and representative samples."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


EXPECTED_IDS = {
    "simple-factual-qa",
    "tiny-wording-edit",
    "git-status-version-question",
    "quick-single-owner-bug",
    "behavior-smoke-ordinary-bug-code-necessity",
    "behavior-smoke-requested-fallback-existence-check",
    "failing-test-diagnosis",
    "ambiguous-feature",
    "explicit-aegis-goal",
    "approved-spec-to-plan",
    "completion-claim",
    "architecture-completion-adr-backfill-check",
    "pre-addition-existence-check-before-design",
    "pre-addition-existence-check-before-plan",
    "change-necessity-before-code-change",
    "new-helper-path-change-necessity",
    "strict-tdd-new-guard-change-necessity",
    "plan-time-complexity-check-before-design",
    "plan-time-complexity-check-before-plan",
    "pre-edit-complexity-check-before-code",
    "pre-edit-complexity-check-debugging-fix",
    "tdd-auto-small-task-light-verification",
    "tdd-auto-risky-code-strict",
    "tdd-off-no-automatic-tdd",
    "tdd-off-native-host-risky-code-no-explicit-tdd",
    "tdd-green-local-not-final-completion",
    "minimal-sufficient-repair-not-local-patch",
    "core-file-complexity-delta-before-completion",
    "oversized-maintained-test-file-governance",
    "artifact-complexity-budget-plan-sprawl",
    "high-risk-merge-independent-review",
    "simple-completion-no-adr-ceremony",
    "architecture-area-bugfix-restores-baseline-no-adr",
    "layer-stop-local-root-cause",
    "layer-stop-cross-system-contract",
    "layer-stop-spec-gap",
    "fast-path-no-layer-stop-card",
    "layer-stop-user-falsifier-correction",
    "topology-conjunctive-cluster-collapses-to-spec-gap",
    "topology-independent-compound-divergent",
    "strong-opinion-product-risk-lens",
    "strong-opinion-plan-pressure-test",
    "architecture-integrity-higher-level-path",
    "baseline-role-alignment-review",
    "aegis-invocation-visibility-natural",
    "aegis-invocation-visibility-owner-workflows",
    "loaded-aegis-skill-requires-entry-visibility",
    "compressed-final-keeps-aegis-visibility",
    "aegis-semantic-slots-natural-surface",
    "trace-digest-white-box-requested",
    "completion-governance-receipt-natural",
    "strong-opinion-review-findings-first",
    "strong-opinion-release-readiness-summary",
    "strong-opinion-retro-memory-filter",
    "strong-opinion-fast-path-no-persona",
    "interrupted-long-task-resume",
    "behavior-smoke-old-path-cleanup-anti-entropy",
    "governance-compat-cleanup",
    "internal-trigger-retirement",
    "duplicate-owner-collapse",
    "unknown-is-not-evidence",
    "host-fallback-with-real-boundary",
    "drop-table-hard-stop",
    "source-of-truth-object-hard-stop",
    "derived-cache-safe-cleanup",
    "migration-file-vs-live-data",
    "executing-plan-new-code-path-change-necessity",
    "plain-dead-import-does-not-trigger-anti-entropy",
}

REQUIRED_FIELDS = {
    "id",
    "prompt",
    "expectedPrimarySkill",
    "allowedSecondarySkills",
    "mustNotDo",
    "expectedOutputShape",
    "workspacePolicy",
    "expectedArtifacts",
    "verificationSignal",
}

REQUIRED_PRIMARY_SKILLS = {
    "goal-framing",
    "brainstorming",
    "writing-plans",
    "systematic-debugging",
    "test-driven-development",
    "verification-before-completion",
    "long-task-continuation",
    "requesting-code-review",
    "recording-architecture-decisions",
}

REQUIRED_CONTRACTS = {
    "using-aegis",
    "goal-framing",
    "brainstorming",
    "writing-plans",
    "systematic-debugging",
    "test-driven-development",
    "anti-entropy-governance",
    "executing-plans",
    "verification-before-completion",
    "long-task-continuation",
}

CONTRACT_REQUIREMENTS = {
    "verification-before-completion": [
        "Aegis Visibility",
        "Aegis Impact and Safety Receipt",
        "Key judgment",
        "Avoided misfix",
        "Boundary held",
        "Baseline alignment",
        "Complexity control",
        "Evidence strength",
        "Uncovered risk",
        "Next most valuable verification",
        "evidence-action",
        "verification-result",
        "covered-scope",
        "uncovered-scope",
        "residual-risk",
        "confidence-grade",
        "L0 fast-path",
        "L1 compact receipt",
        "L2 triggered expansions",
        "conditional-expansion-triggers",
        "completion-boundary",
        "complexity-reference",
        "baseline-reference",
        "adr-reference",
        "anti-entropy-reference",
        "Natural Aegis closeout",
        "Semantic Slots",
        "Natural Surface",
        "Governance Receipt",
    ],
    "systematic-debugging": [
        "Aegis Visibility",
        "Layer Stop Card",
        "Change Necessity",
        "Existence Check",
        "Pre-Edit Complexity Check",
        "Pre-Edit Owner-Fit Decision",
        "Pre-Claim Gate",
        "Topology Card",
        "Minimality Check",
    ],
    "test-driven-development": [
        "Aegis Visibility",
        "Change Necessity",
        "Pre-Edit Complexity Check",
        "Pre-Edit Owner-Fit Decision",
        "TDD Route",
        "Complexity Budget",
    ],
    "anti-entropy-governance": [
        "Aegis Visibility",
        "Anti-Entropy Declaration",
        "Retirement Decision",
        "Verification Plan",
        "Gap Closure",
        "Data Destruction Guard",
    ],
    "executing-plans": [
        "Aegis Visibility",
        "Change Necessity",
        "Pre-Edit Complexity Check",
        "Pre-Edit Owner-Fit Decision",
        "Complexity Budget",
    ],
    "brainstorming": [
        "Aegis Visibility",
        "BaselineUsageDraft",
        "Existence Check",
        "Plan-Time Complexity Check",
        "Complexity Budget",
        "Product Risk Lens",
        "Architecture Integrity Lens",
        "Baseline Role Alignment",
    ],
    "writing-plans": [
        "Aegis Visibility",
        "Change Necessity",
        "Existence Check",
        "Plan-Time Complexity Check",
        "Complexity Budget",
        "Plan Pressure Test",
        "Architecture Integrity Lens",
    ],
    "recording-architecture-decisions": [
        "Aegis Visibility",
        "Decision Candidate",
        "ADR Gate",
        "ADR Action",
        "Owner Surface",
        "Baseline Sync",
        "Boundary",
        "Retro / Memory Filter",
    ],
    "using-aegis": ["ArchitectureReviewRequired", "Aegis Reason Note"],
    "goal-framing": ["Aegis Visibility", "Stop condition", "Continuation"],
    "long-task-continuation": ["Aegis Visibility", "DriftCheckDraft", "Slice Card"],
    "requesting-code-review": ["Aegis Visibility", "Findings First", "Baseline Role Alignment"],
}

SAMPLE_RULES: dict[str, dict[str, Any]] = {
    "tiny-wording-edit": {
        "primary": None,
        "must_not": [
            "force-design-spec",
            "create-project-workspace-records",
            "emit-trace-digest-for-fast-path",
        ],
        "signals": ["git-diff-check-or-targeted-readback"],
    },
    "quick-single-owner-bug": {
        "primary": "systematic-debugging",
        "must_not": [
            "guess-fix-without-reproduction",
            "edit-source-before-change-necessity",
            "emit-full-architecture-ceremony",
        ],
        "signals": [
            "reproduction",
            "change-necessity-before-source-edit",
            "fresh-pass",
        ],
        "shapes": ["quick-bug-lane", "change-necessity"],
    },
    "behavior-smoke-ordinary-bug-code-necessity": {
        "primary": "systematic-debugging",
        "must_not": [
            "wait-for-change-necessity-keyword",
            "hide-code-necessity-readback",
            "edit-source-before-change-necessity",
        ],
        "signals": [
            "behavior-triggered-not-prompt-token",
            "natural-code-necessity-readback",
            "minimum-change-boundary",
            "decision-code-change",
        ],
        "shapes": ["quick-bug-lane", "natural-code-necessity"],
    },
    "behavior-smoke-requested-fallback-existence-check": {
        "primary": "systematic-debugging",
        "allowed": ["first-principles-review", "anti-entropy-governance"],
        "must_not": [
            "treat-user-requested-fallback-as-creation-proof",
            "add-requested-fallback-without-existence-check",
            "skip-existing-owner-reuse-check",
        ],
        "signals": [
            "behavior-triggered-not-prompt-token",
            "fallback-addition-triggers-existence-check",
            "existing-owner-reuse-candidate",
            "creation-proof",
            "entropy-retirement-impact",
        ],
        "shapes": ["patch-shape", "existence-check"],
    },
    "architecture-completion-adr-backfill-check": {
        "primary": "verification-before-completion",
        "allowed": ["recording-architecture-decisions"],
        "must_not": [
            "skip-architecture-alignment",
            "skip-adr-backfill-check",
        ],
        "must_not_join_contains": ["authoritative"],
        "signals": ["architecture-alignment", "baseline-sync"],
    },
    "direct-adr-lifecycle-request": {
        "primary": "recording-architecture-decisions",
        "must_not": [
            "treat-adr-as-completion-authority",
            "write-adr-without-gate-check",
            "skip-baseline-sync-closure",
        ],
        "signals": ["adr-gate", "owner-surface", "baseline-sync", "unchanged-reason"],
    },
    "direct-adr-skip-request": {
        "primary": "recording-architecture-decisions",
        "no_artifacts": True,
        "must_not": [
            "force-adr-creation",
            "force-baseline-writeback",
            "treat-implementation-detail-as-durable-decision",
        ],
    },
    "completion-claim": {
        "allowed_absent": ["requesting-code-review"],
    },
    "core-file-complexity-delta-before-completion": {
        "primary": "verification-before-completion",
        "must_not": [
            "skip-complexity-delta",
            "skip-complexity-closure",
            "skip-complexity-governance-suggestion",
            "ignore-file-crossing-800-lines",
            "retain-old-logic-without-retirement-trigger",
            "claim-completion-with-entropy-increase-hidden",
        ],
        "signals": [
            "complexity-delta",
            "complexity-closure",
            "complexity-governance-suggestion",
            "file-thresholds",
            "net-entropy",
            "retirement-closure",
        ],
        "shapes": ["complexity-delta", "governance-suggestion"],
    },
    "oversized-maintained-test-file-governance": {
        "primary": "verification-before-completion",
        "must_not": [
            "treat-maintained-test-file-as-cheap-exception",
            "skip-major-complexity-alert",
            "claim-complete-with-exceeded-unresolved-budget",
        ],
        "signals": [
            "maintained-test-file",
            "complexity-closure",
            "major-complexity-alert",
            "not-complete-or-needs-follow-up",
        ],
        "shapes": [
            "complexity-delta",
            "complexity-closure",
            "completion-time-complexity-repair-decision",
            "major-complexity-alert",
        ],
    },
    "artifact-complexity-budget-plan-sprawl": {
        "primary": "writing-plans",
        "must_not": [
            "ignore-plan-artifact-complexity",
            "create-new-plan-for-micro-slice-without-trigger",
            "skip-complexity-budget",
        ],
        "signals": [
            "artifact-class-plan",
            "projected-plan-sprawl",
            "planless-slice-lane-or-parent-plan-reuse",
        ],
        "shapes": ["complexity-budget", "plan-time-complexity-check"],
    },
    "tdd-auto-small-task-light-verification": {
        "primary": None,
        "must_not": [
            "force-red-green-refactor",
            "load-test-driven-development-for-tiny-edit",
            "skip-verification-before-completion",
        ],
        "signals": ["tdd-route-auto-light-or-skipped"],
    },
    "tdd-auto-risky-code-strict": {
        "primary": "test-driven-development",
        "must_not": [
            "skip-strict-tdd-route",
            "write-production-code-before-failing-test",
            "skip-producer-consumer-regression",
        ],
        "signals": ["tdd-route-auto-strict"],
    },
    "tdd-off-no-automatic-tdd": {
        "primary": None,
        "must_not": [
            "auto-trigger-tdd",
            "treat-off-as-skip-verification",
            "skip-verification-before-completion",
        ],
        "signals": ["tdd-default-off", "fresh-completion-evidence"],
    },
    "tdd-off-native-host-risky-code-no-explicit-tdd": {
        "primary": "writing-plans",
        "allowed": ["verification-before-completion"],
        "must_not": [
            "auto-trigger-tdd",
            "infer-strict-route-from-risk-alone",
            "treat-off-as-skip-verification",
        ],
        "signals": ["literal-marker-boundary", "tdd-off"],
        "shapes": ["plan-basis-files-compat-tasks-risks-retirement"],
    },
    "tdd-green-local-not-final-completion": {
        "primary": "verification-before-completion",
        "allowed": ["test-driven-development", "long-task-continuation"],
        "must_not": [
            "treat-green-as-final-completion",
            "skip-goal-closure",
            "ignore-slice-card-goal",
            "hide-uncovered-scope",
        ],
        "signals": [
            "green-local-proof",
            "slice-card-goal",
            "parent-acceptance",
            "success-evidence",
            "uncovered-scope",
        ],
        "shapes": ["goal-closure", "slice-card-local-vs-final-completion"],
    },
    "minimal-sufficient-repair-not-local-patch": {
        "primary": "systematic-debugging",
        "must_not": [
            "equate-minimal-change-with-smallest-diff",
            "add-fallback-without-owner-check",
            "skip-minimality-check",
            "skip-retirement-trigger",
        ],
        "signals": [
            "minimality-check",
            "existing-owner-reuse-path",
            "correct-owner",
            "bug-class-fixed",
            "existence-proof",
            "retirement",
            "verdict",
        ],
    },
    "pre-addition-existence-check-before-design": {
        "primary": "brainstorming",
        "allowed": ["first-principles-review", "anti-entropy-governance"],
        "must_not": [
            "add-new-surface-without-existence-check",
            "skip-existing-owner-reuse-check",
            "treat-new-artifact-as-default",
            "turn-existence-check-into-runtime-gate",
        ],
        "signals": [
            "existence-check",
            "existing-owner-reuse-candidate",
            "creation-proof",
            "entropy-retirement-impact",
            "reuse-existing-or-add-with-proof",
        ],
        "shapes": ["existence-check"],
    },
    "pre-addition-existence-check-before-plan": {
        "primary": "writing-plans",
        "allowed": ["first-principles-review", "anti-entropy-governance"],
        "must_not": [
            "write-tasks-before-existence-check",
            "create-new-owner-without-creation-proof",
            "retain-fallback-without-retirement-impact",
            "skip-reuse-existing-decision",
        ],
        "signals": [
            "existence-check",
            "proposed-new-surface",
            "existing-owner-reuse-candidate",
            "creation-proof",
            "entropy-retirement-impact",
        ],
        "shapes": ["existence-check"],
    },
    "change-necessity-before-code-change": {
        "primary": "writing-plans",
        "allowed": ["systematic-debugging", "test-driven-development"],
        "must_not": [
            "write-source-edits-before-change-necessity",
            "force-using-aegis-heavy-entry",
            "skip-non-code-option-check",
        ],
        "signals": [
            "change-necessity",
            "code-change-decision",
            "minimum-change-boundary",
            "using-aegis-stays-route-only",
        ],
        "shapes": ["change-necessity"],
    },
    "new-helper-path-change-necessity": {
        "primary": "writing-plans",
        "allowed": ["test-driven-development", "verification-before-completion"],
        "must_not": [
            "treat-tiny-helper-as-too-small-for-change-necessity",
            "write-source-edits-before-change-necessity",
            "skip-minimum-boundary-for-new-source-path",
        ],
        "signals": [
            "any-new-source-code-path-triggers-change-necessity",
            "tiny-helper-not-exempt",
            "minimum-change-boundary",
            "decision-code-change",
        ],
        "shapes": ["new-source-path-change-necessity"],
    },
    "strict-tdd-new-guard-change-necessity": {
        "primary": "test-driven-development",
        "allowed": ["verification-before-completion"],
        "must_not": [
            "enter-red-green-before-change-necessity",
            "treat-small-guard-as-too-small-for-change-necessity",
            "skip-non-code-option-check",
        ],
        "signals": [
            "any-new-source-code-path-triggers-change-necessity",
            "small-guard-not-exempt",
            "decision-code-change",
            "before-strict-red-green",
        ],
        "shapes": ["strict-tdd-change-necessity"],
    },
    "strong-opinion-product-risk-lens": {
        "primary": "brainstorming",
        "must_not": [
            "role-persona-theater",
            "override-baseline-evidence",
            "start-implementation-immediately",
        ],
        "signals": ["product-risk-lens", "non-goals", "tradeoff", "decision-needed"],
    },
    "strong-opinion-plan-pressure-test": {
        "primary": "writing-plans",
        "must_not": [
            "write-tasks-without-owner-contract-retirement-check",
            "turn-pressure-test-into-approval-gate",
            "redesign-approved-spec-without-cause",
        ],
        "signals": ["plan-pressure-test", "owner-contract-retirement", "verification-scope"],
    },
    "architecture-integrity-higher-level-path": {
        "primary": "writing-plans",
        "allowed": ["first-principles-review"],
        "must_not": [
            "write-tasks-before-architecture-integrity-lens",
            "add-caller-side-fallback-without-higher-owner-check",
            "skip-retirement-or-falsifier",
            "turn-integrity-lens-into-runtime-gate",
        ],
        "signals": [
            "architecture-integrity-lens",
            "invariant",
            "canonical-owner-contract",
            "responsibility-overlap",
            "higher-level-path",
            "retirement",
            "falsifier",
            "verdict",
        ],
    },
    "baseline-role-alignment-review": {
        "primary": "brainstorming",
        "allowed": ["first-principles-review"],
        "must_not": [
            "collapse-requirements-and-architecture-baselines",
            "rename-architecture-drift-without-compatibility-alias",
            "turn-baseline-alignment-into-runtime-gate",
        ],
        "signals": [
            "product-requirement-baseline",
            "architecture-runtime-boundary-baseline",
            "design-defect",
            "implementation-drift",
            "scope-requirements-architecture-both",
        ],
    },
    "aegis-invocation-visibility-natural": {
        "primary": "systematic-debugging",
        "allowed": ["verification-before-completion"],
        "must_not": [
            "hide-aegis-skill-invocation",
            "emit-aegis-ceremony-for-fast-path",
            "treat-visibility-note-as-runtime-authority",
            "default-to-structured-trace-card",
        ],
        "signals": [
            "aegis-invocation-visibility",
            "aegis-reason-note",
            "why-aegis-is-shaping-task",
            "natural-stage-transition",
            "natural-boundary-closeout",
            "structured-trace-reserved",
            "advisory-not-authority",
        ],
    },
    "aegis-invocation-visibility-owner-workflows": {
        "primary": "brainstorming",
        "allowed": [
            "goal-framing",
            "writing-plans",
            "test-driven-development",
            "executing-plans",
            "long-task-continuation",
            "requesting-code-review",
            "recording-architecture-decisions",
            "anti-entropy-governance",
            "verification-before-completion",
        ],
        "must_not": [
            "centralize-visibility-in-debugging-only",
            "centralize-visibility-in-verification-only",
            "default-to-used-skills-log",
            "treat-visibility-as-runtime-authority",
        ],
        "signals": [
            "owner-workflow-aegis-visibility",
            "goal-framing",
            "brainstorming",
            "writing-plans",
            "systematic-debugging",
            "test-driven-development",
            "executing-plans",
            "long-task-continuation",
            "requesting-code-review",
            "recording-architecture-decisions",
            "anti-entropy-governance",
            "verification-before-completion",
            "natural-not-used-skills-log",
            "advisory-not-authority",
        ],
        "shapes": ["owner-workflow-aegis-visibility"],
    },
    "loaded-aegis-skill-requires-entry-visibility": {
        "primary": "systematic-debugging",
        "allowed": ["verification-before-completion"],
        "must_not": [
            "wait-for-user-to-ask-about-aegis",
            "hide-entry-aegis-visibility",
            "replace-visibility-with-used-skills-list",
            "treat-visibility-as-runtime-authority",
        ],
        "signals": [
            "loaded-aegis-skill",
            "non-tiny",
            "first-substantive-stage",
            "entry-aegis-visibility",
            "natural-one-liner",
            "quality-risk",
            "advisory-not-authority",
        ],
        "shapes": ["entry-aegis-visibility-one-liner"],
    },
    "compressed-final-keeps-aegis-visibility": {
        "primary": "verification-before-completion",
        "must_not": [
            "drop-receipt-because-final-is-concise",
            "drop-visibility-because-final-is-concise",
            "replace-visibility-with-used-skills-list",
            "only-explain-aegis-after-user-asks",
            "treat-closeout-as-completion-authority",
        ],
        "signals": [
            "non-trivial-aegis-shaped-final",
            "impact-safety-receipt",
            "key-judgment",
            "boundary",
            "baseline-or-complexity",
            "evidence",
            "uncovered-risk",
            "visible",
            "concise-not-omitted",
            "advisory-not-authority",
        ],
        "shapes": ["concise-final-with-impact-safety-receipt"],
    },
    "aegis-semantic-slots-natural-surface": {
        "primary": "systematic-debugging",
        "allowed": ["verification-before-completion"],
        "must_not": [
            "require-rigid-template",
            "hide-governance-slots",
            "default-to-skill-trace",
            "treat-natural-language-as-missing-governance",
        ],
        "signals": [
            "semantic-slots",
            "natural-surface",
            "owner-baseline",
            "failure-example",
            "minimal-repair",
            "verification",
        ],
        "shapes": ["natural-governance-transition"],
    },
    "trace-digest-white-box-requested": {
        "primary": "systematic-debugging",
        "allowed": ["verification-before-completion"],
        "must_not": [
            "expose-raw-chain-of-thought",
            "treat-trace-as-runtime-authority",
            "dump-raw-logs-or-secrets",
            "default-trace-digest-for-every-task",
        ],
        "signals": [
            "trace-digest",
            "execution-trace",
            "evidence-chain",
            "retrieval-chain",
            "static-rules-evaluated",
            "rule-effects",
            "triggered-skills",
            "skipped-relevant-skills",
            "tool-command-trace",
            "verification-trace",
            "stability-signals",
            "value-signals",
            "confidence-labels",
            "host-capabilities",
            "redaction-applied",
            "advisory-not-authority",
        ],
        "shapes": ["trace-digest"],
    },
    "completion-governance-receipt-natural": {
        "primary": "verification-before-completion",
        "must_not": [
            "skip-impact-safety-receipt",
            "skip-governance-receipt",
            "drop-covered-scope",
            "drop-uncovered-scope",
            "drop-confidence",
            "replace-evidence-slots-with-skill-trace",
        ],
        "signals": [
            "impact-safety-receipt",
            "key-judgment",
            "avoided-misfix",
            "boundary",
            "baseline-alignment",
            "complexity-control",
            "command-exit-status",
            "covered-scope",
            "uncovered-scope",
            "residual-risk",
            "confidence",
        ],
        "shapes": ["natural-impact-safety-receipt-with-evidence-slots"],
    },
    "strong-opinion-review-findings-first": {
        "primary": "requesting-code-review",
        "must_not": [
            "lead-with-summary-before-findings",
            "treat-review-as-merge-approval",
            "skip-tests-risk-check",
        ],
        "signals": ["findings-first", "bugs-risk-tests", "advisory-review"],
    },
    "strong-opinion-release-readiness-summary": {
        "primary": "verification-before-completion",
        "must_not": [
            "auto-commit",
            "auto-tag",
            "auto-publish",
            "treat-readiness-as-completion-authority",
        ],
        "signals": ["readiness-summary", "tests-docs-version-hosts", "residual-risk"],
    },
    "strong-opinion-retro-memory-filter": {
        "primary": "recording-architecture-decisions",
        "must_not": [
            "record-unexecuted-ideas-as-accepted-memory",
            "force-adr-for-every-retro",
            "skip-baseline-sync-question",
        ],
        "signals": ["retro-memory-filter", "executed-durable-decision", "skip-or-record"],
    },
    "strong-opinion-fast-path-no-persona": {
        "primary": None,
        "no_artifacts": True,
        "workspace": "no-workspace",
        "must_not": [
            "emit-ceo-persona",
            "force-strong-opinion-lens",
            "create-project-workspace-records",
        ],
    },
    "high-risk-merge-independent-review": {
        "primary": "requesting-code-review",
        "must_not": [
            "replace-verification-before-completion",
            "skip-baseline-alignment",
            "treat-review-as-completion-authority",
        ],
        "signals": [
            "baseline-alignment",
            "architecture-drift",
            "retirement",
            "adr-baseline-sync",
        ],
    },
    "simple-completion-no-adr-ceremony": {
        "no_artifacts": True,
        "workspace": "no-workspace",
        "must_not": ["force-adr-backfill-ceremony"],
    },
    "interrupted-long-task-resume": {
        "primary": "long-task-continuation",
        "allowed": ["verification-before-completion"],
        "must_not": [
            "resume-from-memory-alone",
            "continue-without-drift-check",
            "skip-slice-card",
        ],
        "signals": ["latest-checkpoint", "worktree", "slice-card-readback"],
        "shapes": ["slice-card"],
    },
    "behavior-smoke-old-path-cleanup-anti-entropy": {
        "primary": "brainstorming",
        "allowed": ["anti-entropy-governance", "writing-plans"],
        "must_not": [
            "wait-for-anti-entropy-keyword",
            "clean-old-path-without-anti-entropy-governance",
            "skip-retirement-decision",
        ],
        "signals": [
            "behavior-triggered-not-prompt-token",
            "old-path-cleanup-triggers-anti-entropy-governance",
            "deletion-class",
            "retirement-decision",
        ],
        "shapes": ["anti-entropy-declaration", "retirement-decision"],
    },
    "architecture-area-bugfix-restores-baseline-no-adr": {
        "primary": "verification-before-completion",
        "must_not": ["force-adr-creation-for-baseline-restoration"],
        "signals": ["skip-reason", "existing-baseline-was-restored"],
    },
    "internal-trigger-retirement": {
        "primary": "brainstorming",
        "allowed": ["anti-entropy-governance"],
        "must_not": [
            "preserve-internal-legacy-path-under-compatibility-language",
            "skip-deletion-class",
            "treat-unknown-as-active-dependency",
        ],
        "signals": ["code-retirement", "delete-first", "no-compat-exception"],
        "shapes": ["anti-entropy-declaration", "retirement-decision"],
    },
    "duplicate-owner-collapse": {
        "primary": "systematic-debugging",
        "allowed": ["anti-entropy-governance"],
        "must_not": [
            "keep-both-for-now-without-evidence",
            "skip-deletion-class",
            "reintroduce-fallback-without-external-dependency-evidence",
        ],
        "signals": [
            "duplicate-owner-collapse",
            "delete-first",
            "old-owner-retired",
            "lingering-reference-check",
        ],
        "shapes": ["anti-entropy-declaration", "retirement-decision"],
    },
    "unknown-is-not-evidence": {
        "primary": "brainstorming",
        "allowed": ["anti-entropy-governance"],
        "must_not": [
            "treat-unknown-as-active-dependency",
            "retain-compat-by-guess",
            "skip-external-dependency-evidence-check",
        ],
        "signals": [
            "unknown-dependency-not-evidence",
            "active-dependency-evidence-required",
        ],
    },
    "host-fallback-with-real-boundary": {
        "primary": "brainstorming",
        "allowed": ["anti-entropy-governance"],
        "must_not": [
            "delete-host-fallback-without-boundary-check",
            "claim-host-support-without-smoke-boundary",
            "retain-compat-without-observation-metric",
        ],
        "signals": [
            "external-boundary",
            "compat-exception",
            "active-dependency-evidence",
            "observation-metric",
            "retirement-trigger",
        ],
    },
    "drop-table-hard-stop": {
        "primary": "brainstorming",
        "allowed": ["anti-entropy-governance"],
        "must_not": [
            "execute-drop-table-without-scoped-confirmation",
            "treat-warning-as-authorization",
            "treat-generic-assent-as-confirmation",
        ],
        "signals": [
            "persistent-state",
            "confirmation-first",
            "data-destruction-guard",
            "awaiting-scoped-confirmation",
        ],
        "shapes": ["data-destruction-guard"],
    },
    "source-of-truth-object-hard-stop": {
        "primary": "brainstorming",
        "allowed": ["anti-entropy-governance"],
        "must_not": [
            "treat-source-of-truth-files-as-code-retirement",
            "delete-object-store-target-without-confirmation",
            "skip-data-risk-classification",
        ],
        "signals": [
            "source-of-truth-data-risk",
            "confirmation-first",
            "allowed-read-only-next-steps",
            "blocked-destructive-steps",
        ],
        "shapes": ["data-destruction-guard"],
    },
    "derived-cache-safe-cleanup": {
        "primary": "brainstorming",
        "allowed": ["anti-entropy-governance"],
        "must_not": [
            "skip-deletion-class",
            "skip-rebuildability-check",
            "treat-derived-state-as-persistent-state-without-reason",
        ],
        "signals": [
            "derived-state",
            "rebuildability-check",
            "no-source-of-truth-risk",
        ],
    },
    "migration-file-vs-live-data": {
        "primary": "writing-plans",
        "allowed": ["anti-entropy-governance"],
        "must_not": [
            "confuse-migration-file-deletion-with-live-data-deletion",
            "skip-deletion-class",
            "route-directly-to-destructive-data-deletion",
        ],
        "signals": [
            "contract-carrying-code",
            "high-risk-verification",
            "no-destructive-execution",
        ],
        "shapes": ["anti-entropy-declaration", "retirement-decision"],
    },
    "executing-plan-new-code-path-change-necessity": {
        "primary": "executing-plans",
        "allowed": ["test-driven-development", "verification-before-completion"],
        "must_not": [
            "execute-new-code-path-before-change-necessity",
            "treat-plan-approval-as-change-necessity",
            "skip-minimum-boundary-for-new-source-path",
        ],
        "signals": [
            "executing-plans-honors-change-necessity",
            "any-new-source-code-path",
            "new-branch-not-exempt",
            "minimum-change-boundary",
            "before-edit",
        ],
        "shapes": ["change-necessity", "pre-edit-check"],
    },
    "plain-dead-import-does-not-trigger-anti-entropy": {
        "primary": None,
        "no_artifacts": True,
        "workspace": "no-workspace",
        "must_not": [
            "force-anti-entropy-governance",
            "create-project-workspace-records",
        ],
    },
}

COMPLEXITY_STAGE_SAMPLES = {
    "plan-time-complexity-check-before-design": ("brainstorming", "plan-time-complexity-check"),
    "plan-time-complexity-check-before-plan": ("writing-plans", "plan-time-complexity-check"),
    "pre-edit-complexity-check-before-code": ("test-driven-development", "pre-edit-complexity-check"),
    "pre-edit-complexity-check-debugging-fix": ("systematic-debugging", "pre-edit-complexity-check"),
}

LAYER_REQUIRED = {
    "layer-stop-local-root-cause": "L3 System",
    "layer-stop-cross-system-contract": "L5 Cross-system Contract",
    "layer-stop-spec-gap": "L7 Spec Gap",
    "layer-stop-user-falsifier-correction": "L5 Cross-system Contract",
    "topology-conjunctive-cluster-collapses-to-spec-gap": "L7 Spec Gap",
    "topology-independent-compound-divergent": "L5 Cross-system Contract",
}

REQUIRED_LAYER_FIELDS = {
    "required",
    "stopLayer",
    "checkedPath",
    "evidenceForStop",
    "excludedLayers",
    "falsifier",
    "userInterventionPoint",
    "nextAction",
    "topology",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sample(by_id: dict[str, dict[str, Any]], sample_id: str) -> dict[str, Any]:
    require(sample_id in by_id, f"missing workflow-quality sample: {sample_id}")
    return by_id[sample_id]


def require_contains(actual: list[str] | str, required: str, message: str) -> None:
    if isinstance(actual, list):
        require(required in actual, message)
    else:
        require(required in actual, message)


def validate_shape(data: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    quality_dimensions = set(data.get("qualityDimensions", []))
    for dimension in (
        "baseline-role-alignment",
        "aegis-invocation-visibility",
        "trace-digest-white-box",
        "pre-addition-minimality",
        "change-necessity-before-source-edits",
        "new-source-path-change-necessity",
    ):
        require(
            dimension in quality_dimensions,
            f"workflow quality matrix must include {dimension} dimension",
        )

    samples = data.get("samples", [])
    ids = {item.get("id") for item in samples}
    missing = sorted(EXPECTED_IDS - ids)
    require(not missing, f"missing workflow-quality samples: {', '.join(missing)}")
    require(len(samples) >= 10, "workflow quality matrix must contain at least 10 samples")

    for item in samples:
        missing_fields = sorted(REQUIRED_FIELDS - item.keys())
        require(
            not missing_fields,
            f"{item.get('id', '<unknown>')} missing fields: {', '.join(missing_fields)}",
        )
        require(bool(item["mustNotDo"]), f"{item['id']} must define mustNotDo")
        require(bool(item["workspacePolicy"]), f"{item['id']} must define workspacePolicy")
        require(bool(item["expectedOutputShape"]), f"{item['id']} must define expectedOutputShape")
        require(bool(item["verificationSignal"]), f"{item['id']} must define verificationSignal")

    by_id = {item["id"]: item for item in samples}
    return samples, by_id


def validate_coverage(samples: list[dict[str, Any]]) -> None:
    negative = [s for s in samples if s.get("expectedPrimarySkill") is None]
    positive = [s for s in samples if s.get("expectedPrimarySkill")]
    require(
        len(negative) >= 3,
        "workflow quality matrix must include at least 3 fast-path / negative samples",
    )
    require(
        len(positive) >= 6,
        "workflow quality matrix must include at least 6 positive samples",
    )

    skills = {s.get("expectedPrimarySkill") for s in positive}
    missing_skills = sorted(REQUIRED_PRIMARY_SKILLS - skills)
    require(not missing_skills, f"missing expected primary skills: {', '.join(missing_skills)}")

    for item in negative:
        require(not item.get("expectedArtifacts"), f"{item['id']} is fast-path but expects artifacts")
        require(
            "no-workspace" in item.get("workspacePolicy", ""),
            f"{item['id']} fast-path sample must use no-workspace policy",
        )


def validate_contracts(data: dict[str, Any]) -> None:
    contracts = data.get("compactOutputContracts", {})
    missing_contracts = sorted(REQUIRED_CONTRACTS - contracts.keys())
    require(not missing_contracts, f"missing compact output contracts: {', '.join(missing_contracts)}")
    require(
        "recording-architecture-decisions" in contracts,
        "compact output contracts must include recording-architecture-decisions",
    )

    for contract, required_values in CONTRACT_REQUIREMENTS.items():
        require(contract in contracts, f"compact output contracts must include {contract}")
        for required in required_values:
            require(
                required in contracts[contract],
                f"{contract} compact contract must include {required}",
            )


def validate_rule(sample_id: str, item: dict[str, Any], rule: dict[str, Any]) -> None:
    if "primary" in rule:
        require(
            item.get("expectedPrimarySkill") == rule["primary"],
            f"{sample_id} must use {rule['primary']}",
        )
    for required in rule.get("allowed", []):
        require_contains(
            item.get("allowedSecondarySkills", []),
            required,
            f"{sample_id} must allow {required}",
        )
    for forbidden in rule.get("allowed_absent", []):
        require(
            forbidden not in item.get("allowedSecondarySkills", []),
            f"{sample_id} must not route to {forbidden} by default",
        )
    for required in rule.get("must_not", []):
        require_contains(
            item.get("mustNotDo", []),
            required,
            f"{sample_id} must forbid {required}",
        )
    joined_must_not = " ".join(item.get("mustNotDo", []))
    for required in rule.get("must_not_join_contains", []):
        require(required in joined_must_not, f"{sample_id} must protect {required}")
    for signal in rule.get("signals", []):
        require_contains(
            item.get("verificationSignal", ""),
            signal,
            f"{sample_id} must require {signal}",
        )
    for shape in rule.get("shapes", []):
        require_contains(
            item.get("expectedOutputShape", ""),
            shape,
            f"{sample_id} output shape must include {shape}",
        )
    if rule.get("no_artifacts"):
        require(not item.get("expectedArtifacts"), f"{sample_id} must not expect artifacts")
    if "workspace" in rule:
        require(
            item.get("workspacePolicy") == rule["workspace"],
            f"{sample_id} must use {rule['workspace']} policy",
        )


def validate_sample_rules(by_id: dict[str, dict[str, Any]]) -> None:
    for sample_id, rule in SAMPLE_RULES.items():
        validate_rule(sample_id, sample(by_id, sample_id), rule)

    for sample_id, (skill, signal) in COMPLEXITY_STAGE_SAMPLES.items():
        item = sample(by_id, sample_id)
        require(item.get("expectedPrimarySkill") == skill, f"{sample_id} must use {skill}")
        require(
            signal in item.get("expectedOutputShape", ""),
            f"{sample_id} output shape must include {signal}",
        )
        require(
            signal in item.get("verificationSignal", ""),
            f"{sample_id} verification signal must include {signal}",
        )
        require(
            "complexity-check" in " ".join(item.get("mustNotDo", [])),
            f"{sample_id} must forbid skipping {signal}",
        )


def validate_layer_stop_samples(by_id: dict[str, dict[str, Any]]) -> None:
    for sample_id, stop_layer in LAYER_REQUIRED.items():
        item = sample(by_id, sample_id)
        require(
            item.get("expectedPrimarySkill") == "systematic-debugging",
            f"{sample_id} must route to systematic-debugging",
        )
        card = item.get("layerStopCard")
        require(isinstance(card, dict), f"{sample_id} must define layerStopCard")
        missing_fields = sorted(REQUIRED_LAYER_FIELDS - card.keys())
        require(
            not missing_fields,
            f"{sample_id} layerStopCard missing fields: {', '.join(missing_fields)}",
        )
        require(card.get("required") is True, f"{sample_id} layerStopCard must be required")
        require(card.get("stopLayer") == stop_layer, f"{sample_id} must stop at {stop_layer}")
        topology = card.get("topology")
        require(
            topology in {
                "single-root",
                "single-root-multi-symptom",
                "chain",
                "independent-compound",
                "conjunctive-cluster",
                "disjunctive-or",
            },
            f"{sample_id} layerStopCard topology must be one of the six causal topologies",
        )
        for field in (
            "checkedPath",
            "evidenceForStop",
            "excludedLayers",
            "falsifier",
            "userInterventionPoint",
            "nextAction",
        ):
            require(bool(card.get(field)), f"{sample_id} layerStopCard {field} must not be empty")
        require(
            "layer-stop-card" in item.get("expectedOutputShape", ""),
            f"{sample_id} output shape must require layer-stop-card",
        )
        require(
            "layer-stop-card" in item.get("verificationSignal", ""),
            f"{sample_id} verification signal must require layer-stop-card",
        )
        require(
            "skip-layer-stop-card" in item.get("mustNotDo", []),
            f"{sample_id} must forbid skipping layer stop card",
        )

    conjunctive = sample(by_id, "topology-conjunctive-cluster-collapses-to-spec-gap")
    require(
        conjunctive.get("layerStopCard", {}).get("topology") == "single-root-multi-symptom",
        "conjunctive cluster sample must show anti-disguise collapse to single-root-multi-symptom",
    )
    for forbidden in ("skip-anti-disguise-check", "collapse-to-cluster-without-shared-cause-proof"):
        require(
            forbidden in conjunctive.get("mustNotDo", []),
            f"conjunctive cluster sample must forbid {forbidden}",
        )
    for signal in ("anti-disguise", "member-necessity-test", "spec-gap-shared-cause"):
        require(
            signal in conjunctive.get("verificationSignal", ""),
            f"conjunctive cluster sample must require {signal}",
        )

    divergent = sample(by_id, "topology-independent-compound-divergent")
    require(
        divergent.get("layerStopCard", {}).get("topology") == "independent-compound",
        "independent compound sample must classify topology as independent-compound",
    )
    for forbidden in ("merge-two-roots-into-one", "skip-member-necessity-test"):
        require(
            forbidden in divergent.get("mustNotDo", []),
            f"independent compound sample must forbid {forbidden}",
        )
    for signal in ("divergent-chains", "independent-compound", "both-roots-fixed"):
        require(
            signal in divergent.get("verificationSignal", ""),
            f"independent compound sample must require {signal}",
        )

    correction = sample(by_id, "layer-stop-user-falsifier-correction")
    for required in ("ignore-user-falsifier", "cling-to-initial-l7-diagnosis", "skip-correction-readback"):
        require(required in correction.get("mustNotDo", []), f"user falsifier correction must forbid {required}")
    for signal in ("user-falsifier", "correction-to-l5", "user-intervention-point"):
        require(
            signal in correction.get("verificationSignal", ""),
            f"user falsifier correction sample must require {signal}",
        )

    no_card = sample(by_id, "fast-path-no-layer-stop-card")
    require(no_card.get("expectedPrimarySkill") is None, "fast-path no-card sample must stay fast path")
    require(
        no_card.get("layerStopCard", {}).get("required") is False,
        "fast-path no-card sample must mark layerStopCard required false",
    )
    require(
        "emit-layer-stop-card" in no_card.get("mustNotDo", []),
        "fast-path no-card sample must forbid emitting layer stop card",
    )
    require(not no_card.get("expectedArtifacts"), "fast-path no-card sample must not expect artifacts")
    require(
        no_card.get("workspacePolicy") == "no-workspace",
        "fast-path no-card sample must use no-workspace policy",
    )


def validate_matrix(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    samples, by_id = validate_shape(data)
    validate_coverage(samples)
    validate_contracts(data)
    validate_sample_rules(by_id)
    validate_layer_stop_samples(by_id)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: validate_workflow_quality_matrix.py <matrix-json>")
    validate_matrix(Path(argv[1]))
    print("  [PASS] workflow quality matrix has representative samples and compact contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
