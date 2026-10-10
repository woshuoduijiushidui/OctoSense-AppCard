"""Offline release-metadata guards, not publisher-proof or approval checks."""
import json
from pathlib import Path
import re
import unittest

APP = Path(__file__).resolve().parents[1]
BUNDLE = APP / "bundle"
REPOSITORY = "https://github.com/woshuoduijiushidui/OctoSense-AppCard"


class ReleaseMetadataTests(unittest.TestCase):
    def test_version_permissions_and_digest_shape(self):
        manifest = json.loads((BUNDLE / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["id"], "pantry-steward")
        self.assertEqual(manifest["version"], "0.6.2")
        self.assertEqual(set(manifest["capabilities"]), {"storage", "model"})
        self.assertRegex(manifest["integrity"]["bundle_blake3"], r"^[0-9a-f]{64}$")

    def test_listing_links_assets_and_platform(self):
        listing = json.loads((BUNDLE / "listing.json").read_text(encoding="utf-8"))
        self.assertEqual(listing["publisher"]["support"], REPOSITORY + "/issues")
        self.assertEqual(listing["publisher"]["privacy_policy_url"], REPOSITORY + "/blob/main/PRIVACY.md")
        self.assertEqual(listing["platforms"], ["windows"])
        self.assertTrue(listing["release_notes"].startswith("0.6.2"))
        for name in listing["screenshots"] + [listing["icon"]]:
            path = (BUNDLE / name).resolve()
            self.assertTrue(path.is_relative_to(BUNDLE.resolve()))
            self.assertTrue(path.is_file(), name)

    def test_package_size_and_no_private_configuration(self):
        files = [path for path in BUNDLE.rglob("*") if path.is_file()]
        self.assertLessEqual(sum(path.stat().st_size for path in files), 8 * 1024 * 1024)
        for path in files:
            self.assertNotIn(path.name.lower(), ("ai.env", ".env", "tools.json", "agent.md"))
            self.assertNotIn(path.suffix.lower(), (".key", ".pem", ".pfx", ".mp4"))

    def test_document_local_links_exist(self):
        for name in ("README.md", "README.zh-CN.md", "PRIVACY.md", "SUPPORT.md", "SUBMISSION.md"):
            path = APP / name
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" in link or link.startswith("#"):
                    continue
                self.assertTrue((path.parent / link.split("#")[0]).is_file(), f"{name}: {link}")

    def test_official_publishing_pin_and_separation(self):
        pin = json.loads((APP / "publisher-toolchain.json").read_text(encoding="utf-8"))
        self.assertEqual(pin["repository"], "OctoSense-org/OctoSense-App-Hub")
        self.assertRegex(pin["revision"], r"^[0-9a-f]{40}$")
        workflow = (APP / ".github/workflows/publish-app.yml").read_text(encoding="utf-8")
        self.assertIn("ref: " + pin["revision"], workflow)
        self.assertIn("publisher-verify", workflow)
        self.assertIn("hub_admission", workflow)
        self.assertNotIn("__HUB_REVISION__", workflow)
        self.assertNotIn("hub stamp", workflow)

    def test_six_cycle_candidates_and_regeneration_exist(self):
        # Offline guard only: the native smoke test exercises the real behaviour.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        self.assertIn("let cycle_days = [1 3 7 15 21 30]", script)
        self.assertIn("fn make_cycle_candidates", script)
        self.assertIn("fn regenerate_cycle", script)
        for key in ('"balance"', '"protein"', '"fiber"', '"trim"'):
            self.assertIn(key, script)

    def test_composed_plan_separates_candidates_from_stages(self):
        # Offline guard only: qa_release.py composes and confirms for real.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        self.assertIn("stages: [] stage_next: 1 plan_history: []", script)
        self.assertIn("fn make_stage(candidate, started){", script)
        for marker in ("fn draft_add(", "fn draft_move(", "fn draft_remove(",
                       "fn draft_replace(", "fn draft_total_days(){", "fn stage_range(",
                       "fn confirm_health_plan(){", "plan_draft.len() >= 12"):
            self.assertIn(marker, script)

    def test_future_stage_editing_locks_started_stages(self):
        # Offline guard only: qa_release.py performs the edits against a real host.
        script = (BUNDLE / "main.splash").read_text(encoding="utf-8")
        self.assertIn("fn stage_locked(", script)
        for marker in ("fn stage_lock_hint(", "fn relayout_stages(", "fn stage_move(",
                       "fn stage_remove(", "fn stage_replace(", "fn plan_done_meals(){",
                       "fn plan_planned_meals(){", "fn plan_progress_percent(){"):
            self.assertIn(marker, script)
        self.assertIn("按日历锁定，不是故障", script)

    def test_byte_protection_and_license_files(self):
        attributes = (APP / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("bundle/** -text", attributes.splitlines())
        for name in ("LICENSE", "NOTICE", "PRIVACY.md", "SUPPORT.md"):
            self.assertTrue((APP / name).is_file(), name)
        for name in ("LICENSE.txt", "NOTICE.txt"):
            self.assertTrue((BUNDLE / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
