# Static Publication Deployment

The public research brief is a static site. It does not need a framework build, server process, database, or runtime secrets.

## Current public deployment: GitHub Pages

Public URL: `https://joseph-th.github.io/higher_education_and_immigration_demo/`

The validated `site/` tree is published from a dedicated `gh-pages` branch. `site/.nojekyll` is tracked so GitHub serves the static publication as authored rather than applying Jekyll processing rules.

The publication branch is downstream of `main`; it is never an analytical authority. Rebuild and validate on `main` first, then replace `gh-pages` with the exact validated `site/` contents. One reproducible local publication sequence is:

```bash
git branch -D gh-pages 2>/dev/null || true
git subtree split --prefix site -b gh-pages
git push --force-with-lease origin gh-pages
```

GitHub Pages should then be configured to serve branch `gh-pages` from `/`. After deployment, verify the public HTTPS home page, a state profile, the research memo, the methodology crosswalk, the bounded population-trend comparison plus CSV/Markdown downloads, the undocumented-pipeline page plus comparison CSV/Markdown downloads, the source-update triage page plus routing CSV/Markdown downloads, the recurring-research operations page, the stage-gated production-cycle page and downloads including the blank live-cycle log template, the PowerPoint management briefing, the SQL analysis page plus query/audit downloads, the ad hoc analysis page plus case CSV/Markdown downloads, the state-recovery page plus decomposition CSV/Markdown downloads, the fixed undergraduate-shift baseline page plus CSV/Markdown downloads, the private-nonprofit growth page plus institution-contribution CSV/Markdown downloads, the complete high-priority QA review plus resolution CSV/Markdown downloads, the planning-scenarios page plus scenario CSV/Markdown downloads, the freshness-monitor page plus captured snapshot/register/notes, the candidate-directory preflight page plus JSON/Markdown downloads, the candidate-directory institution-change review plus CSV/Markdown downloads, the release-readiness page plus control CSV/Markdown downloads, the searchable Research Library, the publication-handoff page, the data-governance page, the public-release register, representative CSV downloads, and the PDF brief. The deployed site must never be read back as an input to the analysis.

**Verified October 14, 2026:** candidate-directory institution-change review commit `7148ef2` was published as the exact validated `site/` tree on `gh-pages` deployment commit `5036105`. The release passed 44/44 repository tests, 24/24 NCES benchmark checks, and desktop/mobile browser QA before publication. The refreshed next-year snapshot at `2026-10-14T17:13:49+00:00` still shows 2 of 4 required 2025 assets available and keeps the project at `HOLD_YEAR_ADVANCE`; the candidate-directory capture at `2026-10-14T17:13:53+00:00` remains a non-authorizing `PASS`. The available `HD2025.zip` and `HD2025_Dict.zip` preserve all 6/6 required join/filter fields and now pass an exact 70/70 full data/dictionary field-set comparison, with all 51 states/DC represented, zero duplicate UNITIDs, and the directory-side eligible frame moving from 3,868 institutions in 2024 to 3,864 in 2025. Continuity remains 3,812 shared, 52 entering, 56 leaving, net -4. The new SHA-256-bound institution-level review covers all 154 affected UNITIDs: 52 directory-side entries, 56 exits, and 46 shared eligible records with a changed name, state, control, or eligible Title-IV indicator. Entry reasons are 35 new directory records, 11 degree-granting-status gains, and 6 eligible Title-IV/First-Look gains; exit reasons are 38 eligible Title-IV/First-Look losses, 15 candidate-directory absences, and 3 degree-granting-status losses. Fifty-four of the 56 frame leavers appear in the current 2024 canonical institution analysis, representing 612 current-year U.S. nonresident students and 17,593 total students; these are review-priority exposure values, not projected 2025 losses, and directory absence is not interpreted as proof of closure. The queue also preserves six shared control changes with 1,069 current-year U.S. nonresident students, three shared state changes with 193, and 41 shared name changes with 10,184. The CSV contains 154 data rows plus its header and is bound to the preflight by SHA-256 `0dd98f80f4c2daaca69951cad325e84af12abd4b9bc4026a1bfe81b0a45edc6a`; the test suite includes a negative corruption check proving that a byte change fails that gate. The candidate directory schema remains 70 fields versus 72 in 2024; removed `DFRCGID` and `DFRCUSCG` are not required by the current analytical join/filter. The candidate archives retain SHA-256 `aadad9277a2255c85813b6d206475ddbf8a7330d79cc0236c2ecae685b00f1bf` for HD2025 and `dc454aa6fbc246f3d47d773cd02ebe3b5efcedacbd2f71c54ff39f5844215343` for its dictionary. `EF2025A.zip` and its dictionary remain required before any 2025 enrollment calculation or R01 persistence decision. The new change-review page, updated preflight page, and freshness monitor were visually reviewed at 1280px desktop and 390px mobile widths with no page-level overflow. Governance now covers 64 registered artifact families / 114 expanded downloads, including PR63-PR64 for the change-review CSV and note. Release readiness remains `READY_WITH_CLAIM_LEVEL_HOLDS` for the current 2024 publication and `HOLD_YEAR_ADVANCE` for candidate 2025. After GitHub Pages reported deployment commit `5036105` as built, the live change-review HTML/CSV/Markdown, candidate preflight, freshness monitor, release-readiness page, data-governance page, home page, public-release register, and release snapshots matched the validated publication after normalizing Git/Windows line endings; the live three-page PDF and six-slide management deck remained byte-for-byte identical to the validated binaries. Twenty-six representative public pages and downloads returned HTTP 200. Live source-health checks resolved with zero broken URLs and zero network errors: Research Library 11 available / 6 documented script-access restrictions, population crosswalk 1 available / 5 documented restrictions, and QA evidence 25 available / 2 documented restrictions across all 27 reviewed records.

