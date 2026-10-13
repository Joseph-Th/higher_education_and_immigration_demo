# Cloudflare Pages Deployment

The public research brief is a static site. It does not need a framework build, server process, database, or runtime secrets.

## Recommended Git-connected setup

The repository now has a GitHub remote, so the recommended publication path is a Git-connected Cloudflare Pages project:

1. Create a Cloudflare Pages project connected to the repository.
2. Use the repository root as the project root.
3. Leave the build command empty.
4. Set the build output directory to `site`.
5. Deploy the `main` branch.

Repository: `https://github.com/Joseph-Th/higher_education_and_immigration_demo`

Before each deployment, run:

```bash
python scripts/validate_project.py
python scripts/browser_smoke.py
python scripts/check_research_library.py
python scripts/check_qa_evidence.py
```

The browser smoke test requires the optional Playwright development dependency and a local Chromium runtime. The two live-link checks are deliberately outside the offline reproducibility lane, but they should be clean or explicitly manually resolved before publication. Only deploy the generated `site/` directory after the required validation lanes pass and the site has been inspected locally.

## Direct upload

If Git integration is not desired, the contents of `site/` can be uploaded as the Pages output directory. The generated CSV downloads and `site/data/site_data.json` must be included; they are part of the published research product.

## Headers

`site/_headers` provides a restrictive Content Security Policy and basic browser security headers compatible with the current static site. If external analytics, fonts, scripts, or embeds are added later, the policy must be reviewed rather than weakened broadly.

## Custom domain

A custom domain can be attached after the first successful Pages deployment. No source code changes are required unless a canonical URL or social-sharing metadata is later added.

