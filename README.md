# cadasto-docs-theme

Brand layer for Cadasto Material-for-MkDocs sites: colours, type, chrome, an optional landing layout, and the company mark.

Not a public theme package. Other Cadasto docs sites fetch these files at a pinned tag.

## What to fetch

See [`files.json`](files.json). At a `vX.Y.Z` tag:

```
https://raw.githubusercontent.com/Cadasto/docs-theme/<tag>/<path>
```

Put the CSS on `extra_css` (after the font URL in the recipe below), merge the two override files into the site's `custom_dir`, and copy `assets/cadasto-mark.png` to `<docs_dir>/assets/`.

## Recipe in the consuming `mkdocs.yml`

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

## Licence

MIT — see [LICENSE](LICENSE).
