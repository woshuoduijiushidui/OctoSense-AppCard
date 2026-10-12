# Migration validation

## Issue #8 six-cycle candidates, merged onto the #2 rework

`bundle/main.splash` was reworked by Issue #2 while Issue #8 added the six-cycle
candidate picker, so this merge re-applies #8's feature onto #2's script instead
of a line merge:

- Cycles 1/3/7/15/21/30 with three profile-derived candidates each; each shows
  name, goal, execution trait, daily and cycle totals, and the difference from
  the cycle baseline. A seeded line-up means `重新生成本周期候选` replaces only the
  viewed cycle's unconfirmed candidates.
- The candidate/config migration is factored into `migrate_candidates`, applied
  to both freshly converted schema-1 states and current schema-2 states. It adds
  `cycle_seed` and rebuilds old-format candidates by shape (`variant` field), so
  user text (preferences, food names) cannot be mistaken for a field name.
- Verified live in the hidden official host after the merge: the cycle page
  renders the six lengths, switching cycles and regenerating the viewed cycle
  keep a confirmed plan and the other cycles untouched, and re-saving the profile
  from a non-default cycle returns the page and marker to 7 days. `hub check
  bundle --allow-unsigned` PASSED.

## Issue #2 foreground verification, 2026-10-11 — user reported pass

After installing digest `ba2d1a2bf588bd48a74c9c6112cfa706146375649c45cdff0fad5e2449498ff5`,
the user reported that the remaining manual checks listed under the historical
foreground checklist below passed: receipt and food-image import, OBS
camera recognition, cancellations and immediate retry, restart persistence,
adjacent profile/menu/consumption flows, and the official-host unsupported
image path. This is a user report, not an independently captured per-step log
or a fresh automated full-shell replay on this digest. The user explicitly
excluded demonstration-video recording from their task and this PR. The old
0.7.0 recording remains historical evidence only. Current synthetic-data
QA captures of the home, profile edit, inventory, image chooser,
official-host fallback, recipe, and consumption review are in `docs/qa/`.
They use synthetic data and do not claim to prove a real provider response.
The prior `main` screenshots were kept under `bundle/screenshots/` at
`af85d81f`; the PR review pairs them by screen while noting that the fixture
data and capture times differ.

Issue #2's four-way quantity distinction is not complete in this PR. The app
records confirmed stock, planned recipe use, and confirmed consumption, but
does not record or display pending-receipt quantities. Its purchase button is
still a placeholder. The simulated-order work in Issue #5 must retain each
pending food, quantity, and unit separately from actual stock, then add only
the quantities the user confirms as received. Issue #2 should remain open
until that integration is verified; this report does not count pending receipt
as passed.

During PR preparation, the pinned App Hub bundle check passed again and all
19 Pantry Python tests passed. The sandboxed run initially hit Windows
`PermissionError` in Python temporary directories; rerunning the same tests
outside that filesystem restriction passed without code changes.

## Issue #2 recipe wording, 2026-10-11 — installed and foreground replayed

The live MiniMax recipe exposed internal fields such as `nutrition_known=false`
and `profile` in its explanation, and `unknown expiry` / `food_id` in its
cooking steps. Recipe prompts now require user-facing Chinese in the title,
explanation, and steps. The app translates these observed internal terms when
saving new model output and when rendering previously saved plans, so the
existing accepted recipe needs no inventory migration.

Bundle digest: `ba2d1a2bf588bd48a74c9c6112cfa706146375649c45cdff0fad5e2449498ff5`.
The pinned Hub check and 19/19 Pantry Python tests passed. In a separate
synthetic official-shell profile, an existing saved plan containing the exact
raw terms rendered as readable Chinese in both its explanation and expanded
steps. The fixture was not copied from the person's inventory. After the user
closed the visible shell, this exact digest was signed, verified, and installed
into the same isolated MiniMax profile. The pantry JSON SHA-256 stayed
`60f59dd3930f36085eb8ceb83366cc18fc73336a94d75d28d265b7cfebda02d1`:
six foods, five inventory events, and one accepted/consumed recipe remain.
Exactly one local catalog matches the new digest. The user reopened that
profile in the foreground, expanded the saved recipe, and reported that none
of `nutrition_known`, `profile`, `food_id`, or `unknown expiry` appeared. This
confirms the saved-plan display; a new live MiniMax completion was not rerun.

## Issue #2 recipe generation with missing nutrition, 2026-10-11 — installed locally

