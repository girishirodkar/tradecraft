# Agent Architecture

**Date:** 17 November 2026 (thesis stage redesigned as a research brief: contracts 3.1, 3.2, 3.3, 3.5, 3.8 and 3.11 revised, 3.12 added; 16 November: Technical Analyst added, Filing Analyst widened; 15 November: system-drafted thesis in on-demand mode; Mode 1 shelved; audit corrections 14 November; first issued 12 November 2026)
**Companion to:** `docs/factor-spec.md` rev 13 (§9a holds the prohibitions and their evidence)
**Scope:** agent contracts and the harness interface. Not implementation.

---

> **Status, 15 November 2026: Mode 1 (index overlay) is shelved** — see
> `docs/decisions/2026-11-15-mode-1-shelved.md`. The index column of the activation
> matrix and the Hedge Supervisor (§3.7) are **inactive and not to be built**. They
> stay in this document so the design is recoverable if Mode 1 returns. **Ten
> agents are live (eleven defined); the build target is the on-demand column.** Index instruments
> reach the agents through on-demand mode.
>
> **Also 15 November 2026: the Thesis agent is active in on-demand mode by default**
> (`docs/decisions/2026-11-15-system-drafted-thesis.md`), and single-name mode will
> be built later as a scan that feeds the on-demand pipeline, not as a second one.

> **Status, 17 November 2026: the thesis stage is a research brief.** Decision record:
> `docs/decisions/2026-11-16-research-brief.md`; full rules in
> `docs/on-demand-mode-design.md`, step 2A. What changed for the agents:
>
> - **No agent sets a figure.** Base rates, usual ranges, the volatility state, the
>   primary-horizon recommendation, the range-bound rule and evidence grades are
>   all computed in code.
> - **The Thesis agent drafts a direction and states no probability.**
> - **The Technical Analyst's output is description.** It is not evidence for a
>   direction and sets no exit.
> - **Findings are combined by precedence, not weights:** company evidence leads,
>   the backdrop qualifies, price has no say. Index instruments have lead and
>   qualifying evidence of their own.
> - **Invalidation is evidence-based and the Monitor watches it.** The price-based
>   risk exit is set in step 12, not here.
> - **One ticker per request.** Lists are out of scope.

> **Status, 17 November 2026 (later): stage 3, market and contracts, uses no agents.**
> Opening the chain, the liquidity re-check, expiry choice, candidate building, the
> measures, the filters and the ranking are deterministic code
> (`docs/on-demand-mode-design.md`, "Stage 3 redesigned"). The orchestrator calls
> them as tools and handles failures, such as falling back to the snapshot when the
> live chain cannot be fetched. The Event Assessor stays inactive until an
> earnings-date source exists. Stage 3 hands the Critic the selected candidate, the
> thesis record with any horizon amendment, the candidates not selected, and how
> the choice was made (expiry, filters, priority, ranking, selection).

> **Status, 17 November 2026 (night): stage 4, the challenge, is designed in full.**
> Decision record: `docs/decisions/2026-11-17-stage-4-challenge.md`; rules in the
> on-demand design, "Stage 4 redesigned". Two agents take part: the Evidence
> Retriever (3.1) and the Critic (3.4). The two checklists, the restated question,
> the readiness line and the check on the Critic's output are code. The Critic
> gives no verdict and, in the first version, holds no veto.

## 1. The rule that produced this design

**Agents are organised by cognitive function, not by mode.** An "index agent" and
a "single-name agent" would share nothing. A Critic that challenges any thesis
against the evidence corpus serves all three modes.

Result: **ten agents, seven shared** as first designed; **eleven since 16 November 2026**, when the Technical Analyst was added for on-demand thesis drafting. Reuse comes from sharing the harness and the
output contract while varying only prompt, tool subset and retrieval scope — the
same class, differently configured. Not inheritance, not abstraction.

### What is deliberately not an agent

The gate, valuation, surface fit, cost ladder, sizing, roll calendar, ladder
scheduler and trial ledger. Everything with a right answer. Agentifying a calendar
is pure cost, and the gate specifically **must** be code: gross returns are higher
in illiquid terciles, so anything permitted to reason about exceptions will request
them and be wrong.

---

## 2. The harness

One framework, ten agents. Every agent gets exactly this and nothing more.

