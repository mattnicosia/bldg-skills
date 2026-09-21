# Primary eval anchor: monday.com Night theme, Agents screen

This is the "3" anchor for every run. Automated tools catch errors. This file
is what "good" looks like, measured off a live monday.com account with the
Night theme selected (the account menu calls it Night; the body class is
`black-app-theme`). The screen is **Agents** (`/ai_agents`), the "Meet your
agents" page. Measured 2026-09-21 at 1450px. Re-measure if monday ships a
redesign, and say so in the scorecard when you do.

The board view (`/boards/...`) in the same theme is **not** the anchor. Matt
dislikes it. It is a dense table where every cell carries the same weight, so
it fails the hierarchy axis on its own terms. Do not screenshot it as a
reference.

Use this file two ways:

1. **Vision judge anchor.** Screenshot the Agents screen in Night theme at
   1440px during step 1 and give it to the blind judge next to BEFORE and
   AFTER. The judge scores against this, not against a generic idea of
   "dark UI".
2. **Token diff.** Compare the AFTER page's measured values against the tables
   below. Any `hard` rule the AFTER page fails is a failed eval.

## Why this screen is the bar

It is a dark product page that does not look like "dark SaaS". Read it against
the ten axes:

- **One dominant element per viewport.** Above the fold there is a short
  centered H1, one line of subhead, and one large prompt box. Nothing else
  competes. Below the fold each section is one wide feature card beside a row
  of small cards, never three identical cards.
- **Chrome is grey, colour is content.** The rail, panes, chips, borders and
  text are all greys. Every saturated pixel is inside a card: the character
  illustration, the tinted feature card, the coloured icon. The single blue
  action colour appears only on the selected nav item.
- **An ambient field behind, never on.** The hero sits on a blurred conic
  gradient at 8% opacity, baked into a static SVG so nothing blurs at runtime.
  Cards on top of it are opaque. That is the field-behind-content rule done
  right.
- **Pacing.** Hero, then a chip row, then sections, each with the same
  big-plus-small rhythm. Scrolling reads as a sequence.
- **Type is two families with a real scale.** Poppins for headings, Figtree
  for everything else. 30, 20, 18, 16, 15, 14. Headings never exceed 600.
- **Depth without shadow.** Panes and cards are `#111` on `#111`, separated by
  a 1px hairline and a 16px corner. The only shadows are the tinted glow under
  each character tile and the focus glow on the prompt box, both of which mean
  something.

## Measured tokens

### Canvas

| Role | Value | Where measured |
|------|-------|----------------|
| App background | `#111111` | `--application-background-color` |
| Pane and card surface | `#111111` | left pane, agent cards |
| Card image band, badge, rail | `#2c2c2c` | `--secondary-background-color` |
| Elevated surface | `#212121` | `--color-surface` |
| Card border | `#3a3a3a` | agent card, 1px |
| Pane hairline | `#4d4d4d` | left pane border, disabled send button |
| Chip border | `#636363` | `--layout-border-color` |
| Control border | `#8d8d8d` | `--ui-border-color` |

Three surface tiers: 17, 33, 44 in lightness. Four greys for lines. Nothing
lighter than `#2c2c2c` is ever a surface.

### Text and icons

| Role | Value | Contrast on #111 |
|------|-------|------------------|
| Primary text | `#eeeeee` | 16.6:1 |
| Secondary text, icons, placeholders | `#aaaaaa` | 8.3:1 |
| Disabled | `#eeeeee` at 38% | |

Two text greys.

### Accent and status

| Role | Value |
|------|-------|
| Action (the only accent) | `#0073ea` |
| Action hover | `#0060b9` |
| Selected nav item | `#133774` fill, white text |
| Link | `#69a7ef` |
| Done / working / stuck (data only) | `#00c875` / `#fdab3d` / `#df2f4a` |
| Gradient, used in two places only | `#1ad5ff` to `#0074fd` to `#c367f2`, left to right |

The gradient appears on the last word of the H1 and as the 1px border of the
prompt box. Nowhere else.

### Hero

