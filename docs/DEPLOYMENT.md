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

GitHub Pages should then be configured to serve branch `gh-pages` from `/`. After deployment, verify the public HTTPS home page, a state profile, the research memo, the methodology crosswalk, the recurring-research operations page, the searchable Research Library, the publication-handoff page, representative CSV downloads, and the PDF brief. The deployed site must never be read back as an input to the analysis.

**Verified October 13, 2026:** the public home page, California state profile, research memo, population crosswalk, recurring-research operations page, searchable Research Library, publication-handoff page, publication-handoff CSV, Research Library CSV, and PDF brief all returned HTTP 200. The deployed Research Library exposed the current population/workflow taxonomy, the publication handoff contained the expected N01-B01 control set, and the deployed site payload reported the expected 1,044,137 Fall 2024 headline value.

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
python scripts/build_pdf_brief.py
python scripts/validate_project.py
python scripts/browser_smoke.py
python scripts/check_for_new_release.py
python scripts/check_research_library.py
python scripts/check_population_crosswalk.py
python scripts/check_qa_evidence.py
```

The PDF build and browser smoke test require the optional Playwright development dependency and a local Chromium runtime. The live-link checks are deliberately outside the offline reproducibility lane, but they should be clean or explicitly manually resolved before publication. `deliverables/research_brief_manifest.json` binds the committed PDF to the exact generated memo source; validation fails when that publication artifact is stale. Only deploy the generated `site/` directory after the required validation lanes pass and the site has been inspected locally.

## Direct upload

If Git integration is not desired, the contents of `site/` can be uploaded as the Pages output directory. The generated CSV/Markdown/PDF downloads and `site/data/site_data.json` must be included; they are part of the published research product.

## Headers

`site/_headers` provides a restrictive Content Security Policy and basic browser security headers compatible with the current static site. If external analytics, fonts, scripts, or embeds are added later, the policy must be reviewed rather than weakened broadly.

## Custom domain

A custom domain can be attached after the first successful Pages deployment. No source code changes are required unless a canonical URL or social-sharing metadata is later added.

