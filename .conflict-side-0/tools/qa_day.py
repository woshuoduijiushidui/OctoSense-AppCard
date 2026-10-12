"""Native acceptance checks with synthetic stock in a task-owned preview only."""
import argparse
import json
import time
from pathlib import Path
import smoke

APP = Path(__file__).resolve().parents[1]


class DayUI(smoke.UI):
    def state_path(self):
        return self.profile / 'pantry-steward/data/pantry.json'

    def state(self):
        files = list((self.profile / 'pantry-steward').rglob('pantry.json'))
        assert len(files) == 1, files
        return json.loads(files[0].read_text(encoding='utf-8'))

    def scroll(self, dy):
        self.get('m', k='scroll', x=750, y=450, dy=dy, wait=1)
        time.sleep(.2)

    def click(self, text=None, name=None, index=0):
        self.scroll(-10000)
        return super().click(text=text, name=name, index=index)

    def fill(self, text, index=0, name=None):
        self.scroll(-10000)
        for _ in range(20):
            fields = [w for w in self.snap() if w['ty'] == 'TextInput' and w['r'][2] > 0]
            matching = [w for w in fields if w.get('i') == name][index:index+1] if name else fields[index:index+1]
            if matching:
                f = matching[0]
                y = f['r'][1] + f['r'][3]/2
                if 0 < y < 780:
                    x, top, width, height = f['r']
                    self.get('click', x=x+width/2, y=top+height/2, wait=1)
                    self.get('k', k='down', c='KeyA', ctrl=1, wait=1)
                    self.get('k', k='up', c='KeyA', ctrl=1, wait=1)
                    if text:
                        self.get('t', t=text, wait=1)
                    else:
                        self.get('k', k='down', c='Backspace', wait=1)
                        self.get('k', k='up', c='Backspace', wait=1)
                    return
            self.scroll(300)
        raise AssertionError('cannot fill ' + str(name or index))


