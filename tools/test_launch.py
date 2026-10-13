"""Offline guards: no custom host, no accidental key generation or secret copying."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("pantry_launch", Path(__file__).with_name("launch.py"))
launch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launch)


class LaunchTests(unittest.TestCase):
    def test_explicit_app_hub_source_requires_pinned_clean_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            host = Path(directory) / "host"
            source = Path(directory) / "app-hub"
            (source / "crates/app-hub").mkdir(parents=True)
            host.mkdir()
            (host / "Cargo.toml").write_text(
                '[workspace.dependencies]\noctosense-app-hub-app = { rev = "pinned" }\n',
                encoding="utf-8",
            )
            (source / "Cargo.toml").touch()
            (source / "crates/app-hub/Cargo.toml").touch()
            with patch.object(launch, "ROOT", host), patch.object(launch, "run", side_effect=["pinned", ""]) as call:
                self.assertEqual(launch.hub_source(source), (source.resolve(), "pinned"))
                self.assertEqual(call.call_count, 2)
            with patch.object(launch, "ROOT", host), patch.object(launch, "run", return_value="other"):
                with self.assertRaisesRegex(RuntimeError, "固定的提交"):
                    launch.hub_source(source)
            with patch.object(launch, "ROOT", host), patch.object(launch, "run", side_effect=["pinned", " M Cargo.toml"]):
                with self.assertRaisesRegex(RuntimeError, "本地修改"):
                    launch.hub_source(source)

    def test_current_hub_check_needs_no_host_or_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            tool = Path(directory) / "hub.exe"
            tool.touch()
            with patch.object(launch, "host_workspace") as host, \
                 patch.object(launch, "prepare_tools") as build, \
                 patch.object(launch, "local_install") as install, \
                 patch.object(launch, "run") as call, \
                 patch("sys.argv", ["launch.py", "--hub", str(tool), "--check"]):
                launch.main()
            host.assert_not_called()
            build.assert_not_called()
            install.assert_not_called()
            self.assertEqual(call.call_args.args[0], [tool.resolve(), "check", launch.APP / "bundle", "--allow-unsigned"])

    def test_current_hub_rejects_implicit_key_creation(self):
        with patch("sys.argv", ["launch.py", "--hub", "hub.exe", "--prepare-local-test"]), \
             patch.object(launch, "prepare_tools") as build, patch.object(launch, "local_install") as install:
            with self.assertRaises(SystemExit) as error:
                launch.main()
            self.assertEqual(error.exception.code, 2)
            build.assert_not_called()
            install.assert_not_called()

    def test_standalone_checkout_requires_host(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(launch, "APP", Path(directory) / "standalone-app"):
                with self.assertRaisesRegex(RuntimeError, "--host-workspace"):
                    launch.host_workspace()

    def test_explicit_host_rejects_incomplete_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "宿主目录不完整"):
                launch.host_workspace(Path(directory))

    def test_launch_does_not_restamp_source(self):
        with patch.object(launch, "host_workspace", return_value=launch.APP), \
             patch.object(launch, "prepare_tools", return_value=(Path("hub"), Path("card-host"), Path("installer"))), \
             patch.object(launch, "run") as call, patch("sys.argv", ["launch.py", "--check"]):
            launch.main()
        self.assertEqual(len(call.call_args_list), 1)
        self.assertEqual(call.call_args.args[0][1], "check")

    @unittest.skipUnless(os.name == "nt", "Windows batch launcher")
    def test_windows_entrypoint_format(self):
        script = (launch.APP / "run.cmd").read_bytes()
        script.decode("ascii")
        self.assertIn(b"\r\n", script)
        self.assertNotIn(b"\n", script.replace(b"\r\n", b""))

    @unittest.skipUnless(os.name == "nt", "Windows batch launcher")
    def test_windows_entrypoint_reaches_python(self):
        result = subprocess.run(
            f'cmd.exe /d /s /c ""{launch.APP / "run.cmd"}" --help"',
            input="", capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=launch.ROOT, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("--prepare-local-test", result.stdout)

    @unittest.skipUnless(os.name == "nt", "Windows batch launcher")
    def test_windows_entrypoint_preserves_failure(self):
        result = subprocess.run(
            f'cmd.exe /d /s /c ""{launch.APP / "run.cmd"}" --invalid-launch-test-option"',
            input="", capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=launch.APP, timeout=30,
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("Launch failed.", result.stdout)

    @unittest.skipUnless(os.name == "nt", "Windows batch launcher")
    def test_default_entrypoint_ignores_untracked_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "run.cmd").write_bytes((launch.APP / "run.cmd").read_bytes())
            (root / ".local-state").mkdir()
            (root / ".local-state/recovery-launch.cmd").write_bytes(b"@echo PRIVATE_OVERRIDE\r\n@exit /b 0\r\n")
            # Intercept Python only inside this isolated fixture, so the default
            # branch can be tested without launching a host or preparing keys.
            (root / "python.cmd").write_bytes(b"@echo OFFICIAL_LAUNCH %*\r\n@exit /b 0\r\n")
            env = dict(os.environ, PATH=str(root) + os.pathsep + os.environ.get("PATH", ""))
            result = subprocess.run(f'cmd.exe /d /s /c ""{root / "run.cmd"}""',
                                    input="", capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", cwd=root, env=env, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("OFFICIAL_LAUNCH", result.stdout)
            self.assertIn("tools\\launch.py", result.stdout)
            self.assertNotIn("PRIVATE_OVERRIDE", result.stdout)

    def test_key_generation_requires_explicit_consent(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(launch, "key_dir", return_value=Path(directory) / "keys"), patch.object(launch, "run") as call:
                with self.assertRaisesRegex(RuntimeError, "本人许可"):
                    launch.local_install(Path("hub"), Path("installer"), False)
                call.assert_not_called()
                self.assertFalse((Path(directory) / "keys").exists())

    def test_source_has_no_secret_or_native_adapter(self):
        files = list((launch.APP / "bundle").rglob("*"))
        self.assertFalse(any(p.name == "ai.env" or p.suffix == ".key" for p in files))
        source = (launch.APP / "bundle/main.splash").read_text(encoding="utf-8")
        manifest = json.loads((launch.APP / "bundle/manifest.json").read_text(encoding="utf-8"))
        self.assertIn("microphone", manifest["capabilities"])
        self.assertEqual(manifest["host_api"]["optional"]["model.transcribe_capability"], 1)
        self.assertEqual(manifest["host_api"]["optional"]["microphone.record_start"], 1)
        self.assertIn('host.request("model.transcribe_capability", {}', source)
        self.assertIn('voice_request("permission_status", "microphone.permission.status", {})', source)
        self.assertIn('voice_request("start", "microphone.record_start"', source)
        self.assertIn('voice_request("transcribe", "model.transcribe"', source)
        self.assertIn("当前宿主暂不支持语音识别，请使用文字输入。", source)
        self.assertIn('host.request("model.complete"', source)
        self.assertIn("不读取 ai.env", source)

    def test_official_budget_does_not_claim_provider_ready(self):
        source = (launch.APP / "bundle/main.splash").read_text(encoding="utf-8")
        self.assertNotIn("r.data.configured", source)
        self.assertNotIn("r.data.model", source)
        self.assertIn('text.search("no_provider")', source)

    def test_generation_defaults_and_automatic_guards(self):
        source = (launch.APP / "bundle/main.splash").read_text(encoding="utf-8")
        self.assertIn("model_enabled: true auto_generate: false", source)
        self.assertIn('if !has_field(value, "auto_generate") { value.auto_generate = false }', source)
        self.assertIn('if !state.auto_generate && automatic_reason(reason) { return }', source)
        for reason in ("库存变化", "库存移除", "用餐后再规划"):
            call = next(line for line in source.splitlines() if f'plan("{reason}")' in line)
            self.assertIn("state.auto_generate", call)
        retry_body = source.split("fn retry_ai(){", 1)[1].split("\nfn ", 1)[0]
        self.assertIn('plan("用户请求重试")', retry_body)
        self.assertIn('automatic_reason(ai_snapshot.reason)', source)


if __name__ == "__main__":
    unittest.main()
