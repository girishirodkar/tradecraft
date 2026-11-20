# Documentation theme

**Decided:** 15 November 2026. Product documentation pages use **Ledger** in light
mode and **Night Desk** in dark mode, as one pair. The other four candidates
(Prospectus, Blueprint, Graphite, Midnight Ink) were not chosen.

Pages follow the reader's light or dark setting. Chart colours are the same blue
and orange in every page so charts read the same way everywhere; the pair was
checked for colour-blind separation and contrast on both panel colours.

## Type

| Role | Face |
|---|---|
| Headings | Space Grotesk, 600 |
| Body | IBM Plex Sans, 400 / 600 |
| Numbers, labels, bid and ask | IBM Plex Mono |

## Colour tokens

| Token | Ledger (light) | Night Desk (dark) | Use |
|---|---|---|---|
| `--bg` | `#f5f7fa` | `#12161b` | page |
| `--surface` | `#ffffff` | `#1b2027` | panels |
| `--ink` | `#17212b` | `#eef1f4` | text |
| `--ink-2` | `#44515f` | `#c1c9d2` | secondary text |
| `--ink-3` | `#5f6c7b` | `#9aa5b1` | captions |
| `--line` | `#d9e0e8` | `#2f3742` | borders |
| `--accent` | `#1c5cab` | `#86b6ef` | links, highlights |
| `--band` | `#e8f0fa` | `#1f2c3d` | callouts |
| `--series-1` | `#2a78d6` | `#3987e5` | chart, first series |
| `--series-2` | `#eb6834` | `#d95926` | chart, second series |
| `--good` | `#0a7d0a` | `#3fbf3f` | pass, always with a word or icon |
| `--crit` | `#c23232` | `#e66767` | fail, always with a word or icon |

Panels have a 1px border and a 6px radius. Reading column is 860px at most.

## Pages

- The product manual, written 19 November 2026 from the application as built: four pages that share one header (meta line, title, introduction, and four tabs that move between the pages). `manual.html` — part 1, what Tradecraft is (added 20 November 2026; the manual was brought up to date with the Cboe, Tradier, snapshot order the same day): the product in brief, what it will not do, why it is built this way, and the pitch video. `manual-logic.html` — part 2, the logic of each stage: one short chapter per stage. `manual-architecture.html` — part 3, the architecture at four levels (100 overview, 200 components and the path of a request, 300 agents, harness, workflow and stores, 400 the code), the course's concepts, and what is not built. `manual-stages.html` — part 4, the four stage pages below shown in full, unchanged, each in a frame. **The header is repeated in the four files: change it in all four.** The manual governs nothing: rules live in the decision records.
- `thesis-stage.html` — stage 2 of on-demand mode: thesis components, inputs and roles, agents, safeguards.
- `market-contracts.html` — stage 3 of on-demand mode: candidate structures, their measures, filters, ranking by a chosen priority, the output screen and the decision record. Six parts, written 17 November 2026.
- `challenge.html` — stage 4 of on-demand mode: the challenge. Eight parts: outline, the six steps, the twelve checks on the thesis, the eleven checks on the contract, the question and the evidence, the critic, the challenge screen with its readiness line, and the decision record. Written 17 November 2026.
- `liquidity-gate.html` — stage 1 of on-demand mode. The reference implementation
  of this theme: copy its `<style>` block when starting a new page.

## Language

Decided 15 November 2026: documentation is written in a professional finance
register, in the third person ("the user", not "you").

| Use | Not |
|---|---|
| bid-ask spread, quoted spread | gap |
| premium, mid | option price |
| underlying; coverage universe | ticker; snapshot list |
| spot | stock price |
| moneyness, distance from spot | strike distance |
| days to expiration (DTE), expiration, tenor | days to expiry |
| invalid quote, crossed market | broken quote |
| eligible, clears the screen | qualifies, survives |
| binding control | the control that failed |
| override, rationale | overrule, reason |
| execution cost, round trip | cost of trading |
| low-premium contracts | cheap options |

Stage names (Liquidity gate, Thesis, Market and contracts, Challenge, Decision
and record, Afterwards) are unchanged so they match the design documents.

## Screens and explanations

Every mock-up or interactive figure carries a tag: `APPLICATION SCREEN` (what the user sees in the application) or `EXPLANATION ONLY` (illustrates a rule; not part of the application). Each stage page lists its screens under "Screens in this stage" in the overview, including screens not yet drawn. Cards, tables and figures are 860px at most, centred in a 1120px page.

## Product name

The product is **Tradecraft** (18 November 2026). Each page's meta line starts `TRADECRAFT · `. Page titles name the stage.

## Application screens

Decided 18 November 2026. `tradecraft-prototype.html` in this folder is the clickable mock-up of the application and the reference for the build; `docs/product-shell.md` specifies it. It adds one token, `--warn` (#8a5a00 light, #e5b454 dark), for the range-bound label. Direction labels: green bullish (`--good`), red bearish (`--crit`), amber range-bound (`--warn`), grey no view (`--ink-3`), each on a light tint of its own colour. On application screens section headers use the display typeface at about 17px with a rule beneath. The wording table for screens is in `docs/product-shell.md`, section 3; it extends the table above.
