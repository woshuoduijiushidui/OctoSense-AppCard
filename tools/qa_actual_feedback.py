"""Unknown stock labels and stable validation feedback in an isolated native UI."""
import argparse
import json
from pathlib import Path
from qa_day import APP, DayUI


def button(ui):
    return next(w for w in ui.snap() if w.get('t') == '确认实际食用并保存')


def exercise(ui):
    ui.click('选择', index=1)
    ui.click('女性')
    for i, value in enumerate(('30', '170', '65', '', '清淡', '')):
        ui.fill(value, i)
    ui.click('下一步 · 选择周期方案  →')
    ui.click('选择1天体验方案')
    ui.click('确认选中方案 · 去录冰箱  →')
    ui.fill('牛肉', name='food_name')
    ui.fill('300', name='food_grams')
    ui.fill('2', name='food_days')
    ui.click('预览并确认入库  →')
    ui.click('确认入库')
    ui.click('完成建档 · 开始托管  →')
    ui.click('✦  方案')
    ui.click('生成 / 更新未确认三餐')
    recommendation = json.loads(json.dumps(next(p for p in ui.state()['programs'] if p['id'] == ui.state()['program_active'])['meals'][0]))
    ui.click('我吃完了 · 核对早餐')
    ui.click('添加 牛肉 · 库存 300g')
    ui.check('unknown stock has inline label fields', '牛肉没有营养参考' in ui.text() and any(w.get('i') == 'stock_actual_kcal' for w in ui.snap()))
    before = ui.state()
    ui.click('确认实际食用并保存')
    ui.check('missing reference names the offending food', '牛肉缺少或填错营养参考' in ui.text())
    ui.check('missing reference makes no writes', before == ui.state())
    rect = button(ui)['r']
    x, y, w, h = rect
    ui.get('click', x=x+w/2, y=y+h/2, wait=1)
    ui.check('failed confirmation preserves scroll position', button(ui)['r'] == rect)
    # Synthetic fixture numbers test arithmetic only, not a nutrition recommendation.
    for name, value in [('stock_actual_kcal', '120'), ('stock_actual_protein', '10'), ('stock_actual_fiber', '0'), ('stock_actual_vitamin', '0')]:
        ui.fill(value, name=name)
    ui.fill('2001', name='actual_extra')
    ui.click('确认实际食用并保存')
    ui.check('extra calories has a separate actionable error', '额外用油、饮料热量请填0–2000整数' in ui.text() and before == ui.state())
    ui.fill('', name='actual_extra')
    ui.shot('inline-stock-labels.png')
    ui.click('确认实际食用并保存')
    s = ui.state()
    entry = s['execution_records'][-1]
    ui.check('complete labels and blank optional calories confirm', len(s['execution_records']) == 1 and entry['kcal'] == 120 and entry['extra_kcal'] == 0)
    ui.check('confirmed stock uses actual grams', s['foods'][0]['grams'] == 200 and entry['actual'][0]['grams'] == 100)
    ui.check('nutrition snapshot stores entered reference', entry['actual'][0]['nutrition'] == dict(known=True, kcal=120, protein=10, fiber=0, vitamin_c=0))
    ui.check('stock reference is not silently edited', 'nutrition' not in s['foods'][0])
    ui.check('recommendation snapshot is preserved', entry['recommendation'] == recommendation)
    ui.check('successful confirmation updates progress once', '已确认进度 33%' in ui.text())
    ui.click('我吃完了 · 核对午餐')
    ui.click('添加 牛肉 · 库存 200g')
    ui.fill('130', name='stock_actual_kcal')
    ui.click('取消实际食用确认')
    ui.check('cancelled label draft never alters history or stock', ui.state() == s)
    (ui.profile/'checks.json').write_text(json.dumps(ui.checks, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--profile', type=Path, required=True)
    args = parser.parse_args()
    profile = args.profile.resolve()
    if not profile.is_relative_to((APP/'.local-state').resolve()) or not profile.name.startswith('qa-'):
        parser.error('requires an isolated qa-* profile')
    exercise(DayUI(args.port, profile))
