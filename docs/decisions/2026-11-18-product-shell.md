# Decision: the product shell and screens follow the clickable mock-up (18 November 2026)

**Decided by:** the operator, after stepping through `docs/site/tradecraft-prototype.html`.

1. **Navigation.** A stage bar with one stage on screen at a time. Completed stages can be reopened read-only.
2. **Screens.** Home and the four stage screens are built as drawn in the mock-up. The contracts and challenge screens are the cards already documented for stages 3 and 4.
3. **Wording.** Screens use trading terms (bid-ask spread, DTE, spot, premium, breakeven, POP, slippage, bull and bear case). The design documents keep their plainer wording. The mapping is in `docs/product-shell.md`, section 3.
4. **The first-ranked candidate is called "best fit", never "recommended".**
5. **Direction labels are coloured:** green bullish, red bearish, amber range-bound, grey no view.
6. **Liquidity gate.** The criteria in use are always visible with their defaults. "Adjust criteria" opens a compact panel of sliders, a preset list and number boxes. A change applies to the current request only.
7. **Thesis screen.** The thesis is a summary sentence and three blocks (catalyst, confirmation, what tempers it). The horizon is explained. Base rate, typical realized move and current volatility are each defined in plain words beside the figures.
8. **New Thesis agent outputs:** `summary`, `rationale {catalyst, confirmation, tempering}`, `horizon_reasons[]`. Checked by the validation check against the findings in the record.

9. **Symbol search on the Home screen (added later the same day).** The box takes a symbol or a company name and suggests matching listed symbols as the user types. It covers all US-listed stocks and ETFs, from a symbol directory stored locally. Detail in `docs/product-shell.md`, section 5.

**Not decided:** welcome screen or login; the Records and Settings pages; stage 5 and 6 screens.

**Why:** the operator found the one-line thesis too thin to act on, wanted the default criteria visible, and wanted the screens to read as a trading tool.
