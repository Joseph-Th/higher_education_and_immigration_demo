# Higher Education and Immigration Research Project Card

**BCA policy:** advisory

**Profiles:** Universal, Artifact Generation

Use [README.md](README.md) for the public research question, current outputs, and source definitions; use the owning file under `docs/` for methodology/governance questions; use [TESTING.md](TESTING.md) for rebuild and publication verification.

<!-- workspace-contract:begin (generated from ../AGENTS.md by tools/sync_agent_context.py; edit the source, not this copy) -->
## Workspace contract

Applies to every agent in every harness. Source, rationale, and evidence: [../AGENTS.md](../AGENTS.md).

The user is a solo developer. Precedence: current request → this contract → project card → standards. This is a safety kernel, not a prescribed workflow. **Hard** rules survive lower-level advice.

### AG-1 Finish the work

Finish the authorized task. On open-ended goals, iterate from evidence until the goal is met or useful in-scope improvements are exhausted; pivot around blockers instead of stopping at them.

### AG-2 Make the calls yourself

Make routine in-scope decisions yourself. Read the project card once, identify the owner and proof route, then work. Ask only when a choice materially changes the deliverable and cannot be inferred.

### AG-3 Write only in your project (hard)

Write only in the requested project. Read-only sibling inspection is allowed when it materially helps. Do not write to the workspace root, parent, or siblings; use project-ignored output or OS temp for scratch.

### AG-4 Done means the user's copy works (hard)

Verify the result in the user's actual copy, including the release, deployment, or running app when applicable. Use the smallest complete project lane and [`REVIEW.md`](../REVIEW.md) for consequential code. Claim only checked results.

### AG-5 Look at what you made

Run or render changed visual, audio, interactive, or published output and inspect the real result against project references and [`STANDARDS_QUALITY.md`](../STANDARDS_QUALITY.md). Tests do not prove appearance.

### AG-6 Real behavior over proxies

Prefer observed product behavior over proxy success. Use tests, harnesses, validators, and metrics as evidence; fix production root causes and proxy divergence rather than weakening gates or hardcoding outcomes.

### AG-7 Answer first, then stop talking

Answer questions directly. Reports state changes, verification limits, and required user action; keep long audit material in project files instead of chat.

### AG-8 Own mistakes; trust the user's evidence

On a reported failure, re-check your work before blaming setup. Try a capability before claiming it is unavailable.

### AG-9 The outcome outranks the process

Skip ceremony and optional diagnostics when they cost more than they protect. Do not skip the proof required by AG-4 through AG-6 or any hard rule.

### AG-10 Leave nothing running

Run automation without disrupting the desktop. Stop task-owned processes, release locks, and remove scratch; never kill or replace the user's program silently.

### AG-11 Git: `main`, commit, push (hard)

Work on `main`; branches or worktrees only when asked. Commit and push verified work unless told not to. Stage task-owned paths explicitly in dirty trees and never discard or sweep in unrelated work.

### AG-12 Current docs describe the present

Update the authority for changed behavior. Keep history and session notes out of current docs and comments.

### AG-13 CI is local; GitHub Actions are banned (hard)

Use repository-owned local verification. Never create, enable, invoke, or push `.github/workflows/`.

### Optional workspace accelerator

Use native navigation first. If cold-start routing is still expensive or ambiguous, run:

```text
python ../tools/agent_context.py brief immigration_education_demonstration <task ...>
```

It returns bounded authority, verification, and likely-source evidence. Tool output is evidence, not authority. Use `python ../tools/agent_context.py --help` only when a specific unresolved question justifies a deeper probe. No shared analysis command is a prerequisite to editing.
<!-- workspace-contract:end -->

## Project guardrails

- IPEDS and each external comparison source keep their own population definition, vintage, and provenance. Do not combine non-addable populations or treat ecological stock/flow comparisons as individual transitions.
- Raw source archives and source manifests are inputs. Derived CSV, HTML, PDF, XLSX, PPTX, and site files are downstream artifacts and must reconcile to their analytical owners before publication.
- A partial next-year source package does not advance the analysis year. Release-readiness and year-advance decisions remain separate.
- Institution-level QA dispositions and claim holds do not rewrite source values. Evidence may change interpretation or publication scope, not the underlying authoritative measurement.
- Public release is allowlist-driven and fail-closed. Restricted or person-level partner data is nonpublic by default.
- Generated publication artifacts must be rebuilt from validated sources and inspected in their actual rendered or consumer form when presentation is part of the change.

## Completion

Follow [TESTING.md](TESTING.md). Use the focused owner script/test for a narrow analytical change; use the complete offline validator for changes that alter shared data, publication outputs, or cross-artifact reconciliation. Visual publication changes also require browser/render inspection.