The visible profile has seven confirmed food batches, four inventory events,
and no recipe candidates. None of its seven batches has a complete per-100-g
nutrition reference, so the earlier generator discarded every batch before
calling the model. Some count items also lack an average item weight, and one
package item lacks a package conversion. No private inventory was used as a
test fixture.

Generation now prefers batches with complete nutrition and convertible grams
for numeric planning. If there are no such batches, it uses eligible stock in
native g, ml, or piece units to create a recipe marked `营养未核算`. Expired or
excluded stock remains ineligible; unknown expiry requires a freshness check.
Package stock without a conversion remains ineligible. The model request for
this path omits nutrition totals and numeric cycle budgets. Accepting the
recipe and confirming consumption deducts the actual native quantities and
records a meal with `nutrition_known: false`; it does not add invented kcal or
nutrients to cycle totals. The profile labels numeric balances as known-only.

Final bundle digest: `031cc4e93300982d9afdcd507af997a928a8ebf1471ead540d8b53e5462ba58e`.
Pinned Hub check and 19/19 Pantry Python tests passed. On the preceding
`1b277a009256be8536f20f16a782c7765e07f48d5ad1117f07d7e7728de79e1a`
digest, the unmodified official shell passed 27/27 existing UI/data checks,
2/2 restart checks, 2/2 focused unquantified-recipe checks using a count item
without an average weight, and a focused unquantified-meal restart check. The
final edit restores strict legacy-state validation and treats only explicit
`numeric: false` plans as unquantified. On the final digest, a synthetic
official-shell profile loaded its prior unquantified meal, then generated and
confirmed another count-item recipe; inventory decreased and neither cycle
kcal nor weekly nutrients were invented. A separate synthetic g-quantity
replay on an earlier digest also verified inventory deduction and zero added
kcal. The `ce016c254f0768019a1efeab8c6f6e9577aa78b869f84ebab97d09057d9e735b`
digest entered `model.complete` and reported the expected `no_provider`
result because that synthetic profile has no model credentials. After the user
reopened the final digest in the visible isolated host, a read-only check found
one new candidate persisted with source `在线 AI · 营养未核算`, five inventory uses,
and no acceptance or consumption. The live UI showed the candidate title,
unquantified source, and `就吃这套` action; the seven food batches and four
inventory events were unchanged. The host produced an online recipe result.
The user previously reported MiniMax `Connected`; the provider identity was
not independently inspected during this recipe call. This is a text recipe
completion, not evidence of image recognition, which was still pending then.

After the user closed the visible shell, the final digest was signed, verified,
and installed into the same isolated MiniMax profile using existing local test
keys. The profile JSON SHA-256 remained
`472c26fa4dd699422719957dacfc1a991e60e859fceb2d1e0af2c54d3e5e3a8e`:
seven foods, four events, zero plans, and completed onboarding immediately
after installation. The later visible run created the candidate described
above. Receipt import, cancellation, and video checks were still open then.

## Issue #2 profile return and selected controls, 2026-10-11 — installed locally

The inventory date inputs now have separate full-width rows in onboarding and
the regular inventory form; a native capture showed the complete date
placeholder. Expanded inventory rows and the consumption review use a
per-food `第 N 批` label without exposing the global storage ID.

`重新设置用户画像` now opens an editable three-step profile flow. The existing
profile and inventory stay on disk while it is open. `取消修改 · 返回设置`
restores the original in-memory state from any step; closing the host before
confirmation also leaves the saved profile intact. Confirming a new cycle
plan saves the edited profile and returns to Settings without repeating the
initial inventory step. Selected scene, sex, activity, cycle plan, meal-goal,
unit, draft-row, and navigation controls use a dark fill and light text.

The 0.8.0 bundle digest is
`aeb5dccc946b5a289b05aeade5ee896f468750e206b175c3472b7287000b547d`.
Pinned Hub check and 19/19 Pantry Python tests passed. In task-owned profiles,
the unmodified official shell passed 27/27 UI/data checks and 2/2 restart
checks. A separate focused replay verified profile cancel leaves the saved
JSON byte-for-byte unchanged, successful confirmation preserves the foods and
events, and closing mid-edit restores the prior profile on restart. Native
captures covered the date field, selected controls, and per-food batch label.
After the user closed the visible host, the exact bundle was signed, verified,
and installed into the existing isolated MiniMax profile with the existing
local test keys. The profile JSON SHA-256 stayed
`e9d0e54235447b6b917679fc5aa4896b910e0410e58a02da49153f7efca76701`:
seven foods, four inventory events, and completed onboarding remain. Exactly
one local catalog matches the new digest. The user's foreground view of this
bundle, receipt import, remaining cancellation stages, and a final video were
still pending at this checkpoint.