| Element | Value |
|---------|-------|
| H1 | Poppins 500 30px / 40px, letter-spacing -0.5px, centered |
| H1 accent word | same type, gradient text fill |
| Subhead | Figtree 400 16px / 22px, personal ("Hey Matt, ...") |
| Prompt box | 644 x 175px, `#111` fill, 1px gradient border drawn by a pseudo-element |
| Prompt focus | a blurred copy of the border (6px blur) fades from 0 to visible and hue-shifts 40deg |
| Send button | 32px square, radius 8, `#4d4d4d` until there is input |
| Ambient field | static SVG, conic gradient of cyan, teal, green and violet at 8% opacity, gaussian blur 35 baked in, stretched to the 629px hero block |

### Chips

| State | Value |
|-------|-------|
| Size | 32px tall, radius 16 (pill), padding 0 16px, Figtree 15px |
| Unselected | `#111` fill, 1px `#636363` border, `#eee` text |
| Selected | `#eee` fill, `#111` text. Inverted, no accent colour. |
| Hover | 30% grey overlay, border goes transparent |

### Section grid

| Element | Value |
|---------|-------|
| Content width | 970px |
| Row | one feature card 473px wide plus two agent cards 225px wide, 24px gaps, all 289px tall |
| Following rows | four agent cards |
| Section heading | Poppins 600 18px / 24px |

### Agent card (225 x 289)

| Element | Value |
|---------|-------|
| Surface | `#111` fill, 1px `#3a3a3a` border, radius 16 |
| Image band | 120px tall, `#2c2c2c`, square corners inside the card |
| Character tile | 72px, radius 16, drop shadow `0 24px 18px 8px` in the character's own colour at 20% |
| Body padding | 0 16px 16px |
| Name badge | `#2c2c2c` fill, radius 4, 24px tall, Figtree 15px |
| Title | Figtree 600 16px / 22px |
| Description | Figtree 400 14px / 20px, clamped to 2 lines |
| Footer | coloured app icon left, install count right, 15px |
| Hover | 70ms transition on border-color, box-shadow and transform |

### Feature card (473 x 289)

| Element | Value |
|---------|-------|
| Surface | `#2c2c2c` base under a category-tinted photographic gradient image, 1px inset ring `#2c2c2c`, radius 28 |
| Padding | 28px 40px 28px 28px |
| Title | Figtree 500 20px / 28px, letter-spacing -0.1px |
| Body | Figtree 300 16px / 22px |
| Icon tile | 117px square, `#111` fill, radius 28, one coloured line icon |

The feature card is the one surface with a gradient on it, and the gradient is
an image treated as photography, not a CSS ramp on chrome. Its tint changes
per section, which is how each section gets its own identity without a new
layout.

### Scales

| Scale | Values |
|-------|--------|
| Spacing | 4, 8, 16, 24, 32 |
| Radius | 4, 8, 16, 28 |
| Type | 30, 20, 18, 16, 15, 14 |
| Weight | 300, 400, 500, 600. Never 700. |

## Pass rules for the token diff

`hard` rows fail the eval. `soft` rows are noted in the scorecard.

| Rule | Kind |
|------|------|
| Body text contrast on its surface is 7:1 or better | hard |
| At most two text greys | hard |
| One accent hue on chrome, used only on actions and selection | hard |
| Every card on top of a field is fully opaque | hard |
| No runtime `filter: blur()` on any element larger than a control | hard |
| No shadow on cards or panes except one that carries meaning (a focus state, a tinted glow under an image) | hard |
| Headings at weight 600 or lighter, and 500 where the house rules say 500 | hard |
| At most two type families | hard |
| Above the fold: one H1, one line of support, one interactive element | hard |
| A section grid mixes one large card with several small, never N identical cards | hard |
| Ambient field at or under 10% opacity, baked static, blurred at build time | soft |
| Surfaces from three lightness tiers | soft |
| Radius from one four-step scale | soft |
| Spacing on a 4 or 8 grid | soft |
| Gradient on at most one word of the H1 and one border, and only where the house rules allow gradient text at all | soft |

## What not to copy

- **The board view.** See the top of this file.
- **The cartoon characters themselves.** They are monday's brand. Take the
  system: a hero tile per card, a tinted shadow that borrows the tile's colour,
  a grey band behind it. Put the buyer's real subject matter in the tile.
- **Gradient text where the house rules ban it.** BLDG Vision bans gradient
  text fills outright, so an AFTER page for that product uses the solid `#eee`
  H1 and keeps the gradient for the one border, or drops it.
- **The personal greeting.** "Hey Matt" works inside a logged-in product. A
  landing page stranger has no name yet.
