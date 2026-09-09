# AGENTS.md

Canonical instructions for this repository. `.claude/CLAUDE.md` imports this file.

## Project

Cadasto brand layer for Material-for-MkDocs docs sites. Tokens, chrome, optional landing layout, two HTML overrides, and the company mark. No product copy, no build, no MkDocs project.

Consuming sites fetch these files at a **pinned tag**, the same way other Cadasto docs sites already fetch install docs. Do not point a live site at `main`.

## Layout

| Path | Role |
|------|------|
| `tokens.css` | Palette, type stacks, light/dark semantic tokens |
| `material.css` | Header, headings, body stack, footer attribution |
| `landing.css` | Optional landing chrome (hero, cards, home nav/footer) |
| `overrides/home.html` | Landing template — product name/logo/nav come from the consumer |
| `overrides/partials/copyright.html` | Docs-page footer with the Cadasto mark |
| `assets/cadasto-mark.png` | Shared mark; consumer copies it to their `docs_dir/assets/` |
| `files.json` | The fetch list |

## Commands

There is no build. Edit the CSS or overrides and tag a release when a consumer should pick it up.

## How a site consumes this

Pin a `vX.Y.Z` tag. Fetch every path in `files.json` (raw GitHub is enough). Wire:

- `extra_css`: Google Fonts URL below, then `tokens.css`, `material.css`, and `landing.css` if the site has a landing page
- `theme.font: false`
- both Material palettes (`slate` first, then `default`) with the brightness toggle
- `theme.custom_dir` that includes the two override files
- the `privacy` plugin, so the font URL is self-hosted at build time
- `markdown_extensions`: `attr_list`, `md_in_html`, and `pymdownx.emoji` with the
  twemoji generator — the landing classes are attached with `attr_list`, the card
  grids wrap Markdown in `<div>`, and the icon chip styles the `.twemoji` SVG that
  `pymdownx.emoji` emits. Without them a landing page renders unstyled.
- the mark at `<docs_dir>/assets/cadasto-mark.png`

Font URL (Fira Sans 500/700, Roboto, Roboto Mono, `display=swap`):

```
https://fonts.googleapis.com/css2?family=Fira+Sans:wght@500;700&family=Roboto:ital,wght@0,300;0,400;0,500;0,700;1,400&family=Roboto+Mono:ital,wght@0,400;0,700;1,400&display=swap
```

Product logo, nav, pages, and any extra CSS stay in the consuming repo.

## Landing page contract

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
Renaming or omitting one of these classes fails silently — the element simply
keeps Material's default styling.

## Gotchas

- **`--md-text-font-family` and the scheme colour tokens must be set on `body`**, not only `:root`. Material declares them on `<body>`; a `:root` value is inherited and then overwritten. The page keeps `-apple-system` or the default Material colours if this is "fixed".
- **Fonts are requested from the consuming `mkdocs.yml`**, not from these CSS files. An `@import` here starts the font request after this file parses and the swap lands late.
- **`display=swap`**, not `optional`. `optional` keeps Helvetica or the system UI for the whole visit when the webfont misses first paint. cadasto.com uses swap.
- **Do not put product copy, a product logo, or JSON-LD in this repo.** Those belong in the consuming site.
- **`material.css` hides the desktop sidebar's nav title**, on the assumption the
  site enables `features: [toc.integrate]` so that column carries the page contents
  instead. Without `toc.integrate` the left column loses its heading. The drawer
  title on small screens is unaffected — the rule is behind a min-width query.
- **Landing is optional.** A docs-only site can skip `landing.css` and `home.html`.
- Tags are `vX.Y.Z`, annotated. Never move a published tag.

## Conventions

- Conventional Commits with a scope: `feat(tokens):`, `fix(material):`, `docs:`.
- Keep this file short. A rule that belongs in a CSS comment stays next to the rule.