## Issue #2 chooser retry and inventory labels, 2026-10-11 — installed locally

After a native file-picker cancellation, the user saw an occasional
`foreground_required` error on an immediate second attempt; waiting restored
the import path. The host checks that the requesting app is the active
foreground surface. Pantry now treats this specific error as retryable: the
picture chooser stays open, explains that the user should click the Pantry
window, and keeps `选择已有图片` and Cancel available. A normal file-picker
cancellation still returns to manual inventory input. No host permission check
was relaxed and no automatic second import is sent.

Recognition draft rows now show the compact `✓ 已选中` / `○ 未选中` status, with
an adjacent explanation that only selected rows are confirmed. Inventory
groups continue to show their own batch count. Expanded rows now use `第 N 批`
for the position within that food and identify the persistent global key as
`库存 ID #N`; the consumption selector uses the same ID terminology.

Stamped 0.8.0 digest at that checkpoint:
`04d8bd5ccf1fdcd7cf45ea8b72fc9ebd7815def3e6bd68ff89ee62502b4d5e3b`.
Pinned Hub check and 19/19 Pantry tests passed. In task-owned
an isolated test profile, the unmodified official shell passed 26/26
UI/data and 2/2 restart checks. Native captures showed both selection states
fully visible and a milk row labelled `第 1 批` with a separate global ID.
A task-only bundle injected the exact host error:
the chooser retained its retry and cancel buttons, showed the focus hint,
and left foods/events unchanged; the fixture was not shipped. The restamped
bundle was signed, verified, and installed into the existing isolated MiniMax
profile with existing local test keys. Its six foods, three inventory events,
and completed onboarding were unchanged; one mirror matches the new digest.
The actual native cancel/immediate-retry timing still needed a user foreground
replay. Receipt import, remaining cancellation stages, and a final video were
also pending at this checkpoint.

## Issue #2 recognized-unit correction, 2026-10-11 — installed locally

The foreground custom host showed a real OBS Virtual Camera preview and returned
five editable rows from a MiniMax image request. One row was `Green Onion`,
quantity `2`, unit `bunch`; this unit is outside Pantry's eight selectable
inventory units and blocked the selected-row confirmation. The user corrected
the draft by excluding that row, confirmed the remaining rows, and closed the
host. The isolated profile now contains four `food_image` batches with app-local
image paths and one inventory event; onboarding is complete. This is live
provider/camera/confirmation evidence for that one image. Receipt import,
stage-by-stage cancellation, and final video remain unverified.

The 0.8.0 bundle digest at that checkpoint was
`83fec87ae1f98177285c2b996a19b4a7f2f2cbaab8041990fa7136cd32cfd772`.
Recognition now retains only the eight inventory units shown by the UI; unknown
units become blank and require an explicit choice. Unsupported package-size
units also become blank. The draft labels its current selection state, reports
the row and reason beside the confirmation button without resetting scroll,
and makes unfinished-draft actions visibly unavailable. The bundle was
restamped, signed, verified, and installed into the same isolated profile using
its existing test keys; provider settings and inventory were preserved.

The pinned Hub check and 19/19 Pantry Python tests passed. A task-only response
fixture returned `2 bunch` and `2 个`: the first row displayed an unselected
unit, confirmation refused it without writing inventory, then choosing `个`
produced two batches in one event and allowed onboarding to finish. This
fixture was never shipped. The unmodified official shell passed 26/26 UI/data
checks and 2/2 restart checks on the exact current bundle in an isolated
test profile; both image buttons retained the manual fallback.
The updated unit behavior has not yet been replayed by the user in the real
foreground MiniMax host.

## Issue #2 camera consent visibility repair, 2026-10-11 — foreground preview verified

The user reported that both buttons on the camera screen appeared inert. A
read-only snapshot of their running host found a live `DevicePermissionPrompt`
with `Continue` and `Not now` buttons above the app, although the user's screen
showed only the Pantry camera card. An isolated replay reproduced the invisible
sheet: Pantry's root `GlassPanel` moved its children into an overlay draw list
above the native consent sheet, while the sheet still captured clicks.

