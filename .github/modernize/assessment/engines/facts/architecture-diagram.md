# Architecture Diagram

Proposed modular architecture for the AI Efficiency & Performance Auditor.
This is a design view, not a deployed system or a claim that proposed modules
exist. Skills are selectively loaded instructions in one auditor session,
not independent agents, services or executable plugins.

## Application Architecture

Solid arrows show existing architectural relationships; dotted arrows show
proposed additions. Existing includes the added recommendation-planning and
change-impact-review skills, whose live behavior is not yet validated.

<!-- mermaid-checked: no \n, no em-dash/en-dash, no {} in labels, subgraphs are id["label"], arrows are -->|"label"|, all subgraphs closed by end, ids unique -->
```mermaid
flowchart TD
    AUser["Developer explicitly selects scope and modes"]
    AEvidence["Named source, reports and eligible sanitized traces"]

    subgraph ACore["Existing core auditor"]
        ACoordinator["Scope, privacy, evidence rules and shared budgets"]
        AReporting["Six-section report assembly and save verification"]
    end

    subgraph ASkills["Opt-in instruction modules"]
        AReviews["Existing context, orchestration and service reviews"]
        AComparison["Existing audit-comparison"]
        APlanning["Added recommendation-planning"]
        AChange["Added change-impact-review"]
        AMeasurement["Proposed measurement-readiness"]
        AVerification["Proposed finding-verification extension"]
        ABudgetAdvice["Proposed efficiency-budget interpretation"]
    end

    AReports["One detailed audit and one Executive Summary"]

    subgraph ATooling["Proposed separately authorized companion tooling"]
        AAdapters["Sanitized trace adapters"]
        ARunner["Measurement and benchmark runner"]
        AGates["Deterministic budget and regression gates"]
        AArtifacts["Provenanced evidence and check results"]
    end

    AUser -->|"invoke auditor"| ACoordinator
    AEvidence -->|"scoped read-only evidence"| ACoordinator
    ACoordinator -->|"load only requested instructions"| AReviews
    ACoordinator -->|"load only when requested"| AComparison
    ACoordinator -->|"load only when requested"| APlanning
    ACoordinator -->|"load only when requested"| AChange
    ACoordinator -.->|"future explicit opt-in"| AMeasurement
    AComparison -.->|"extend rather than duplicate"| AVerification
    ACoordinator -.->|"future explicit opt-in"| ABudgetAdvice
    ASkills -->|"contribute under core rules"| AReporting
    AReporting -->|"report-only new Markdown files"| AReports

    AUser -.->|"separate tooling authorization"| AAdapters
    AUser -.->|"separate execution authorization"| ARunner
    AUser -.->|"approved budgets and CI policy"| AGates
    AAdapters -.->|"normalized eligible evidence"| AArtifacts
    ARunner -.->|"measurements and quality results"| AArtifacts
    AArtifacts -.->|"comparable supplied measurements"| AGates
    AGates -.->|"explicit pass, fail or inconclusive"| AArtifacts
    AArtifacts -.->|"user supplies exact eligible paths"| AEvidence
```

### Technology Stack Summary

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Host | GitHub Copilot custom-agent support in VS Code or CLI | Host-dependent | Explicit user invocation; cloud remains experimental |
| Core | Markdown agent definition | Methodology 0.5.0 candidate | Shared scope, evidence, privacy, budgets and reporting |
| Analysis modules | Opt-in Markdown SKILL.md directories | Repository revision | Specialized analysis and handoff instructions, no new tools |
| Evidence semantics | Internal advisory evidence and Markdown contracts | advisory-evidence/1; advisory-markdown/1 | Consistent provenance, units, unknowns and non-overlapping findings |
| Output | Markdown | Not applicable | One detailed report and one bounded Executive Summary |
| Companion tooling | Proposed adapters, runner and CI checks | Not implemented | Authorized acquisition, normalization, calculation and enforcement |

### Data Storage & External Services

The auditor reads authorized workspace evidence and creates new report Markdown
under the existing no-overwrite workflow. No application database, telemetry
backend or direct external-service connection is required or introduced.
Future companion tooling may acquire measurements only through separately
approved access; the auditor does not invoke that tooling. Tooling must establish
sanitization and provenance before artifacts become eligible audit evidence.
An adapter does not by itself establish that its input is safe to read.

### Key Architectural Decisions

- Keep the core small: safeguards and report contracts remain shared; specialized
  instructions load only for explicitly requested modes. Combining modes adds
  neither permissions nor exploration budgets.
- Keep execution separate: skills recommend experiments and instrumentation;
  separately authorized tooling performs acquisition, benchmarking and CI
  enforcement. No core-to-runner execution edge is proposed.
- Keep evidence honest: supplied reports are attributed rather than reverified,
  hypotheses stay unranked, and fewer calls alone do not prove improved quality.

## Component Relationships

The core coordinates instruction loading, evidence reuse and a single report
pair. Solid arrows describe current responsibilities; dotted arrows describe
future modules or extensions. The companion tooling boundary is shown above,
not implemented by these instruction components.

