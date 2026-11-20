# Tradecraft: build log

A running record of what is built, what is next and what was decided, session by session. The design documents hold the rules; this file says where the build stands. Newest session first.

## 20 November 2026, about 12:25 PT: the rolling job is hourly and slowed; BRK.B fixed (operator decisions)

The operator chose the slower, hourly rolling refresh (07:00, 08:00, 09:00, 10:00, 12:00 Pacific, about 65 Tradier requests a minute) and kept the 7 min 21 s take as the demo video. **BRK.B was the one name with no rows** in both morning runs: Tradier writes it BRK/B and lists its expirations only with `includeAllRoots`. Fixed in `chain_census.py` and in `chain.live_tradier`, which now also asks for all roots. Tested on real data: BRK.B 1,524 rows through the job and 1,524 contracts through the application; SPX through the application 25,866 contracts over 38 expirations. **The 11:00 archive file of 20 November has no BRK.B rows and cannot be refilled.** 376 tests pass. The operator installs the new schedule with `ops/reinstall.sh`. Not yet seen: a full run at the slower pace (estimated at about 45 minutes).

## 20 November 2026, 11:40 PT: the demo re-recorded at real speed; the first full snapshot runs on Tradier

**Why again.** The operator found the scrolling in the 10:01 take rushed and allowed a longer video. The cause was in the recorder's assembly, not its scrolling: any passage longer than its narration was sped up to fit. Now a passage is never sped up (it lasts as long as its actions at real speed or as its narration, whichever is longer, with silence after the voice), scrolls move at no more than about 380 pixels a second with a 0.7 second pause after each, and the frames and timings are kept (`takes.json`) so a change of pacing needs no new recording.

**Takes of the day (all in `data/video/demo/takes/`, read-only, git-ignored).** 10:01: 5 min 9 s, TGT main, $0.82. 10:50: 5 min 9 s, AMZN main, $1.00 (slower scrolls, but still squeezed by the assembly). **11:40: 7 min 21 s, MSFT main (bullish), AMZN bearish, NVDA conflict, SPY index, $0.91: the one made at real speed.** Two attempts produced nothing ($0 and about $0.16). About $2.90 on recording today. Seen on contact sheets only; not watched or heard by the build. **At 7 min 21 s the demo leaves under three minutes of the ten for the presentation: for the operator to decide.**

**Three recorder faults found on live quotes and fixed,** all the same kind: it read the page before a step that now takes a second or two had finished (the gate re-screen, stage 3 after Retry, Home after an abandoned attempt). One remains: the first symbol tried sometimes fails on a click at the gate ("nothing to point at") and the recorder moves to the next. **Seen along the way:** TGT had candidates at 10:00 and none at 10:30 (both spreads filtered, the single option not built), so it is fragile on real-time quotes.

**The snapshot jobs.** The rolling job was run once by hand at 10:04 (23.5 minutes, 105 names from Tradier, one with no rows, 196,300 rows). **The 11:00 archive run was the first under launchd with the fallback: Cboe refused, 105 names from Tradier, one with no rows, 196,300 rows, 27 minutes (11:00 to 11:27),** and the spread ladder was written. The 11:30 rolling refresh was held off while the recording ran. **A problem for the operator:** Tradier allows 120 requests a minute and a full run uses about 110 of them for 24 to 27 minutes, so with a refresh every half hour the job holds most of the allowance most of the time, and the application's own requests to Tradier compete with it while Cboe is down.

## 20 November 2026, about 10:00 PT: the live demo video is recorded; the snapshot job gets Tradier and a rolling file

**The live take.** The 10:00 scheduled run was switched off and the recorder run by hand at the operator's request. First attempt: stopped after 90 seconds with no model call, a fault in the recorder (it read the gate before the re-screen had finished, which is slower on live quotes); fixed with a proper wait. **Second attempt: a finished video, 5 min 9 s, 19 passages, $0.82,** market open, quotes from Tradier. Main run TGT (bullish), then AMZN (bearish), NVDA (no view, conflict), SPY (no view, index). On the way AMZN was tried first as the main run and **stage 3 built no candidate for it on live quotes** (not looked into), and MSFT failed on a recorder click. Files: `data/video/demo/takes/tradecraft-demo-live-20261120-1001.mp4`, its silent copy and transcript (git-ignored). Developer switches all false afterwards; `config/test_failures.json` unchanged. Seen on a contact sheet of twelve frames, not watched or heard. Two small things in the picture: Home lists the abandoned AMZN attempt under "Recent analyses", and the stage 3 test-failure message still names Cboe alone.

**The snapshot job (operator decisions).** (1) The 11:00 archive run now uses `--source auto`: Cboe, then Tradier per name. (2) A second job writes a rolling `snapshots/latest/` file every half hour in market hours, because the operator did not want the application to fall back to quotes from 11:00 the day before; the application uses whichever snapshot is newer. Tested on four real names with the job's Python (AMZN, _SPX, TLT, MSFT: 31,884 rows from Tradier in 108 seconds, Greeks filled, read back correctly by the application). **Not yet seen:** a full 106-name run on Tradier (estimated at about twenty minutes), and the rolling job under launchd, which the operator installs with `ops/reinstall.sh`. Detail: `ops/README.md`.

## 20 November 2026, about 09:45 PT: the four demo symbols checked on live data (operator request)

Stage 2 was run once, live, on each of the recorder's four symbols, with the market open and quotes from Tradier. **All four give the outcome the demo expects:** AMZN bearish (weakly supported), MSFT bullish (weakly supported), NVDA no view (conflict), SPY no view (nothing carries a direction). Each passed the gate on live quotes (19, 28, 10 and 179 contracts). No replacement symbol was looked for. Cost $0.33 in total (AMZN $0.09, MSFT $0.14, NVDA $0.06, SPY $0.04). Outputs in `data/runs-2026-11-20/` (git-ignored). Stages 3 and 4 were not run.

## 20 November 2026, morning: option quotes from Cboe, then Tradier, then the snapshot (operator decision)

After the rehearsal below failed on Cboe's block, the operator first had a "Use the latest snapshot" question built for stage 3 (commit `5f1dbf0`), then obtained a Tradier token and replaced it: **Cboe, then Tradier, then the snapshot, automatically, with the source shown and no error screen.** Built the same morning. `chain.live` tries Cboe then Tradier; stage 3 falls back to the snapshot by itself; stages 1 and 3 name the source. The decision, the as-built table (for the operator to correct) and what was seen are at the end of `docs/decisions/2026-11-17-stage-3-contract-selection.md`; product-shell 6.3, `config/data_sources.json`, `config/limits.json` and `.env.example` are amended. 376 tests pass.

**Seen with the market open and Cboe refusing:** AMZN, SPY and MSFT from Tradier in 1.1 to 1.6 seconds; MSFT through stages 1 to 3 on the replay app with no error screen. **Not seen:** the real app; stage 4; the snapshot leg on screen. **SPY passed 169 contracts on Tradier against 429 on the snapshot of 19 November: not looked into.** FMP was checked for option quotes at the operator's request and serves none on this key. The pitch video has a thumbnail and the manual a new part 1 (both pushed by the operator). **The demo recorder no longer deletes a finished recording** (changed about 09:40 PT, before the 10:00 take): it moves it aside as `out-live-motion-kept-[time]`; only an unfinished run is cleared. Its narration needed no change: it names no quote source, and its stage 3 failure passage uses the developer switch, which still shows Retry.

## 20 November 2026, 07:30 PT: the live rehearsal of the demo recorder failed; Cboe refuses the option chain

**What ran.** The scheduled rehearsal ran `data/video/demo/make_demo_motion.py live` once, at 07:30 PT with the market open. All three developer switches were false before and after; `config/test_failures.json` is unchanged; there was no `data/replay_mode.txt`.

**Result: no video.** AMZN, then MSFT, then TGT each stopped at stage 3 with "The live option chain could not be retrieved: Cboe delayed quotes: cboe.chain: HTTP 403". The recorder assembled nothing. Cost $0.26 (29 model calls: stage 2 for the three symbols).

**Cause: the data source, not the recorder.** `https://cdn.cboe.com/api/global/delayed_quotes/options/[SYMBOL].json` now answers 307 to `cdn-api.cboe.com`, which answers 403 with Cloudflare's "Sorry, you have been blocked" page. Seen with curl from this machine, outside the sandbox, for AMZN and SPY, three times between 07:38 and 07:39 PT. Whether the block is on this machine's address or on all automated clients is not known. Stage 1 recovers from this by falling back to the daily snapshot; stage 3 by design has no fallback while the market is open (`stage3.contracts_step` returns `source_failed`), so no request can pass stage 3 during market hours while the block lasts.

**Nothing was changed.** The recorder scripts are untouched: the fault is not in them. No second run was made, since it would fail the same way. Application code, `config/` and tests were not touched. No way round Cloudflare's block was tried.

**A loss to record.** The recorder deletes `out-live-motion/` when it starts, so the output of the live run of 19 November (18 passages, 4 min 59 s, after hours) is gone; it had not been copied elsewhere. The only demo video now on disk is the dry run in `out-dry-motion/` (keyless demo app, 4 min 47 s).

**Also affected.** The daily snapshot job uses the same Cboe address and will probably fail today; a session not logged cannot be reconstructed. The 10:00 PT take will fail in the same way unless Cboe answers again by then.

**For the operator to decide.** (1) Whether the 10:00 take goes ahead (it costs about $0.26 if it fails the same way). (2) If Cboe stays blocked: record after the close on the snapshot (screens show PROVISIONAL, as on 19 November), or have stage 3 changed to use another source or the snapshot during market hours (an application change), or use the dry-run video. **Not checked:** anything past stage 2 on live quotes; the Critic-failure and SPY passages; the audio.

## 20 November 2026 (early): both repositories published by the operator

The operator created a GitHub account and two public repositories and pushed each as a single commit under the account's no-reply address: `github.com/girishirodkar/tradecraft` (the clean copy from `python -m tradecraft.publish`, 146 files) and `github.com/girishirodkar/tradecraft-demo-data` (the demo bundle, 17 files). The author and committer of both commits were checked before the push. `tradecraft.publish` now refreshes the copy in place and keeps its `.git` folder, so later changes are committed and pushed from `data/publish/tradecraft/`. The README and `docs/recorded-demo.md` now carry the real clone addresses, the demo-data link and the manual's GitHub Pages address. GitHub Pages was then switched on by the operator (branch `main`, folder `/docs`) and the manual checked live at `https://girishirodkar.github.io/tradecraft/site/manual.html`: all three parts and the stage tabs load in Chrome, with the stage manuals at full height and holding steady. **Still to do:** add the demo video link; push `docs/.nojekyll` and later changes from `data/publish/tradecraft/`.

## Session of 19 November 2026 (night): the product manual