The root app surface now uses a normal `RoundedView` and the camera stage shows
an authorization hint plus the camera's native error text on failure. With the
restamped 0.8.0 digest
`e01f367bf455c41fa8b4d1e6b2b6c3cf5cba71938ab2c09cf00475f6e5f3f925`,
an isolated local-host installation rendered the native camera-consent sheet
clearly on top of Pantry. Choosing `Not now` returned to manual entry with a
visible authorization message. The pinned Hub gate and 19/19 Pantry tests
passed; the unmodified official full shell passed 26/26 UI/data and 2/2
restart checks in an isolated test profile. Native `Continue` requires a
physical foreground click and was not automated. After the user relaunched the
visible host, a read-only remote capture showed the OBS Virtual Camera image
inside Pantry's camera preview. Capture, file selection, MiniMax image
completion, and the final video remain unverified. After the user closed the
previous visible host, the new bundle was signed,
verified, and installed into the existing isolated MiniMax profile without
regenerating keys or changing provider settings. Foreground capture and model
replay are pending.

## Issue #2 foreground chooser visibility repair, 2026-10-11 — awaiting user replay

The user opened the real local-host Pantry window and reported that the photo
recognition screen was dark with unreadable controls. A remote snapshot showed
that the `打开摄像头` and `选择已有图片` widgets existed, but a native capture confirmed
the full-screen dim layer covered their text. An isolated test of draw-list
batching did not fix the image. The recognition chooser was then moved into the
main app body as a centered, readable screen; the overlapping dim layer was
removed. The same selected camera/import/model states and cancel action remain.

The 0.8.0 digest at that checkpoint was
`849dd4d7b721076d41d57bd603900d398c23a39b83d9fdb60300885a322d4af9`.
The pinned Hub gate passed, and Pantry tests passed 19/19. The first sandboxed
test attempts hit Windows ACL failures in Python's temporary directories; the
same 19 tests passed when their process could access its own temporary files.
An isolated local-host installation with the exact bundle digest displayed the
chooser title, both buttons, and Cancel in native captures from onboarding and
the later inventory tab. Both photo and receipt chooser cancellation left zero
foods and inventory events in onboarding; a later inventory-tab cancellation
left its existing inventory event count unchanged and restored manual entry. On the same
new digest, the unmodified official full shell passed 26/26 UI/data checks and
2/2 restart checks in an isolated test profile. The new bundle was
installed into the original isolated MiniMax profile after the user closed the
old window. Foreground user replay, native file selection, camera capture,
actual Pantry MiniMax image results, and final video are still pending.

## Issue #2 documentation and manual handoff, 2026-10-11 — local preparation complete

At this handoff checkpoint, the 0.8.0 bundle had `storage`, `model`, `camera`, and `files` grants,
the optional `camera.permission.request@1` host API, and digest
`0f08bd1b1044e56b70f66e1d6af45be56cff01ff1cf8d37aedc611961171cbb5`.
The later chooser repair above changed the bundle digest. Its listing was
reviewed against the image-recognition evidence; no bundle bytes changed during
this documentation pass.
The bilingual READMEs, privacy policy, review answers, submission checkpoint,
and historical brief now distinguish the official manual fallback from the
Windows local-host image path. The four bundled screenshots and existing video
are explicitly labelled as historical 0.7.0 manual-flow material. New captures
must come from a real foreground demonstration, so they were not replaced.
Older sections below are point-in-time evidence, not claims about today's bundle.

Repository handoff: Pantry is on
`feat/issue-2-pantry-inventory-multimodal` at HEAD
`af85d81f0027507ec2a74f3b1afe4838b9371257` (base `main` at
`d6d08d1ccf67b785ecf8813ea3b5a0eb6be04588`). Its earlier inventory,
menu, image-intake, and documentation work shares 21 modified tracked paths and
remains uncommitted; an isolated documentation commit
would misleadingly include earlier edits. OctoSense is on
`feat/pantry-steward-vision-bridge` at local HEAD
`808005eaabe00b60f4fc37cc1967e4fa4fc061a2` (base `main` at
`40ca21da68cc05ae930931adcfcf6d382d49ec26`) with a clean worktree.
No branch was pushed, no production identity was used, and no release, Hub
submission, or upstream platform PR was made.

### Historical foreground checklist — later user-reported pass

The checks used an isolated test profile, synthetic fixtures, and OBS Virtual
Camera. API keys stayed in the host-owned AI providers page. The user launched
the local test host from their own PowerShell so native windows had foreground
access.

The local test launch selected the then-stamped 0.8.0 bundle and started the
modified release host in a foreground window. The configured
`minimax-cn / MiniMax-M3` had shown `Connected` in AI providers; that host
connection check is prior user-reported evidence, not a Pantry image result.
At this earlier checkpoint, the following checks were pending. The user later
reported that checks 1–5 passed; see the current report at the top of this
file. No per-step log was independently captured. Model outputs must be judged
as actual provider results rather than fixed fixture rows:

