"""Isolated native request-control regression; no live provider or user data.

Uses qa_merge's synthetic fixture and official card-host. The private shim only
captures/delays model replies and exposes production actions to this driver.
The app's guards, callbacks, persistence and watchdog execute unchanged; the
timeout control advances the request deadline instead of waiting 95 seconds.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

from qa_merge import prepare, APP
from qa_day import DayUI


SHIM = '''
fn qa_deliver(reply, callback){
    if !fs.exists("qa-release.txt") { start_timeout(0.1, || qa_deliver(reply, callback)) return }
    let release = fs.read("qa-release.txt").trim()
    if release == "error" { callback({is_ok: false error: "synthetic failure"}) return }
    if release == "malformed" { callback({is_ok: true data: {output: {}}}) return }
    if release == "timeout" { model_deadline = time_now() - 1 return }
    callback(reply)
}
let qa_command_seen = ""
start_interval(0.1, || {
    if !booted || ai_phase == 0 || !fs.exists("qa-command.json") { return }
    let cmd = fs.read("qa-command.json").parse_json()
    if cmd.id == qa_command_seen { return }
    qa_command_seen = cmd.id
    if cmd.action == "remove" { request_remove(1) confirm_remove() }
    if cmd.action == "manual" { plan("用户请求") }
    if cmd.action == "auto" { toggle_auto_generation() }
    if cmd.action == "model" { toggle_model() }
    if cmd.action == "image" { recognize_image("synthetic.png") }
    if cmd.action == "stock" { estimate_nutrition(nutrition_items(false), "stock", "库存营养估算") }
    fs.write("qa-result.json", {id: cmd.id busy: ai_busy enabled: use_ai auto: state.auto_generate
        blocked: storage_blocked requests: qa_requests state: state}.to_json())
})
'''


def until(read, predicate, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            value = read()
            if predicate(value):
                return value
        except (OSError, ValueError):
            pass
        time.sleep(.1)
    raise AssertionError('native result timed out')


class Case:
    def __init__(self, args, name, legacy=False, enabled=True, trial=False):
        self.args = args
        self.profile = args.profile / ('qa-' + name)
        if self.profile.exists():
            raise ValueError('Use a fresh task-owned profile: ' + str(self.profile))
        prepare(self.profile, args.hub, legacy=legacy)
        self.data = self.profile / 'pantry-steward'
        path = self.data / 'pantry.json'
        state = json.loads(path.read_text(encoding='utf-8'))
        state.update(model_enabled=enabled, auto_generate=True)
        if trial:
            state['stages'][0].update(kind='experience', days=1)
        path.write_text(json.dumps(state, ensure_ascii=False), encoding='utf-8')
        source = self.profile / 'qa-bundle/main.splash'
        text = source.read_text(encoding='utf-8')
        text = text.replace('callback({is_ok: true data: {output: {estimates: estimates}}})',
                            'qa_deliver({is_ok: true data: {output: {estimates: estimates}}}, callback)')
        # Capture even a forbidden image request instead of calling a provider.
        text = text.replace('host.request("model.complete", {task:',
                            'qa_host_request("model.complete", {task:')
        text = text.replace('if has_field(payload.input, "items") {',
                            'if has_field(payload.input, "kind") { return 1 }\n    if has_field(payload.input, "items") {')
        source.write_bytes((text + SHIM).encode('utf-8'))
        subprocess.run([str(args.hub), 'stamp', str(source.parent)], check=True, stdout=subprocess.DEVNULL)
        self.serial = 0
        self.checks = []
        self.proc = None
        self.start()

    def start(self):
        env = dict(os.environ, MAKEPAD_HIDE_WINDOWS='1', MAKEPAD_REMOTE=str(self.args.port))
        self.log = (self.profile / 'native.log').open('ab')
        self.proc = subprocess.Popen([str(self.args.card_host), '--bundle', str(self.profile / 'qa-bundle'),
                                     '--allow-unsigned', '--app-data', str(self.profile), '--size', '1200x800'],
                                    env=env, stdout=self.log, stderr=subprocess.STDOUT,
                                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        self.ui = DayUI(self.args.port, self.profile)
        self.command('inspect')

    def close(self):
        if self.proc is None:
            return
        try:
            self.ui.get('quit')
        except Exception:
            pass
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.terminate()
            self.proc.wait(timeout=10)
        self.log.close()
        self.proc = None

    def command(self, action):
        self.serial += 1
        token = str(self.serial)
        (self.data / 'qa-command.json').write_text(json.dumps(dict(id=token, action=action)), encoding='utf-8')
        return until(lambda: json.loads((self.data / 'qa-result.json').read_text(encoding='utf-8')),
                     lambda r: r['id'] == token)

    def count(self):
        return len(list(self.data.glob('request-[0-9]*.json')))

    def release(self, result):
        (self.data / 'qa-release.txt').write_text(result, encoding='utf-8')
        time.sleep(1.3)
        return self.command('inspect')

    def check(self, name, condition):
        assert condition, name
        self.checks.append(name)
        print('PASS', self.profile.name, name, flush=True)


def disabled(c):
    r = c.command('inspect')
    c.check('saved opt-out survives load', not r['enabled'] and not r['blocked'] and not r['state']['model_enabled'])
    # Reproduce the review through real inventory/settings UI on the legacy file.
    c.ui.click('▣  冰箱'); c.ui.click('展开 / 收起', index=0)
    c.ui.click('丢弃/移除'); c.ui.click('确认移除')
    c.command('manual'); c.command('stock'); c.command('image')
    c.check('discard, menu, nutrition and image send no model requests', c.count() == 0)
    c.check('subsequent save keeps disabled', not c.ui.state()['model_enabled'])
    c.close(); c.start()
    c.check('real restart preserves opt-out', not c.command('inspect')['enabled'] and c.count() == 0)
    c.ui.click('⚙  设置'); c.ui.click('启用在线 AI')
    c.check('explicit enable persists without sending a request', c.ui.state()['model_enabled'] and c.count() == 0)
    c.command('manual')
    r = c.release('success')
    c.check('explicitly enabled menu estimates then generates', c.count() == 2 and len(r['state']['plans']) == 1)
    c.command('model'); c.close(); c.start()
    c.check('explicit disable survives restart', not c.command('inspect')['enabled'])


def pending(c, outcome, trigger='remove', cancel='auto', reenable=False):
    c.command(trigger)
    c.check('nutrition request is held before the menu', c.count() == 1 and c.command('inspect')['busy'])
    c.command(cancel)
    if reenable:
        c.command(cancel)
    r = c.release(outcome)
    c.check('cancelled flow sends no second request', c.count() == 1)
    c.check('cancelled response writes no nutrition or menu', not r['state']['plans'] and
            all('nutrition' not in f for f in r['state']['foods']) and not r['busy'])
    c.check('confirmed history untouched', not r['state']['execution_records'])


def manual(c, outcome):
    c.command('manual'); c.command('auto')
    r = c.release(outcome)
    c.check('auto-off retains explicit manual generation', c.count() == 2 and len(r['state']['plans']) == 1)
    c.check('manual generation does not confirm consumption', not r['state']['execution_records'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--hub', type=Path, required=True)
    parser.add_argument('--card-host', type=Path, required=True)
    parser.add_argument('--port', type=int, default=18679)
    parser.add_argument('--only', default='')
    args = parser.parse_args()
    args.profile = args.profile.resolve()
    if not args.profile.is_relative_to((APP / '.local-state').resolve()) or not args.profile.name.startswith('qa-'):
        parser.error('use a fresh task-owned qa-* directory under .local-state')
    cases = [('legacy-disabled', dict(legacy=True, enabled=False), disabled),
             ('current-disabled', dict(enabled=False), disabled)]
    for outcome in ['success', 'error', 'malformed', 'timeout']:
        cases.append(('auto-' + outcome, {}, lambda c, o=outcome: pending(c, o)))
        cases.append(('manual-' + outcome, {}, lambda c, o=outcome: manual(c, o)))
    cases += [('auto-off-on', {}, lambda c: pending(c, 'success', reenable=True)),
              ('trial-auto', dict(trial=True), lambda c: pending(c, 'success')),
              ('stock-auto', {}, lambda c: pending(c, 'success', trigger='stock')),
              ('model-off', {}, lambda c: pending(c, 'success', cancel='model'))]
    report = []
    for name, options, run in cases:
        if args.only and args.only != name:
            continue
        c = Case(args, name, **options)
        try:
            run(c)
            report.append(dict(case=name, checks=c.checks))
        finally:
            c.close()
    (args.profile / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('PASS', sum(len(r['checks']) for r in report), 'native request-control checks')


if __name__ == '__main__':
    main()
