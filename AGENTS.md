# AGENTS.md

Canonical instructions for this repository. `.claude/CLAUDE.md` imports this file.

## Project Overview

Cadasto brand layer for Material-for-MkDocs docs sites. Tokens, chrome, optional landing layout, two HTML overrides, and the company mark. No product copy, no build, no MkDocs project; do not add a build or an MkDocs project. The human pitch and the full `mkdocs.yml` recipe are in [README.md](README.md#installation).

Consuming sites fetch these files at a **pinned tag**, the same way other Cadasto docs sites already fetch install docs. Do not point a live site at `main`.

## Domain Context

### How a site consumes this

Pin a `vX.Y.Z` tag. Fetch every path in `files.json` (raw GitHub is enough). Wire:

- `extra_css`: Google Fonts URL below, then `tokens.css`, `material.css`, and `landing.css` if the site has a landing page
- `theme.font: false`
- both Material palettes (`slate` first, then `default`) with the brightness toggle
- `theme.custom_dir` that includes the two override files
- the `privacy` plugin, so the font URL is self-hosted at build time
- `markdown_extensions`: `attr_list`, `md_in_html`, and `pymdownx.emoji` with the
  twemoji generator. The landing classes are attached with `attr_list`, the card
  grids wrap Markdown in `<div>`, and the icon chip styles the `.twemoji` SVG that
  `pymdownx.emoji` emits. Without them a landing page renders unstyled.
- the mark at `<docs_dir>/assets/cadasto-mark.png`

Font URL (Fira Sans 500/700, Roboto 400/500/600/700 + italic, Roboto Mono,
`display=swap`). The weight list is not decorative; see the gotcha below:

```
https://fonts.googleapis.com/css2?family=Fira+Sans:wght@500;700&family=Roboto:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Roboto+Mono:ital,wght@0,400;0,700;1,400&display=swap
```

Product logo, nav, pages, and any extra CSS stay in the consuming repo.

### Landing page contract

`landing.css` styles two groups of class names. The chrome ones
(`home-nav*`, `home-footer*`, `home`) are emitted by `home.html`; the rest are
the **contract a consuming `index.md` has to honour**, because nothing else
declares them:

| Class | Applied to |
|-------|-----------|
| `home-hero` | The hero section; its `h1`, plus `home-hero__mark` on the logo image |
| `home-tagline` | Hero sub-headline paragraph |
| `home-cta` | Button row; buttons use Material's `md-button` / `md-button--primary` |
| `home-reassure` | Small print under the buttons |
| `section-title` | Centred section `h2` |
| `features-grid` > `feature-card` | Auto-fit card grid; each card is icon, `h3`, `p` |
| `two-products` > `product-card` | Wider card grid with a green left border |
| `quick-start` | Narrow centred block ending in a code fence |

A page opts into the template with `template: home.html` in its front matter.
Renaming or omitting one of these classes fails silently: the element simply
keeps Material's default styling.

## Repository Layout

| Path | Role |
|------|------|
| `tokens.css` | Palette, type stacks, light/dark semantic tokens |
| `material.css` | Header, headings, body stack, footer attribution |
| `landing.css` | Optional landing chrome (hero, cards, home nav/footer) |
| `overrides/home.html` | Landing template; product name/logo/nav come from the consumer |
| `overrides/partials/copyright.html` | Docs-page footer with the Cadasto mark |
| `assets/cadasto-mark.png` | Shared mark; consumer copies it to their `docs_dir/assets/` |
| `files.json` | The fetch list |
| `tools/contrast.py` | WCAG check over `tokens.css`; not fetched by consumers |

## Development

There is no build. Edit the CSS or overrides and tag a release when a consumer should pick it up.

One check. No dependencies, and it needs no MkDocs site. Run it before tagging; it must end with `contrast: OK`:

```bash
python3 tools/contrast.py   # every token pair in tokens.css against WCAG AA
```

Keep this file short. A rule that belongs in a CSS comment stays next to the rule.

### Commit Messages

- Conventional Commits with a scope: `feat(tokens):`, `fix(material):`, `docs:`.

### Versioning

- Tags are `vX.Y.Z`, annotated. Never move a published tag.

## Gotchas

- **`--md-text-font-family` and the scheme colour tokens must be set on `body`**, not only `:root`. Material declares them on `<body>`; a `:root` value is inherited and then overwritten. The page keeps `-apple-system` or the default Material colours if this is "fixed".
- **Light mode uses `--cadasto-ink-blue` / `--cadasto-ink-green`, never the raw brand blue and green.** Those two are tuned for the navy surface; on white they measure 2.27:1 and 1.72:1 against a WCAG AA floor of 4.5:1. The ink tokens mix each toward the navy to clear AA while keeping the hue, and `--cadasto-on-ink` is the only label colour the fills can carry. Reaching for `var(--cadasto-blue)` in a rule that paints text or a fill on the *page* surface silently reintroduces the failure: it looks right in dark mode, which is the default. The unmixed hues are still correct on navy, which is why both footers keep them. `tools/contrast.py` fails if any pair regresses.
- **`overrides/home.html` replaces `header`, so it has to re-include `partials/palette.html` and `partials/javascripts/palette.html`.** Material keeps the radio inputs *and* the localStorage restore inside its own header, not in the bundle. Drop either include and the landing page renders the first-listed scheme with no toggle, ignoring what the visitor chose on every other page. The mismatch is invisible while the site ships one scheme.
- **The font URL's weight list is coupled to these stylesheets.** Fira Sans is used at 500 and 700, Roboto at 400/500/600/700 and italic 400. A weight the CSS uses but the URL omits gets a synthesised face, which no build step reports. Roboto 300 is deliberately absent: the only rule that wanted it was Material's `h1`/`h2`, which `material.css` overrides to Fira Sans.
- **Fonts are requested from the consuming `mkdocs.yml`**, not from these CSS files. An `@import` here starts the font request after this file parses and the swap lands late.
- **`display=swap`**, not `optional`. `optional` keeps Helvetica or the system UI for the whole visit when the webfont misses first paint. cadasto.com uses swap.
- **Do not put product copy, a product logo, or per-site JSON-LD in this repo.** Those belong in the consuming site.
- **`material.css` hides the desktop sidebar's nav title**, on the assumption the site enables `features: [toc.integrate]` so that column carries the page contents instead. Without `toc.integrate` the left column loses its heading. The drawer title on small screens is unaffected; the rule is behind a min-width query.
- **Landing is optional.** A docs-only site can skip `landing.css` and `home.html`.