| Provision | Detail |
|---|---|
| **Tool registry** | Per-instantiation allowlist. An agent cannot call a tool it was not granted |
| **Output schema** | Structured, validated, rejected on failure. **Evidence grades are mandatory on every claim** |
| **Retrieval scope** | Which corpus strands this instantiation may query |
| **Question reframe** | Assertions converted to questions before the model sees them. Measured: latent sycophancy β 1.13 → 0.51 (instructed) → **−0.55** (reframed). Applied by the harness, not the agent |
| **Trace log** | Every step, for the Eval Judge. Step-level, not outcome-level |
| **Guardrail hooks** | Pre-call and post-call. Parameter store is read-only at this layer |
| **Trial ledger write** | Any configuration change is logged here. Agents cannot reach it |

**Base model selection is a harness-level decision and it dominates everything
above.** Confident-false-expert follow rates measured 4%, 11% and 80% across model
generations — a ~20× spread that likely swamps every prompt-level mitigation.
Choose on that metric first.

### 2a. Additions for the demo build (18 November 2026)

The course requires that every agent has guardrails and a harness and that agents are reusable. The harness above already provides most of that. Four things are added; the table of guardrails by agent is in `docs/build-plan.md`, section 5.

1. **Retrieved text is untrusted.** Anything fetched from a filing, a data provider or the research corpus is passed to the model wrapped and labelled as data. An instruction found inside it is never followed.
2. **Input checks before any agent runs.** The symbol must come from the symbol directory; one underlying per request. A thesis supplied by the user is length-limited before extraction.
3. **Run limits,** all settings in configuration: tool calls, time and output length per agent; time per stage; text size per document and per tool result; retries; refusal of a repeated identical call; spend per request and per day; rate limits and caching for outside services; network and file allowlists; one request at a time. Values in `docs/build-plan.md`, section 4.
4. **Demonstrable guardrails.** Three scripted tests show a guardrail firing: a thesis draft that states a probability is rejected; an instruction inside a filing excerpt is ignored; a tool outside an agent's allowlist is refused.

**Reuse in the demo:** the Evidence Retriever runs in stage 2 and stage 4 from two configurations of one agent; the three analysts are one class with three configurations.

**As built (18 November 2026).** The harness is `tradecraft/harness/`: one function, `run_agent`, takes an `AgentConfig` (instructions, model, allowed tools, output format, output checks, effort). Three things were added after a review of the first version: a limit on the text sent to the model in one call; API retries and tool fetches held inside the agent's time limit; and a fingerprint of each agent's configuration written to every run's trace, which answers "log every configuration tried". Analyst findings are handed to the Thesis agent wrapped as data, since they can quote filing text. The agents' tools are in `tradecraft/tools.py`; none returns a stock quote, an option price or implied volatility.

**Orchestration (operator decision, 18 November 2026): LangGraph runs the workflow;** the harness runs inside each node. The framework decides which node runs next. The harness decides what an agent may do.

**Reasoning patterns the capstone grades** (`docs/build-plan.md`, section 4a): the Evidence Retriever and the Fundamental Analyst run a ReAct loop with tools, with one recovery shown in the demo. The Thesis agent works as a Tree of Thought in one pass: three branches (bullish, bearish, no view), each tested against the precedence rules, pruned with a reason, the remainder selected. Its output gains `branches[{view, supporting[], opposing[], meets_precedence, pruned_reason}]`. This is not debate or self-critique, the agent is not asked again, and code re-checks the selected branch.

---

## 3. Agent contracts

### 3.1 Evidence Retriever — shared

- **In:** query, strand scope filter
- **Out:** `claims[{claim, source, evidence_grade, strand, polarity}]`
- **Tools:** vector search over the 19-strand corpus
- **Prohibitions:**
  - May not synthesise a verdict. It returns evidence; something else decides.
  - **Must return balanced polarity, never disconfirming-only.** One-sided exposure
    drives stance to endpoints and *moves* the human reader rather than being
    discounted (~16% polarity shift). Correctness problem, not credibility.
  - Returns empty rather than low-relevance matches. A padded result set is worse
    than none.
- **Second duty in on-demand thesis drafting (step 2A):** fetches and stores the
  evidence for the ticker (filings, earnings materials, news, estimates, the earnings
  date, the macro calendar), each item with source and timestamp. **It does not grade
  them.** Each finding's grade (strong, moderate, weak) is set in code from three
  checks: primary source, recent, specific.
- **In stage 4 (17 November 2026):** searches the research corpus (`docs/research/`,
  the factor specification, the decision records) and nothing else. One topic per
  claim plus one for the structure type; each searched both ways; at most three
  passages a side; one reworded retry, then "nothing found". No web search.