<!-- mermaid-checked: no \n, no em-dash/en-dash, no {} in labels, subgraphs are id["label"], arrows are -->|"label"|, all subgraphs closed by end, ids unique -->
```mermaid
flowchart LR
    subgraph CInput["Explicit request and scoped inputs"]
        CRequest["Named scenario and requested modes"]
        CSource["Authorized source and eligible artifacts"]
        CSupplied["Named supplied audit reports"]
    end

    subgraph CCore["Core policy and coordination"]
        CScope["Scope selection and stop states"]
        CLoader["Requested-skill loader"]
        CLedger["Shared evidence ledger and exploration budget"]
        CGuards["Privacy, provenance and safety invariants"]
    end

    subgraph CModules["Optional skill instructions"]
        CReview["Context, orchestration and service review"]
        CCompare["Baseline and candidate comparison"]
        CPlan["Recommendation cards and developer handoff"]
        CDiff["Added supplied-diff review"]
        CMeasure["Proposed telemetry-gap advice"]
        CVerify["Proposed finding-verification extension"]
        CBudget["Proposed budget-result interpretation"]
    end

    subgraph COutput["Shared report composition"]
        CFindings["Evidence-linked findings and overlap handling"]
        CDesign["Proposed design and supported cards"]
        CValidation["Blocked hypotheses and acceptance proposals"]
        CSave["One report pair and core save-consent workflow"]
    end

    CRequest -->|"establish intent"| CScope
    CScope -->|"explicit modes only"| CLoader
    CScope -->|"bind exact inputs"| CLedger
    CSource -->|"eligible scoped reads"| CLedger
    CSupplied -->|"attributed report-only claims"| CLedger
    CGuards -->|"constrain scope and reads"| CScope
    CGuards -->|"constrain evidence handling"| CLedger
    CLoader -->|"when requested"| CReview
    CLoader -->|"when requested"| CCompare
    CLoader -->|"when requested"| CPlan
    CLoader -->|"when requested"| CDiff
    CLoader -.->|"future opt-in"| CMeasure
    CLoader -.->|"future opt-in"| CBudget
    CCompare -.->|"reuse comparison rules"| CVerify
    CLedger -->|"reuse evidence within one budget"| CModules
    CReview -->|"supported mechanisms"| CFindings
    CCompare -->|"qualified deltas and finding status"| CFindings
    CDiff -->|"scoped change findings"| CFindings
    CVerify -.->|"evidence-backed status"| CFindings
    CFindings -->|"link original finding IDs"| CPlan
    CPlan -->|"supported cards"| CDesign
    CPlan -->|"blockers and proposed checks"| CValidation
    CMeasure -.->|"missing measurements"| CValidation
    CBudget -.->|"qualified gate interpretation"| CValidation
    CGuards -->|"constrain report claims and writes"| CSave
    CFindings -->|"ranked evidence"| CSave
    CDesign -->|"proposed changes"| CSave
    CValidation -->|"unknowns and next steps"| CSave
```

### Component Inventory

| Component | Layer | Type | Responsibility |
|---|---|---|---|
| Scope selection and stop states | Core | Existing instructions | Bind the target; stop on missing or ambiguous scope; named-report-only planning skips app discovery |
| Requested-skill loader | Core | Existing routing instructions | Read only explicitly requested skill guidance; disclose missing modules |
| Shared evidence ledger and budget | Core | Existing audit method | Reuse reads, preserve provenance and unknowns, enforce one shared exploration budget |
| Privacy and safety invariants | Core | Existing cross-cutting instructions | Preserve sanitization, authorization, freshness, idempotency, quality and permission boundaries |
| Context, orchestration and service review | Skills | Existing optional modules | Specialized efficiency and service analysis |
| Audit comparison | Skills | Existing optional module | Establish comparability and qualified deltas; no resolution from omitted findings |
| Recommendation planning | Skills | Added optional module | Smallest proposed change, dependencies, effort rationale, safeguards, acceptance and rollback |
| Change-impact review | Skills | Added optional module | Analyze supplied changes and affected call paths without a whole-app re-audit |
| Measurement readiness | Skills | Proposed new module | Identify telemetry gaps and advise on payload-free instrumentation without installing it |
| Finding verification | Comparison | Proposed extension | Verify individual findings using matched candidate evidence and preserved quality contracts |
| Efficiency-budget interpretation | Skills | Proposed module | Explain separately computed results against approved limits, including inconclusive outcomes |
| Evidence-linked findings | Reporting | Existing shared method | Link mechanisms and IDs; avoid duplicate findings and overlapping benefit claims |
| Proposed design and validation plan | Reporting | Existing sections with added cards | Keep supported changes separate from blocked hypotheses and unapproved thresholds |
| Report persistence | Reporting | Existing workflow | Create one no-overwrite report pair; read back; preview only after explicit consent |

Generated finding IDs remain audit-local unless supplied identity and matching
evidence support continuity. Recommendation cards do not establish that work is
implemented, resolved or validated. All skill behavior remains instruction-based,
not a filesystem sandbox or a guarantee of host enforcement.

See the [extension roadmap](../../../../../docs/agent-guide.md#modular-design-and-extension-roadmap)
and [recommendation-planning usage](../../../../../docs/usage-prompts.md#recommendation-planning).