**On the operator's word:** `docs/site/manual.html`, one self-contained page in the stage pages' theme. Part 1 gives one short chapter per stage and links to the stage pages instead of restating them. Part 2 is the architecture as built, at four levels: 100 (one page for anyone), 200 (components and the path of a request, with a diagram), 300 (each agent's contract and limits, the harness loop, the workflow, the stores, the guardrails), 400 (module map, the request's state, how to add an agent or a check, how the tests stand in for models). It ends with the course's concepts and where each occurs, and what is not built. Chain of Thought is deliberately not claimed.

**Navigation added on the operator's word:** a sidebar listing every section and the sub-sections of levels 300 and 400, with the section on screen marked; on screens under 1,180 pixels it becomes a drawer under a top bar that names the current section; "previous", "next" and "top" at the foot of each main section. **Revised the same night on the operator's layout:** the sidebar has two major rows, "The logic of each stage" and "The architecture", each of which opens and closes; a level's sub-sections appear while the reader is inside it; the stage-page links sit below as a quieter list. The sidebar now shows from 900 pixels wide (it had needed 1,180, which is why the operator did not see it). The four stage pages gained one line at the top linking to the manual and to each other; nothing else in them was changed. Seen at 1,440 and 390 pixels, in both themes, with no sideways scroll.