### 3.2 Regime Assessor — shared

- **In:** date, instrument class
- **Out:** `{regime: ok | hostile | unknown, basis[], evidence_grade}`
- **Tools:** VIX term structure, realised vol, realised correlation, higher-timeframe trend state (spec §9b role 5)
- **Prohibitions:** **market-level only, never per-name.** No credible evidence was
  found for implied correlation as a cross-sectional selector. May return `unknown`.
- **In on-demand thesis drafting (revised 17 November 2026):** also reports sector and
  macro findings, each with its bearing on a view.
  - *Single names:* its findings **qualify** a view. They may support or oppose one
    that company evidence has established and may not start one.
  - *Equity indices (SPY, SPX, XSP, QQQ, IWM):* macro and policy findings are **lead
    evidence** and may start a view (operator decision).
  - *TLT:* it is the lead analyst. Rates and policy are the lead evidence.
  - Index trend, breadth and VIX are description and risk context, never support
    for a direction.

### 3.3 Thesis — shared

*Contract revised 17 November 2026.*

- **In:** the analysts' findings (3.2, 3.5, 3.11), each with its kind, grade and bearing
- **Revised 18 November 2026 (night), `docs/decisions/2026-11-18-stage-2-anchored-bearings.md`:** only a bearing-carrying finding (results against estimates, a guidance change, a new event on the list) can start, support or oppose a view; context cannot. Any one such finding graded moderate or strong can start a view. Two with opposite bearings, graded moderate or strong, give `no_view`, whatever their source. Code adds `support: weak | normal` (weak when the view rests on the earnings result alone) and, for a no view, which reason applies: conflict, or nothing carries a direction. For a thesis the user enters after a no view the record carries `relied_on[{evidence_id, kind}]` and `verdict`, both computed in code.
- **Out:** `{view: bullish | bearish, basis, branches[{view, supporting[], opposing[], meets_precedence, pruned_reason}], summary, rationale{catalyst, confirmation, tempering}, horizon_reasons[], resolution_criterion, falsifiers[{finding_id, type, trigger, action}], supporting[], opposing[], contested}` **or** `{no_view: true, kind: nothing_found | declined | insufficient_data, reason}`
- **Prohibitions:**
  - **States no probability and sets no figure.** Code places the base rate beside
    the view. A view may carry a probability of its own only after about 100
    resolved views show it beating the base rate.
  - **Must be able to decline.** `no_view` is a first-class result, not a failure.
  - **Combines findings by precedence, not weights.** A view needs at least one
    company-specific finding graded moderate or strong (for an index, one from its
    lead evidence). Qualifying evidence cannot start a view. Conflicting lead
    evidence gives `no_view`. Opposition from qualifying evidence is listed and the
    view is marked `contested`.
  - **Writes the text of the thesis screen (added 18 November 2026).** `summary` is
    one sentence giving the view and its main reason. `rationale.catalyst` and
    `rationale.confirmation` explain the supporting findings. `rationale.tempering`
    states the thesis's own weak points: concentration of the evidence in one
    family, any move in the price since the catalyst, and anything opposing.
    `horizon_reasons[]` says why the recommended horizon fits the evidence, why
    the adjacent horizons do not, and which known events fall inside it. **Every
    sentence must rest on a finding or a measured figure already in the record;**
    the validation check rejects the draft otherwise. The agent still sets no
    figure. The definitions of base rate, typical realized move and current
    volatility on that screen are fixed templates in code
    (`docs/product-shell.md`, 6.2).
  - **Citations (operator decision, 18 November 2026).** `summary`, each part of
    `rationale` and each entry of `horizon_reasons` is `{text, cites[]}`: the ids of
    the findings or measured facts the sentence rests on. The screen shows the text
    only. The validation check uses the citations and tests every number in the
    text against them (on-demand design, "Validation check").
  - **May not cite price trend, momentum, relative strength or chart levels in
    support of a direction.**
  - **Every falsifier is evidence-based.** None is a price level.
  - **Every falsifier carries a `type` from the fixed list** in the on-demand design (stage 4, check 8), so that code can tell whether the condition can be watched.
  - **Does not produce the range-bound view.** That is set by rule in code (no
    directional view, quiet volatility state, 7- or 14-day row, no event inside).
  - May not emit a cardinal score.
  - **In on-demand mode it is active by default** (path A) and skipped when the user
    supplies their own thesis (path B, see 3.12).
  - **Never receives option prices, implied volatility or a market-implied
    probability.**
  - Nothing from the dead list (§10).
  - **It is not asked again for a different answer.**
  - Every output is logged and later resolved, traded or not. **Exception:** after
    `no_view`, if the user chooses Stop, nothing is recorded.

