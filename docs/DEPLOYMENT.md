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

GitHub Pages should then be configured to serve branch `gh-pages` from `/`. After deployment, verify the public HTTPS home page, a state profile, the research memo, the methodology crosswalk, the recurring-research operations page, the stage-gated production-cycle page and downloads including the blank live-cycle log template, the PowerPoint management briefing, the SQL analysis page plus query/audit downloads, the ad hoc analysis page plus case CSV/Markdown downloads, the state-recovery page plus decomposition CSV/Markdown downloads, the private-nonprofit growth page plus institution-contribution CSV/Markdown downloads, the complete high-priority QA review plus resolution CSV/Markdown downloads, the planning-scenarios page plus scenario CSV/Markdown downloads, the freshness-monitor page plus captured snapshot/register/notes, the searchable Research Library, the publication-handoff page, the data-governance page, the public-release register, representative CSV downloads, and the PDF brief. The deployed site must never be read back as an input to the analysis.

**Verified October 13, 2026:** feature commit `f826871` was published as the exact validated `site/` tree on `gh-pages` deployment commit `c529911`. Twenty-six representative public pages and downloads returned HTTP 200, including the home page, California state profile, research memo, methodology crosswalk, recurring-research operations page, production-cycle page, SQL and ad hoc analysis pages, state-recovery and private-nonprofit analyses, the complete high-priority QA review, planning scenarios, freshness monitor, Research Library, publication handoff, data governance, public-release register, current site-data payload, management briefing, and PDF brief. The QA review page and its CSV/Markdown downloads matched the validated publication content after normalizing Git/Windows line endings; the CSV contained all 27 high-priority institution rows in deterministic queue order, with 6 `safe_with_context` decisions and 21 `hold_for_confirmation` decisions for 100% queue coverage. The private-nonprofit page also matched the validated tree and now carries Webster University's resolved `Safe with context` gate rather than an unresolved state. The publication-handoff page confirms that all 27 current high-priority rows have explicit publication dispositions, and the regenerated three-page PDF matched the deployed binary byte-for-byte. Governance remains 50 registered artifact families / 100 expanded downloads. The current NCES next-year snapshot remains `HOLD_YEAR_ADVANCE` with 2 of 4 required 2025 assets available. Live source-health checks resolved with no broken URLs or network errors: Research Library 7 available / 6 documented script-access restrictions, population crosswalk 1 available / 5 documented restrictions, and QA evidence 25 available / 2 documented script-access restrictions across all 27 reviewed records.

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

