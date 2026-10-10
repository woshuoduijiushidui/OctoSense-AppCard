# Migration validation

## Composed plans with ordered stages, 2026-10-10 — unreleased 0.6.2 working tree

Implementation for Issue #9. Candidates and confirmed stages are now separate
records, and a plan is an ordered list of stage snapshots.

- `bundle/main.splash`: `state.programs` holds unconfirmed candidates only;
  `state.stages` holds the confirmed plan's snapshots in order, and
  `state.plan_history` holds archived plans. `make_stage` copies a candidate's
  targets at confirmation; the compose page shows total days and each stage's
  date range and targets, with add / move / remove / replace and a hard cap of
  12 stages. The current stage is the first stage whose date range still covers
  today, so a multi-stage plan advances on its own dates. The GPU renderer is
  unchanged.
- Storage schema stays 1. `migrate_state` splits a previously active program
  into a one-stage plan and turns legacy `program_history` entries into plan
  history without dropping `consumed_kcal` or `intake`. A re-serialization after
  the split prevents the fallback defaults from overwriting the split result.
- `tools/qa_release.py` gained compose, cap, and ordered-stage assertions;
  `tools/smoke.py` follows the new `确认计划 · 去录冰箱  →` label, its
  `stages` schema, and a small `scroll` helper; `tools/test_release.py` guards the
  new symbols. Bilingual READMEs and `CYCLE-PLANS.md` describe the flow. The
  version stays 0.6.2 because it is set at release, not per feature PR.

### Native run, 2026-10-10 — unreleased 0.6.2 working tree

- Restamped the editable bundle with the pinned official App Hub
  `655114c4943cd2490daaefa2173e7b5aaa20669f` (`hub stamp bundle`):
  `bundle_blake3 = 54f917fcbe012ddd7195b7d35c9aef57cdc5a692d3f1392dda31558a251a2d0d`.
  `hub check bundle --allow-unsigned` then **PASSED** with only the expected unsigned
  warning and unchanged grants (model, storage, 16 MiB, no agent, no hosts).
- Hidden official `card-host.exe` (same pinned revision) standalone at 1200x800
  with task-owned `--app-data` under `.local-state/qa-*`:
  `tools/qa_release.py` — **14/14 checks passed**: first-run onboarding; six
  cycles x three candidates without auto-activation; cycle switching;
  per-cycle regeneration; reorder, remove and replace in the draft; the 12-stage
  cap; clearing the draft leaves candidates unconfirmed; the compose page sums
  cycles (7+15 = 22 days); confirmation writes two ordered stages whose start
  dates meet end-to-start; inventory preview does not commit; explicit commit
  persists; manual default does not generate. A restart then preserved the exact
  synthetic state.
- Migration checks with real old-schema fixtures (copies of the Issue #8
  synthetic profile): the previously active 7-day program opened as a
  one-stage plan with its 11550 kcal target, 17 candidates stayed unconfirmed,
  and `stage_next` continued its id space. A fixture with a legacy
  `program_history` entry migrated it into `plan_history` with its 3210 kcal
  preserved. Tab 3 rendered the plan stages and plan history; `选择下一份计划…`
  archived the 2-stage plan (`2 个阶段 · 22 天`) and returned to candidate
  selection; the demo profile resolved its stage so menu generation still
  worked.
