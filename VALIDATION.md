# Migration validation

## PR #21 review corrections, 2026-10-12

Addresses the five comments by power246 on commit 84f7c0a. This supersedes
historical free-text recipe validation and nutrition-estimate failure behavior.

- Default `run.cmd` only delegates to tracked `tools/launch.py`; it never runs an
  ignored recovery script. The optional local compatibility helper is explicitly
  user-invoked and documented separately. Added a no-argument Windows fixture
  proving that a present ignored recovery script cannot replace the entry point.
- Optional fields are checked by iterating actual top-level keys, normalizing ID
  and string key encodings. Stock names and legacy goal text cannot impersonate
  nutrition or execution fields. Missing execution-next IDs are computed from
  existing records, without overwriting them.
- AI title/action enums and step ingredient IDs are validated and rendered from
  allocated stock; unallocated IDs and arbitrary ingredient prose are rejected.
  Unconfirmed old free-text menus are cleared; consumed menus and independent
  execution snapshots remain intact. No local recipe generator was added.
- Failed, malformed or timed-out nutrition estimates keep unknown references and
  continue once to online menu generation. Stale replies are rejected before
  queueing, preventing an old response from clobbering the current one. Explicit
  cancellation and changed state still invalidate results.
- Preserved unused original background artwork at `design/sunlit-pantry-bg.png`
  outside the bundle, keeping size headroom. The UI uses its existing shader;
  historical screenshots and legal notices remain unchanged.

Validation on isolated synthetic profiles with the official hidden native host:
**29 review-specific checks**, including a real process restart, plus **21 stock
checks** and **30 nutrition checks**. **19 automated tests passed**, including
both launch failure/help guards and the default-launch regression. Native
captures inspected; successful logs contain no script errors. Provider fixtures
are private copied bundles; none is distributed or used with real inventory.

Official source gate passed with the expected unsigned-source warning. Digest:
`efb77a17781ac5a706e0e71f27a35b357d5210faf6571f6c4e1e1797a99526bb`; bundle **6,863,810 bytes** (limit 8,388,608).
No keys generated, no real model calls, no user data edits, no release signing,
publication or review-thread messages. Live provider quality/accuracy, other
platforms and release installation remain unverified.

## Automatic online nutrition estimates and usable unknown stock, 2026-10-11

This supersedes the historical requirement for users to fill nutrition labels.
Physical stock availability is checked separately from nutritional references.
Online AI estimates missing per-100g energy, protein, fibre and vitamin C after
stock entry and before menu requests, and for unknown actual-food drafts.
Estimates are approximate and labelled with source, time and raw/cooked
assumptions. User-provided packaging references take precedence. Estimation
never changes quantity or confirms a meal; final actual confirmation freezes
its reference and provenance. Failure or ambiguity stays explicitly unknown,
with incomplete totals shown as the referenced portion, rather than fake zero.

- `tools/qa_ai_nutrition.py`: **30 native checks passed** with deterministic
  model fixtures in a private copied bundle. Covers physically available unknown
  stock, expired/zero/avoided exclusions, per-100g schema, estimates without body
  profile, request failure, duplicate keys, mismatched names and invalid ranges,
  automatic stock and outside-food estimates, actual arithmetic, source/time/
  assumptions, packaging corrections, draft cancellation and late replies,
  ambiguity, actual-estimate retry, three meals, 100% and immutable history.
- `tools/qa_stock_only.py`: **21 native checks passed again** on this behavior,
  retaining the stock-only restrictions, exact exhausted-batch removal and
  independent confirmed snapshots. The existing automated suite: **18 passed**.
- Final native captures were visually inspected. No script errors in successful
  logs. Official source gate passed with expected unsigned-source warning.
- Source digest: `cbc3411d1a8ef4dc945c0b7b1d7051aa93c6ea0bb03db4f709e386a044c4b59c`. Bundle: **8,387,990 bytes**
  (limit 8,388,608). No fixture dispatch is present in the distributed source.
- Stock/history tests used isolated synthetic profiles. No real user inventory
  writes or real model calls were performed for these tests; no keys generated.
- Full live-provider success, other platforms and release installation remain
  unverified. Menu quality and nutrition accuracy are not established by model
  fixtures. This remains a local editable candidate, not a published release.

## Stock-only menus and requested exhausted-batch removal, 2026-10-11

This supersedes the replenishment behavior described in historical entries.
Removed simulated replenishment and purchase UI, request schema fields and
stock-insertion functions. Ordinary and trial menus use online AI with existing
inventory only. Unknown IDs, aggregate excess quantities, missing-item output,
and unallocated known/inventory food names in recipe text are rejected.
Insufficient stock returns a reason and preserves current data.

- `tools/qa_stock_only.py`: **21 native checks passed**, using synthetic
  provider replies in a private test bundle. Includes exact exhausted-batch
  removal, preserving other stock and confirmed records, clearing old unconfirmed
  missing menus, missing/unknown/excess/text rejection, schema and UI removal,
  stock-only three meals, 33/66/100%, regeneration and history retention.
- Existing automated suite: **18 tests passed**. Native completed-trial captures
  inspected; successful run has no script errors. Source gate passed with the
  expected unsigned-source warning.
- Batch-removal markers only match ID, name, expiry and 0g; the separate marker
  prevents an older open window from restoring the requested exhausted batch
  after reload. Confirmed execution snapshots remain independent of inventory.
- Digest: `a46ae2352cdb10ddf9b5747ba001e1118e63880bb779ff7aceb70fee100b2b78`. Bundle: **8,377,163 bytes** (limit 8,388,608).
- Test data were isolated. The separately authorized user-stock removal is a
  backed-up operation, not test evidence. No keys, real model calls or purchase.
