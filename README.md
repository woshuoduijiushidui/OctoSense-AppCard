# Pantry Steward · 冰箱管家

English | [简体中文](README.zh-CN.md)

Turn confirmed pantry inventory into a meal you can review and execute.

## Version and evidence

This branch contains the unpublished **0.8.0 source candidate** for Issue #2. Alongside manual inventory, cycles, and menus, it creates editable drafts from a camera or imported image when the locally modified host reports image capability. The official host falls back to manual entry. The bundle passes the pinned App Hub gate. [Issue #99](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/99) reviews **0.6.1**, not this candidate; no release or Hub approval is claimed.

Only Windows is targeted. On 2026-10-11 the 0.8.0 bundle passed the pinned App Hub gate and 19 Python tests. In an isolated profile, the unmodified full official host passed 26 UI/data checks and restart checks, including manual fallback from both image buttons. The locally modified host passed the capability probe, shared chooser, and cancellation checks; task-only model fixtures exercised both editable image drafts and a multi-row inventory commit. The user reported that the remaining foreground MiniMax image, camera, retry, and restart checks passed; per-step logs were not captured independently. Formal Store publication remains unverified. See [VALIDATION.md](VALIDATION.md).

## What it does

Confirm a dietary profile and a 7/21/30-day cycle; preview inventory batches; generate a local-rule or official model.complete candidate; review recipe steps and quantities; accept it; separately confirm actual consumption before deducting inventory and recording intake. Daily/cycle values are prototype estimates. Archive a cycle without deleting stock.

The profile separates allergies, avoidances, and preferences. Intake creates editable batches before confirmation and accepts g/kg, ml/L, pieces, or simple packages with a user-confirmed conversion. Inventory retains separate batches and freshness states. Image recognition is enabled only after a positive `model.vision_capability` probe from the locally modified host; users fill uncertain fields before confirming.

Generation is manual by default. Optional automatic generation must be enabled in Settings; acceptance and consumption still require confirmation. Deleting a plan does not restore inventory or erase meal records. See [cycle details](CYCLE-PLANS.md).

## Demo

[Historical manual-flow recording](video/演示视频.mp4)

![Prior Windows card-host home capture](bundle/screenshots/01-main.png)

[Candidate](bundle/screenshots/02-plan.png) · [Consumption](bundle/screenshots/03-confirm.png) · [Inventory](bundle/screenshots/04-updated.png)

The video and four captures show the prior 0.7.0 manual flow in an isolated official Windows card-host. Their image-button state does not represent the current 0.8.0 UI. Current synthetic-data captures: [home](docs/qa/issue-2-home-after.png), [profile editing](docs/qa/issue-2-profile-edit-after.png), [inventory](docs/qa/issue-2-inventory-after.png), [local-host image chooser](docs/qa/issue-2-image-chooser-after.png), [official-host fallback](docs/qa/issue-2-official-fallback-after.png), [recipe](docs/qa/issue-2-recipe-after.png), and [consumption review](docs/qa/issue-2-consumption-after.png). The current captures illustrate the UI only; they do not prove live image recognition, Store publication, or a live provider response. Recording a new video is outside this PR.

## Windows source launch

This is an app-only repository, not its host or an installer. Use root run.cmd, not the absent apps/pantry-steward/run.cmd path.

Prerequisites: Git, Python 3.11+, Rust, Windows C++ tools and Windows SDK. Follow the [official Quickstart](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/QUICKSTART.md) to prepare the current native workspace. The 0.8.0 camera consent declaration requires the full OctoSense shell; standalone card-host lacks that broker.

The older 0.6.2 publishing workflow pins App Hub 655114c4943cd2490daaefa2173e7b5aaa20669f. The current OctoSense host instead pins App Hub 8347a489141c0e24cab564883db7c4592935a8b2. Use the current host pin to validate this edited bundle.