**A third row, "Detailed stage manuals" (operator's word, the same night).** The four stage pages are shown in full inside the manual, unchanged, each in a frame that the manual sizes to its content. The sidebar lists each page's own sections under it, and a click scrolls to that section. The frames follow the manual's light or dark theme. To make that work each stage page gained a short script at its end that runs only when the page is shown inside the manual (it reports the page's height and sections, takes the theme, and hides the page's own theme button and link line); opened by itself a stage page behaves as before. Part 1's "Full rules" links now go to these sections. Seen at 1,280 pixels in both themes: all four frames sized (11,100 to 21,400 pixels tall), 32 sub-sections listed, a jump into "Filtering and ranking" landing on it with the sidebar marking it. **Not checked:** the embedded manuals on a phone-width screen, and print (the frames are left out of a printed copy, which gives the links to the four pages instead).

**Then made three pages (operator's feedback, the same night).** The operator did not want one long page with a navigation bar to move around it, and could not click anything in the copy shown in the app. The three sidebar rows became three pages with one shared header (meta line, title, introduction, three tabs), identical down to the blue rule: `manual.html` (the logic of each stage), `manual-architecture.html`, `manual-stages.html`. The sidebar, the drawer and the script-built previous and next links are gone. Navigation is now plain links, which work without scripts: the tabs between pages, a row of "On this page" links within a page, and previous-part and next-part links at the foot. The theme chosen on one page carries to the others. On the third page the four stage manuals load without scripts and scroll inside their frames; with scripts each frame grows to the manual's full height. Clicked through in Chrome at 1,280 pixels: each tab, an in-page link, the theme carrying across, all four frames at full height, and a "Full rules" link from part 1 landing on its stage manual; at 390 pixels the tabs stack and nothing scrolls sideways. **The preview inside the Claude app shows a static copy in which links do not work; the manual has to be opened in a browser.**

**Fault found by the operator and fixed: part 3 kept growing.** Each embedded stage manual reported a height taken from its own window, the manual made the frame that tall plus a margin, the frame then reported a larger height, and so on without end. The stage pages now report the height of their content, and only when it changes. Watched for ten seconds and across a window resize: the four frames stay at 10,186, 20,540, 12,127 and 13,600 pixels. (My earlier check had recorded different heights on successive runs and I did not follow it up.) A sidebar was not put back: the operator found the tabs.

**Two consistency fixes (operator, the same night).** On part 3 the "On this page" links and the section headings read "Stage 1: Liquidity gate", "Stage 2: Thesis", "Stage 3: Market and contracts", "Stage 4: Challenge". On each of the four stage pages the strip that marks "this page" showed six stages; it now shows the four that are built ("Decision and record" and "Afterwards" removed). The pages' own text still mentions stage 5 where a rule hands something on to it; that was not changed.

**Part 3 as four tabs (operator's suggestion, the same night).** One stage manual is on screen at a time, chosen by a row of four tabs ("Stage 1 Liquidity gate" to "Stage 4 Challenge") that stays at the top of the window while the manual scrolls. The tabs are plain links and the choice is in the address, so a link from part 1 opens part 3 on the right stage and the browser's Back button moves between stages. Clicked through in Chrome: each tab shows its manual alone at full height (10,098 to 20,452 pixels), heights hold steady, a "Full rules" link from part 1 opens the Challenge tab; at 390 pixels the tabs sit two to a row. A printed copy lists all four.

**The stage strip removed from the four stage pages (operator, the same night):** the row of boxes marking "this page" repeated what the manual's tabs already say.

**Checked:** every one of the 127 file paths and names it gives exists; no script errors; rendered in the light and dark themes at desktop width and at a 390-pixel phone width with no sideways scroll; the three diagrams read in both themes. Linked from `README.md` and listed in `docs/site/THEME.md`. **Not checked:** printing to PDF. **Out of step with the build, and not edited:** `docs/site/challenge.html` predates the operator's 19 rulings on stage 4; `liquidity-gate.html` and `thesis-stage.html` have not been compared with the later rulings. The manual says the decision records govern where they differ.

## Session of 19 November 2026 (night): pitch video and the demo recorder

**Operator decisions:** the pitch and the demo are narrated by a macOS voice, Nathan (Enhanced); the operator records the presentation separately and appends the demo; 10 minutes in total, about 4 for the demo; the demo is built on live data on 20 November at 10:00 PT. `imageio-ffmpeg` 0.8.1 (22.6 MB) was installed as a development dependency on the operator's approval.

| Piece | Where (all under `data/video/`, git-ignored) | State |
|---|---|---|
| Pitch video, first cut | `pitch/tradecraft-pitch.mp4`; rebuild with `pitch/build.py` | 1 min 22 s, full HD, the approved 225-word script. Frames from the replay app on MSFT, captured with headless Chrome on a throwaway profile. The agents-working frame and the Home frame were stand-ins and **were replaced on 20 November** with frames of the real screens from the live recording of 19 November (AMZN); the other screens are still MSFT from the replay app, and the thesis frame shows replay artefacts. **Published on 20 November as `docs/media/tradecraft-pitch.mp4` (7.8 MB) and linked from the README** |
| Manual, part 1 added (20 November) | `docs/site/manual.html`, `manual-logic.html` | The manual is four pages: **What is Tradecraft** (new; `manual.html`, so the published link opens on it), the logic of each stage (moved to `manual-logic.html`), the architecture, the stage manuals. Part 1 holds the pitch video, the stage diagram and "Why it is built this way" (both moved from the logic page). By operator decision it has no recorded-demo section and no status-and-limits section, and text on all four pages runs the full column width |
| Demo recorder | `demo/make_demo.py dry` or `live` | Drives the app's own screens in headless Chrome over its debugging protocol (clicks, folds, full-page captures), writes the narration from what the run returned, speaks it and assembles the video. `live` uses its own fresh database, `data/demo-recording.sqlite3`; the permanent record is not touched |
| Dry run (deleted 19 November, night, on the operator's word: superseded by the live-action runs) | `demo/out-dry/tradecraft-demo.mp4` | 3 min 21 s on the keyless demo app: AMZN (bearish, bear call spread) through all four stages, NVDA for the no-view path. Frames checked on a contact sheet. The audio was not heard by the session |
| Scheduled | Task "tradecraft-live-demo-video", once, 20 November 10:00 PT, saved in Auto mode | Runs `make_demo.py live`, checks the result and reports. **The live path has not been run:** only the dry run has |

**Extended the same night (operator's instruction: 5 to 6 minutes, every path in each stage).** The recorder now also shows: the criteria tightened until the gate fails, the override panel and a reset; a failed option-data source with Retry; ranking, the cost cap tightened and an expiration switched and switched back; the Critic made to fail once with Retry (live only); a return to contracts, a second selection and a second challenge; a thesis the user enters, frozen and taken through contracts and the challenge; and an index instrument's no view by rule (live only, SPY). It turns `option_chain_fail_once` and `critic_fail_once` on for a few seconds each and restores `config/test_failures.json` exactly; TEST FAILURE ON shows on those two screens, and the narration says a developer switch is in use. The second dry run: 16 passages, about 4 min 27 s; the switches file was unchanged afterwards. A full live run has 18 passages. The scheduled task's instructions were updated to match; expected cost $0.70 to $1.00.

**A second request in the other direction (operator's instruction, the same night).** After the main run the recorder looks for a symbol whose view on the day's live data is the direction the main run did not return: bullish if the main run is bearish (MSFT, then TGT, CSCO, AAPL), bearish otherwise (AMZN, GOOGL, JPM). Each probe runs the gate and stage 2 (about $0.09); the first match goes on through contracts and the challenge and gets one short passage; a symbol that does not match is rejected and left out. Third dry run, with MSFT as the bullish example: 17 passages, about 4 min 44 s. A full live run has 19.

**Live action in place of stills (operator's instruction, after the first cuts).** `data/video/demo/make_demo_motion.py` records what the page draws while it operates the app: a cursor that moves, typing, click marks, slider drags, smooth scrolling, and the agents' panels as a time-lapse. Each passage's narration is generated before its action so the action is paced to the words, and each passage is muxed with its own narration at exactly the same length. Dry run: 17 passages, 4 min 47 s, picture and voice the same length. The operator has heard the Nathan voice and accepts it. The scheduled task now runs this recorder; the still-frame one, `make_demo.py`, is its fallback.

**The stage 4 as-built table was accepted in full by the operator (19 November, night),** with two rows corrected first (what context the Critic receives; the passage count). Recorded in the decision record.

**The first live run of the recorder (operator, the same night, market closed): 18 of 19 passages, 4 min 59 s, $0.75.** AMZN bearish through every path, with the real agents' panels, the failed data source and the Critic failure each recovered by Retry; MSFT returned bullish and became the second request; NVDA returned no view (conflict) and the operator-thesis path ran through contracts and the challenge. The switches file was unchanged afterwards. Because the market was closed the screens show PROVISIONAL. **The SPY passage was dropped, and that exposed a fault in the app:** after "Take a view yourself" was used in one request, the next request that returned no view opened straight on the "Take a view yourself" screen instead of the brief. Fixed in `app.js` (a new request clears that state); shown by running two no-view requests in a row on the keyless app. 373 tests pass. Not yet seen: SPY's passage in a recording, and any of this with the market open.

**Not in the demo video:** the Retriever's silent recovery from a failed source in stage 2 (there is no trace viewer to show it), a stage 2 failure with Retry, a rejected Critic output, the market-closed and provisional states, and a range-bound thesis. The demo narration is a draft the operator has not yet approved.

## Session of 19 November 2026 (evening): the README and the copy to publish

**On the operator's word.** `README.md` is rewritten for the evaluators (what Tradecraft is, the keyless demo, tests, a live run, where each graded requirement is in the code, safety, limits, what is left out). The census text it replaced is `docs/liquidity-census.md`. It has two placeholders: the demo video link and the demo-data repository link.

`python -m tradecraft.publish` writes a fresh copy of the last commit, with no history, to `data/publish/tradecraft/` and runs the checks of build plan section 12; any failure stops it.

| Left out of the copy | Why |
|---|---|
| `logs/` (4 files) | They hold this machine's folder paths and user name |
| `ops/` (5 files) | The scheduled job's machine-specific files, with the operator's name |
| `ladder_out/` (5 files) | Daily output derived from third-party option quotes |
| `universe.txt.pre-mode1` | A superseded working file |

**Checks, all passed on the copy (143 files, 3.9 MB):** no value from `.env`; no home-folder path; no email address; the operator's name nowhere (read from git's settings and the home folder's name); no `data/`, `snapshots/`, `label_out/` or `.env`; `.env.example` empty. `scripts/README.md` named the scheduled job's file, which carries the operator's first name; reworded.

**Tested inside the copy,** with no `.env` and the network blocked: 372 tests passed and one failed, `test_real_pool_reads_only_single_stocks`, which reads the unpublished price archive; it now skips when the archive is absent. With the bundle copied in, the keyless demo walked AMZN, MSFT and NVDA as before.

**Not done, and the operator's:** creating the two remote repositories, committing under the hosting service's no-reply address and pushing (the tool prints the commands); filling the README's two links. **Not checked:** `uv sync` on a machine without the project's `.venv`; the history of the working repository was not scanned, because it is not published.

**Re-run `python -m tradecraft.publish` after any further commit:** the copy is of the commit it was made from.

## Session of 19 November 2026 (evening): the recorded demo for evaluators

**Operator decision:** the evaluators get the main repository and a second, small, public repository of demo data, so that the replay works with no keys; neither may expose a secret.

| Part | Where | State |
|---|---|---|
| The keyless app | `tradecraft/demo.py` (`tradecraft.demo:app`, port 8324) | Built. The replay app fed only from `data/demo-bundle/`: "today" is the snapshot's date, the market is treated as closed, no source on the network is asked. Every page carries RECORDED DEMO with the date of the data |
| The bundle | `data/demo-bundle/` (git-ignored here; to be its own repository) | Built for AMZN, MSFT and NVDA: 3.1 MB. One snapshot cut to three symbols (6,824 rows), three price histories, three saved thesis runs with the fetched text removed, dividend dates, the symbol list |
| Recording | `python -m tradecraft.demo record AMZN MSFT` | Made once, live: six selections (three strategies each), **$0.61 in total**; every Critic answer passed first time ($0.09 to $0.11 each); retrieval on chromadb. Spend went to `data/demo.sqlite3` |
| Secrets scan | `python -m tradecraft.demo scan` | Clean: no value from `.env`, no home-folder path, no email address in any file of the bundle. One test plants each and checks the scan finds it |
| Instructions | `docs/recorded-demo.md`; a pointer at the top of `README.md` | Written |

**Checked on a clean copy:** the committed files only (`git archive`), no `.env`, no `snapshots/`, no `label_out/`, no embedding model, the network blocked, with the bundle copied in. All three symbols walked through the API: AMZN and MSFT reached the challenge with the Critic's output for each of the three strategies; NVDA returned no view and offered "Take a view yourself".

**Not checked:** the demo app in a browser (its launch entry could not be added to `.claude/launch.json` from the session, which is protected; the command in `docs/recorded-demo.md` starts it); a real `git clone` and `uv sync` on another machine; the RECORDED DEMO marker on screen.

**Still the operator's:** creating both remote repositories and pushing (build plan, section 12). The bundle folder has not been made a git repository, so no commit carries the operator's email. The bundle publishes a small sample of third-party data (Cboe quotes, Yahoo prices, FMP-derived figures, filing-based findings); its README says so. The full README for evaluators is still to be written.

## Session of 19 November 2026 (late afternoon): stage 4 built

### Where it stopped

**Stage 4 (the challenge) is built, tested, checked on the replay app and run live once through the real app, all four stages, on AMZN ($0.20; below).** Its two agents were also run live once on MSFT, outside the app. 370 tests pass (52 new). Nothing pushed.

### Operator decisions

Eighteen, ruled one by one before any code was written. The list is in `docs/decisions/2026-11-17-stage-4-challenge.md`, "Operator decisions for the build"; what they change on screen is in `docs/product-shell.md` 6.4. The largest: the Critic's output check runs on the harness with one return in total; C11 uses stage 4's own fetch of the chain; two rejected-signal patterns were tightened (the file is shared with stage 2; the change can only remove false refusals there); check 4 reads any finding carrying the opposite direction; check 9 is withheld from the Critic; each case is at most 90 words; a third developer switch, `critic_fail_once`.

### What was built

| Part | Where | State |
|---|---|---|
| Research index | `tradecraft/research.py`; `config/stage4.json`; index in `data/research-index/` (19 MB), model in `data/embedding-model/` (168 MB unpacked) | Built. chromadb 1.5.9 with its default local model, all-MiniLM-L6-v2: 1,406 passages from 30 files, built in 11 seconds. **Method in use: chromadb.** Keyword search over the same passages is the fallback and is what the tests use. Rebuild with `.venv/bin/python -m tradecraft.research build` after the corpus changes; an out-of-date index falls back to keyword search and says so in the record |
| Both checklists, the question, the fresh quotes, readiness | `tradecraft/stage4.py` | Built. All 23 checks run; none is a stub |
| Retrieval | `stage4.passages_step`, the Evidence Retriever's second configuration with one tool, `search_research` | Built |
| The Critic and its output check | `stage4.critic_step`, `stage4.output_check`, `stage4.no_verdict` | Built. Opus 5.5, no tools, 4,000-token cap |
| Workflow | `tradecraft/workflow/graph.py` | The `critic_check` node reports the harness's check (`in_harness`); the challenge record carries the passages, the output check and the model; a stage 4 panel in `progress4` |
| Screen | `index.html`, `app.js`; mock-up changed first for the working panel and the "More detail" fold | Built. `tradecraft.css` is unchanged: no new style was needed |
| Replay | `tradecraft/dev_replay.py` | Stage 4's code runs for real; the two agents are served from `data/stage4-saved/`. New words for `data/replay_mode.txt`: "critic_fail", "critic_reject", "nopassages" |
| Developer switch | `config/test_failures.json`, `critic_fail_once` (false) | Built and tested; not seen in the browser |

### The rejected-signal patterns, before and after

Across the 49 saved runs (1,022 texts). Before: the price-trend pattern matched 61 texts, 19 of them thesis texts for "over 30 days"; "61.8" matched CVX's "$61.82B" three times. After: 43 matches, of which 40 are the Regime Assessor's and Technical Analyst's descriptions ("below its 200-day average"), which check 1 does not read; one thesis text; none on CVX. Still matching by design: "Volatility is elevated" (PYPL's tempering text, which check 1 does not read), and "momentum", "moving average" and "non-accrual" in three context findings.

### Live, once: stage 4's two agents on MSFT ($0.23)

Run on the state of a replayed MSFT request (bullish, bull put spread 470 / 500, 18 December), outside the app. Spend and trace went to `data/replay.sqlite3`; nothing reached the permanent record.

| Agent | Result | Cost |
|---|---|---|
| Evidence Retriever | 3 model calls, 4 searches (each of the two topics searched twice), 11 seconds. One passage for the earnings claim; three for and three against for the strategy | $0.005 |
| Critic | 2 model calls, 47 seconds. The first answer was returned once: "The case against is 92 words; the limit is 90." The second passed | $0.226 |

The Critic gave five objections, three loss paths, one standing ("narrower form"), and named four missing inputs, each citing ids that exist. It gave no verdict. After this run its instructions were changed to aim for about 72 words a case and to keep ids out of its sentences; **neither change has been seen on a live run.**

### Live through the real app, once: AMZN, all four stages ($0.20)

Made on the operator's word, after the close (19:26 PT), so the gate and the contracts ran on the snapshot. **It wrote to the permanent record** (request `req_d836a66df3ca`): eight decision records, from `gate_pass` to `challenge_proceed`. About two minutes from start to "Proceed to decision".

| Stage | Result | Cost |
|---|---|---|
| 1 | PASS on the snapshot, provisional | none |
| 2 | Bearish, weakly supported (the earnings result alone) | $0.092 (Thesis agent $0.078, the four Haiku agents $0.014) |
| 3 | 18 December; bear call spread 260 / 285 (1.8% of max loss), bear put spread, long put; all kept. The first was selected | none |
| 4 | READY, "13 items for your judgement". Thesis: 7 flagged, 1 not checked, 4 passed. Contract: 4 flagged, 1 not checked, 6 passed | $0.109 (Critic $0.104, Evidence Retriever $0.005) |

- **The Critic passed its output check on the first answer** (one model call), with the instruction to aim under the word limit in force. Five objections, three loss paths, one claim "narrower form". "Bear case" came first, as the wording rule asks for a bearish thesis. No id appeared in a sentence.
- **The working panel showed real statuses:** Evidence Retriever WORKING then DONE, Critic WORKING, Output check WAITING.
- **Market closed:** check 11 and C11 read "could not be checked", check 10 was flagged for provisional data, and the readiness line said why. So C11 and check 11 have still not been seen with live quotes through the real app (they were on the replay app).
- **Retrieval used keyword search, not chromadb, on this run.** The index had been built before this session's edits to the decision records, which are part of the corpus, so it was out of date and the fallback took over, as designed; the record says "keyword" and why. Four passages were kept. **The index was rebuilt afterwards. Any edit under `docs/research/`, `docs/decisions/` or to `docs/factor-spec.md` puts stage 4 back on keyword search until `python -m tradecraft.research build` is run.**
- The day's spend stood at $5.36 of the $10 daily limit after this run.

### The index is brought up to date at start (operator decision, 19 November, evening)

Built after the AMZN run showed the trap: `research.ensure_current()` runs once when the real app or the replay app starts, rebuilds the index if a corpus file has changed, and prints one line saying which method is in use. Two tests (372 pass). With no embedding model on disk it does not download one; it starts on keyword search and prints the build command. **Seen once:** the real app was started straight after the decision record was edited, and its log read "Research index: rebuilt, chromadb, 1,411 passages." before the server came up. Not seen: a start with no model on disk, and a stage 4 run through the app after such a rebuild.

### Checked in the browser (replay app, port 8322)

| State | Seen |
|---|---|
| The challenge with the Critic's output (MSFT, saved run) | Header, READY with "9 items for your judgement", the same-model caution, bull case, bear case, three loss paths, five objections with their grounds, both check boxes, the three buttons |
| "N passed" folds and "More detail" | Open and close; notes and the claim's standing, priced-in reading, missing inputs and passages are listed |
| Critic failure | "The Critic timed out after 180 seconds", the three-row panel, Retry, "Continue with the checklists only", "Return to contracts", Stop. Retry ran the Critic and kept the checklists |
| Checklists only | NOT READY, "1 blocking condition.", one line in the Critic's column |
| Rejected output | NOT READY and the 6.4 line; the rejected output is not in what the page receives |
| No passages | The grey line under the caution |
| Market closed | C11 and check 11 "could not be checked"; check 10 flagged for provisional data; the readiness sentence says why |
| A thesis the user entered (NVDA, bearish) | "Your thesis, 30-day horizon"; check 9 flagged with the verdict; check 4 flagged on the finding standing against it; the question does not say whose thesis it is |
| After "Proceed to decision" | The end panel; all four stages reviewable and read-only, which also re-checked the gate, thesis and contracts screens after the script changed; Home lists "Bull put spread · Proceeded to decision" |
| Dark theme, and 375 pixels wide | Rendered; the two columns stack with no sideways scroll |

**Not checked:** stage 4 live through the real app with the market open (C11 and check 11 on live quotes); chromadb retrieval through the real app (the MSFT run outside the app used it); `critic_fail_once` in the browser; iron condors (not in the demo).

### What the runs showed, for the operator

The three items are in the decision record, "Seen on the build's runs": the Critic costs about $0.11 a call and its one return doubled that; active volatility flags check 12 and C2 on most names today; the replayed Critic text quotes its own run's figures.

**A copy of the app was still running on port 8321** when this session tried to start one; the new copy was given 8323 and stopped again. The old copy has no stage 4 until it is restarted.

## Session of 19 November 2026 (afternoon): stage 3 built

### Where it stopped

**Stage 3 (market and contracts) is built, tested and run live on five symbols.** Stage 4 is not started; its page is still the marked placeholder. 314 tests pass. Nothing pushed.

### Two operator decisions at the start of the session

- **Stage 2's rules are frozen as of 19 November 2026.** Recorded at the top of `docs/decisions/2026-11-18-stage-2-anchored-bearings.md` and in `CLAUDE.md`. What a run shows about stage 2 goes on the "After the demo" list below and is not changed, unless it stops a run from finishing or makes a screen show something false; then the build session stops and asks.
- **The 22 stage 3 gaps were ruled on.** The list is in `docs/decisions/2026-11-17-stage-3-contract-selection.md`, "Operator decisions for the build"; what they change on screen is in `docs/product-shell.md` 6.3. The largest: legs leave out the DTE criterion; there is no override in stage 3; events are shown and not filtered; the levels are the 60-day closing high and low; "before slippage" and "approximate" on the three chance figures.

### What was built

| Part | Where | State |
|---|---|---|
| Implied volatility and Greeks on each contract | `tradecraft/data/chain.py` | Built. Field names checked against the live Cboe feed |
| The engine: eligibility, expirations, candidates, payoff, the two history figures with the pool, implied POP and move, cost cap, ranking | `tradecraft/stage3.py` | Built, 29 tests (`tests/test_stage3.py`). One test reproduces the mock-up's EXMP figures |
| The workflow step and the four outcomes | `stage3.contracts_step`, `tradecraft/workflow/graph.py` | Built. The stage 3 override is removed; an update is recorded as a user decision; Retry and "Return to contracts" fetch the chain again; the selection record carries the candidate, the contracts proposed and the candidates not selected |
| The screen | `tradecraft/web/static/index.html`, `app.js` | Built. The mock-up was changed first for the decisions it could show (events line, filters chip, tile labels, 60-day labels) |
| The stage 1 override panel's added sentence | `index.html` | Built. **Not seen in the browser** |
| Development-only replay | `tradecraft/dev_replay.py`, the `tradecraft-replay` entry in `.claude/launch.json` | Stage 2 replayed from the outputs saved on 19 November, on `data/replay.sqlite3`. A build tool, by operator decision; not a product feature |

### Checked in the browser

On the replay app (no model call): MSFT (bullish), AMZN (bearish), NVDA and SPY on a user thesis, and a gate fail with an override leading to "No candidate built: no eligible contracts at your criteria." On MSFT: the three rankings, the max-loss field (recorded when it loses focus), switching expiration with its horizon amendment, a filtered-out row and its detail, Continue, the placeholder for stage 4, the read-only review, and a narrow width. The gate and thesis screens were re-checked after the script changed.

**Live through the real app, once each, $0.37 in total:** MSFT $0.076, AMZN $0.092, NVDA $0.065, TGT $0.092, SPY $0.047. **All five wrote to the permanent record.**

| Symbol | Stage 2 | Stage 3 |
|---|---|---|
| MSFT | Bullish, weakly supported | 15 January (57 DTE). Bull put spread 460 / 505 and long call 505 kept; bull put spread 505 / 550 filtered (8.6% of max loss). Selected and continued; Home lists "Bull put spread" |
| AMZN | Bearish, weakly supported | 15 January. Bear call spread 260 / 280 and long put 260 kept; bear put spread 240 / 260 filtered (5.2%) |
| NVDA | No view, then a bearish user thesis | 24 December (35 DTE). Three candidates kept |
| TGT | Bullish (it passed the gate on live data: 8 contracts) | 15 January. Three candidates kept; the first was at exactly 5.0% |
| SPY | No view, then a bullish user thesis | 24 December. Three candidates kept |

**Not checked:** the market-closed and provisional states, the source-failure state with Retry, and "no eligible expiration serves the horizon" (engine tests only); the dark theme (one capture, taken mid-transition); iron condors on a screen; the stage 1 override panel's new sentence; a row marked for earnings before expiration (no test symbol reports before its expiration).

### How often candidates are filtered for cost (build plan, section 7)

Stage 3 was run over the 33 directional views saved from the 19 November runs, on live chains at about 12:40 ET, at default criteria. No model call; nothing recorded. Script and output: `data/runs-2026-11-19/stage3_cost_count.py` and `.json` (git-ignored).

| Cost cap | Candidates over it | Symbols losing at least one | Symbols left with none |
|---|---|---|---|
| 2% | 54 of 72 | 31 of 33 | 17 |
| 5% (default) | 35 of 72 | 27 of 33 | 6 |
| 10% | 15 of 72 | 13 of 33 | 4 |

- At 5%: 17 of 24 "hold" spreads and 18 of 22 "move" spreads are over the cap; no single option is (0 of 26).
- 21 shapes could not be built at all for want of an eligible strike, and two symbols (GS, PYPL) had nothing eligible.
- On the four test symbols, live: MSFT and AMZN each lost one spread; TGT and NVDA lost none.
- **So filtering for cost happens on the symbols to be recorded.** By the plan's test the on-screen cost-cap control is worth building; the decision is the operator's.

**The operator decided the same afternoon: build the control.** Built: a slider beside the filters (2% to 10%, steps of 0.5, default 5%), drawn in the mock-up first. Checked on the replay app: on MSFT, 2% filtered the spread and 5% restored it; on VZ, whose one candidate was at 9.1%, the screen read "No candidate is left", kept the slider, and 10% brought the candidate back with Continue. One test added (311 pass). Not checked: the control on a live run through the real app; the sentence "Raising the cost cap, or switching expiration, rebuilds the candidates.", added after the check. The slider, its step and applying on release are the build's choices.

### What the runs showed, for the operator to rule on

1. **The 30-day horizon usually misses the monthly expiration.** The rule is "the nearest eligible expiration on or after the horizon date". On 19 November the 18 December monthly is 29 DTE, so it does not serve a 30-day thesis: MSFT, AMZN and TGT were given 15 January (57 DTE, "27 days beyond it"); NVDA and SPY have a 24 December weekly. For AMZN the 18 December expiration is not offered at all.
2. **The far strike is often pulled in, and the kept construction is often the dearer one.** Out-of-the-money options a typical move away tend to fail the 5% spread criterion, so the far strike moves in, or only the construction built from in-the-money options is eligible. MSFT's bull put spread 505 / 550 is an example. This is why most spreads are over the cap.
3. **SPY's long call was at 731 with spot at 720.27:** no call nearer the price was eligible on the 24 December expiration.
4. **A second copy of the app was already running on port 8321,** so the check ran on 8323. Two copies share one database; the older copy has no stage 3 until it is restarted.

### The operator's rulings on those items, and the re-run (19 November, afternoon)

Rulings 1 to 3 are in `docs/decisions/2026-11-17-stage-3-contract-selection.md` ("Operator rulings on what the first runs showed") and the amendment to `docs/decisions/2026-11-15-liquidity-controls.md`. Built, with four tests (314 pass). Also built on the operator's word: filtered-out rows carry a FILTERED label in place of a rank.

**Stage 3 re-run on the tested symbols,** engine only, live chains at 12:53 ET, default criteria, 30-day horizon, the views of the day's live runs. No model call; nothing recorded. Script: `data/runs-2026-11-19/stage3_rerun_tested.py`.

| Symbol | Expiration | Built | Kept | Over the 5% cost cap | Not built |
|---|---|---|---|---|---|
| MSFT (bullish) | 18 December, 29 DTE, 1 day before the horizon date | 3 | 3 | 0 | 0 |
| AMZN (bearish) | 18 December | 3 | 3 | 0 | 0 |
| NVDA (bearish, user thesis) | 18 December | 3 | 3 | 0 | 0 |
| TGT (bullish) | 18 December | 3 | 3 | 0 | 0 |
| SPY (bullish, user thesis) | 18 December | 3 | 3 | 0 | 0 |
| VZ (bullish; tested on the replay app) | 18 December | 3 | 3 | 0 | 0 |

Before the rulings the live runs gave MSFT 3 built and 1 over the cap, AMZN 3 and 1, NVDA 3 and 0, TGT 3 and 0, SPY 3 and 0, VZ 1 and 1, all but NVDA and SPY on the 15 January expiration. The kept construction is now the cheaper one in every spread (for example MSFT's bull put spread 480 / 510 at 2.7% of max loss against 5.8% for the call construction). SPY's long call is at 724 with spot at 724.39.

**The 33 saved views again, same script as before, about 12:55 ET:** 86 candidates built (72 before), 13 shapes not built (21). Over the cap: 60 of 86 at 2%, **27 of 86 at 5%** (35 of 72 before), 13 of 86 at 10%. Symbols left with none at 5%: 8 (6 before). At 5%: 9 of 31 "hold" spreads, 18 of 33 "move" spreads and 0 of 22 single options. The two counts were taken about 15 minutes apart on different expirations (mostly 29 DTE now, 57 DTE before), so they are not a like-for-like comparison.

**Checked on the replay app (VZ):** "Matches the 30-day horizon · 1 day before it"; the wide-leg sentence under three legs; "The strike, 46, is 1.4% above spot." Not checked on a live run through the real app.

**Ruling 4, NVDA: neither; the earlier note in this log was wrong.** All four NVDA runs recorded on 19 November (00:20, 00:50, 08:35 and 09:34 PT) returned no view with the reason code "conflict", on the same two bearing-carrying findings: results above estimates (bullish, moderate) and the chief executive's departure with no permanent successor (bearish, strong). The build session had read the field `thesis.kind`, which says "nothing_found" in all four records, in place of `no_view_reason_code`. The screen reads the reason code. The context findings did vary between runs (the Hugging Face acquisition appears in three, the buyback in two); the outcome did not. `thesis.kind` disagreeing with the reason code is on the list below; it was not looked into further.

### The remaining stage 3 states checked (19 November, afternoon)

The operator confirmed three as-built points (strike distance on every leg; the nearest allowed expiration in calendar days, a tie going to the one on or after; the wide-leg sentence under its leg's row), recorded in the stage 3 decision record.

To see states that cannot be had on demand, the replay app gained a switch (`data/replay_mode.txt`: "closed", "nosnap", "fail"), read on every call. A build tool; the real app is not touched. Seen on the replay app, on MSFT:

| State | What the screen showed |
|---|---|
| Market closed, symbol in the snapshot | The PROVISIONAL chip; "quotes 14:00 ET, 18 November"; "Snapshot of 18 November, 14:00 ET · market closed. Provisional: every figure is from the latest snapshot, not from live quotes."; three candidates; Continue available |
| Market open, live chain fails | "The option data could not be retrieved." with "Source that failed: Cboe delayed quotes (live option chain)."; Retry and Stop; after three retries, Stop only |
| Market closed, no snapshot | "Contracts cannot be chosen until the market opens." and the stage 1 sentence; Stop only |
| Stage 1 override panel | The added sentence, under the rationale box |
| Dark theme | The header, expiration cards, slider, rows, payoff chart and detail |

**One live run through the real app under the new rules: AMZN, $0.084.** Bearish; 18 December, "1 day before it"; three candidates kept, none over the cap; a wide-leg sentence on one leg of each spread; "The strike, 265, is 0.5% above spot." It wrote to the permanent record (stopped at contracts).

**Not seen in the browser:** iron condors: **not in the demo** (range-bound is engine-only for the demo, operator decision, 19 November 2026).

**Earnings before expiration, seen (operator's instruction, 19 November).** On the replay app, MSFT switched to the 19 February expiration, which falls after its 27 January report. The dates line read "Next earnings report: 27 January, before this expiration."; all three rows carried "Earnings report before expiration (27 January)."; the detail's checks read "Earnings before expiration: Yes, 27 January". The two spreads also carried the ex-dividend marker.

**Developer-only test failures (operator's instruction, 19 November).** Two switches in `config/test_failures.json`, **both false by default**, each making one source fail once per request so that a recovery can be shown. The file is read on every use, so no restart is needed. `tradecraft/testfail.py`.

| Switch | What it does | What was seen |
|---|---|---|
| `option_chain_fail_once` | Stage 3's first fetch of the option chain fails | Replay app, MSFT: "The option data could not be retrieved." with "Source that failed: Cboe delayed quotes (live option chain)" and a message naming the switch; Retry succeeded and built three candidates. Decision records, in order: `contracts_source_failed` (system, marked `test_failure`), `retry` (user, attempt 1, with the source and message), `contracts_ok` |
| `stage2_source_fail_once` | The first call to one stage 2 data tool fails (`stage2_source_tool`, set to `list_filings`); the harness retries a failing tool once | One live run through the real app, MSFT, $0.156: the Evidence Retriever's trace shows `tool_call` list_filings, `tool_error` attempt 1 naming the switch, then `tool_result` available. The run finished as usual (bullish, weakly supported) and was rejected at the thesis; it is in the permanent record |

- **So that neither is left on by accident:** while either is true, every page shows **TEST FAILURE ON** in its header (seen with each switch on, and gone with both off), the failure's message names the switch, and a test fails if either is true in the repository.
- **To show a recovery in the demo:** set the switch to true, run the request, then set it back to false. Each fires once per request.
- A Retry in stage 3 is now written to the decision record as a user decision (it was not recorded before).
- The $0.156 is about double a usual run; why was not looked into.

**The design documents brought up to date (19 November, afternoon).** The "Stage 3 redesigned" section of `docs/on-demand-mode-design.md` now opens with a table of the rules in force, and the lines it contradicts are marked as amended. `docs/site/market-contracts.html` was revised throughout (leg criteria, expiration rule, events shown and not filtered, the on-screen cost cap, the 60-day high and low, the approximate and before-trading-cost labels, data gaps, implementation status). Both it and the mock-up were loaded in a browser afterwards with no script errors; the mock-up's cost-cap slider was exercised at 2%, 3% and 10%.

**Stage 2's horizon rows against what stage 3 served, on the day's live runs.** On MSFT and TGT stage 2 marked the 7- and 14-day rows "no eligible contracts" while stage 3 offered an expiration for each (TGT's 60- and 90-day rows were set aside by stage 2 and not served by stage 3 either). The 30-day row was recommended on all five symbols, so no recommended horizon was affected. AMZN, NVDA and SPY showed no difference. The item is on the list below.

### The as-built table accepted; the slider moved; the shortlist (19 November, afternoon)

**Operator rulings,** recorded in the stage 3 decision record: every row of the as-built table is accepted, with three notes (what "eligible" means for an expiration; differing far strikes take the pair nearest the target, a tie going to the cheaper, and the other construction reads "Not available at these strikes."; the pooled figure is the average of each stock's own share, read that way deliberately). The cost-cap slider sits in the filters row in place of the static label. SPY and AMZN stay as demo symbols.

Built: the tie rule and the new wording, with a test (318 pass); the slider moved, mock-up first. Checked on the replay app: the slider in the filters row with no static label (CSCO), and "Equivalent construction. Not available at these strikes." (TGT).

**The shortlist on the snapshot of 19 November (11:00 PT), default settings, 30-day horizon.** Engine only: no model call, nothing recorded. Script: `data/runs-2026-11-19/shortlist.py`. The views are those of the 19 November runs; NVDA and SPY return no view, so they are given the user thesis used in the checks. Every symbol's expiration is 18 December (29 DTE, one day before the horizon date).

| Symbol | Stage 1 gate at default | View used | Built | Kept | Filtered for cost | Not built |
|---|---|---|---|---|---|---|
| TGT | PASS, 2 contracts | Bullish | 3 | 3 | 0 | 0 |
| CSCO | PASS, 4 | Bullish | 3 | 1 (long call) | 2 (9.0%, 7.4%) | 0 |
| PYPL | PASS, 3 | Bullish | 2 | 1 (bull put spread, 4.7%) | 1 (6.3%) | 1 (long call) |
| AMZN | PASS, 18 | Bearish | 3 | 3 | 0 | 0 |
| GOOGL | PASS, 12 | Bearish | 3 | 2 | 1 (6.8%) | 0 |
| MSFT | PASS, 33 | Bullish | 3 | 3 | 0 | 0 |
| NVDA | PASS, 23 | Bearish (user thesis) | 3 | 3 | 0 | 0 |
| SPY | PASS, 429 | Bullish (user thesis) | 3 | 2 | 1 (5.9%) | 0 |

- **All eight pass the gate on this snapshot.** TGT, CSCO and PYPL failed it on the 18 November snapshot; TGT passes with exactly the minimum of two contracts.
- **CSCO is fragile.** On the live chain 34 minutes later (14:34 ET, replay app) both of its spreads were over even a 10% cap (10.3% and 13.1%) and the long call was not built: no candidate at any setting of the slider.
- PYPL's saved view predates the guidance rules; recomputed in code it is a no view (earlier table), so in the demo it would need a user thesis.
- SPY's filtered spread is the put construction 721 / 749, kept because its far strike was nearer the target than the call construction's.

### After the demo

- **Stage 2's horizon rule and stage 3's leg rules use different tests (operator, 19 November 2026; stage 2 stays frozen).** Stage 2 counts contracts that pass the bid-ask criterion and expire on or after the horizon date; stage 3 judges spread legs on the whole structure and accepts an expiration up to three sessions earlier. On a thin name stage 2 can set aside a horizon that stage 3 could serve. Fix with one shared definition of a horizon that can be served.
- **Stage 2 (frozen; recorded, not changed):** on a no view by conflict the record's `thesis.kind` reads "nothing_found" while `no_view_reason_code` reads "conflict" (NVDA, four runs). No screen reads `kind`.
- **Replay artefact, not a fault:** a replayed brief shows "Latest report: not available", because the saved outputs predate that field.

## Session of 18 November 2026 (evening and night)

### Where it stopped

**Stage 2 runs live end to end on its own screens** (built 19 November; see "Stage 2 screens built"). The one re-run of the six symbols has been made (below), and nothing in stage 2's rules is to be adjusted on it.

### The 43-symbol run (19 November 2026; item 9; made once, nothing adjusted)

The other 43 covered symbols, run live two at a time through stage 2's steps (not through the app, so nothing was written to the permanent record). About 17 minutes; cost $3.24.

| Outcome | Count | Symbols |
|---|---|---|
| Bullish, weakly supported (the earnings result alone) | 15 | AAPL META TSLA AMD INTC GS V XOM CVX KO DIS UBER COIN SHOP RIOT |
| Bullish, resting on more than the result | 7 | CSCO VZ F RIVN PLTR PYPL SOFI |
| Bearish, weakly supported | 2 | BAC BA |
| Bearish, resting on more than the result | 3 | GOOGL ADBE HOOD |
| No view: the findings conflict | 10 | NFLX UNH JNJ PFE ABBV NKE SBUX GE LMT GM |
| No view: nothing carries a direction | 3 | SPY (an index: by decision), WFC and COST (results mixed against estimates) |
| Did not finish: a technical failure, not a no view | 3 | C PEP T |

**Totals: 27 views (22 bullish, 5 bearish; 17 of them weakly supported), 13 no views, 3 that did not finish.** With the six symbols of the earlier re-run: 31 views, 15 no views and 3 unfinished out of 49.

- Every one of the 10 conflicts is results above estimates against guidance below consensus (GE, LMT and GM also have guidance findings pointing higher).
- 17 of the 27 views rest on the earnings result alone.
- No draft failed the validation check twice. Three drafts were returned once and then passed.
- One reply was cut off at an output limit (the Regime Assessor, at 1,500 tokens). The Thesis agent used at most 2,497 tokens, under its new limit of 4,000.
- 12 of the 43 symbols fail the stage 1 gate at default settings on the snapshot; stage 2 was run on them regardless, as for TGT.

**Faults the run showed.** None was fixed at the time. The operator ruled on all four later the same day; see "Rulings on the four faults" below.

1. **The three unfinished runs are a build fault.** The Regime Assessor reported a scheduled macro release as a "new event" with a kind of its own ("macro_calendar"); the output check refused it (18 times across 15 symbols) and returned the answer. On C, PEP and T the second answer came back empty and the stage stopped. The check for event kinds was written for the Fundamental Analyst; code already sets every Regime Assessor finding to context.
2. **INTC's result is probably wrong.** Intel's $23 billion public equity offering was refused as a rejected signal because the sentence contained "to support" (the support-and-resistance pattern), so it was reported as context. A share offering is a listed bearish event; with it, INTC would be a conflict and a no view, not a weakly supported bullish view.
3. **ADBE's bearish view rests on guidance that is in effect in line.** Its EPS target of $24.45 to $24.50 was read as below a consensus of $24.48, and its revenue target likewise. This is the case left open after ruling 3: a guided range that contains the consensus figure. The 1% tolerance applies to results, not to guidance.
4. **A false alarm in the validation check's price-level pattern:** "falls below consensus" in an invalidation condition was read as a price condition four times. Each draft was returned once and passed, at about double the cost of the run.

### The brief's evidence in three cards (operator decision, 19 November 2026)

The operator found the evidence panel hard to read: the evidence that carries a direction, the context and the sector and macro backdrop ran as one long list in one card. Of three layouts shown, the operator chose separate cards. Changed in the mock-up first (`docs/site/tradecraft-prototype.html`), then copied to the app.

- **Evidence that carries a direction** keeps its card, and its heading now carries a tally ("1 bullish · 1 bearish").
- **Context, with no direction** and **Sector and macro backdrop** are each a card of their own that folds, with a count beside the heading. A card with no rows is not shown.
- **Proposed in the build and confirmed by the operator the same day:** context starts open when it has four rows or fewer and folded otherwise; the backdrop starts folded. The user's own opening or closing is kept while the brief is on screen. The backdrop card's one-line description ("What the sector and the market have done. Description only: it cannot start, support or cancel a view.") is the build's wording.
- The mock-up had no backdrop section (the operator added it during the build); it now has one, with two example rows.

Checked in the browser on NVDA's no-view brief at two widths. Not checked: a brief with a view, and the dark theme.

**"What you can do" moved into the no-view card (operator decision, 19 November 2026).** On a no view the two choices (Stop; Take a view yourself) and the line "The agents are not asked again for a different answer" now sit in the view card, under the report dates, side by side on a wide screen. The right-hand column is not shown on a no view, so the three evidence cards take the full width. The wording is unchanged and the buttons stay at the bottom. A brief with a view is unchanged: invalidation criteria stay beside the evidence. Changed in the mock-up first. The view card was also given the same 14-pixel gap as the other cards (it had none in the app). Checked in the browser on NVDA at two widths; a brief with a view was not re-checked.

**"Flags and missing inputs" folds (operator decision, 19 November 2026).** The card folds like the context card and its heading shows the counts. Two things are the build's proposal: the heading shows flags and missing inputs as separate counts ("1 FLAG", "4 MISSING"), and the card starts open when a flag is raised and folded when there are only missing inputs, so a folded card never hides a flag. App only: the mock-up does not draw this card (the operator added it during the build). Checked in the browser on NVDA (no flags, four missing inputs); a brief with a raised flag was not seen.

**Also fixed on 19 November:** the gate screen showed "[object HTMLSpanElement]" in place of every contract count. Two functions in the page's script were both called `num`; the one added with the stage 2 screens replaced the gate screen's number formatter. Found by the operator on MSFT with live data.

### Rulings on the four faults (operator decisions, 19 November 2026, morning)

The operator ruled that these are build faults or a gap in the rule, so they are fixed. All four are built, with tests (252 pass).

| # | Ruling | As built |
|---|---|---|
| 1 | The event-kind check applies to the Fundamental Analyst only. Every Regime Assessor finding is context, set in code. A scheduled macro release goes to the calendar and the risk flags, not to findings. The Regime Assessor's output limit is 2,500 tokens | The Regime Assessor no longer runs the bearing-standard check. Code drops any of its findings that cites only the macro calendar (counted in `calendar_findings_dropped`) and its instructions say not to report them. `config/limits.json` |
| 2 | "Support" and "resistance" match only as chart terms. A finding whose kind is a defined event is never refused as a rejected signal | `config/rejected_signals.json`: "support and resistance", "support level/zone/line", "support at/near/around" a figure, and the same for resistance. The rejected-signal check now applies to guidance changes only |
| 3 | Guidance against consensus is set in code from the two figures. A guided range that contains consensus is in line (bearing none, reason `in_line`); wholly above is above; wholly below is below. A single guided figure within 1% of consensus is in line | `stage2.guidance_vs_consensus`; `guidance_tolerance_pct` in `config/stage2.json`. The analyst's own bearing is kept only as `bearing_as_reported` |
| 4 | A price condition needs a price, a currency amount, or "close" or "share price" beside "above" or "below". The fixed conditions written by code are exempt | `validation._PRICE_LEVEL`. The code-written conditions are added after the check and never reach it |

**Choices made while building them, for the operator to correct.**
- Ruling 3, figures code cannot read (no number in one of them, a consensus quoted as a range, or the two more than a factor of two apart after allowing for units): bearing "none", reason "No stated comparison". None of the 49 saved runs has one.
- Ruling 3, "at least $20.50" (UNH) is read as the single figure $20.50.
- Ruling 3 does not cover guidance against the company's earlier guidance: the analyst still sets that bearing.
- Ruling 4: the unambiguous terms stay in the pattern (moving average, support level, resistance level, stop-loss, "share price falls", "stock falls" with a number).

**The 49 saved runs recomputed under rulings 2 and 3, in code, no model call.** Nine change outcome.

| Symbol | Was | Becomes | Why |
|---|---|---|---|
| ADBE | Bearish, more than the result | No view: nothing carries a direction | Both guided ranges contain consensus; results were not directional |
| PYPL | Bullish, more than the result | No view: nothing carries a direction | EPS guidance of about $5.60 is within 1% of consensus ($5.59) |
| INTC | Bullish, weakly supported | No view: conflict | The $23 billion share offering is no longer refused; it is a bearish event |
| GM | No view: conflict | Bullish, more than the result | EPS range $12.75 to $13.75 contains consensus ($13.48); free-cash-flow guidance was raised |
| LMT | No view: conflict | Bullish, more than the result | EPS and sales ranges contain consensus; free-cash-flow guidance was raised |
| JNJ | No view: conflict | Bullish, weakly supported | EPS range $11.05 to $11.15 contains consensus ($11.11) |
| NKE | No view: conflict | Bullish, weakly supported | EPS range $1.15 to $1.35 contains consensus ($1.28) |
| SBUX | No view: conflict | Bullish, weakly supported | EPS range $3.15 to $3.25 contains consensus ($3.22) |
| UNH | No view: conflict | Bullish, weakly supported | "At least $20.50" is within 1% of consensus ($20.60) |

Bearings change without changing the outcome on CSCO, SOFI, NFLX and PFE. PLTR stays bullish on a revenue range of $8.530 to $8.534 billion against a consensus of $8.529 billion: wholly above, by 0.01%. These nine were not re-run.

**The tightened patterns tested against every saved finding and thesis (1,022 texts from the 49 runs).** "Support" and "resistance" now match nothing (they appeared eight times, all ordinary wording). What still matches:

| Pattern | Matches | What it is matching |
|---|---|---|
| Price trend: `(above\|below\|over\|under) (the \|its )?(\d+)[ -]?(day\|week...)` | 61 | 40 are price description ("below its 200-day average"), which is allowed. 19 are thesis text saying "over 30 days", the horizon (the operator kept this pattern on 19 November) |
| Fibonacci: `61\.8` | 3 | CVX's revenue estimate of $61.82B |
| Volatility verdict: "volatility is elevated" | 1 | PYPL, "What tempers it", describing the VIX |
| Price trend: "momentum" | 1 | ADBE, a chief executive's quoted remark, context |
| Price trend: "moving average" | 1 | WFC, a news report, context |
| Accruals | 1 | C, "non-accrual loans", context |

None of these refuses anything in stage 2 now. Stage 4 reads the same file, where a match is a flag. The price-level check matches none of the 74 invalidation conditions the agents wrote.

**C, PEP and T run once (19 November, during market hours).** All three finished with no answer returned: bullish, weakly supported, on the earnings result alone. Cost $0.24 ($0.076, $0.090, $0.075). Nothing was written to the permanent record.

Two of the three differ from what code gives on the findings saved from the first run, because the Fundamental Analyst classified the same evidence differently:
- **PEP.** The first run reported two guidance cuts (core EPS growth) as bearish and a revenue-growth raise as bullish, all against earlier guidance: a conflict. This run reported the same three with bearing "none", so they are shown as context under "Mixed: one measure above, one below", beside a raised `guidance_reduction` flag. The instruction added for ruling 3 ("against consensus, leave bearing as none") is the likely cause. **Settled the same day:** code now sets every guidance bearing (next section). PEP has not been run again.
- **T.** The first run reported the $2.6 billion impairment on the Mexico business as a `material_impairment` event (bearish): a conflict. This run reported it as context and the sale of the business as a material agreement.

### Every guidance bearing set in code (operator decision, 19 November 2026)

The operator withdrew the choice of leaving guidance against earlier guidance to the analyst. The decision is in section 2 of `docs/decisions/2026-11-18-stage-2-anchored-bearings.md`: the analyst extracts measure, period, basis and the low and high figures for both sides and classifies nothing; only EPS, revenue or net sales, and operating income or operating margin can carry a bearing; a comparison needs measure, period and basis to match; raised, lowered, reaffirmed and mixed are set by rule; worded guidance is context. Built in `stage2.guidance_comparison` and `agents.Guidance`, with tests (280 pass).

**Checked once on a live model: PEP, 19 November, $0.06.** The Fundamental Analyst filled the new format on its first answer (measure, period, basis, low and high on both sides; nothing returned) and wrote no bearing. Code set: core EPS growth lowered (+2.5% to +3.5% from +5% to +7%), core constant-currency EPS growth lowered, net revenue growth raised (about +6% from +4% to +6%), organic revenue growth mixed (about +3% from +2% to +4%). Result: no view, findings conflict, as the saved findings predicted. One symbol only; guidance against consensus in the new format has not been seen live. Nothing was written to the permanent record.

**Choices made while building it** are listed in the decision document under "As built, for the operator to correct". The ones that move results: EBIT is not operating income (F); a segment's revenue is not revenue (CSCO's AI infrastructure, NFLX's advertising); basis is not matched against consensus.

**The 49 saved runs recomputed in code, no model call. Approximate:** the saved findings hold each side as one quoted string with no separate basis, so measure, period and basis were taken to match. Against the outcomes of the original runs, 15 change (the nine of the earlier table, six of them differently, plus six more):

| Symbol | Was | Becomes | Why |
|---|---|---|---|
| ADBE | Bearish, more than the result | No view: nothing carries a direction | Guided ranges contain consensus |
| PYPL | Bullish, more than the result | No view: nothing carries a direction | EPS guidance within 1% of consensus |
| HOOD | Bearish, more than the result | No view: nothing carries a direction | The only guidance was on operating expenses |
| VZ | Bullish, more than the result | No view: nothing carries a direction | Raised guidance was on cash flow and subscriber additions; EPS range contains consensus |
| INTC | Bullish, weakly supported | No view: conflict | The share offering is no longer refused |
| CSCO | Bullish, more than the result | Bullish, weakly supported | EPS and revenue ranges contain consensus; the raise was on a segment's revenue |
| F | Bullish, more than the result | Bullish, weakly supported | The raise was on adjusted EBIT |
| RIVN | Bullish, more than the result | Bullish, weakly supported | The raise was on vehicle deliveries |
| GM | No view: conflict | Bullish, weakly supported | EPS range contains consensus; the raise was on free cash flow |
| LMT | No view: conflict | Bullish, weakly supported | EPS and sales ranges contain consensus; the raise was on free cash flow |
| NFLX | No view: conflict | Bullish, weakly supported | Revenue guidance within 1% of consensus; the cut was on advertising revenue |
| JNJ, NKE, SBUX, UNH | No view: conflict | Bullish, weakly supported | EPS guidance in line with consensus |

**Counts across the 49 under these rules** (C, PEP and T from the findings saved on their first run): 26 bullish on the result alone, 3 bullish on more (TGT, PLTR, SOFI), 4 bearish on the result alone, 1 bearish on more (GOOGL), 8 no view by conflict (NVDA, WMT, ABBV, GE, PFE, INTC, PEP, T), 7 no view with nothing carrying a direction (SPY, WFC, COST, ADBE, PYPL, HOOD, VZ). 30 of the 34 views rest on the earnings result alone. None of these was re-run.

### Stage 2 screens built (19 November 2026)

The placeholder page is replaced. Markup and styles are ported from the mock-up; the stylesheet is the mock-up's, copied whole.

| Screen | State |
|---|---|
| Agents-working panel, with Stop | Built. Seen live: statuses move in order, the page polls every 1.5 seconds |
| The brief for a view | Built. Checked live on **TGT** (bullish; results above estimates and two guidance findings) |
| The brief for a weakly supported view | Built. Checked live on **MSFT** (the WEAKLY SUPPORTED chip, "This view rests on the earnings result alone, reported 22 days ago.", the blocks "The basis", "What is missing", "What tempers it", the fixed invalidation conditions first) |
| The brief for a no view | Built. Checked live on **NVDA** (conflict: results above estimates against the chief executive's departure) |
| "Take a view yourself" | Built. Checked live on NVDA: bearish, the departure and one context item ticked, "PARTLY SUPPORTED", the condition "A permanent chief executive or chief financial officer is named", frozen as the user's thesis |
| Freeze and read-only review | Built. The stage bar shows "Frozen" and the time; reviewing shows the banner and disables every button |
| The four additions | Built: the report-dates line; "Base rate, lower close" and the against-the-base-rate sentence (seen on NVDA's bearish user thesis, 42%); "Flags and missing inputs"; "How the system reasoned" |
| Stage stopped on a failure (6.5) | Built. **Not seen in the browser:** covered by engine tests only |
| Range-bound; draft failed validation twice | One plain line each, as instructed. Not seen in the browser |
| No view: nothing carries a direction, declined, insufficient data | Built from the fixed wording. **Not seen in the browser:** no run produced them |
| Stages 3 and 4 | A marked "not built yet" page with Stop |

Engine changes made for the screens, each an operator decision of 19 November: `context_reason` on context findings, set in code wherever code knows it; an event that is not recent is reported as context ("Too old to count as new") instead of being refused; the horizon reasons built in code; fixed wording for the four no-view results; FAILED, TIMED OUT and NOT RUN on the panel; "Take a view yourself" offered only when there is evidence to rely on. Five more event kinds were added for events with no direction (planned succession, material agreement, acquisition by the company, buyback, dividend change), so that code can name the reason.

Two things done without being asked, both to keep the screen to the design: the Thesis agent wrote citation ids such as "(F5)" inside its text on MSFT, so its instructions now forbid that and the page strips any that remain; and quarterly guidance is recognised by a pattern in the finding's text ("quarter" or "Q4" near "outlook" or "guidance"), which is a heuristic.

**Not checked:** the dark theme; Stop pressed in the browser while the agents run (tested through the API on 19 November); a spend-limit stop.

The three live checks wrote to the permanent record: TGT bullish (stopped at contracts), MSFT bullish (thesis rejected), NVDA bearish, the user's thesis (stopped at contracts). Cost $0.22.

### Rulings on the seven items from the re-run (19 November 2026)

None changes any of the six results and nothing was re-run.

| # | Ruling | Done |
|---|---|---|
| 1 | The rejected-signal check applies only to findings that carry a bearing, and to the Thesis agent's text. Description is exempt | Done for the analysts' findings. For the Thesis agent's text the operator decided (19 November) to keep the validation check's own list of price-derived terms; the shared patterns are not applied to it |
| 2 | Thesis agent's output limit raised to 4,000 tokens | Done, `config/limits.json` |
| 3 | One guidance figure yields one finding; compared with consensus where one exists for the period, otherwise with earlier guidance | Done: instructions, and an output check that refuses two findings on the same measure and period |
| 4 | No rule change. The brief shows the age of the latest report and the date of the next one, prominently | The record carries `report_dates`; the placeholder page shows them; the screen is to come |
| 5 | A view resting on results alone takes its invalidation conditions from a fixed set, in code; an agent-written one may be added | Done, `stage2.results_only_conditions` |
| 6 | Fix the singular | Done ("1 day") |
| 7 | No change: TGT failing the gate is handled by adjusting criteria or overriding | Nothing to do |

**Ruling 1 and the Thesis agent's text: settled, keep the existing list.** Tested against the six saved drafts before building it, the rejected-signal patterns would have refused three of the four views for the phrase "over 30 days": the price-trend pattern `(above|below|over|under) (the |its )?(\d+)[ -]?(day|week|...)` is meant for "over its 50-day average" and also matches a horizon. The patterns file is shared with stage 4, where a match is a flag and false alarms are accepted; here a match would use the draft's one return or fail it. The Thesis agent's summary, catalyst and confirmation are already tested for price-derived support by the validation check's own list (trend, momentum, relative strength, moving average, support level, resistance, breakout, overbought, oversold). The operator chose to leave the Thesis text to that list; the shared patterns are unchanged.

**A second point ruling 3 left open, settled on 19 November ("Rulings on the four faults", ruling 3):** a guided range that contains the consensus figure is in line, with no bearing, and code sets it.

### After the demo

- Classifying guidance that is stated in words, with its own stability test (operator, 19 November 2026). Today worded guidance is context: "Stated in words, not figures".
- Stage 3: the expiration rule "after the catalyst date where the view is dated". The stage 2 record carries no catalyst date, so the rule does not apply in the demo (operator, 19 November 2026).
- Stage 3: a control to include or exclude candidates whose expiration falls after an earnings or ex-dividend date. For the demo events are shown and not filtered (operator, 19 November 2026).
- A results-against-estimates finding should stop counting as recent after a fixed number of days (operator, 19 November 2026). Today it is recent for as long as no newer report exists: WMT's was 91 days old.

- **Rethink how the thesis is constructed (operator, 19 November 2026).** Today stage 2 weighs evidence from filings above everything else: a view can start only from results against estimates, a guidance change or a filed event, and every other dimension is context. That follows partly from the free data sources and partly from the anchoring standard of 18 November. After the demo, explore other dimensions a thesis could be built on, and for each one how it would be anchored and tested. Starting points: expectations (estimate revisions and their history, quarterly consensus, guidance against consensus on more measures); valuation; sector and macro evidence with an expectation to compare against; and whether an earnings result alone should start a view (20 of the 31 views in the 49-symbol run rested on it, and 24 of the 31 were bullish). Check every candidate dimension against the rejected-signal list first. A new dimension is a design change with its own decision record; anything scored against outcomes is a pre-registered trial.

### Stage 2 wired into the app (19 November 2026, early morning)

| Piece | What was done |
|---|---|
| Real steps | `steps.real_steps()` registers the gate and `stage2.STEPS`; `thesis_not_built` is removed |
| Background run | An action that starts a long stage returns after 1.5 seconds at most with `running: true`; the page asks `/api/requests/open` again every 1.5 seconds. Quick steps still answer at once |
| Agent status | `Workflow.progress` reads each agent's status (waiting, working, done, failed) from the trace; the view carries it as `progress`, with the three analysts marked as the parallel group |
| Stop while running | The "stop" action cancels the agents at their next step; the request ends and its pending log is discarded |
| "Take a view yourself" | After a no view the pause offers "stop" and "own_view". The entry needs a direction, a horizon from the measured table, at least one item relied on and at least one nameable condition; otherwise the pause says what is missing. Freezing writes `thesis_user_frozen`, commits the pending log and goes on to contracts. The no-view result carries `own_view_options` for the screen |
| Placeholder page | Shows the agents' status, the result, the summary and the bearing-carrying findings as plain text. It is a build placeholder, not a designed screen |

Checked live through the running app, with the analysts in parallel on a live model for the first time:

| Run | Result | Time | Cost |
|---|---|---|---|
| MSFT | Bullish, weakly supported; validation passed first time; panel statuses moved in order; reload restored the open request | 42 s | $0.08 |
| NVDA | No view (conflict), then a bearish thesis entered through the API: verdict "partly supported", the earnings result standing against it, the condition "a permanent chief executive or chief financial officer is named" | 31 s | $0.05 |

**These two checks wrote to the permanent record,** which is append-only: Recent analyses now lists "MSFT bullish, stopped at thesis" and "NVDA bearish, stopped at contracts". The database is `data/tradecraft.sqlite3` (git-ignored). The operator may want a clean database before recording the demo.

### The six-symbol re-run (19 November 2026, early morning; made once)

Made after the operator's amendment that an event is "new" when recent by the grades' test (within 30 days, or since the latest earnings report). Before the amendment the stability test had shown NVDA's departure, dated five days before its report, being treated as context.

| Symbol | Result | Bearing-carrying findings |
|---|---|---|
| NVDA | **No view: conflict** | Bullish, moderate: EPS $2.68 against $2.49 (+7.6%), revenue $115.84B against $109.28B (+6.0%). Bearish, strong: chief executive departed, interim named, no permanent successor (new event) |
| AMZN | **Bearish, weakly supported** | Bearish, moderate: EPS $1.89 against $1.97 (-4.1%), revenue $201.94B against $202.22B (-0.1%, in line). Report 21 days old |
| TGT | **Bullish** | Bullish, moderate: EPS $2.65 against $2.10 (+26.2%), revenue $27.07B against $26.53B (+2.0%). Bullish, strong: fiscal 2026 EPS guidance $10.65 to $11.40 against consensus $10.25 |
| WMT | **No view: conflict** | Bullish, moderate: EPS $0.81 against $0.74 (+9.2%), revenue in line (+0.7%). Bullish, strong: FY27 adjusted EPS guidance raised to $2.80 to $2.87 from $2.75 to $2.85; net sales and operating income guidance raised. Bearish, strong: that EPS guidance is below the consensus of $2.89 |
| JPM | **Bearish, weakly supported** | Bearish, moderate: EPS $5.75 against $5.93 (-3.0%), revenue $50.17B against $51.23B (-2.1%). Report 37 days old |
| MSFT | **Bullish, weakly supported** | Bullish, moderate: EPS $4.89 against $4.72 (+3.6%), revenue $92.28B against $90.62B (+1.8%). Report 22 days old |

Four views (one resting on two findings, three on the earnings result alone) and two no views, both by conflict. Every draft passed the validation check first time; no reply was cut off. Cost $0.45.

**Seen in the run and left as they were; ruled on later the same day (see "Rulings on the seven items"):**

1. The rejected-signal refusal fires on the Regime Assessor in every run: its description of SPY against its 200-day average matches the "price trend" pattern, so its first answer is returned once and the finding dropped. No outcome was affected (its findings carry no bearing). The same pattern refused one Fundamental Analyst context finding on MSFT.
2. The Thesis agent used 2,260 to 2,341 of its 2,500 output tokens on three of the four views. Not cut off, but close.
3. WMT's conflict is one guidance figure read two ways: raised against the company's earlier guidance, and below consensus.
4. WMT's "latest report" is 20 August, 91 days old, and still counts as recent because nothing newer exists; it reports on 19 November. JPM's is 37 days old.
5. The invalidation conditions the agent wrote for a results-only view ("an amended filing or restatement") differ from the mock-up's ("the next earnings result misses consensus").
6. A measured fact reads "1 days ago" (TGT).
7. TGT fails the stage 1 gate at default settings on the snapshot; its stage 2 was run regardless.

### What is built (branch `build/demo`, nothing pushed)

| Part | Where | State |
|---|---|---|
| Measured figures for six horizons (blended base rate, typical realized move, volatility state, trend, risk reference) | `tradecraft/figures.py` | Built, tested, checked on cached prices |
| Recommended-horizon rule and range-bound rule | `tradecraft/horizon.py` | Built, tested |
| Numbers handed to the analysts (technical, sector, market regime, earnings reactions) | `tradecraft/context.py` | Built, tested; sources fetched live once |
| Evidence store and grades | `tradecraft/evidence.py`, `tradecraft/storage.py` | Built, tested |
| Five agents as `AgentConfig`s | `tradecraft/agents.py` | Built, tested on a scripted model, run live |
| Validation check, run in one place | `tradecraft/validation.py` | Built, tested. No directional draft has yet passed through it live |
| Stage 2 workflow steps | `tradecraft/stage2.py` | Built, tested, wired into the app and run live through it |
| Anchored bearings (decision section 7, items 1 to 5) | The three files above; `config/stage2.json` | Built, tested |
| Stability test (item 7) | `tests/test_live.py` | Passed once live on NVDA |
| A thesis the user enters after a no view | `validation.user_verdict`, `stage2.user_thesis_step`, the graph's `own_view` action | Built, tested, run live through the API. No screen |

218 tests pass (`.venv/bin/python -m pytest -q`).

### What is not built

- Designs still to come from the operator: the range-bound brief; the brief when a draft fails validation twice; the "analysed before" line.
- Index instruments: by decision they return no view (nothing carries a direction). Not run.
- Stages 3 and 4.

### Next, in the operator's order

1. Done: the one re-run (above).
2. Done: stage 2 wired into the app (above).
3. Done: the stage 2 screens (above).
4. Done: the 43-symbol run (above). Nothing was adjusted on it.

### Decisions made tonight

Each is recorded, dated, in the document named.

| # | Decision | Recorded in |
|---|---|---|
| 1 | Conflicting company evidence: first limited to primary-source findings; **superseded the same night** by decision 14 | On-demand design, "Five points settled for the build" and the clarification beside it |
| 2 | A finding takes the grade of its best cited item; a data provider's copy of reported figures is not a primary source | On-demand design, same section |
| 3 | Sector context from the FMP sector mapped to a SPDR sector fund; market regime from SPY, `^VIX` and `^VIX3M` on Yahoo | Same; `config/data_sources.json` |
| 4 | What is computed for the Technical Analyst: trend against the 50-day, 30-week and 10-month averages; 1-, 3- and 12-month change; 52-week and 60-day closing extremes; 3-month change against the sector fund and SPY | On-demand design, same section |
| 5 | Horizon rule 2: at least two contracts passing the stage 1 criteria without DTE, expiring from the horizon date to twice the horizon away | Same |
| 6 | `cites[]` on the summary, each rationale part and each horizon reason | On-demand design, "Validation check"; agent architecture 3.3 |
| 7 | Every number in that text must equal a number in what it cites; code supplies day counts and dates | On-demand design, "Validation check" |
| 8 | One draft return in total; a cut-off or badly formatted reply uses it; a manual Retry is a fresh run | Same; build plan, section 4 |
| 9 | Output caps may be raised after a cut-off, to 4,000 (Haiku agents) and 8,000 (Thesis agent) | Build plan, section 4; `config/limits.json` |
| 10 | Clarification: a conflict needs findings graded moderate or strong; a weak finding against the view is contrary evidence; a standing disclosure carries no bearing | On-demand design, under the precedence rules |
| 11 | **Anchored bearings.** A finding carries a bearing only as results against estimates (set in code), a guidance change quoting both figures, or a new event on a fixed list. Everything else is context | `docs/decisions/2026-11-18-stage-2-anchored-bearings.md`; on-demand design 2A; agent architecture 3.5 |
| 12 | Results against estimates can start a view; a view resting on it alone is weakly supported; an officer departure is bearish when unplanned or with no permanent successor named; no bullish event other than raised guidance | The decision, sections 3 and 4 |
| 13 | The results-against-estimates finding always grades moderate; the mock-up rows were corrected | The decision, section 2; the mock-up |
| 14 | Two bearing-carrying findings graded moderate or strong with opposite bearings give no view, whatever their source. Replaces the primary-source wording of commit `37dc892` | The decision, section 4; on-demand design |
| 15 | Regime Assessor findings carry bearing "none" and are shown under "Sector and macro backdrop"; `contested` cannot be set until a source for macro expectations exists; an index request returns no view | The decision, section 4; on-demand design |
| 16 | Three outcomes of stage 2, and "Take a view yourself" as the structured form of step 2B and the commit point after a no view | The decision, sections 5 and 6; on-demand design 2B; product shell 6.2 |
| 17 | Order of work: engine, documents, the one re-run, this log; screens and the 43-symbol run on 19 November | This file |
| 19 | Which invalidation conditions the system can name for a user thesis: two general ones, plus the reversal of each matching event finding. Proposed by the build session; the operator said go ahead (19 November) | The decision, section 6 |
| 18 | An event is "new" when recent by the grades' test: dated within the last 30 days, or since the latest earnings report (19 November) | The decision, section 3; on-demand design; agent architecture 3.5 |

Changed under decision 9: the Evidence Retriever's and the Fundamental Analyst's output caps, from 1,500 to 4,000 tokens, after both final answers were cut off on the first live run.

### What the live runs showed

| Run | Result |
|---|---|
| NVDA, AMZN (first rules) | Both no view: strong primary-source findings from one earnings release pointed both ways |
| NVDA, AMZN, TGT, WMT, JPM, MSFT (after the clarification) | Six of six no view, for the same reason. Bearings were set by tone and were not stable between runs. This led to decision 11 |
| Stability test, NVDA (anchored bearings) | Identical bearings on two runs. The only bearing-carrying finding was the code-built result (EPS $2.68 against $2.49, revenue $115.84B against $109.28B: bullish). The departure was reported as context both times |

Spend on model calls: about $4.55 in total ($0.51 before the re-run, $0.45 on it, $0.13 on the two runs through the app, $0.22 on the three screen checks, $3.24 on the 43-symbol run). A full stage 2 run costs about $0.06 and takes about 45 seconds with the analysts run one after another.

### Open questions for the operator

**Added 19 November, midday.**
- **Speed.** A stage 2 run took 30 seconds on MSFT by the trace (Retriever 10, analysts 13, Thesis agent 7); a full view is nearer 45. Three changes that alter no rule were offered and the operator said "not now": the Retriever asking for all its tools in one step; the Fundamental Analyst given the guidance passage up front; the Regime Assessor losing the macro calendar tool. Two others touch decisions: skipping the Thesis agent when code already knows the result is no view, and a lower effort or smaller model for it.
- **Demo symbols.** SPY returns no view by rule and AMZN is bearish on the result alone; TGT, CSCO and PYPL fail the stage 1 gate on the 18 November snapshot.
- **From the guidance rules:** whether EBIT counts as operating income, whether a segment's or organic revenue counts as revenue, basis against consensus, a tolerance for a guided range (PLTR is "above" by 0.01%), where the quoted passage of worded guidance is shown, and the three reason sentences worded in the build.
- **Rejected-signal patterns that still match ordinary text** ("over 30 days", "$61.82B", "non-accrual"); stage 4 reads that file.
- **The saved run outputs** are in `data/runs-2026-11-19/` (git-ignored, so not in the repository the evaluators will see).

1. The seven items listed under the six-symbol re-run.
2. Stage 2 screen gaps still open from the first list: the wording when a bearish view runs against the base rate; the range-bound brief; the brief shown when a draft fails validation twice; where risk flags, the risk reference and unavailable inputs appear.
3. SPY is a demo symbol meant to run all four stages, and by decision 15 it now returns no view.
4. The Retriever's "one recovery" for the demo: a scripted test exists; nothing fails naturally on NVDA.
5. Four directional drafts have now passed the validation check live; none has been seen on a screen.
