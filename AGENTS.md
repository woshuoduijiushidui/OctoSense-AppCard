# Working on Pantry Steward

This is a non-system script app, migrated to the unmodified official OctoSense.
Keep the id pantry-steward; do not pack it as an os.* system app or patch the
shell to provide this app with additional privileges.

- Application behaviour lives in bundle/main.splash. Only bundle/ is submitted.
- No secrets, login or secret-input fields in the bundle. AI credentials are
  entered only on the host-owned AI providers panel. Never copy ai.env.
- The official model.budget reports usage, not provider readiness.
- Speech recognition is unavailable in this tested host. Do not silently
  restore custom microphone calls or claim the icon records audio.
- Use tools/launch.py --check and tools/test_launch.py. Native UI regression:
  tools/smoke.py in a task-owned hidden official shell with separate --app-data.
  Never reuse a person's normal inventory for testing.
- --prepare-local-test generates local test keys outside the repository. Obtain
  explicit human approval first; never use these as the production identity.
- Official CLI build copies stay under target and use the host's pinned
  .sources. Never modify cached upstream sources or clone duplicate frameworks.
- Restamp after bundle changes: run the pinned `hub stamp bundle` so the
  manifest digest matches, but keep the manifest version unchanged — the version
  is set at the release checkpoint, not by a feature PR. Keep real screenshots
  and bilingual READMEs honest. Record what was tested and what remains
  unverified in VALIDATION.md.
- Formal identity, privacy, signing and submission are human checkpoints.
- Before changing text another person wrote on the tracker (an issue body, a spec), post the
  intended change and reasoning as a comment on the Parent Issue first. After the change lands,
  add a follow-up comment referencing the commit.

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues on `woshuoduijiushidui/OctoSense-AppCard`, managed with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The default five triage roles, each label string equal to its name. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
