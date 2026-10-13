# Pantry Steward · 冰箱管家

English | [简体中文](README.zh-CN.md)

Plan meals from confirmed pantry inventory. Only actual-consumption confirmation changes stock and intake.

## Version and publication status

This is the **0.8.0 release candidate**, separate from its companion OctoSense host. The App ID remains `pantry-steward`. This repository was renamed from the previous app repository; existing tags and history are not moved or overwritten.

Publication preparation starts at source commit `c814a7d0d8659cebfabcd2dcb4711e6f27b5308d`, without changing the business script. The GitHub Release, sealed-pack verification and App Hub approval are pending. Local checks do not mean admission. The existing request is [App Hub #166](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/166).

## Features

- Profile: health direction, allergies, exclusions and ordinary preferences are separate.
- Inventory: reviewed drafts, separate same-name batches, native quantities/units, confirmed conversions and expiry data.
- Plans: 1/3/7/15/21/30-day candidates; compose up to 12 stages, reorder/remove/replace before confirmation. Started stages lock; future edits preserve actual records.
- Day menus: the host's online AI proposes breakfast/lunch/dinner from eligible inventory only, never invented out-of-stock ingredients. Generation and acceptance do not consume stock.
- Missing items and mock shopping: later stock changes create a derived gap. In-app products, cart, orders and receipt confirmation are simulated, with no Meituan API, payment or delivery. Only receipt confirmation adds inventory batches.
- Actual execution: review actual food/quantity, then append independent snapshots, consume stock and update intake/progress only on final confirmation. Recommendations remain separate.
- One-day experience: inventory-only, no shopping, complete/review after three actual meal confirmations.
- Ask the Steward: same-day multi-turn text and soft memory through host `model.complete`. Proposals go to existing review screens before any business write. This is not an independent background octos app agent.
- Optional images/voice: enabled by actual host/provider support. Images produce editable inventory drafts; transcripts fill editable input and need a separate Send action. Missing support retains manual/text paths.

See [CYCLE-PLANS.md](CYCLE-PLANS.md), [EXPERIENCE.md](EXPERIENCE.md), [GLOSSARY.md](GLOSSARY.md) and docs/adr/ for the domain rules.

## Host and model boundaries

Companion modified Windows host: [woshuoduijiushidui/OctoSense](https://github.com/woshuoduijiushidui/OctoSense). The bundle carries no host/native code and installs no new host API.

Images use the host's reported `model.complete@2`; speech requires foreground microphone/transcription APIs and a compatible provider. An official update or a capability declaration alone cannot prove support. Unmodified official released hosts were not revalidated in this preparation.

Menus, nutrition estimation and chat need online AI. Disabled/unavailable AI produces a notice, not a fabricated local menu; inventory and existing records remain manageable. Provider credentials belong in the host-owned AI providers UI. The app neither reads ai.env nor collects keys.

Nutrition may come from users, packaging or provenance-labelled AI estimates. It is planning reference, not medical advice or a guarantee of nutrition, allergy or food safety. See [PRIVACY.md](PRIVACY.md).

## Checks and screenshots

Publication preparation on 2026-10-14:

- Source gate at official App Hub `386359153ed6377b5f047bd9ed2767a6a2ac2bc7` passes with only the expected unsigned warning.
- All 36 automated tests pass, including production helpers in the pinned Makepad Script VM.
- An existing locally TEST-signed fixture with identical business script, empty test provider/account directories and the companion modified Windows host passed 19 native checks and 2 restart checks.
- Four new native screenshots were inspected. They use synthetic inventory with online AI off, without live recording or provider requests.

![Current Windows Home with online AI off](bundle/screenshots/05-current-home.png)

[Inventory](bundle/screenshots/06-current-inventory.png) · [Unsent chat draft](bundle/screenshots/07-current-chat-draft.png) · [Settings](bundle/screenshots/08-current-settings.png)

These are not live-model, camera or microphone success evidence. Old 01–04 images are historical, not this release's listing screenshots; the [historical video](video/演示视频.mp4) is not new-version full-flow proof. Dated evidence remains in [VALIDATION.md](VALIDATION.md); current checks are in [review/LOCAL-CHECKS.md](review/LOCAL-CHECKS.md).

**Unverified**: current live chat/menu/ASR/camera/image providers; the final GitHub-attested pack; official released-host install/update and full new-feature regression; Android/iOS/macOS/Linux.

## Development checks

Git, Python 3.11+ and Rust are required. Native Windows builds also need the C++ build tools and SDK.

With current official tools on PATH (equivalent absolute-path commands were run):

```text
hub check bundle --allow-unsigned
hub scan bundle --packet build/review.json
python -B -X utf8 -m unittest discover -s tools -p "test_*.py"
```

The VM test additionally needs `OCTOSENSE_HOST_WORKSPACE` to point at prepared host source; otherwise it explicitly skips. A skip is not a pass.

Current `card-host` supplies no model/camera/recording services and refuses applications requiring `host-api-v1`. Do not strip requires to force a preview. Use a compatible shell with a separate test profile, never personal inventory.

Restamp edited source with `hub stamp bundle` and recheck, never restamp a sealed pack. The launcher's historical local-test-signature route is a human-authorized rehearsal, not publisher identity.

## Publishing

Submit bundle/ only. Credentials, inventory, keys, test profiles and review packets stay outside it. The workflow and publisher-toolchain.json pin current official tools and follow [GitHub publishing](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md).

Source commits, release tags and public releases need publisher confirmation. After the workflow succeeds, download/verify the pack and receipt, then update the existing submission. Those external steps have not run. See [SUBMISSION.md](SUBMISSION.md) and [the issue draft](review/APP-HUB-ISSUE.md).

## License and support

[Apache License 2.0](LICENSE); [NOTICE](NOTICE) records provenance. The author declared the background original on 2026-10-08; this is not independent ownership verification.

Authors: leoniaodo, zix, power胖丸, Roooy. Support: [repository Issues](https://github.com/woshuoduijiushidui/pantry-steward/issues). Do not attach credentials, personal profiles or complete real inventory.
