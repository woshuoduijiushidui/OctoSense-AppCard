# Pantry Steward · 冰箱管家

English | [简体中文](README.zh-CN.md)

Turn confirmed pantry inventory into a meal you can review and execute.

## Version and evidence

This checkout is the editable **0.6.2 candidate**, correcting publication metadata and the standalone launcher. This editable checkout now adds the optional 1-day experience and independent confirmed execution snapshots; it is no longer script-identical to 0.6.1. [Issue #99](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/99) requests review of **0.6.1**, not this candidate. Neither is claimed as admitted.

Only Windows is claimed: the current pinned tools passed source admission and a limited native smoke test. Full 0.6.2 live-provider regression, new-computer installation, full functional regression and sealed-release installation remain unverified. See [VALIDATION.md](VALIDATION.md).

## What it does

Confirm a dietary profile and a 7/21/30-day cycle; preview inventory batches; generate an online-AI candidate through official model.complete; review recipe steps and quantities; accept it; separately confirm actual consumption before deducting inventory and recording intake. Daily/cycle values are prototype estimates. Archive a cycle without deleting stock.

Click Generate to request online AI by default. Optional automatic generation must be enabled in Settings; acceptance and consumption still require confirmation. Deleting a plan does not restore inventory or erase meal records. See [cycle details](CYCLE-PLANS.md).

## Optional 1-day experience

Keep the primary 7/21/30-day programs, or explicitly select the 1-day experience after profiling. Ask online AI to generate breakfast/lunch/dinner, using only available inventory. There is no replenishment or purchase flow; insufficient stock produces an explanation instead of a missing-ingredient menu. After each meal, edit actual foods and quantities, including stock substitutions and food eaten outside the fridge. Only final confirmation writes intake, completion and stock changes. Three confirmed slots reach 100%; the review separates execution progress from estimated nutrition goals and links to the next health program.

Users only need food names, grams and expiry. Online AI automatically estimates per-100g calories, protein, fibre and vitamin C for unknown stock after entry and before menu generation. Adding outside food or an unknown stock substitution also estimates the actual draft. AI estimates show their source and raw/cooked assumptions; optional package labels take precedence. Final confirmation freezes the reference used with actual quantities. Estimation never deducts stock or confirms a meal. Failed or ambiguous estimates stay explicitly unknown, rather than zero. Menu/trial estimate errors, malformed replies or timeouts continue once to online menu generation with unknown references; actual grams can still be confirmed and incomplete totals are labelled. Blank optional extra calories count as zero.

Confirmed `execution_records` preserve recommendation and actual snapshots independently and survive menu regeneration, deletion and cycle changes. These same rules apply to newly confirmed meals in multi-day programs. Old unconfirmed trial menus that require missing ingredients are cleared on migration; confirmed history stays intact. Exact exhausted-batch removal requests are stored in inventory-removals.json and replayed on load only when batch ID, name, expiry and zero grams match. Historical records without actual details are not reconstructed from old recommendations. See [experience and record rules](EXPERIENCE.md). Multi-stage combination editing is outside this change.

## Demo

[Recorded demonstration](video/演示视频.mp4)

![Historical Windows capture](bundle/screenshots/01-main.png)

[Candidate](bundle/screenshots/02-plan.png) · [Consumption](bundle/screenshots/03-confirm.png) · [Inventory](bundle/screenshots/04-updated.png)

These are historical genuine Windows captures, not phone screenshots or complete 0.6.2 live-model evidence. The video stays outside the distributed bundle.

## Windows source launch

This is an app-only repository, not its host or an installer. Use root run.cmd, not the absent apps/pantry-steward/run.cmd path.

Prerequisites: Git, Python 3.11+, Rust, Windows C++ tools and Windows SDK. Follow the [official Quickstart](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/QUICKSTART.md) to prepare the current native workspace and build hub/card-host. Reuse shared frameworks at the exact official pins; an old cached binary is not equivalent.

The workflow pins App Hub 655114c4943cd2490daaefa2173e7b5aaa20669f. Its unmodified source and lock file were used to build the local gate. A complete cold-download/build on a fresh computer remains unverified.

Assuming the tools repository is the sibling OctoSense-App-Hub, run from this app directory:

```cmd
run.cmd --hub ..\OctoSense-App-Hub\target\release\hub.exe --check
run.cmd --hub ..\OctoSense-App-Hub\target\release\hub.exe --card-host ..\OctoSense-App-Hub\target\release\card-host.exe --standalone
```

--hub --check needs no host workspace or keys. --standalone uses official card-host to inspect the UI and service-unavailable behavior; it provides no model service, cannot generate menus, and is not a Store install. --app-data selects an isolated test directory; preview defaults to .local-state/standalone. Back up needed data before deleting it.

The launcher checks the existing digest without silently repairing it. VALIDATION.md records the current source digest. Old Windows hub builds hash paths differently and may misclassify license URLs. Update the tools after refusal; do not remove legal notices, widen grants, bypass the gate or restamp a sealed release.

The old --host-workspace / --prepare-local-test route is retained only for isolated historical 0.6.1 compatibility rehearsal, not recommended for this candidate. Local test-key creation outside Git requires separate human consent; none was performed in this repair. Original host workspaces and inventory were untouched.

Live AI requires a compatible OctoSense host serving official model methods, configured in its AI providers panel. These card-host commands cannot test it. The final sealed pack also requires publisher-github-v1, with a compatible released host still pending. Installation and complete online behavior are not claimed as verified.

The tracked `run.cmd` always delegates to `tools/launch.py`, even if an ignored local recovery file exists. On an old locally configured host, `.local-state\recovery-launch.cmd` must be invoked explicitly after inspecting its source; it is a local compatibility helper outside this repository, not the default entry point or release evidence. No test keys were generated by this repair.

New AI recipe replies use cooking/action enums and ingredient IDs. Titles and instructions are rendered from validated inventory, so arbitrary unavailable ingredients cannot appear as executable recipe text. Old unconfirmed free-text menus are cleared on load; confirmed history remains unchanged. The unused original background artwork is preserved at `design/sunlit-pantry-bg.png` outside the size-limited bundle; the current UI uses its shader background.

## AI, privacy and limitations

- storage saves only this app's inventory, profile, plans, history and backups.
- model sends goals, profile, inventory/composition and cycle budgets through the official host to the person's configured model provider. Credentials stay with the host. No ai.env or key input.
- Configure the host's own AI providers panel. model.budget success is not provider readiness. Menus use online AI only, including the 1-day experience. Local generators and their toggle have been removed. On failure, fix the host configuration and retry; inventory and confirmed records stay unchanged. Already-sent calls may incur charges despite stopping the wait.
- No direct network hosts, microphone grant or independent app-agent tools. Voice is unavailable; no recording, OCR, photos or execution after the host closes.
- Nutrition is a prototype estimate, not medical advice, allergy safety or food-safety assurance. AI estimates are approximate references, with provenance and assumptions; package labels can correct them. Unknown portions are excluded from numeric totals and explicitly flagged.

The user reported earlier online generation; this candidate's full live-provider regression is unverified. See the publisher-confirmed [privacy policy](PRIVACY.md), [support](SUPPORT.md) and [review answers](REVIEW-ANSWERS.md).

## Publishing

Only bundle/ is distributed; tools, video, review packets and local state stay outside it. Git attributes preserve its exact bytes on Windows.

The [current default route](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md) uses the prepared GitHub tag workflow and an immutable toolchain. A developer signing secret is not needed. Review the workflow; authorize publication; push a NEW v0.6.2 tag; verify the sealed release pack; create a NEW issue linked to #99. Never move v0.6.1. The workflow is only prepared locally: no workflow run, tag, release, new issue or approval is claimed. Its sealed pack requires publisher-github-v1 support; a compatible released host remains pending according to the referenced guide.

See [SUBMISSION.md](SUBMISSION.md) for pending human checkpoints. A source check or workflow success is not competition qualification or Hub admission.

## License and source

[Apache License 2.0](LICENSE), with [NOTICE](NOTICE). Dependencies and third-party assets retain their own licenses. On 2026-10-08 the author confirmed sunlit-pantry-bg.png is their own original artwork; this declaration is recorded in NOTICE, not independently verified or a Hub approval.

Authors: leoniaodo, zix, power胖丸, Roooy.

[OctoSense](https://github.com/OctoSense-org/OctoSense) · [Design Flow](https://github.com/OctoSense-org/OctoScript-App-Design-Flow) · [App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)
