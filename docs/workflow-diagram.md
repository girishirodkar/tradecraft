# Tradecraft workflow diagram

Generated from the LangGraph graph in `tradecraft/workflow/graph.py` by
`python -m tradecraft.workflow.diagram`. Do not edit by hand.

Solid arrows always run. Dotted arrows are choices: the user's action at a pause
(`*_pause`, `stage2_stopped`, `stage4_stopped`), the one-time return of a draft
(`validate` to `thesis`, `critic_check` to `critic`), or a stage stopping.
The three analysts run in parallel between `grades` and `analysts_done`.

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	gate(gate)
	gate_pause(gate_pause)
	figures(figures)
	retriever(retriever)
	grades(grades)
	fundamental_analyst(fundamental_analyst)
	regime_assessor(regime_assessor)
	technical_analyst(technical_analyst)
	analysts_done(analysts_done)
	thesis(thesis)
	validate(validate)
	range_rule(range_rule)
	brief(brief)
	stage2_stopped(stage2_stopped)
	thesis_pause(thesis_pause)
	contracts(contracts)
	contracts_pause(contracts_pause)
	checklists(checklists)
	question(question)
	passages(passages)
	critic(critic)
	critic_check(critic_check)
	readiness(readiness)
	stage4_stopped(stage4_stopped)
	challenge_pause(challenge_pause)
	decision_next(decision_next)
	stopped(stopped)
	__end__([<p>__end__</p>]):::last
	__start__ --> gate;
	analysts_done --> thesis;
	brief -.-> stage2_stopped;
	brief -.-> stopped;
	brief -.-> thesis_pause;
	challenge_pause -.-> contracts;
	challenge_pause -.-> decision_next;
	challenge_pause -.-> stopped;
	checklists --> question;
	contracts --> contracts_pause;
	contracts_pause -.-> checklists;
	contracts_pause -.-> contracts;
	contracts_pause -.-> stopped;
	critic --> critic_check;
	critic_check -.-> critic;
	critic_check -.-> readiness;
	figures --> retriever;
	fundamental_analyst --> analysts_done;
	gate --> gate_pause;
	gate_pause -.-> figures;
	gate_pause -.-> gate;
	gate_pause -.-> stopped;
	grades --> fundamental_analyst;
	grades --> regime_assessor;
	grades --> technical_analyst;
	passages --> critic;
	question --> passages;
	range_rule --> brief;
	readiness -.-> challenge_pause;
	readiness -.-> stage4_stopped;
	readiness -.-> stopped;
	regime_assessor --> analysts_done;
	retriever --> grades;
	stage2_stopped -.-> figures;
	stage2_stopped -.-> stopped;
	stage4_stopped -.-> checklists;
	stage4_stopped -.-> contracts;
	stage4_stopped -.-> stopped;
	technical_analyst --> analysts_done;
	thesis --> validate;
	thesis_pause -.-> contracts;
	thesis_pause -.-> stopped;
	validate -.-> range_rule;
	validate -.-> thesis;
	decision_next --> __end__;
	stopped --> __end__;
	challenge_pause -.-> challenge_pause;
	contracts_pause -.-> contracts_pause;
	gate_pause -.-> gate_pause;
	stage2_stopped -.-> stage2_stopped;
	stage4_stopped -.-> stage4_stopped;
	thesis_pause -.-> thesis_pause;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```