- No real inventory, keys, provider calls or AI credentials were used.
- Real captures of this run: `docs/qa/issue-9-compose.png` (a 7+15+21 draft:
  43 total days, stages 10月10日–10月16日 / 10月17日–10月31日 / 11月1日–11月21日),
  `docs/qa/issue-9-plan.png` (the confirmed plan's stages) and
  `docs/qa/issue-9-history.png` (the archived 3-stage plan under 计划历史).
  These are hidden Card-runtime captures of synthetic data, not phone images.

An independent two-axis review (standards + spec) of the feature commit found
no blocker. Acting on it: `draft_move` now clears the armed replace target so a
reorder cannot make 替换 hit the wrong stage; the replace prompt is shown inline
and points to the candidates above; the archive/clear sequence is one
`archive_plan` helper; and `tools/smoke.py`'s `--legacy` assertions now compare
the migrated field set (`foods`, `plans`, active/revision/meal fields) instead of
requiring the pre-migration `programs` shape.

### Still unverified

- Not run: the full `tools/smoke.py` regression and its `--legacy` fixture. On
  the standalone `card-host` the AI-provider check (`宿主服务可用`) fails because
  that host intentionally has no model service; that check needs the full
  desktop host. `tools/launch.py --check` against a full host workspace, live
  provider calls, and non-Windows platforms are also unverified. Signing and
  submission remain human checkpoints. No tag, release, new Issue or submission
  was performed.

## Six cycle candidates and per-cycle regeneration, 2026-10-10 — unreleased 0.6.2 working tree

Implementation for Issue #8: cycle lengths 1/3/7/15/21/30 days, three
profile-derived candidates per cycle, and a `重新生成本周期候选` action that
replaces only the selected cycle's unconfirmed candidates.

- `bundle/main.splash`: per-cycle totals come from the profile (age, sex, height,
  weight, activity, health direction). Three emphasis templates (baseline /
  higher protein / higher fibre, plus lower-energy `控卡` or a bulking `加餐`)
  are shown, rotated by a small per-cycle seed so regeneration yields a
  different but still-safe line-up. A profile that is not numeric-ready (missing
  height/weight, or a base estimate below 1350 kcal = the 1200 kcal floor plus
  the 150 kcal 控卡 step) gets no numbers and a stated reason; 控卡 targets are
  floored at 1200 kcal. A started/active program is a confirmed snapshot and is never
  removed or rewritten by regeneration; `program_history` is untouched.
- Storage schema stays 1. A six-integer `cycle_seed` field is added and migrated;
  old unconfirmed 7/21/30 candidates are rebuilt from the profile while a
  confirmed program is kept.
- `tools/smoke.py` and `tools/qa_release.py` now expect six cycles × three
  candidates and additionally exercise cycle switching and regeneration.
- Bilingual READMEs, `CYCLE-PLANS.md` and the `bundle/listing.json` description were
  updated; the version stays 0.6.2 because it is set at release, not per feature PR.

### Native run, 2026-10-10 — unreleased 0.6.2 working tree

- Restamped the editable bundle with the pinned official App Hub
  `655114c4943cd2490daaefa2173e7b5aaa20669f` (`hub stamp bundle`):
  `bundle_blake3 = 4102012b82809f27ebb522afd764bafa8ad6b69a118fefd1314ec6fa06d86940`.
  `hub check bundle --allow-unsigned` then **PASSED** with only the expected
  unsigned warning and unchanged grants (model, storage, 16 MiB, no agent, no hosts).
- Ran the hidden official `card-host.exe` (same pinned revision) standalone at
  1200x800 with task-owned `--app-data .local-state/qa-issue8`:
  `tools/qa_release.py --port 18533 --profile .local-state/qa-issue8` — **8/8
  checks passed**: first-run onboarding; six cycles × three candidates without
  auto-activation; cycle switching shows that cycle's candidates; regeneration
  replaces only the viewed cycle (other cycles' ids and `program_active`
  unchanged); explicit cycle activation; inventory preview not committed;
  explicit commit persists; manual default does not generate. No real inventory,
  keys or provider calls were used.
- Real captures of the run: `docs/qa/issue-8-six-cycles.png` (7-day candidates)
  and `docs/qa/issue-8-regenerated.png` (after regeneration the second candidate
  changes from 高蛋白 to 高纤). The four distributed `bundle/screenshots/*` still
  show the previous 7/21/30 page and were not replaced.

### Review fix, #13

- `make_programs()` resets `cycle_view`, so re-saving the profile from the cycle
  page cannot leave the selected candidate off the shown cycle.
- Migration detects pre-0.6.3 candidates from the candidate record itself, not a
  whole-file text search that user diet/food text can trigger.
- Regressions: `tools/smoke.py` adds the profile re-save path to `exercise`, and
  `--seed-legacy-candidates` / `--legacy-candidates` for a legacy candidate list
  whose user text contains `difference`. Both paths were also verified live in
  the hidden official host.

### Still unverified

- Not run: the full `tools/smoke.py` 45-check regression, its `--legacy` fixture
  (which must include `cycle_seed` before its exact-equality restore check passes),
  `tools/launch.py --check` against a full host workspace, live-provider calls,
  and non-Windows platforms. Signing and submission remain human checkpoints.
  The version stays 0.6.2: it is set at release, so this feature branch does not bump
  it. No tag, release, new Issue or submission was performed.

## Original-artwork confirmation, 2026-10-08 — current 0.6.2 candidate

The author confirmed sunlit-pantry-bg.png is their own original artwork.
Recorded that declaration in root/bundle notices, bilingual READMEs, review
answers and submission checklist. This resolves the author's outstanding
asset-origin checkpoint; it is not independent rights verification. Earlier
pending-artwork statements below describe the earlier repair checkpoint.

Only notices/docs changed; application logic and artwork are unchanged.
The current official pinned hub restamped the editable bundle after this
notice edit. Current source digest:
`851f2c46a63bd1a129a8c451acbe4992e2d11a8f7e81ffa3376307268640d103`.
Source gate passed with only the expected unsigned warning; scan regenerated
seven questions; all 18 automated tests passed again; git diff --check passed.
Current total size: 8,357,004 bytes, 31,604 bytes below 8 MiB.

The seven native checks below were performed before this notice-only edit;
they were not rerun or relabelled as full functional regression. Live-provider
tests, attested-release verification, platform limits and human approval
remain as listed below. No commit, tag, push, release or Issue was made.

## Local compliance repair, 2026-10-08 — 0.6.2 candidate

This dated entry supersedes earlier pending publisher/privacy statements;
it does not rewrite the historical test records below or admit any version.
The user confirmed publisher display names, Windows-only claims and privacy
disclosure, and authorized local repair only. No commit, pushed tag, GitHub
workflow run, release or submission issue was created in this repair.

### Source and metadata

- Repair checkout: app-only remote main at
  `fd5baccd45e2aa39a8723e7c1efdd263342b0c7d`, local branch
  `codex/compliance-0.6.2`. The original full host at `E:\codeh\OctoSense`
  and its user's inventory were not replaced.
- `bundle/main.splash` is unchanged: Git blob
  `8e9660e130b45d6a3e71f8ff94f1bfb1e7d0d78e`, identical in the baseline
  remote commit, repair checkout and original full host's app directory.
- Corrected support/privacy URLs, release notes/version, bilingual launch
  instructions and review answers. Added Apache-2.0 license and notices
  at the repository root and inside the bundle with allowed `.txt` names.
- `.gitattributes` disables bundle text conversion; native installer source
  and tool scripts use LF, Windows batch entrypoint remains CRLF.
- `sunlit-pantry-bg.png` and historical screenshots were preserved. Image
  ownership/redistribution evidence remains a release-blocking author checkpoint.

### Current official source gate

- App Hub: `655114c4943cd2490daaefa2173e7b5aaa20669f`, the workflow pin.
  Built both `hub` and `card-host` on Windows with Rust 1.98.1, from the
  unmodified official checkout using `cargo build --locked --release`.
  The original workspace and lock file were unchanged. Its exact dependencies
  were reused from Cargo-managed caches via local junctions; no user's shared
  framework checkout was modified.
- Native pins: Makepad `32d6415fb7476345ad36ee4f98d6f844d1f07fd2`,
  Octoscript-Makepad `33dea2f1f3ad3f1346a219aa8cf6e91b31361e23`,
  Octoscript `2e37d9e657a246f16718d9a475e167ccd2d5b5fa`.
- The old `0d5b47...` Windows CLI first passed the pre-license bundle, then
  incorrectly treated the full Apache license URL as a remote asset. The
  current CLI also exposed its old path-hash mismatch. These were not worked
  around with extra grants, stripped legal text or changes to the gate.
- Restamped only the unsigned editable source with the current official tool:
  `4f09efe71f2db070322f4959e8e86b2b36aa8555b9426547ae45198a63661c0e`.
  This is NOT a sealed-release proof or a manually invented hash.
- `hub check bundle --allow-unsigned` and its JSON form passed, structural
  stage, with only the expected unsigned warning. Grants: storage/model,
  no outbound hosts, 16 MiB storage, no app agent.
- `hub scan bundle --packet build/review.json` generated all seven questions;
  no external reviewer ran. Answers are in REVIEW-ANSWERS.md.
- `python -B -X utf8 tools/launch.py --hub
  build/hub-reviewed/target/release/hub.exe --check` passed with no host,
  key generation, installation or implicit restamping.
- Total bundle size is 8,357,017 bytes, below 8,388,608 bytes. Remaining
  headroom is only 31,591 bytes; future artwork changes must recheck size.

### Automated and native checks

- `python -B -X utf8 -m unittest discover -s tools -p 'test_*.py'`:
  **18 passed**. Includes batch dispatch/error status, explicit tool/host
  resolution, no implicit key creation, no launcher restamp, permission and
  metadata guards, required legal files, platform and local-document links.
- Both new listing URLs returned HTTP 200. The remote pages still describe
  the previously pushed state until these local changes are authorized/pushed.
- Isolated Git index checkout with `core.autocrlf=true` under `build/`
  preserved the bundle's bytes; the current gate passed that checkout and
  SHA256 of main.splash matched. This is a local byte-conversion test,
  not a new remote tag clone or release download verification.
- Current official `card-host`, hidden 1200x800, separate synthetic
  `.local-state/qa-current-062`, remote port 18529: **7 native checks passed**.
  First run rendered; 7/21/30-day choices required confirmation; explicit
  cycle activation worked; inventory preview did not commit; confirmed
  synthetic spinach committed; manual default did not generate a plan;
  restart preserved the exact saved synthetic state.
- Native driver: `build/native_compliance.py` for the six first-run checks,
  followed by `tools/qa_release.py --port 18529 --profile
  .local-state/qa-current-062 --restart` for persistence. The equivalent
  reusable driver is now in tools/qa_release.py and requires a task-owned
  qa-* profile under .local-state. Do not point it at real inventory.
- Opened and visually inspected both genuine native test captures. They
  remain outside bundle/. No app callback/closure/error-level messages were
  found in these run/restart logs. Native startup produced informational
  UI-hang samples and the build produced upstream compiler warnings; these
  are not claimed as warning-free runs. All task-owned hidden instances quit.
- `git diff --check` passed. Local-state, build products and test captures
  are ignored. No real AI credentials, model calls or new signing keys used.

### Still pending — no approval guarantee

Background rights, full current-toolchain feature regression, live model
provider tests, fresh-computer setup, other platforms, GitHub Actions
execution, downloaded attested release-pack/receipt verification, publisher
continuity against the authenticated catalog, Store installation and Hub
approval are unverified. The prepared workflow does not supply any of that
evidence until it actually runs and its downloaded artifacts are verified.
Its pinned Rust 1.97.1 Linux environment is distinct from this Windows build.
The teacher decides competition qualification and deadline eligibility.

Issue #99 still refers to immutable 0.6.1. Current submission rules require
one issue per planned version; 0.6.2 needs a new issue linked to #99 after
human authorization, never a moved v0.6.1 tag or a replacement version comment.

## Cycle program addition, 2026-10-06

- Bundle 0.6.1 adds explicit 7/21/30-day programs to the existing desktop UI.
  Official model/storage grants, manual-default generation and deletion remain.
- Official cached Windows Card runtime: synthetic `qa-cycle` profile, hidden
  1200x800 viewport. Twelve UI/data checks passed: candidate duration and totals,
  explicit activation (21 and 30 days), no automatic generation during inventory
  entry or consumption, inventory validation, cycle intake, deletion preserving
  intake, and renewal archiving the old cycle without losing inventory.
- Restart preserved the exact saved profile, active cycle, history and inventory.
- Synthetic pre-cycle `qa-legacy`: three additional checks passed for 7-day
  confirmation, inventory/plans/meal preservation, and zero initial new-cycle
  intake. No script errors appeared in its runtime log. The quit route closes
  the server connection on this build; that cleanup is not a failed app check.
- App Hub `stamp` and `check --allow-unsigned` passed. Unsigned source warning
  is expected; production identity/signing and store publication remain unverified.
- Fresh period screenshots are hidden Card-runtime captures, not phone images.
  This update has not been tested on Android or with a live model request.
- Existing user's `.local-state/` is not used as a test profile. Original sources
  are backed up before deployment; no host code or downloaded APK is replaced.

Earlier 0.4.3 results below describe that earlier version, not the cycle change.

## Manual-default and deletion regression, 2026-10-04–05

- Bundle 0.4.3: manual generation by default; persisted opt-in automatic mode;
  invalid-plan notice and explicit Home entry; confirmed single-plan deletion.
- Current official checkout HEAD: 6794abd2026574bd283265d13fcaa76b5323a9e1.
  App Hub CLI pin: 0d5b47a2ae9eb98020feca26b7c895a3cf797dc1.
- `python -B -X utf8 apps/pantry-steward/tools/launch.py --check` passed:
  unchanged storage/model permissions, source unsigned warning expected.
- `python -B -X utf8 -m unittest discover -s apps/pantry-steward/tools
  -p 'test_*.py'`: 7 passed, including manual defaults and automatic-trigger guards.
- Native hidden official-shell tests used a cached desktop executable and separate
  synthetic profiles; no host source edits, real inventory or model calls.
  `tools/smoke.py` with qa-manual: 36 UI/data checks passed. Covers onboarding,
  cancelled edits, confirmed edits/removals without generation, expiry notice
  without generation, explicit generation, visible invalid-plan notice, no
  generation from the Home entry alone, consumption without next-plan generation,
  deletion/cancellation/last-plan/active-plan cases, automatic opt-in and opt-out.
  Same command with `--restart`: exact persistence check passed.
- A separate qa-manual-legacy profile was preloaded with synthetic old state
  (no auto_generate property) and an old before-demo backup. `--legacy`: 8 checks
  passed for manual migration, preserved stock/plans/meals, backup restoration,
  opt-in automatic consumption/addition/removal, switching back to manual, and
  the explicit alternative button. Total: 45 UI/data checks.
- After the final wording adjustment, the 36-check run was repeated in
  qa-manual-final and all 8 legacy checks were repeated; both passed with no
  native callback/closure errors. Final digest:
  `5bbfba5f084678c9009f81249cd33f93ec2a57b1c5d77f82e15dac799643a824`.
- Real native captures of invalid-plan and manual settings were visually checked.
  Existing four submission screenshots were not replaced by these QA captures.
  Task-owned hidden windows were closed using their own remote endpoint; restart
  and legacy logs contained no error-level, callback or closure-failure messages.
- Before this change, 0.4.2 deletion regression also passed 23 UI/data checks,
  persistence and two maximized-window reachability checks. Deletion remains
  included in the 0.4.3 regression above.

Limitations: setup reports the existing `.sources/octoscript-makepad` checkout is
at another revision. Its clean checkout was not updated. These script-only tests
use the existing desktop binary, so a fresh host rebuild against the current
runtime lock is **unverified**. Do not interpret the bundle gate as a host build.
Late live-network response cancellation and provider charging were not exercised;
the sequence guard is retained and disabling ignores automatic results.
The user reported successful host-AI generation, but these automated checks did
not use real credentials or make provider requests. Mobile/release signing and
publication remain unverified; no Git commit, push or submission was performed.

## Verified on Windows, 2026-10-02

- Official OctoSense source: b221f7b4c877dd823d04e4ee510cc74880de5535.
- Pinned App Hub: 58c3c8aed8fc811a16d67c5f784a8a44214ff876.
- `python -X utf8 tools/setup.py --hub <existing dependency directory>` succeeded.
- `python -X utf8 apps/pantry-steward/tools/launch.py --check` built the
  official CLI sources, reusing `.sources/` without custom host services.
- `python -X utf8 -m unittest discover -s apps/pantry-steward/tools -p 'test_*.py'`:
  3 passed (key-generation consent, no secrets/custom microphone calls in the
  bundle, official budget semantics).
- The launcher with `--prepare-local-test --hidden --remote 18442 --app-data
  apps/pantry-steward/.local-state/qa-official` generated local test keys only
  after explicit consent; signed a separate snapshot; published ONLY to a local
  mirror; verified the catalog and installed through App Hub's real Store.
- `python -X utf8 apps/pantry-steward/tools/smoke.py --profile
  apps/pantry-steward/.local-state/qa-complete`: 17 native UI/data checks passed.
  Includes first-run onboarding, invalid quantities, preview/confirmation,
  microphone-unavailable notice, honest budget status, local mode, demo consent,
  expiry replanning, acceptance, invalid consumption, cancellation, consumption,
  and returning to the profile form without losing inventory.
- Same command with `--restart`: persistence check passed (18 UI/data checks total).
- Native remote logs after the successful run/restart contained no `[E]`,
  callback errors or on_render closure failures.
- Final default profile launcher (`--hidden --remote 18443`) opened the app in
  the unmodified official shell. `cargo build --release --locked -p octosense`
  succeeded; the official source files remained unchanged.
- Independent preview (`--standalone --hidden --remote 18444`) was admitted
  by the unmodified official card-host and rendered its initial onboarding page.
- `target/release/hub scan apps/pantry-steward/bundle --packet
  apps/pantry-steward/build/review.json` created the seven-question review packet;
  no external reviewer was used. Draft answers: REVIEW-ANSWERS.md.
- Four real full-window captures from the official-shell test were opened,
  visually inspected and copied without editing to `bundle/screenshots/`:
  `01-main.png`, `02-plan.png`, `03-confirm.png`, `04-updated.png`.
- Final bundle size: 8,308,715 bytes, below the 8,388,608-byte gate limit.

Final unsigned source-bundle gate output:

```text
pantry-steward 0.4.1 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"model", "storage"}, hosts {}, storage 16777216 bytes, agent none
```

Local signed snapshots also passed without that unsigned warning. They are not
production publisher signatures. The source bundle remains unsigned for editing.

## Compatibility gaps found and fixed

- The Windows batch entrypoint used LF-only newlines. Running it through
  cmd.exe reproduced truncated commands before Python could start. Changed it
  to ASCII with CRLF, added a Git checkout rule, and guarded its dispatch and
  failure exit status with Windows-only tests.
  All six launcher tests passed. Running run.cmd from the app directory with
  a separate qa-batch profile opened the official shell and Pantry Steward's
  first onboarding page; verified via the native UI snapshot and real capture.
  The task-owned hidden test window was closed through its remote endpoint.
- The original 2 MiB quota failed `fs.write` in the official runner, because
  this runtime counts the installed bundle/resources inside the jail. Raised
  the requested quota to the supported 16 MiB ceiling and reran onboarding.
- Official `model.budget` returns usage, not `configured` or model identity.
  Removed that assumption and stopped labelling a successful budget query as a
  configured provider.
- The tested official host has no original `microphone.start/stop` adapter.
  Removed its calls and microphone grant. The icon now explains unavailability;
  no audio is recorded. Original speech code is preserved in the source project.
- A manifest-only edit does not change the bundle digest. Local snapshot caches
  now include manifest bytes, so storage/version changes cannot reuse stale grants.

## Not verified

Live model-provider calls, no-provider response end-to-end, speech recognition,
other operating systems, mobile devices, release signing and App Hub submission.
No real AI credentials were copied or used, and no provider API call was tested.
The original project's inventory and ai.env were not migrated. All created
hidden test windows were closed through their own remote endpoint.

Publisher identity and privacy text remain unapproved; the existing listing
keeps the author's pending identity. Local test-key creation was explicitly
approved by the user. Production signing and submission were not authorized.