1. Before recognition, note inventory count and event count. Click `导入小票`
   then `选择已有图片`; select the synthetic receipt image.
   Check that the real model returns an editable draft, uncertain values remain
   blank, and no inventory changes before confirmation. Edit one field,
   deselect/remove a row, confirm selected valid rows once, and inspect the
   resulting separate batches/events.
2. Click `拍照识别` then `选择已有图片`; select the synthetic fridge image.
   Check the food-photo prompt, editable rows, and final confirmation. Model
   names, row counts, and units may vary; correct them rather than assuming the
   synthetic illustration proves recognition quality.
3. Exercise the camera path from `拍照识别` → `打开摄像头`; personally grant host
   consent if asked. Check the OBS preview, then `拍照并识别`; verify that capture
   yields an app-local image and a real editable model draft. Use an OBS image
   source with the synthetic fixture if avoiding personal imagery. Camera
   source selection is automatic in the current minimum demo.
4. Cancel once in the chooser, native file picker, camera preview, model wait,
   and draft review. Compare inventory/events before and after each cancellation;
   manual entry must still work. Immediately retry `导入小票` after canceling
   the native file picker. If the host briefly returns `foreground_required`,
   confirm Pantry remains on its picture chooser with a focus hint and an
   available `选择已有图片` button; click the Pantry window and retry. A request
   already sent to a provider may still be billed after the app stops waiting.
5. Restart the same isolated profile; verify confirmed batches persist and
   adjacent dietary profile, menu, and consumption flows remain usable.
   The unmodified official full shell already passed 26 UI/data checks and two
   restart checks with the **same digest**. A human visual spot check of both
   official-host image buttons should show `当前宿主暂不支持图片识别，请使用手动录入`, without
   a chooser or recognition call.
6. Review screenshots and host logs for secrets or personal paths before
   sharing. Review the public support/privacy links and final release identity
   separately before publication. The user later excluded new video recording
   from this PR; the current synthetic inventory comparison only illustrates
   UI changes.

## Issue #2 image-intake verification, 2026-10-11 — earlier checkpoint

At the first image-intake checkpoint, the unpublished Pantry 0.8.0 bundle
digest was
`0f08bd1b1044e56b70f66e1d6af45be56cff01ff1cf8d37aedc611961171cbb5`.
`python -X utf8 tools/launch.py --hub D:\projects\GOSIMAPP\OctoSense\target\release\hub.exe --check`
passed; `python -X utf8 -m unittest discover -s tools -p 'test_*.py' -q`
passed 19/19 with the test process allowed to clean its own Windows temporary
directories. The locally modified OctoSense branch passed
`cargo test --locked --offline -p octosense-llm-service --test complete -- --test-threads=1`
(23/23), `cargo test
--locked --offline -p octosense-shell --features app-hub platform_services --lib
-- --test-threads=1` (12/12), and `cargo build --release --locked --offline -p
octosense --no-default-features --features octos-core,app-hub`. The unchanged
official release executable was preserved separately in ignored `target` before
that custom build. Both worktrees were checked for credential-shaped values and
tracked/untracked key, profile, app-data, log, or build artifacts; none appeared
in the changed file lists. OctoSense's tracked tree remains clean.

The unmodified official full shell with that earlier bundle in an isolated
test profile passed all 26 `tools/smoke.py` UI/data checks and
both restart checks. Both recognition buttons displayed the exact unsupported
message without a chooser; manual inventory, menu, consumption, and profile
flows worked. The negative `begin_recognition` path returns before file, camera,
or image-model requests, and the isolated host created no model ledger. This
supports zero admitted model calls; no separate request trace was captured.

The locally modified OctoSense release host opened the shared chooser using
the same bundle and a task-owned profile configured for `minimax-cn / MiniMax-M3`.
Before a provider call, cancel left zero foods and zero inventory events. Native
UI capture exposed a retained overlay after cancel; the bundle now toggles the
overlay view's visibility, and a new capture confirmed that the chooser closes
and manual entry remains usable. This change was restamped and reinstalled.
No real MiniMax image result, Pantry camera capture, native file import, or
final demo video had yet to be verified. Those checks needed a foreground host
window launched from the user's own Windows terminal; the agent's shell has no
Windows foreground window and cannot complete the native chooser or consent.

## Issue #2 image intake, 2026-10-11 — local implementation

