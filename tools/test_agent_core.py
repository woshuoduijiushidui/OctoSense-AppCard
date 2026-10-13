"""Run the production Splash helpers in the pinned Makepad Script VM."""

import os
from pathlib import Path
import shutil
import subprocess
import unittest


APP = Path(__file__).resolve().parents[1]
HOST = Path(os.environ.get("OCTOSENSE_HOST_WORKSPACE", APP.parent / "OctoSense"))
SCRIPT_CRATE = HOST / ".sources" / "makepad" / "platform" / "script"
CASES = (
    "session_restart_and_local",
    "session_file_and_failed_write",
    "session_cap",
    "budget_and_current_once",
    "projection_known_fields_only",
    "projection_real_stage_and_accepted_menu",
    "byte_trigger_under_fifteen",
    "final_input_budget_never_truncates",
    "summary_failure_and_success",
    "summary_batches_and_visibility",
    "bounded_compaction_segments",
    "memory_confirmation_and_expiry",
    "memory_rules_and_limit",
    "menu_memory_final_confirmation",
    "menu_memory_write_failure_keeps_confirmation",
    "production_menu_save_and_accept",
    "production_accept_memory_failure",
    "text_entry_and_contract",
    "text_one_model_call_and_retry",
    "text_compaction_then_one_answer",
    "text_compaction_failure_stops_answer",
    "text_invalid_provider_and_stale_reply",
    "text_snapshot_changes",
    "text_day_rollover",
)


class AgentCoreVmTests(unittest.TestCase):
    def test_production_helpers(self):
        if not SCRIPT_CRATE.is_dir() or not shutil.which("cargo"):
            self.skipTest("Pinned OctoSense Makepad Script source and Cargo are required")
        work = APP / "target" / "m1-vm"
        work.mkdir(parents=True, exist_ok=True)
        manifest = work / "Cargo.toml"
        manifest.write_text(
            '[package]\nname = "pantry-agent-core-vm"\nversion = "0.1.0"\n'
            'edition = "2021"\n[[bin]]\nname = "pantry-agent-core-vm"\n'
            'path = "../../tools/agent_core_vm.rs"\n[dependencies]\n'
            f'makepad-script = {{ path = "{SCRIPT_CRATE.as_posix()}" }}\n',
            encoding="utf-8",
        )
        run = subprocess.run(
            ["cargo", "run", "--quiet", "--offline", "--manifest-path", str(manifest)],
            cwd=APP,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(run.stdout.splitlines(), [f"{name}: ok" for name in CASES])


if __name__ == "__main__":
    unittest.main()
