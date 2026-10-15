# Higher Education and Immigration Research Project Card

**BCA policy:** advisory

**Profiles:** Universal, Artifact Generation

Use [README.md](README.md) for the public research question, current outputs, and source definitions; use the owning file under `docs/` for methodology/governance questions; use [TESTING.md](TESTING.md) for rebuild and publication verification.

<!-- workspace-contract:begin (generated from ../AGENTS.md by tools/sync_agent_context.py; edit the source, not this copy) -->
## Workspace contract

Applies to every agent in every harness. Source, rationale, and evidence: [../AGENTS.md](../AGENTS.md).

The user is a solo developer. Precedence: current request → this contract → project card → standards. **Hard** rules survive lower-level workflow advice.

### AG-1 Finish the work

Finish the authorized task; plans, progress, or deferred notes are not delivery. Delegate only bounded read-only work when authorized.

### AG-2 Make the calls yourself

Make in-scope decisions yourself; state consequential choices briefly and continue. Ask only when the answer changes the result and cannot be inferred. Read the project card once, then resolve authority, owner, and proof. Expand only for unresolved scope or boundaries. Links and profiles are lookups; research and artifact work starts at the product workflow.

### AG-3 Stay in your project (hard)

Work only in the requested project. Do not create top-level directories or write to the workspace root or project parent. Put scratch work in the project's ignored output (normally `target/agent-output/`) or OS temp.

### AG-4 Done means the user's copy works (hard)

Verify every requirement against the user's actual copy. Refresh and check the affected release, deployment, or running app; source edits alone do not update it. Docs-only work verifies docs and routes. Use the smallest complete project lane and [`REVIEW.md`](../REVIEW.md) for consequential code. Claim only checked results; report what remains unverified.

### AG-5 Look at what you made

Run or render changed visual, audio, interactive, or published output; inspect it against [`STANDARDS_QUALITY.md`](../STANDARDS_QUALITY.md) and project references. Verify requested files, fix defects, and report rendered evidence. Internal prose needs only readability and route review. Tests do not prove appearance.

### AG-6 Real behavior over proxies

Observe user-experienced behavior. Tests, harnesses, validators, and metrics are evidence, not the goal. Repair proxy/product divergence; never weaken gates, hardcode outcomes, suppress warnings, or retry until green. Simulations stay causal and parameterized (STANDARDS_QUALITY.md QUAL-3).

### AG-7 Answer first, then stop talking

Answer questions directly; they are not permission to act. Reports state changes, verification limits, and required user action. Put long audits or research in a project file. No lectures or revisiting dismissed topics.

### AG-8 Own mistakes; trust the user's evidence

On a user-reported failure, re-check your work before blaming setup; own and fix mistakes. Try a tool, file, or capability before claiming it is unavailable.

### AG-9 The outcome outranks the process

Skip ceremony, optional diagnostics, or intermediate process when they cost more than they protect, and state what you skipped. Do not use this rule to skip the smallest complete verification lane (AG-4), applicable inspection of user-visible output (AG-5), or real-behavior evidence (AG-6). Hard rules still apply.

### AG-10 Leave nothing running

Stop task-owned processes, servers, watchers, and terminals; release locks and remove scratch. Keep deliverables and the app the user should run. Never kill or replace the user's program silently. Built software cleans up child processes on exit.

### AG-11 Git: `main`, commit, push (hard)

Work on `main`; branches or worktrees only when asked. Commit and push verified work unless told not to. In a dirty shared tree, stage task-owned paths explicitly; broad add/commit-all modes MUST NOT sweep in unrelated changes. Never revert, stash, overwrite, or discard others' changes. Shared progress MAY be included only when deliberately selected, reviewed, and verified as complete; otherwise leave it untouched and report it.

### AG-12 Current docs describe the present

Update the single authority for changed behavior. Keep history, session notes, and changelog prose out of current docs/comments. Plans and design intent do not prove capability.

### AG-13 CI is local; GitHub Actions are banned (hard)

Use repository-owned local verification. Never create, enable, invoke, or push `.github/workflows/`; remove existing workflows while keeping their local equivalent.
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
