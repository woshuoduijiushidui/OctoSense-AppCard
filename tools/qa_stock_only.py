"""Synthetic native regression: no replenishment and exact exhausted-batch removal."""
import argparse
import copy
import json
import time
from pathlib import Path
from qa_day import APP, DayUI
from qa_recipe import menu
from qa_online import fixture, request, prepare, wait


def seed(profile, seed_file, hub):
    # Use the existing test-only request substitute, not a live model account.
    prepare(profile, seed_file, hub, True)
    data=profile/'pantry-steward'
    s=json.loads((data/'pantry.json').read_text(encoding='utf-8'))
    expiry=int(time.time())+86400
    s['foods']=[dict(id=1,name='豆腐',grams=100,expires=expiry),
                dict(id=91,name='豆腐',grams=0,expires=expiry-100),
                dict(id=92,name='豆腐',grams=0,expires=expiry-50)]
    old=copy.deepcopy(s['programs'][0]);old.update(id=51,kind='experience',days=1,name='旧缺菜体验',meals=[dict(slot=0,title='菠菜豆腐',uses=[dict(food_id=1,name='豆腐',grams=30)],missing=[dict(name='菠菜',grams=20,avoided=False)],steps='旧推荐',source='在线 AI')])
    s['programs'].append(old);s['program_next']=52
    (data/'pantry.json').write_text(json.dumps(s,ensure_ascii=False),encoding='utf-8')
    (profile/'before.json').write_text(json.dumps(s,ensure_ascii=False),encoding='utf-8')
    (data/'inventory-removals.json').write_text(json.dumps([dict(id=91,name='豆腐',expires=expiry-100)],ensure_ascii=False),encoding='utf-8')


def output(slots=(0,1,2),grams=30):
    return dict(feasible=True,reason='合成测试响应',meals=[menu([dict(food_id=1,grams=grams)],slot=slot) for slot in slots])


def exercise(ui):
    initial=json.loads((ui.profile/'before.json').read_text(encoding='utf-8'))
    s=ui.state()
    ui.check('only requested exhausted tofu batch removed', [f['id'] for f in s['foods']]==[1,92])
    ui.check('positive stock and other exhausted batch untouched', s['foods']==[f for f in initial['foods'] if f['id']!=91])
    ui.check('batch removal preserves confirmed history exactly', s['execution_records']==initial['execution_records'])
    ui.check('legacy unconfirmed missing-stock menu cleared', next(p for p in s['programs'] if p['id']==51)['meals']==[])
    bad=dict(feasible=True,title='菠菜豆腐餐',minutes=10,reason='合成测试',uses=[dict(food_id=1,grams=30)],steps=['称重豆腐','将菠菜与豆腐做熟'])
    fixture(ui,bad);ui.click('生成这一餐  →');wait(ui)
    ui.check('ordinary AI cannot name unallocated spinach', ui.state()['plans']==[] and ui.state()['foods']==s['foods'])
    ui.click('⚙  设置');ui.click('选择下一周期方案…');ui.click('选择1天体验方案')
    ui.click('确认选中方案 · 去录冰箱  →');ui.click('完成建档 · 开始托管  →');ui.click('✦  方案')
    baseline=ui.state()
    for name,alter in [
        ('missing-item response',lambda v:v['meals'][0].__setitem__('missing',[dict(name='菠菜',grams=20)])),
        ('unknown food id',lambda v:v['meals'][0]['uses'][0].__setitem__('food_id',999)),
        ('aggregate overbooking',lambda v:[m['uses'][0].__setitem__('grams',60) for m in v['meals']]),
        ('unallocated ingredient in title',lambda v:v['meals'][0].__setitem__('title','菠菜豆腐')),
        ('unallocated ingredient in instructions',lambda v:v['meals'][0]['steps'].append('添加菠菜')),
    ]:
        v=output();alter(v);fixture(ui,v);ui.click('生成 / 更新未确认三餐');wait(ui)
        after=ui.state();p=next(p for p in after['programs'] if p['id']==after['program_active'])
        ui.check(name+' rejected without stock or ledger writes', p['meals']==[] and after['foods']==baseline['foods'] and after['execution_records']==baseline['execution_records'])
    fixture(ui,dict(feasible=False,reason='当前库存不足以满足请求',meals=[]));ui.click('生成 / 更新未确认三餐');wait(ui)
    ui.check('insufficient inventory shows reason without substitution', '当前库存不足' in ui.text() and ui.state()['foods']==baseline['foods'])
    fixture(ui,output());ui.click('生成 / 更新未确认三餐');wait(ui)
    p=next(p for p in ui.state()['programs'] if p['id']==ui.state()['program_active'])
    ui.check('AI creates three meals only from available tofu', len(p['meals'])==3 and all(m['uses']==[dict(food_id=1,name='豆腐',grams=30)] and m['missing']==[] for m in p['meals']))
    schema=request(ui)['schema']['properties']['meals']['items']
    ui.check('request schema removes missing and requires stock uses', 'missing' not in schema['properties'] and schema['properties']['uses']['minItems']==1 and 'missing_references' not in request(ui)['input'])
    ui.check('replenishment buttons no longer present', not any(w.get('t') in ('预览模拟补菜','确认模拟补菜入库','生成采购清单 · 扩展能力') for w in ui.snap()))
    ui.check('generation leaves stock unchanged', ui.state()['foods']==baseline['foods'])
    ui.shot('stock-only-three-meals.png')
    for slot,name,progress in [(0,'早餐',33),(1,'午餐',66),(2,'晚餐',100)]:
        ui.click('我吃完了 · 核对'+name);ui.click('确认实际食用并保存')
        ui.check('stock-only '+name+' confirmation advances '+str(progress), ('已确认进度 '+str(progress)+'%') in ui.text() if progress<100 else '体验复盘 · 100%' in ui.text())
        if slot==0:
            history=copy.deepcopy(ui.state()['execution_records'])
            fixture(ui,output((1,2)));ui.click('生成 / 更新未确认三餐');wait(ui)
            ui.check('regeneration preserves confirmed snapshot', request(ui)['input']['slots']==[1,2] and ui.state()['execution_records']==history)
    final=ui.state()
    ui.check('only actual stock quantities deducted', next(f['grams'] for f in final['foods'] if f['id']==1)==10 and next(f['grams'] for f in final['foods'] if f['id']==92)==0)
    ui.check('earlier history remains available after complete trial', final['execution_records'][:len(initial['execution_records'])]==initial['execution_records'])
    ui.shot('stock-only-complete.png')
    (ui.profile/'checks.json').write_text(json.dumps(ui.checks,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--profile',type=Path,required=True)
    parser.add_argument('--port',type=int)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--seed',type=Path)
    parser.add_argument('--hub',type=Path)
    args=parser.parse_args();profile=args.profile.resolve()
    if not profile.is_relative_to((APP/'.local-state').resolve()) or not profile.name.startswith('qa-'):
        parser.error('isolated qa-* profile required')
    if args.prepare:
        if not args.seed or not args.hub:parser.error('--prepare needs --seed and --hub')
        seed(profile,args.seed,args.hub)
    else:
        if not args.port:parser.error('--port required')
        exercise(DayUI(args.port,profile))