The unpublished `pantry-steward` 0.8.0 bundle has `storage`, `model`, `camera`,
and `files` grants, declares the complete shell's `host-api-v1` device-consent
broker, and has digest `09543dcb848f92e32bc4565a7483c7abef5f1c144ada64090b171224a4d5c4c0`.
The pinned `hub.exe stamp bundle` and `python -X utf8 tools/launch.py --hub
<OctoSense>/target/release/hub.exe --check` passed. `python -X utf8 -m
unittest discover -s tools -p "test_*.py" -v` passed 19/19 when run with a
task-owned temporary directory; the managed Windows sandbox ACL blocked
`tempfile` cleanup in the first attempt, so that run was repeated with the
test process allowed to clean its own temporary files.

Local test signatures installed the unchanged final bundle into isolated full
shell profiles. The unmodified official release shell passed 26 checks from
`tools/smoke.py` in an isolated test profile, plus two restart checks. The
exact final bundle then passed a focused official fallback check in a second
isolated profile. Both image buttons displayed
`当前宿主暂不支持图片识别，请使用手动录入` without an image chooser;
manual inventory, menu, and consumption flows still passed. In source,
`begin_recognition` returns on that probe result before the chooser, file API,
or image `model.complete`; no separate host-call trace was recorded. The
locally modified debug shell at OctoSense commit `808005e` passed the positive
capability,
shared camera/file chooser, cancellation, and zero-inventory-write checks in
an isolated profile with the exact final bundle. An ignored, task-only
model-response fixture passed receipt/photo draft, row edit/removal, two-batch
single-operation add, cancellation, and unavailable-provider-to-manual checks
in another isolated profile. Fixture responses were never shipped in the
bundle. No real image was sent to MiniMax/Kimi from Pantry at this checkpoint;
camera capture inside the full Pantry UI, real image recognition, and a new video
remained for later foreground verification. The standalone `card-host` could
not admit this bundle because it lacked the required device-consent broker;
the official fallback was tested in the unmodified full shell.

Pantry was on `feat/issue-2-pantry-inventory-multimodal` at `af85d81` with
earlier inventory and menu work already uncommitted before image intake. The
image-intake changes were left uncommitted to avoid combining earlier work into
a misleading isolated commit. The locally modified OctoSense branch was clean at local commit
`808005e`. Neither repository was pushed or published at this checkpoint.

## Issue #2 host readiness, 2026-10-11 — incomplete at this checkpoint

The unmodified OctoSense source at
`40ca21da68cc05ae930931adcfcf6d382d49ec26` passed the locked release
build during official-host verification. This check reused that exact executable;
a redundant build retry was stopped before completion. No tracked OctoSense
source was changed for this check.

After explicit user approval, the 0.7.0 Pantry bundle was signed with local
test keys, verified and installed through App Hub in
an isolated test profile. The full official desktop launched its onboarding
page from that profile. No production signing key or personal pantry data was
used. A separate ignored host API probe bundle was signed and installed
for host API rehearsal. With a synthetic 345-byte PNG selected through the
native chooser, `files.import` returned an app-local PNG path; the file in the
probe's app jail was byte-identical to the selected image. A later second
import was refused with `foreground_required` when the app was no longer the
native foreground window; the earlier import remained intact.

The user enabled OBS Virtual Camera for the rehearsal, but the unmodified
Windows host refused `CameraPreview.start()` with `this app was not granted the
camera`. Its device-consent request API is currently limited to Android and
macOS, while the installed app runner applies host-managed consent on Windows.
Camera capture and its app-local return path have therefore **not** been
verified. The user configured MiniMax in the isolated host's AI providers UI
and reported `Connected` from `Test connection` on 2026-10-11. That host test
sends a small real provider request; this result was observed by the user,
not independently through Pantry's `model.complete` path. Camera capture and
the Pantry image-recognition path were still open at this checkpoint.

## Issue #2 local handoff, 2026-10-11 — unpublished at this checkpoint

Pantry branch: `feat/issue-2-pantry-inventory-multimodal`; local HEAD:
`af85d81f0027507ec2a74f3b1afe4838b9371257`. The working tree contains
uncommitted source, tools, docs, listing, manifest, and screenshot edits.
The two `.local-planning/` milestone sets remain ignored and local-only.
The official OctoSense checkout is on `feat/pantry-steward-vision-bridge` at
`40ca21da68cc05ae930931adcfcf6d382d49ec26` with no tracked changes.

