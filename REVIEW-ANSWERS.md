# Review answers — 0.8.0 unpublished source candidate

These are local review notes for the current bundle, not an App Hub decision or
proof of a sealed release. The pinned Hub source gate and an isolated local
test-signature installation in the full Windows shell passed. The official host
manual fallback passed 26 UI/data checks and restart checks. The user reported
that the live MiniMax image flow passed in the foreground; per-step logs were
not independently captured. Sealed release and Store publication are unverified.

1. **Claims.** The app confirms a dietary profile and 7/21/30-day cycle,
   previews manual food-batch intake, groups exact-name batches without losing
   per-batch actions, proposes local-rule or official model candidates, and
   deducts inventory only after a separate consumption confirmation. Quantity
   and unit checks reject incompatible or unconfirmed conversions. The global
   Agent keeps same-day text context and offers bounded inventory, menu and
   intake handoffs through the existing review screens. On the modified
   Windows host its microphone fills an editable draft. Nutrition and calories
   are prototype estimates. See README.md and VALIDATION.md.
2. **Platforms/category.** Only Windows is listed. The same bundle passed an
   isolated local test-signature installation in the unmodified official shell
   and the locally modified shell. The user reported live Pantry image recognition
   passed in the foreground. A sealed release, publication, and other platforms
   have not been tested. The lifestyle
   category matches pantry and meal planning.
3. **Grants/hosts.** The manifest requests storage, model, camera, files and
   microphone, plus optional host speech methods. There is no direct outbound
   host. Image and voice calls first probe the local host's capability; the
   unmodified official host keeps manual image intake and text Agent input.
   Recording requires foreground device consent. The host sends the app-local
   WAV to the configured MiniMax speech provider; the app never sees its key.
   PRIVACY.md describes model inputs, triggers and retention.
4. **Deception.** No app secret, login or payment field is present. The image
   buttons open a chooser only on a positive vision probe. The local Windows
   host records only after a microphone click and consent; its transcript is
   editable and needs a separate Send action. The official host states that
   speech is unsupported. The four bundle screenshots and linked video show
   the earlier 0.7.0 manual-flow candidate, not this 0.8.0 voice or image UI.
   The current synthetic inventory comparison illustrates UI changes only.
   No new release video or App Hub approval is claimed.
5. **Instructions.** The online planning prompt requests meal JSON for the
   visible feature and passes profile/inventory as task data. The global Agent
   accepts one bounded proposal at a time; local validation and the existing
   review screens control every business write. No tools.json, AGENT.md or
   independent app-agent skill ships in the bundle.
6. **Abuse.** Local source review and synthetic native tests found no abusive
   content directed at a private person; this is not external review approval.
7. **Human route.** Before any release, review current public support/privacy
   links, publication workflow and identity, final tag, Store/provider evidence,
   sealed pack verification, and the original-artwork declaration in NOTICE.
   The 0.8.0 source candidate is unsigned; only its isolated installation used
   a local test signature. It is unpublished, with no new review issue or Hub
   approval claimed. Local test keys are not publisher identity.

## Historical 0.6.2 editable candidate — not an approval

These answers describe the earlier 0.6.2 candidate, whose script was unchanged
from 0.6.1. The current Issue #2 feature branch has edited the script; the
0.8.0 notes above replace these answers for local handoff. These historical
answers do not claim a release, paid provider test or Hub approval for the
feature branch.

1. **Claims.** bundle/main.splash implements explicit profile/cycle confirmation,
   inventory preview, local/model candidates, acceptance, actual consumption,
   deletion and persistence. Generation is manual by default. The then-current
   listing recorded prototype nutrition, historical captures and unverified live-provider/
   cold-start behavior. See CYCLE-PLANS.md and VALIDATION.md.
2. **Platforms/category.** Windows has historical evidence and a limited
   current-toolchain native smoke test. lifestyle fits pantry/meal planning.
   Full functional regression, other platforms and sealed-release installation
   remain unverified.
3. **Grants/hosts.** bundle/manifest.json requests storage/model only.
   The script uses its filesystem sandbox and official model.complete/budget.
   No direct outbound hosts or microphone grant. PRIVACY.md describes inputs
   leaving the device and optional automatic triggers.
4. **Deception.** No secret/key/login/payment input or system-approval imitation.
   Candidates identify source; the microphone explains unavailability.
   bundle/screenshots holds historical genuine Windows captures, not phone
   screenshots or complete 0.6.2 live-model evidence.
5. **Instructions.** online_plan requests constrained meal JSON as the visible
   planning feature, not an instruction to reviewers. Profile/inventory remains
   input data. No tools.json, AGENT.md or app-agent skills are shipped.
6. **Abuse.** Source review found no abusive wording directed at a private person.
   Test records use synthetic profiles; this is not external review approval.
7. **Route: human review.** Check final links, tag, latest-toolchain gate, UI/
   provider evidence, the recorded original-artwork declaration and the
   downloaded sealed release. The author confirmed the background is their
   own original artwork on 2026-10-08; this is not independent verification.
   Publisher names, Windows-only claim and privacy disclosure were confirmed
   by the user during local repair. Publication authorization, release proof
   and Hub approval are pending. Local test keys are not publisher identity.

If the regenerated packet adds questions, answer them rather than silently
reusing seven answers. No app-agent files were added by this repair.