### 3.4 Critic — shared, holds the veto

- **In:** reframed thesis (never the raw assertion), retrieved evidence, deterministic checklist results
- **Not told who wrote the thesis** (17 November 2026). The restated question is built by a fixed template in code from the stage 2 fields (on-demand design, stage 4, step 3).
- **Model:** **a different model family from the Thesis agent whenever the thesis is system-drafted.** If none is available the LLM critic is skipped and the user reviews the checklist. *Demo exception (operator decision, 17 November 2026):* the Critic runs on the same family, and the screen and the report say so.
- **Out (revised 17 November 2026):** `{objections[{text, cites[]}] (at most five), claim_dispositions[{claim_id, disposition: holds | narrower | does_not_hold}], case_for, case_against, loss_paths[{text, cites[]}], missing[{text, source}], priced_in[{claim_id, reading}]}`. Nine tasks and five rules in the on-demand design, stage 4, step 5. The veto is not built in the first version.
- **Prohibitions:**
  - **Veto fires only on a structural precondition computed outside the model.**
    A critic whose veto rests on its own judgement degenerates: in the best
    disconfirming study the critic fired 163 times, changed the action 41% of the
    time, never revised its own output, and its prompt evolved to empty.
  - **Steelman is mandatory**, not optional.
  - May not set a verdict from one-sided retrieval.
  - Confined to what rules cannot do: load-bearing-ness, paraphrase detection,
    composition errors, steelman. The closed list of refuted signals is checked by
    code.

**Why the checklist comes first:** telling a model to be critical is mostly theatre.
Anti-sycophancy preambles *reduced* accuracy on most models tested (one preprint, flagged internally
inconsistent); suppressing
sycophantic agreement by 20.9 points produced genuine-correction rates **below
0.6%**. Injected substantive flaws moved review scores −0.07 (ns) while an explicit
"strong reject" sentence moved them −1.65 — the model tracks the stated verdict,
not the reasoning.

**Required metric: concession-on-good-theses.** Hardening against agreement is not
free — anti-pressure training cut yielding 32.9 points but cut *evidence-driven
updating* 53.7 points. A critic that never concedes is broken the other way.

### 3.5 Fundamental Analyst (was Filing Analyst) — single-name; active in on-demand thesis drafting

*Widened 16 November 2026: besides filings it reads earnings releases, company news, analyst estimates and revisions, and past earnings reactions (on-demand design, step 2A inputs 1–6). Revised 17 November 2026: its company-specific findings are the **lead evidence** for a single-name view, and it raises risk flags from the defined list. For index instruments it reports aggregate earnings and results from the largest holdings. Its findings change no figure.*

- **In:** ticker, filing document
- **Out:** `findings[{finding, location, source, date, bearing: supports_bullish | supports_bearish | none}]`, `risk_flags[{flag, evidence_id}]`. Grades are attached in code.
- **Revised 18 November 2026 (night): what earns a bearing** (`docs/decisions/2026-11-18-stage-2-anchored-bearings.md`). Each finding has a `kind`: `guidance_change` (with the two figures compared), `new_event` (with an `event_kind` from the fixed list) or `context`. A bearing other than "none" is allowed only on a guidance change that quotes both figures and on a listed event that is recent (dated within the last 30 days, or since the latest earnings report; operator decision, 19 November 2026), whose bearing code sets from the list. **The results-against-estimates finding is built in code from the earnings figures; the analyst does not report it and does not set its bearing.** Everything else is context with bearing "none". A rejected signal is refused as a finding. The analyst still reports what it finds on both sides; it no longer says "which way a fact points". Run twice on the same stored evidence it must produce identical bearings.
- **Tools:** EDGAR submissions, XBRL frames, full-text search
- **Prohibitions:**
  - **Extraction, with a stated bearing per finding. It does not form the view.** The Thesis agent applies the precedence rules.
  - May raise only flags on the defined list.
  - Never point an unanchored prompt at a filing: 73.8% of generic-dictionary
    "negative" hits in 10-Ks are finance-neutral words.
  - **Must flag parametric-hindsight risk.** The model's training cutoff postdates
    any backtest period, so a summary of a historical filing may be conditioned on
    the subsequent price move. No purging, embargo or deflation detects this.

### 3.6 Event Assessor — single-name, active whenever the expiry spans a report