With the pinned tools built under the sibling OctoSense checkout, run from this app directory using a fresh test profile. The second command uses that checkout's current branch; its host identity depends on whether the checkout is the unmodified official base or the local patch. Keep it running and execute the third in another terminal:

```cmd
run.cmd --hub ..\OctoSense\target\release\hub.exe --check
run.cmd --host-workspace ..\OctoSense --hidden --remote 18442 --app-data target\qa-d2
python -X utf8 tools\smoke.py --port 18442 --profile target\qa-d2
```

`--hub --check` needs no host workspace or keys. Isolated installation in the full shell uses local test keys created with prior consent. The native smoke driver expects a fresh, isolated `--app-data` directory. Restart the same profile and rerun with `--restart` to check persistence.

The launcher checks the existing digest without silently repairing it. The current 0.8.0 candidate was restamped with the pinned App Hub and passed its bundle check. Restamp after any later bundle change.

D2 was installed with a local test signature in an isolated full-shell profile; this is not Store publication. `--prepare-local-test` creates local test keys outside Git and requires human consent. Do not use a person's existing inventory for testing.

Live AI requires the locally modified OctoSense host and a provider configured in its AI providers panel. The unmodified official shell was checked separately for manual fallback; the command above alone does not identify a host as official. The user reported a successful foreground MiniMax image-provider flow. The final sealed pack also requires publisher-github-v1. Local test-signature installation is not formal publication.

## AI, privacy and limitations

- storage saves this app's inventory, profile, plans, history, backups, and selected images.
- model sends goals, the entered profile (including allergies, avoidances, and preferences), and eligible batch names with native units and quantities through the official host to the person's configured provider. Numerical planning also sends gram estimates, nutrition references, and cycle budgets; unquantified recipe planning sends only whether each nutrition reference is complete. Credentials stay with the host. No ai.env or key input.
- Configure the host's own AI providers panel. model.budget success is not provider readiness. On failure, manually select local rules. Already-sent calls may incur charges despite stopping the wait.
- Image recognition requests camera/files permission. The Windows local host accepts one app-local JPEG, PNG, or WebP image up to 10 MiB with `MiniMax-M3` on `minimax`/`minimax-cn` or `kimi-k2.5` on `moonshot`; it sends the image and recognition prompt to the configured provider and returns an editable draft. The official host shows a manual-entry fallback. There are no direct network hosts, microphone grant, independent app-agent tools, voice capture, or execution after the host closes.
- Nutrition is a prototype estimate, not medical advice, allergy safety or food-safety assurance. Planning prefers ingredients with complete nutrition references. Other usable stock may produce a recipe marked as unquantified; confirmed consumption deducts its native inventory quantity but adds no invented calories or nutrients to cycle totals. Complete per-100-g references are required for numerical planning.

The user reported foreground online recipe and image-recognition checks on this candidate; a complete independently logged provider regression was not captured. See the publisher-confirmed [privacy policy](PRIVACY.md), [support](SUPPORT.md) and [review answers](REVIEW-ANSWERS.md).

## Publishing

Only bundle/ is distributed; tools, video, review packets and local state stay outside it. Git attributes preserve its exact bytes on Windows.

The [App Hub submission guide](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md) describes publication. The 0.8.0 candidate still needs a formal release evidence review, public-link review, and separate human authorization to publish. No publishing workflow, tag, release, new issue, or approval is claimed.

See [SUBMISSION.md](SUBMISSION.md) for pending human checkpoints. A source check or workflow success is not competition qualification or Hub admission.

## License and source

[Apache License 2.0](LICENSE), with [NOTICE](NOTICE). Dependencies and third-party assets retain their own licenses. On 2026-10-08 the author confirmed sunlit-pantry-bg.png is their own original artwork; this declaration is recorded in NOTICE, not independently verified or a Hub approval.

Authors: leoniaodo, zix, power胖丸, Roooy.

[OctoSense](https://github.com/OctoSense-org/OctoSense) · [Design Flow](https://github.com/OctoSense-org/OctoScript-App-Design-Flow) · [App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)