The unpublished source candidate is `pantry-steward` **0.7.0**. Its listing
describes manual units and batch grouping, the separate consumption step,
offline/online evidence limits, and unavailable image/voice features. Four
historical screenshots were replaced with genuine 1800×1200 PNG captures
from the edited bundle in an isolated official Windows card-host using
synthetic data: home, local-rule candidate, consumption review, and grouped
inventory with batch details. They were visually inspected. The older video
was not revised and remains outside `bundle/`.

After those bundle changes, pinned App Hub commit
`8347a489141c0e24cab564883db7c4592935a8b2` stamped digest
`4df2bd4f4613b336a6782683dfec745e75423d75cc96f36122136acc222f512f`.
`python -X utf8 tools/launch.py --host-workspace D:\projects\GOSIMAPP\OctoSense
--app-hub-source D:\projects\GOSIMAPP\OctoSense\target\dependency-probe\app-hub
--check` returned `pantry-steward 0.7.0 — PASSED`, with the expected unsigned
source warning. Bundle bytes excluding manifest: 4,849,230 / 8,388,608.
No production signing identity or local test key was used.

After the 0.7.0 restamp, a fresh isolated official card-host profile passed
all 26 `tools/smoke.py` UI/data checks; a restart of the same profile passed
both persistence checks. The 19 Python `tools` unit tests passed under ordinary
Windows permissions, including the updated version/listing guards. Sandboxed
Python test attempts could not create temporary files because of Windows ACLs;
their metadata assertions were updated before the successful normal-permission
run. The unchanged business script had already passed the full pinned parser
and 33 source-extracted VM cases during official-host verification; these were
not rerun for the later metadata and screenshot edits.

Full Store installation, live model-provider calls, other platforms, sealed
publisher pack verification, current remote privacy-page review, App Hub
admission, and competition qualification remain unverified. The existing
publisher-toolchain.json and tag workflow still pin the earlier App Hub
`655114c4943cd2490daaefa2173e7b5aaa20669f`, rather than the host pin
used here; the publishing route must be reviewed before any 0.7.0 tag.
No commit, push, tag, release, review issue, or submission was made for this
candidate.

## Issue #2 official-host verification, 2026-10-11

The initial official-host retry waited for the default Cargo cache lock held by
a separate background download, then stopped without interrupting it. A later
Git CLI/OpenSSL retry fetched the pinned Git dependencies and passed
`cargo build --release --locked -p octosense` on the unmodified official
checkout (80m 37s). `target/release/octosense.exe` is 514,735,104 bytes;
OctoSense tracked files remain clean at `40ca21da68cc05ae930931adcfcf6d382d49ec26`.
The pinned App Hub `hub.exe`, `card-host.exe`, and `pantry-local-install.exe`
also built in release mode. No tracked OctoSense source was changed.

The exact pinned App Hub commit `8347a489141c0e24cab564883db7c4592935a8b2`
is present in an ignored task-owned sparse checkout. `tools/launch.py` now
accepts `--app-hub-source` and verifies that source's commit and clean status
against the official host pin. The Python tool suite passed 19 tests with normal
Windows permissions; sandbox-only temporary-directory ACL failures were not
application failures. The official `hub` CLI refused a stale digest as expected.
After the final source edit in this verification pass, `hub stamp bundle` wrote
`fc160ecda2e1f144dad4b54ee01424d7fc4876e03fac806b4fef501c6f6dea83`;
`python -X utf8 tools/launch.py --host-workspace D:\projects\GOSIMAPP\OctoSense
--app-hub-source D:\projects\GOSIMAPP\OctoSense\target\dependency-probe\app-hub
--check` passed with the expected unsigned-source warning. The bundle is
8,371,753 bytes excluding its manifest, below the 8,388,608-byte gate. Its
background PNG was recompressed losslessly to keep the bundle within that gate;
all non-IDAT chunks and the decompressed image data were preserved.

The official pinned card-host admitted the bundle in hidden standalone mode
with task-owned app data. A native UI run found that the first manual intake
form was blank; moving its dynamic controls directly into the active render
tree fixed it. The updated `tools/smoke.py` passed 26 UI/data checks on a fresh
isolated profile and its `--restart` mode passed both persistence checks.
The checks cover onboarding, atomic rejection, manual preview/add/edit/discard,
unit and package conversion, grouping, all four freshness labels, disabled
image buttons, fallback when the model service is unavailable, local rule and
automatic generation switches, candidate creation and acceptance, consumption
cancellation and confirmation, plan deletion, profile edit and restart. The state file was
byte-identical across restart. A second isolated card-host loaded a synthetic
schema-1 file, migrated and saved it as schema-2, and preserved profile fields,
two batch IDs, plan ID, program history, log and next IDs across restart.
The complete bundle passed the pinned script parser; 33 source-extracted VM
cases passed after the UI edit. No test keys, signing identity, production data,
provider credentials or live provider request were used. Full Store installation
requires the separate test-key approval in `AGENTS.md`; release version/listing,
current screenshots and live-provider validation remain open.