## Optional Cloudflare Pages setup

If a Cloudflare deployment is preferred later, the same repository can be connected directly to Cloudflare Pages:

1. Create a Cloudflare Pages project connected to the repository.
2. Use the repository root as the project root.
3. Leave the build command empty.
4. Set the build output directory to `site`.
5. Deploy the `main` branch.

Repository: `https://github.com/Joseph-Th/higher_education_and_immigration_demo`

Before each deployment, run:

```bash
python scripts/build_management_deck.py
python scripts/build_pdf_brief.py
python scripts/check_for_new_release.py --write-snapshot data/release_monitor_snapshot.json
python scripts/check_candidate_directory.py --write-snapshot data/candidate_directory_preflight.json
python scripts/validate_project.py
python scripts/browser_smoke.py
python scripts/check_research_library.py
python scripts/check_population_crosswalk.py
python scripts/check_qa_evidence.py
```

The PowerPoint builder requires `python-pptx`; the PDF build and browser smoke test require Playwright plus a local Chromium runtime. All are included by `requirements-dev.txt`. The live-link checks are deliberately outside the offline reproducibility lane, but they should be clean or explicitly manually resolved before publication. `deliverables/management_briefing_manifest.json` binds the committed PPTX to its current builder and validated analytical sources; `deliverables/research_brief_manifest.json` binds the committed PDF to the exact generated memo source. Validation fails when either publication artifact is stale. `data/public_release_register.csv` separately governs the public data/download surface and validation fails on an unregistered public file. Only deploy the generated `site/` directory after the required validation lanes pass and the presentation/PDF/site outputs have been inspected.

## Direct upload

If Git integration is not desired, the contents of `site/` can be uploaded as the Pages output directory. The generated CSV/Markdown/PDF downloads and `site/data/site_data.json` must be included; they are part of the published research product.

## Headers

`site/_headers` provides a restrictive Content Security Policy and basic browser security headers compatible with the current static site. If external analytics, fonts, scripts, or embeds are added later, the policy must be reviewed rather than weakened broadly.

## Custom domain

A custom domain can be attached after the first successful Pages deployment. No source code changes are required unless a canonical URL or social-sharing metadata is later added.