def exercise(ui):
    ui.check('onboarding shown', '首次建档' in ui.text())
    ui.click('选择', index=1)
    ui.click('女性')
    for i, value in enumerate(('30', '170', '65', '', '清淡', '')):
        ui.fill(value, i)
    ui.click('下一步 · 选择周期方案  →')
    candidates = ui.state()['programs']
    ui.check('multi-cycle remains primary; optional 1-day candidate', [p['days'] for p in candidates] == [7,21,30,1])
    ui.click('选择1天体验方案')
    ui.check('selection alone is not activation', ui.state()['program_active'] == 0)
    ui.click('确认选中方案 · 去录冰箱  →')
    ui.fill('鸡蛋', name='food_name')
    ui.fill('200', name='food_grams')
    ui.fill('3', name='food_days')
    ui.click('预览并确认入库  →')
    ui.check('inventory preview does not write stock', not ui.state()['foods'])
    ui.click('确认入库')
    ui.click('完成建档 · 开始托管  →')
    ui.click('✦  方案')
    ui.click('生成 / 更新未确认三餐')
    s = ui.state()
    p = next(p for p in s['programs'] if p['id'] == s['program_active'])
    ui.check('three separate menus; no execution yet', len(p['meals']) == 3 and not s['execution_records'] and s['foods'][0]['grams'] == 200)
    ui.check('missing ingredients displayed', any(m['missing'] for m in p['meals']))
    ui.click('预览模拟补菜')
    ui.check('shopping preview does not add stock', len(ui.state()['foods']) == 1)
    ui.click('取消补菜')
    ui.check('cancel shopping does not add stock', len(ui.state()['foods']) == 1)
    ui.click('预览模拟补菜')
    ui.click('确认模拟补菜入库')
    s = ui.state()
    p = next(p for p in s['programs'] if p['id'] == s['program_active'])
    ui.check('confirmed simulated stock has explicit origin', len(s['foods']) > 1 and all(f.get('origin') == '模拟补菜' for f in s['foods'][1:]))
    ui.check('all three menus have stock', all(not m['missing'] for m in p['meals']))
    baseline = json.loads(json.dumps(s))
    ui.shot('01-three-menus.png')
    ui.click('我吃完了 · 核对早餐')
    ui.click('取消实际食用确认')
    ui.check('cancellation leaves stock and intake unchanged', ui.state() == baseline)
    ui.click('我吃完了 · 核对早餐')
    ui.fill('实际早餐：鸡蛋与豆腐', name='actual_title_input')
    ui.click('移除', index=1)
    ui.click('添加 豆腐 · 库存 150g', index=0)
    ui.fill('50', name='actual_amount', index=1)
    ui.check('edited draft still has no stock mutation', ui.state() == baseline)
    ui.click('确认实际食用并保存')
    s = ui.state()
    ui.check('breakfast produces one immutable record', len(s['execution_records']) == 1)
    e = s['execution_records'][0]
    ui.check('actual differs from preserved recommendation', [u['name'] for u in e['recommendation']['uses']] == ['鸡蛋','菠菜'] and [u['name'] for u in e['actual']] == ['鸡蛋','豆腐'])
    ui.check('actual nutrients use actual quantities', e['kcal'] == 181 and e['protein'] == 17)
    before_food = {f['id']:f['grams'] for f in baseline['foods']}
    after_food = {f['id']:f['grams'] for f in s['foods']}
    for u in e['actual']:
        before_food[u['food_id']] -= u['grams']
    ui.check('only actual ingredients deducted', before_food == after_food)
    ui.check('breakfast counts once (33 percent)', '33%' in ui.text())
    ui.check('confirmed breakfast has no repeat button', '我吃完了 · 核对早餐' not in ui.text())
    first = json.loads(json.dumps(e))
    ui.click('生成 / 更新未确认三餐')
    ui.check('regeneration cannot overwrite execution', ui.state()['execution_records'][0] == first)
    ui.click('预览模拟补菜')
    ui.click('确认模拟补菜入库')
    ui.click('我吃完了 · 核对午餐')
    ui.click('确认实际食用并保存')
    ui.check('two confirmed slots (66 percent)', len(ui.state()['execution_records']) == 2 and '66%' in ui.text())
    ui.click('我吃完了 · 核对晚餐')
    current = ui.state()
    dinner_amount = next(p for p in current['programs'] if p['id'] == current['program_active'])['meals'][2]['uses'][0]['grams']
    ui.scroll(-10000)
    ui.fill('0', name='actual_amount', index=0)
    before_invalid = ui.state()
    ui.click('确认实际食用并保存')
    ui.check('zero quantity rejects confirmation without writes', ui.state() == before_invalid)
    ui.fill(str(dinner_amount), name='actual_amount', index=0)
    ui.fill('鸡蛋', name='external_name')
    ui.fill('50', name='external_grams')
    ui.click('添加库存外实际食物')
    ui.shot('02-actual-editor.png')
    stock_before = {f['id']:f['grams'] for f in ui.state()['foods']}
    ui.click('确认实际食用并保存')
    s = ui.state()
    ui.scroll(-10000)
    ui.check('all three confirmed and 100 percent recap', len(s['execution_records']) == 3 and '体验复盘 · 100%' in ui.text() and '体验完成！' in ui.text())
    dinner = s['execution_records'][2]
    ui.check('external intake counted with no stock deduction', any(u['food_id'] == 0 and u['name'] == '鸡蛋' for u in dinner['actual']))
    for u in dinner['actual']:
        if u['food_id'] > 0:
            stock_before[u['food_id']] -= u['grams']
    ui.check('external food never deducted from fridge', stock_before == {f['id']:f['grams'] for f in s['foods']})
    ui.check('earlier record unchanged after subsequent meals', s['execution_records'][0] == first)
    ui.shot('03-complete-review.png')
    records = json.loads(json.dumps(s['execution_records']))
    ui.click('选择后续健康方案')
    ui.click('确认选中方案 · 去录冰箱  →')
    ui.click('完成建档 · 开始托管  →')
    ui.click('◔  档案')
    ui.scroll(10000)
    ui.check('long-term tracking retains all confirmed execution', ui.state()['execution_records'] == records and '实际早餐：鸡蛋与豆腐' in ui.text())
    ui.shot('04-long-term-history.png')
    ui.click('⌂  首页')
    ui.click('生成这一餐  →')
    recommended = json.loads(json.dumps(ui.state()['plans'][-1]))
    ui.click('就吃这套 · 设为今晚方案  →')
    ui.click('我吃完了 · 核对实际用量')
    ui.fill('50', name='actual_amount', index=0)
    ui.fill('2000', name='actual_extra')
    ui.click('确认实际食用并保存')
    s = ui.state()
    ui.check('multi-day confirmation uses same independent ledger', len(s['execution_records']) == 4 and s['execution_records'][-1]['slot'] == -1)
    entry = s['execution_records'][-1]
    expected_kcal = 2000 + int(sum(u['grams'] * u['nutrition']['kcal'] / 100 for u in entry['actual']))
    active = next(p for p in s['programs'] if p['id'] == s['program_active'])
    ui.check('actual beyond reference goal is recorded honestly', entry['kcal'] == expected_kcal and entry['kcal'] > active['daily_kcal'])
    ui.check('ordinary recommendation is not overwritten by actual amount', s['plans'][-1]['uses'] == recommended['uses'] and s['execution_records'][-1]['actual'][0]['grams'] == 50)
    history = json.loads(json.dumps(s['execution_records']))
    ui.click('删除这个方案…')
    ui.click('确认删除方案')
    ui.check('deleting menu retains all confirmed history', ui.state()['execution_records'] == history)
    (ui.profile/'expected-state.json').write_text(json.dumps(ui.state(), ensure_ascii=False), encoding='utf-8')
    (ui.profile/'checks.json').write_text(json.dumps(ui.checks, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=18641)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--restart', action='store_true')
    parser.add_argument('--legacy', action='store_true', help='preseeded synthetic pre-ledger state only')
    args = parser.parse_args()
    profile = args.profile.resolve()
    if not profile.is_relative_to((APP/'.local-state').resolve()) or not profile.name.startswith('qa-'):
        parser.error('requires isolated task-owned qa-* profile')
    ui = DayUI(args.port, profile)
    if args.legacy:
        before = ui.state()
        ui.click('⚙  设置')
        ui.click('关闭提醒')
        after = ui.state()
        ui.check('migration retains legacy stock and plans', after['foods'] == before['foods'] and after['plans'] == before['plans'])
        ui.check('migration does not fabricate actual history', after['execution_records'] == [] and after['execution_next'] == 1)
        ui.check('legacy program remains active', after['program_active'] == before['program_active'])
        ui.check('legacy multi-day programs get default kind', all(p['kind'] == 'health' and p['meals'] == [] for p in after['programs']))
    elif args.restart:
        expected = json.loads((profile/'expected-state.json').read_text(encoding='utf-8'))
        ui.check('restart preserves stock, recommendations and execution snapshots', ui.state() == expected)
    else:
        exercise(ui)
