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

GitHub Pages should then be configured to serve branch `gh-pages` from `/`. After deployment, verify the public HTTPS home page, a state profile, the research memo, the methodology crosswalk, the bounded population-trend comparison plus CSV/Markdown downloads, the undocumented-pipeline page plus comparison CSV/Markdown downloads, the source-update triage page plus routing CSV/Markdown downloads, the recurring-research operations page, the stage-gated production-cycle page and downloads including the blank live-cycle log template, the PowerPoint management briefing, the SQL analysis page plus query/audit downloads, the ad hoc analysis page plus case CSV/Markdown downloads, the state-recovery page plus decomposition CSV/Markdown downloads, the fixed undergraduate-shift baseline page plus CSV/Markdown downloads, the private-nonprofit growth page plus institution-contribution CSV/Markdown downloads, the complete high-priority QA review plus resolution CSV/Markdown downloads, the high-priority category diagnostic plus CSV/Markdown downloads, the medium-priority QA triage plus routing CSV/Markdown downloads, the medium-priority category diagnostic plus CSV/Markdown downloads, the planning-scenarios page plus scenario CSV/Markdown downloads, the freshness-monitor page plus captured snapshot/register/notes, the candidate-directory preflight page plus JSON/Markdown downloads, the candidate-directory institution-change review plus CSV/Markdown downloads, the candidate-year QA carry-forward watchlist plus CSV/Markdown downloads, the release-readiness page plus control CSV/Markdown downloads, the searchable Research Library, the publication-handoff page, the data-governance page, the public-release register, representative CSV downloads, and the PDF brief. The deployed site must never be read back as an input to the analysis.

## Deployment verification

A deployment is complete only when the published branch represents the exact validated `site/` tree for the intended `main` revision. Verification must establish all of the following:

- the analytical/publication validation required by [`../TESTING.md`](../TESTING.md) passed for the revision being published;
- the `gh-pages` root tree matches the validated `site/` tree rather than a separately edited copy;
- the public HTTPS home page and representative linked pages/downloads return successfully after Pages propagation;
- browser-facing changes receive the required desktop/mobile visual review;
- representative published files match their validated local counterparts, accounting only for expected transport/line-ending normalization where applicable;
- deployment does not change analytical authority, QA disposition, source interpretation, or candidate-year readiness. Those facts remain owned by their analytical/governance documents and data files.

Release-specific commit hashes, deployment commits, test counts, page widths, source-health results, QA movements, and institution-by-institution verification notes are release evidence. Keep them in version control and the owning release/QA evidence rather than appending them to this current deployment procedure.

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

