# Pantry Steward · 冰箱管家

English | [简体中文](README.zh-CN.md)

Turn confirmed pantry inventory into a meal you can review and execute.

## Version and evidence

This checkout is the editable **0.6.2 candidate**. The working tree also carries the Issue #8–#11 features (six-cycle candidates, composed plans, future-stage editing and the Overview page); the release version is set by the release checkpoint, not by each feature branch. [Issue #99](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/99) requests review of **0.6.1**, not this candidate. Neither is claimed as admitted.

Only Windows is claimed: the current pinned tools passed source admission and a limited native smoke test. Full 0.6.2 live-provider regression, new-computer installation, full functional regression and sealed-release installation remain unverified. See [VALIDATION.md](VALIDATION.md).

## What it does

Confirm a dietary profile and 1/3/7/15/21/30-day cycles with three comparable candidates each (the 1-day cycle is the short trial); regenerate one cycle's candidates without touching a confirmed plan. Confirm a single candidate as a one-stage plan, or add candidates of different cycles in order (repeats allowed, e.g. 7+7) and reorder, remove or replace stages before confirming; the compose page shows the summed total days and each stage's date range and targets, up to 12 stages. A confirmed stage locks on its start date; stages that have not started can still be reordered, replaced, removed or retargeted in the Archive tab, which recalculates the later stages' dates and the plan totals while confirmed progress and intake records stay untouched. Then preview inventory batches; generate a local-rule or official model.complete candidate; review recipe steps and quantities; accept it; separately confirm actual consumption before deducting inventory and recording intake. Each confirmed stage snapshots its candidate's targets, so later edits to a candidate do not change it. Daily/cycle values are prototype estimates. Archive a plan without deleting stock. The Overview tab shows the long-term plan, the current stage, today's per-meal progress and the current stage's kcal/protein target against actuals; progress counts only confirmed meals over days × 3 meals and never moves when a menu is only generated or confirmed — only a confirmed meal increases it. The target follows the stage whose dates cover today.

Generation is manual by default. Optional automatic generation must be enabled in Settings; acceptance and consumption still require confirmation. Deleting a plan does not restore inventory or erase meal records. See [cycle details](CYCLE-PLANS.md).

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

--hub --check needs no host workspace or keys. --standalone uses official card-host for local rules; it provides no model service and is not a Store install. --app-data selects an isolated test directory; preview defaults to .local-state/standalone. Back up needed data before deleting it.

The launcher checks the existing digest without silently repairing it. VALIDATION.md records the current source digest. Old Windows hub builds hash paths differently and may misclassify license URLs. Update the tools after refusal; do not remove legal notices, widen grants, bypass the gate or restamp a sealed release.

The old --host-workspace / --prepare-local-test route is retained only for isolated historical 0.6.1 compatibility rehearsal, not recommended for this candidate. Local test-key creation outside Git requires separate human consent; none was performed in this repair. Original host workspaces and inventory were untouched.

Live AI requires a compatible OctoSense host serving official model methods, configured in its AI providers panel. These card-host commands cannot test it. The final sealed pack also requires publisher-github-v1, with a compatible released host still pending. Installation and complete online behavior are not claimed as verified.

## AI, privacy and limitations

- storage saves only this app's inventory, profile, plans, menu history and backups.
- model sends goals, profile, inventory/composition and cycle budgets through the official host to the person's configured model provider. Credentials stay with the host. No ai.env or key input.
- Configure the host's own AI providers panel. model.budget success is not provider readiness. On failure, manually select local rules. Already-sent calls may incur charges despite stopping the wait.
- No direct network hosts, microphone grant or independent app-agent tools. Voice is unavailable; no recording, OCR, photos or execution after the host closes.
- Nutrition is a prototype estimate, not medical advice, allergy safety or food-safety assurance. Unknown ingredients need complete package labels for numerical planning.

The user reported earlier online generation; this candidate's full live-provider regression is unverified. See the publisher-confirmed [privacy policy](PRIVACY.md), [support](SUPPORT.md) and [review answers](REVIEW-ANSWERS.md).

## Publishing

Only bundle/ is distributed; tools, video, review packets and local state stay outside it. Git attributes preserve its exact bytes on Windows.

The [current default route](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md) uses the prepared GitHub tag workflow and an immutable toolchain. A developer signing secret is not needed. Review the workflow; authorize publication; push a NEW v0.6.2 tag; verify the sealed release pack; create a NEW issue linked to #99. Never move v0.6.1. The workflow is only prepared locally: no workflow run, tag, release, new issue or approval is claimed. Its sealed pack requires publisher-github-v1 support; a compatible released host remains pending according to the referenced guide.

See [SUBMISSION.md](SUBMISSION.md) for pending human checkpoints. A source check or workflow success is not competition qualification or Hub admission.

## License and source

[Apache License 2.0](LICENSE), with [NOTICE](NOTICE). Dependencies and third-party assets retain their own licenses. On 2026-10-08 the author confirmed sunlit-pantry-bg.png is their own original artwork; this declaration is recorded in NOTICE, not independently verified or a Hub approval.

Authors: leoniaodo, zix, power胖丸, Roooy.

[OctoSense](https://github.com/OctoSense-org/OctoSense) · [Design Flow](https://github.com/OctoSense-org/OctoScript-App-Design-Flow) · [App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)