- **In:** ticker, chain, verified earnings datetime
- **Out:** `{sigma2_jump, implied_move, historical_moves[], shrunk_forecast}`
- **Prohibitions:** **requires verified before-open / after-close timing. Must
  refuse rather than guess.** A wrong event date produces a wrong strip, which
  produces a false "expensive" verdict — the error this agent exists to prevent.

### 3.7 Hedge Supervisor — index only (INACTIVE: Mode 1 shelved 15 November 2026)

- **In:** position greeks, constant target delta, band width
- **Out:** `{drift, action: hold | adjust, contracts}`
- **Prohibitions:** recommends only; **no execution capability**; index mode only.
  A single-name hedged module is dead (~150 bps/yr cost against 28 at index level).

### 3.8 Monitor — shared, post-trade

- **In:** open position, entry record, daily batch
- **Out:** `{triggered[], order_tickets[]}`
- **Prohibitions:**
  - **Pre-registered conditions only.** May not re-form an opinion — a losing
    position always has adverse news attached, and hindsight reasoning will find it.
  - **Output is order tickets, never notifications.** Resting stop/take orders moved
    the disposition effect +0.082 → −0.106; a notify-only treatment measured 0.088,
    i.e. nothing. The mechanism disciplines the trade, not the trader.
  - No execution capability.
- **Revised 17 November 2026: what it watches.** The pre-registered conditions are
  the thesis's **evidence-based invalidation conditions** (a guidance change, an
  estimate revision past the stated threshold, a flagged event resolving), together
  with the price-based risk exit set in step 12. A price move alone does not
  invalidate a researched view. **Its detailed design, including the data it needs
  to watch filings and estimates while a position is open, is open.**

### 3.9 Post-mortem — shared, post-trade

- **In:** closed position, entry record, outcome label
- **Out:** `{measurements{}, process_grade, narrative}`
- **Prohibitions:**
  - **No write path to parameters.** Not a configuration choice — an architectural
    boundary.
  - Narrative labelled unreliable in the UI.
  - Must separate tiers: measurements (reliable at n=1), process grade (graded
    against what was knowable at entry, never against the outcome), narrative
    (unreliable).

### 3.10 Eval Judge — shared

- **In:** agent trace
- **Out:** `{step_scores[], kappa, errors_identified[], measured_recall}`
- **Prohibitions:**
  - **Step-level only.** Outcome-only judges showed 34–76% recall with **zero
    paired discrimination**; step-level scored 53.8–64.1 against 35.1–43.9.
  - **Must report its own measured recall** beside any quality score. A judge whose
    recall is unmeasured is not evidence.
  - Report **κ, not raw agreement** — "85% agreement" has been measured at κ 0.48.
  - Primary metric is **error-identification accuracy, not detection recall.**
    Match-F1 runs 0.50–0.97 while error-*grading* lands at 5–75%, and the hardest
    class is flawed reasoning reaching a correct conclusion (7–24%) — exactly this
    use case.

---

### 3.11 Technical Analyst — on-demand thesis drafting (added 16 November 2026; revised 17 November 2026)

- **In:** values computed in code from daily prices: trend and momentum on daily, weekly and monthly bars; support and resistance levels; relative strength against sector and index.
- **Out:** `{price_description, timeframes{daily, weekly, monthly}, levels[]}`
- **Prohibitions:**
  - **Its output is description.** It is not evidence for a direction, is not counted as an evidence family, and sets no invalidation condition or exit. Measured 16 November 2026: price trend shifted the chance of closing higher by under a point, in the mean-reverting direction, and not consistently for any one name.
  - **Interprets numbers it is given; never computes or estimates a level itself.**
  - Timeframes are reported side by side. **No agreement count, no composite score.**
  - Chart levels are carried forward to stage 3, where they are shown beside each candidate as context and recorded for later measurement. They place no strike (operator decision, 17 November 2026).
  - Chart patterns carry a weak grade. Candlesticks, Fibonacci and Elliott wave are display only and may not appear in the description.
  - Never receives option prices or implied volatility.

### 3.12 Evaluating a user-supplied thesis — not a new agent (added 17 November 2026)

The user enters a thesis as free text (on-demand design, step 2B). Existing agents do the work.