- Live provider success, other platforms and release installation unverified.


## Online-only menus, 2026-10-11 — editable candidate

This supersedes earlier local-rule behavior and validation descriptions below.
New ordinary and 1-day trial menus use official model.complete only. The status
no longer says manual generation; default requests still start on button clicks,
and multi-day automatic candidate generation remains optional.

- Removed the local generator, fixed trial templates and local-mode switch.
  Old local-mode settings migrate to online-only. Existing history is retained.
- Three-meal responses are validated as one update: exact unconfirmed slots,
  stock IDs, aggregate stock across meals, expiry/avoid rules, missing-item
  references and daily calorie budget. Confirmed slots keep their snapshots.
- `tools/qa_online.py`: **4 native checks** on the unmodified source in an
  unsupported host, proving no local ordinary/trial fallback or local toggle.
- **26 native checks** with deterministic provider fixtures in a private
  copied test bundle. Only host-request dispatch is substituted; production
  request builders, response callbacks, validators, persistence and confirmation
  are exercised. Checks include no-provider failure, ordinary AI routing, malformed
  and excessive responses, three AI meal snapshots, simulated replenishment,
  33/66/100% confirmation, preserved history and cancelled/stale replies.
  These are synthetic responses, not evidence of actual provider output.
- Existing automated suite: **18 tests passed**. Source admission passed with
  the expected unsigned warning. Successful native logs contain no script errors.
- Digest: `11605b65e1b382de1b2be772835eefa49faac76ff2f60d62aeebc2a3bdd8a6e7`. Bundle: **8,380,043 bytes** (limit 8,388,608).
- Native completed-trial screenshot inspected. No real inventory, credentials,
  purchase, model API bill, key generation, publication or release installation.
- Live configured-provider success, other platforms and sealed release remain
  unverified. Source launch rechecks the private compatibility snapshot on reload.


## Actual confirmation feedback fix, 2026-10-11 — editable candidate

- Cause: unknown stock nutrition and invalid optional calories shared an ambiguous
  error; rerendering the editor reset its scroll position.
- Inline stock-reference fields, separate named validation errors, and in-place
  notices now preserve drafts and scrolling. Blank extra calories count as zero.
  Stock references entered here belong to the confirmed execution snapshot.
- `tools/qa_actual_feedback.py`: **12 native checks passed** in a separate
  synthetic `qa-feedback-labels-final` profile, including unknown-reference
  rejection without writes, stable scrolling, successful stock deduction and
  snapshot preservation, and cancelling a label draft.
- Shared `tools/qa_day.py`: **30 native checks passed** in `qa-feedback-full3`
  before the final field-label-only edit. Its fill helper now supports clearing
  text and editors that intentionally retain their scroll position.
- Existing automated suite: **18 tests passed**. Source gate passed with the
  expected unsigned warning; final native log has no script errors.
- Final source digest: `3bc9c37849d862466a75de20c890d24201df544bfbd904703857d06412cbe573`. Bundle: **8,379,395 bytes**, below
  8,388,608 bytes. Native screenshot inspected. No real stock or provider calls.
- This updates the editable source. Existing open windows must reload the new
  bundle; release signing, submission and other platforms remain unverified.


## 1-day experience and independent execution ledger, 2026-10-11 — editable candidate

This development change supersedes the earlier statement that the script is
unchanged from 0.6.1. It has not been published or admitted. Primary health
programs remain 7/21/30 days; the 1-day experience is optional and local-rule only.

- Unmodified official Windows hub/card-host from the pinned 655114c4943cd2490daaefa2173e7b5aaa20669f toolchain.
- `tools/qa_day.py` in a task-owned hidden 1200x900 card-host, separate synthetic
  `qa-day10` data: **30 native acceptance checks passed**. Includes onboarding,
  optional selection/activation, three menus and missing ingredients, simulated
  replenishment preview/cancel/confirmation, actual stock substitution and
  changed grams, no writes before confirmation, 33/66/100% execution progress,
  invalid-quantity refusal, outside-stock intake without stock deduction,
  preserved recommendations and execution after regeneration, 100% review,
  subsequent health program, actual intake beyond reference goals recorded
  honestly, and history preserved when a menu is deleted.
- `tools/qa_day.py --restart`: **1 exact-state persistence check passed**,
  including inventory and all four confirmed execution snapshots.
- `tools/qa_day.py --legacy` in a separate synthetic pre-ledger profile:
  **4 migration checks passed**. Stock/plans/active program retained; existing
  multi-day programs received defaults; actual history was not invented.
- Existing automated suite: **18 tests passed**. Updated native smoke/preview
  expectations for the optional fourth candidate; their full legacy drivers
  were not separately rerun. New native QA above exercises the shared confirmation path.
- `tools/launch.py --hub <current-official-hub> --check` passed with the expected
  unsigned-source warning. No key generation, model API requests or real purchases.
- Final source digest: `22b0bff8e95428bb7876a6e946c409e86c001aef3a5e3cc96f7211f9322081bf`.
  Bundle: **8,376,659 bytes**, below 8,388,608 bytes (11,949 bytes remaining).
- Genuine native three-menu and completed-review captures were visually inspected;
  evidence remains outside bundle. Historical distributed screenshots remain historical.
- Successful final run, restart and migration logs contained no script errors.
  Intermediate compatibility failures were fixed by splitting confirmation and
  finalization into smaller functions; they are not passing evidence.
- Task-owned hidden previews were closed through their remote quit endpoints.
  The user's normal inventory and pre-existing run.cmd edits were untouched.

Full live-provider regression, other platforms, multi-stage combination editing,
new-machine installation and sealed-release installation remain unverified.
Confirmed record rules are documented in EXPERIENCE.md and ADR-0002.


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