## Issue #2 non-multimodal plan and offline recheck, 2026-10-11 — uncommitted

At the earlier plan split, the local-only milestone covered the active profile/manual-inventory/menu plan
and `.local-planning/deferred-multimodal/` for image recognition, the local
OctoSense bridge, custom-host video, and related release claims. Neither plan
is distributed. At that point the Pantry source still had disabled image buttons;
there was no recognition request or OctoSense source patch. The image-intake section
above records the subsequent local implementation.

The full edited bundle passed the pinned Makepad parser. Two ignored harness
generators extracted functions from the current script; all 33 resulting VM
cases passed. Their storage commit and some host/UI calls are stubbed, so this
is offline behavior evidence, not native persistence or rendering. The 18
existing Python tests passed under ordinary Windows permissions. A sandboxed
attempt failed in Python temporary-directory ACL operations and was rerun;
no product assertion failed.

Both READMEs, PRIVACY.md, and the small historical brief/review/submission
notes now distinguish this uncommitted feature branch from the earlier 0.6.2
candidate. `bundle/listing.json` and `bundle/manifest.json` still identify the
old candidate. The current source digest now passes the pinned official Hub
gate, but final versioning/listing and a subsequent restamp are needed before
distribution.
The subsequent official-host verification section above supersedes the
dependency and native-check limits of this earlier offline checkpoint. No test
keys or provider credentials
were created, and no source was changed in OctoSense.

## Issue #2 local UI and menu compatibility, 2026-10-10 — uncommitted at this checkpoint

The Pantry feature branch now has separate allergy, avoidance, and preference
inputs; one editable intake draft for manual and future image rows; grouped
inventory summaries with batch detail actions; and menu uses that distinguish
confirmed quantity/unit from estimated grams. Count consumption deducts pieces,
while mass consumption deducts grams. Automatically generated menus use known,
non-expired dates in expiry order; the consumption review can switch to another
compatible batch, including one with an unknown date. Expired, volume, and
unconverted package batches are excluded from gram-based menu generation.

The task-owned ignored parser harness extracts actual script
functions and passes 19 focused Makepad VM cases for migration, calendar boundaries,
multi-row atomic confirmation, profile revision staleness, grouped totals and
freshness, manual edit/discard, rule/model menus, plan acceptance, cancellation,
count deduction, manual unknown-date allocation, and plan deletion. Its storage
commit and some host/UI functions are stubbed. The full bundle passes the pinned
script parser, and the existing Python `tools` suite passes 18 tests.

Native UI, filesystem restart, and the official bundle gate were not run. The
official OctoSense build did not reach compilation: Cargo stopped at another
pinned Git dependency, `octos-org/octos` revision
`18fcd3f16e527d2b601d7ae244f056fb711bb6b8`. The current
`tools/launch.py --host-workspace ... --check` exits because its pinned App Hub
checkout is still missing. The edited bundle's manifest
digest still needs an official Hub restamp. No local test keys were generated.

## Issue #2 local inventory data work, 2026-10-10 — uncommitted at this checkpoint

The Pantry feature branch contains schema-2 migration, unit and expiration
normalization, and one confirmed-inventory mutation boundary in
`bundle/main.splash`. The pinned Makepad script parser accepts the complete
bundle. Seven focused VM cases using the bundle's actual data-core functions
passed: representative schema-1 migration and JSON round trip; all supported
unit labels and expiration boundaries; add/edit/discard/consume, duplicate ID,
and atomic rejection; confirmed package conversion; zero-quantity removal;
confirmation-day expiry conversion and cancellation; and built-in demo data
migration. At this checkpoint the manual UI still exposed only grams; the
later UI work above added other units, unknown expiry, and confirmed printed
dates. The task-owned parser harness was ignored by Git; its commit
function is stubbed, so this is not native filesystem or host launch evidence.
The existing `tools` unittest suite passed all 18 tests. `git diff --check`
passed. The editable bundle's manifest digest has not been restamped; the
official host bundle gate, native restart, and real-provider flows were not
run while the Cargo dependency download remained incomplete. No local test
keys, publisher artifacts, or release were created.

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