- **Extraction (Thesis agent):** direction, time frame, each factual claim, and at least one invalidation condition, which the user confirms or corrects.
- **Claim check (Fundamental Analyst, Regime Assessor):** each claim is marked supported, contradicted or not found against the stored evidence, with the item cited.
- **Rejected-signal check (code):** the closed list in spec §10, as in the Critic's checklist.
- **Shown beside it (code):** opposing evidence, the base rate for the stated direction, risk flags.
- **Verdict, in words:** well supported, partly supported, not supported, or rests on a rejected signal. The mapping from claim marks to the verdict is a fixed rule in code (on-demand design, step 2B, decided 17 November 2026).
- **Prohibitions:** no score; the verdict does not gate the workflow; opposing evidence is always shown. The Critic (3.4) challenges the thesis afterwards as for any other.

## 4. Mode activation

| Agent | Index | Single-name | On-demand |
|---|---|---|---|
| Evidence Retriever | ● | ● | ● |
| Regime Assessor | ● | ● | ● |
| Thesis | ● | ● | ● default; in the extraction role (3.12) if the user supplies the thesis |
| Critic | ● | ● | ● centrepiece |
| Fundamental Analyst | — | ● | ● always: drafts findings, or checks a supplied thesis's claims |
| Technical Analyst | — | — | ● description only |
| Event Assessor | — | ● | ● when expiry spans a report |
| Hedge Supervisor | ● | — | — |
| Monitor | ● | ● | ● |
| Post-mortem | ● | ● | ● |
| Eval Judge | ● | ● | ● |

Index mode uses **one** mode-specific agent; single-name uses **two**; on-demand
uses **zero new ones**. The asymmetry is correct — index mode is more mechanical,
so there is less for judgment to do. Do not add agents to make it look even.

---

## 5. Do not build

- **Debate or self-critique.** Intrinsic self-correction degrades (75.8 → 38.1,
  flipping 39.8% of correct answers to fix 5.8%); debate loses to plain majority
  voting at matched compute (83.0 vs 88.2); round-two novelty median 0.068, with
  confidence correlating +0.69 with round-one confidence and only **+0.10 with
  correctness**. And models that are wrong agree on the *same* wrong answer at
  0.42–0.60 against a 0.13–0.33 chance baseline — **two instances of one model
  cannot find a blind spot they share.**
- **Static persona diversity.** Lowered false-premise recovery to 35.8% from a
  43.9% baseline.
- **Model confidence displays.** Move switch rates 40.5% → 69.6% with no accuracy
  gain; users detect miscalibration 26–29% of the time. Show corpus evidence grades.
- **Explanation-as-trust-builder.** Measured: no significant reliance effect, 28.3%
  rated positively. Trust and preference were *negatively* correlated with
  performance.
- **An in-app parameter tuner.** ~45 trials on 60 monthly observations (Bailey et al.; ~12 on their conservative bound) before the
  zero-skill Sharpe bar reaches 1.0.

---

## 6. Veto mechanics

A clinical study measured an override rate of **0.68**; treat it as a prior and measure your own.

- Veto bound to a structural precondition, computed outside the model
- **Cognitive forcing function** on override — the best-measured mechanic moved
  overreliance 0.64 → 0.48 (p=.003, d=.36). Prefer assumption-surfacing (63.0%
  overreliance) over a what-if variant (80.7%)
- **Rate-limit it.** Clinical alerts at 6.4 per 100 orders produced 56–63%
  inappropriate dismissal. A critic that objects constantly is ignored entirely
- Record the override and typed reason. Honest caveat: **no credible evidence was
  found that typing a reason changes behaviour.** Keep it for the record

---

## 7. Evaluation protocol

**120 planted theses:** 40 resting on refuted signals, 20 right-for-wrong-reasons,
20 base-rate-violating, 20 out-of-corpus, 20 clean controls to catch false vetoes
(zero false vetoes in 20 bounds the rate only below ~15%; enlarge the control set if
a tighter bound is needed).

Paired across configurations: ~30–35 items detects a 30pp difference, ~120 detects
15pp.

Report per configuration: error-identification accuracy, false-veto rate,
concession-on-good-theses, premise-disposition distribution (reformulation is what
theatre looks like in the data — 94% reformulated a false premise against 2%
conceding it), and κ.

---

## 8. Honest limits

- Every human-factors finding above comes from clinical, recidivism, writing or QA
  tasks — **never financial theses.** Transfer is assumed, not demonstrated.
- Nearly all 2026 sources behind §3.4 and §6 are unreviewed preprints, several
  internally inconsistent.
- Three open questions returned **no credible evidence**: whether a typed override
  reason changes behaviour, whether users learn to discount a one-sided critic, and
  **whether question-reframing survives multi-turn pushback** — which matters,
  because conversation is multi-turn by nature.
