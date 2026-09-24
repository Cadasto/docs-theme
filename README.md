# Cadasto Docs Theme

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/release/Cadasto/docs-theme?label=version)](https://github.com/Cadasto/docs-theme/releases)
[![Material for MkDocs](https://img.shields.io/badge/Material_for_MkDocs-brand_layer-526CFE?logo=materialformkdocs&logoColor=white)](https://squidfunk.github.io/mkdocs-material/)

The brand layer for Cadasto's Material-for-MkDocs documentation sites, for maintainers who wire a Cadasto docs site. It provides the colour and type tokens, the header, heading and footer chrome, an optional landing layout, two template overrides, and the company mark.

It carries only the brand. Each consuming site owns its content, product logo, nav, pages, any extra CSS, and its own `mkdocs.yml`. This repo has no build and no MkDocs project, and it is not a public theme package: other Cadasto docs sites fetch these files at a pinned tag.

**Requirements.** A site built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) and its `privacy` plugin; this repo does not pin a Material version. The site's `mkdocs.yml` must request the Google Fonts URL given under [Installation](#installation) itself, because the stylesheets load no fonts and depend on the weights that URL lists.

## Table of contents

- [What to fetch](#what-to-fetch)
- [Installation](#installation)
- [Upgrading](#upgrading)
- [Development](#development)
- [License](#license)

## What to fetch

See [`files.json`](files.json). At a `vX.Y.Z` tag:

```text
https://raw.githubusercontent.com/Cadasto/docs-theme/<tag>/<path>
```

Put the CSS on `extra_css` (after the font URL in the recipe below), merge the two override files into the site's `custom_dir`, and copy `assets/cadasto-mark.png` to `<docs_dir>/assets/`.

## Installation

Add this to the consuming site's `mkdocs.yml`:

```yaml
theme:
  name: material
  custom_dir: overrides
  font: false
  palette:
    - scheme: slate
      primary: custom
      accent: custom
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
    - scheme: default
      primary: custom
      accent: custom
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode

extra_css:
  - https://fonts.googleapis.com/css2?family=Fira+Sans:wght@500;700&family=Roboto:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Roboto+Mono:ital,wght@0,400;0,700;1,400&display=swap
  - stylesheets/tokens.css
  - stylesheets/material.css
  - stylesheets/landing.css   # omit on a docs-only site

plugins:
  - privacy
```

`theme.font: false` is required: the theme's own loader uses `display=fallback` and a different stack. The `privacy` plugin self-hosts the font URL at build time.

Both palette entries are needed, in that order. `home.html` re-includes Material's palette partials, so a landing page gets the same toggle as every other page and honours the visitor's stored choice.

The font URL's weight list is not decorative: the stylesheets use Fira Sans at 500 and 700 and Roboto at 400/500/600/700 plus italic 400. Trim one and that face is synthesised, with nothing in the build to say so.

The product logo, nav, and pages stay in the consuming repo. Landing pages set `template: home.html` in their front matter.

A landing page also needs the `attr_list`, `md_in_html` and `pymdownx.emoji` Markdown extensions, the last with the `twemoji` generator. Without them the landing classes never attach and the page keeps Material's default styling. The [landing page contract](AGENTS.md#landing-page-contract) lists the class names its `index.md` must use. A docs-only site can skip `landing.css` and `home.html`.

`material.css` hides the desktop sidebar's nav title on the assumption that the site enables `features: [toc.integrate]`. Without it, the left column loses its heading.

## Upgrading

Tags are never moved, so a pinned tag always serves the same files. Never point a live site at `main`. To move to a newer tag:

1. Check what changed on the [releases page](https://github.com/Cadasto/docs-theme/releases) or the [tags page](https://github.com/Cadasto/docs-theme/tags).
2. Change the pinned tag and fetch every path in `files.json` at the new tag, reading `files.json` from that tag too.
3. Compare the font URL under [Installation](#installation) at the new tag with the one in your `mkdocs.yml`. The weight list follows the stylesheets, so a release can change it: v0.2.0 added weight 600 for body text and dropped 300.

## Development

Nothing here needs building. Edit the CSS or overrides, run the contrast check, and tag a release when a consumer should pick up the change:

```bash
python3 tools/contrast.py   # every token pair in tokens.css against WCAG AA
```

The check has no dependencies and needs no MkDocs site. Tag each release as an annotated `vX.Y.Z` tag, and never move a published one. Conventions and the silent failure modes are in [AGENTS.md](AGENTS.md).

## License

[MIT](LICENSE)
