"""PR #21 regression with isolated synthetic stock and native restart phases."""
import argparse,copy,json,time,subprocess,sys
from pathlib import Path
from qa_day import APP,DayUI
from qa_recipe import menu
from qa_online import fixture,request
from qa_ai_nutrition import estimate_fixture


def seed(profile,seed_path,hub):
    subprocess.run([sys.executable,'-B','-X','utf8',str(APP/'tools/qa_ai_nutrition.py'),'--prepare','--profile',str(profile),'--seed',str(seed_path),'--hub',str(hub)],check=True)
    p=profile/'pantry-steward/pantry.json';s=json.loads(p.read_text(encoding='utf-8'))
    s['foods']=[dict(id=1,name='豆腐',grams=100,expires=int(time.time())+172800),dict(id=7,name='nutrition bar',grams=50,expires=int(time.time())+172800)]
    s['last_goal']='execution_records execution_next auto_generate';s.pop('execution_records');s.pop('execution_next');s.pop('auto_generate')
    old=dict(id=70,title='番茄豆腐汤',uses=[dict(food_id=1,name='豆腐',grams=30)],accepted=True,consumed=False,revision=1,created=int(time.time()),reason='旧自由文本',goal='',source='在线 AI',previous='',minutes=10,steps='加入番茄和豆腐')
    consumed=copy.deepcopy(old);consumed.update(id=71,consumed=True,title='历史已确认菜单')
    s['plans']=[old,consumed];s['active']=70
    p.write_text(json.dumps(s,ensure_ascii=False),encoding='utf-8');(profile/'before.json').write_text(json.dumps(s,ensure_ascii=False),encoding='utf-8')
    q=profile/'qa-bundle/main.splash';src=q.read_text(encoding='utf-8');src=src.replace('fs.write("qa-request.json", payload.to_json())','''fs.write("qa-request.json", payload.to_json())
    let calls = []
    if fs.exists("qa-calls.json") { calls = fs.read("qa-calls.json").parse_json() }
    let kind = "menu"
    if has_field(payload.input, "items") { kind = "nutrition" }
    calls.push(kind) fs.write("qa-calls.json", calls.to_json())''');src='let qa_late_callback = nil\n'+src;src=src.replace('if fixture.delay { start_timeout', 'if has_field(fixture, \"force_timeout\") && fixture.force_timeout { model_deadline = time_now() - 1 if has_field(fixture, "race") && fixture.race { qa_late_callback = callback } else { start_timeout(3.0, || callback(fixture.reply)) } return 1 }\n    if fixture.delay { start_timeout');src=src.replace('else { callback(fixture.reply) }', 'else { callback(fixture.reply) if qa_late_callback != nil { let late = qa_late_callback qa_late_callback = nil late({is_ok: false error: \"late overwritten reply\"}) } }');q.write_bytes(src.encode('utf-8'));subprocess.run([str(hub),'stamp',str(q.parent)],check=True)


def reset_calls(ui):
    (ui.profile/'pantry-steward/qa-calls.json').write_text('[]',encoding='utf-8')


def timeout_fixture(ui,race=False):
    (ui.profile/'pantry-steward/qa-nutrition-reply.json').write_text(json.dumps(dict(delay=False,force_timeout=True,race=race,reply=dict(is_ok=False,error='late nutrition reply'))),encoding='utf-8')


def once(ui):
    return json.loads((ui.profile/'pantry-steward/qa-calls.json').read_text(encoding='utf-8'))==['nutrition','menu']


def trial(slots=(0,1,2)):
    return dict(feasible=True,reason='合成库存测试',meals=[menu([dict(food_id=7,grams=5)],slot=s) for s in slots])


def exercise(ui):
    old=json.loads((ui.profile/'before.json').read_text(encoding='utf-8'))
    ui.check('legacy text collision stock loads without storage block','库存文件无法读取' not in ui.text())
    ui.click('▣  冰箱');ui.check('unlabelled nutrition-name stock readable','nutrition bar' in ui.text())
    estimate_fixture(ui,[dict(key=i,name='nutrition bar',known=False,kcal=0,protein=0,fiber=0,vitamin_c=0,basis='品牌未知') for i in (7,100)])
    ui.fill('nutrition bar',name='food_name');ui.fill('30',name='food_grams');ui.fill('2',name='food_days');ui.click('预览并确认  →');ui.click('确认入库');time.sleep(1)
    s=ui.state()
    ui.check('nutrition-name food enters stock without fake optional field',len(s['foods'])==3 and all('nutrition' not in f for f in s['foods'][1:]))
    ui.check('top-level execution fields initialized despite text collision',s['execution_records']==[] and s['execution_next']==1 and s['auto_generate'] is False)
    ui.check('legacy goal text preserved',s['last_goal']==old['last_goal'])
    ui.check('unconfirmed free-prose menu removed and active cleared',s['active']==0 and [p['id'] for p in s['plans']]==[71])
    ui.check('consumed legacy menu snapshot preserved',s['plans'][0]==old['plans'][1])
    baseline=copy.deepcopy(s)
    normal=dict(feasible=True,reason='合成菜单',minutes=10,**menu([dict(food_id=7,grams=10)]))
    bads=[]
    free=copy.deepcopy(normal);free.update(title='番茄豆腐汤',uses=[dict(food_id=1,grams=30)],steps=['加入番茄和豆腐','煮熟']);bads.append(('ordinary unknown tomato prose',free))
    ids=copy.deepcopy(normal);ids['steps'][0]['food_ids'].append(999);bads.append(('ordinary unallocated ingredient ID',ids))
    action=copy.deepcopy(normal);action['steps'][0]['action']='加入番茄';bads.append(('ordinary arbitrary ingredient action',action))
    for label,reply in bads:
        estimate_fixture(ui,error='network unavailable');fixture(ui,reply);reset_calls(ui);ui.click('⌂  首页');ui.click('生成这一餐  →');time.sleep(1.2)
        after=ui.state();ui.check(label+' rejected',after['plans']==baseline['plans'] and after['foods']==baseline['foods'] and after['execution_records']==[])
    estimate_fixture(ui,error='network unavailable');fixture(ui,normal);reset_calls(ui);ui.click('⌂  首页');ui.click('生成这一餐  →');time.sleep(1.2)
    s=ui.state();ui.check('failed ordinary estimate continues exactly one menu request',once(ui) and len(s['plans'])==2 and request(ui)['input']['inventory'][1]['nutrition']=={'known':False})
    ui.check('structured ordinary recipe rendered only from allocated IDs',s['plans'][-1]['title']=='水煮 · nutrition bar' and '番茄' not in s['plans'][-1]['steps'] and s['plans'][-1]['recipe_version']==2)
    estimate_fixture(ui,[]);fixture(ui,normal);reset_calls(ui);ui.click('⌂  首页');ui.click('生成这一餐  →');time.sleep(1.2)
    ui.check('malformed ordinary estimate still plans exactly once',once(ui) and len(ui.state()['plans'])==3)
    count=len(ui.state()['plans']);timeout_fixture(ui);fixture(ui,normal);reset_calls(ui);ui.click('⌂  首页');ui.click('生成这一餐  →');time.sleep(1.2)
    ui.check('nutrition timeout continues exactly one ordinary menu',once(ui) and len(ui.state()['plans'])==count+1)
    saved=copy.deepcopy(ui.state());time.sleep(3)
    ui.check('late timed-out nutrition reply cannot overwrite menu',ui.state()==saved)
    count=len(ui.state()['plans']);timeout_fixture(ui,race=True);reset_calls(ui);ui.click('⌂  首页');ui.click('生成这一餐  →');time.sleep(1.2)
    ui.check('stale reply cannot clobber queued current menu response',once(ui) and len(ui.state()['plans'])==count+1)
    estimate_fixture(ui,error='network unavailable')
    ui.check('unknown nutrition is shown without fake zero calories','营养未完整估算' in ui.text())
    ui.click('就吃这套 · 设为今晚方案  →');ui.click('我吃完了 · 核对实际用量');time.sleep(1);ui.click('确认实际食用并保存')
    s=ui.state();record=copy.deepcopy(s['execution_records'][0]);ui.check('unknown food confirmation records actual quantity',record['actual'][0]['name']=='nutrition bar' and record['actual'][0]['grams']==10 and record['nutrition_complete'] is False and s['foods'][1]['grams']==40)
    ui.click('⚙  设置');ui.click('选择下一周期方案…');ui.click('选择1天体验方案');ui.click('确认选中方案 · 去录冰箱  →');ui.click('完成建档 · 开始托管  →');ui.click('✦  方案')
    baseline=copy.deepcopy(ui.state())
    for label,edit in [('trial unknown tomato prose',lambda x:x['meals'][0].update(title='番茄豆腐汤',steps=['加入番茄和豆腐','煮熟'])),('trial unallocated ingredient ID',lambda x:x['meals'][0]['steps'][0]['food_ids'].append(999)),('trial arbitrary ingredient action',lambda x:x['meals'][0]['steps'][0].update(action='加入番茄'))]:
        out=trial();edit(out);estimate_fixture(ui,error='network unavailable');fixture(ui,out);ui.click('生成 / 更新未确认三餐');time.sleep(1.2)
        after=ui.state();p=next(p for p in after['programs'] if p['id']==after['program_active']);ui.check(label+' rejected',p['meals']==[] and after['foods']==baseline['foods'] and after['execution_records']==baseline['execution_records'])
    estimate_fixture(ui,error='network unavailable');fixture(ui,trial());reset_calls(ui);ui.click('生成 / 更新未确认三餐');time.sleep(1.2)
    p=next(p for p in ui.state()['programs'] if p['id']==ui.state()['program_active']);ui.check('failed trial estimate continues exactly one three-meal request',once(ui) and len(p['meals'])==3)
    estimate_fixture(ui,[]);reset_calls(ui);ui.click('生成 / 更新未确认三餐');time.sleep(1.2)
    ui.check('malformed trial estimate still plans exactly once',once(ui) and ui.state()['execution_records']==baseline['execution_records'])
    ui.click('我吃完了 · 核对早餐');time.sleep(1);ui.click('确认实际食用并保存');s=ui.state()
    ui.check('unknown trial meal advances execution without faking nutrition','已确认进度 33%' in ui.text() and s['execution_records'][-1]['nutrition_complete'] is False)
    ui.check('planning and trial confirmation preserve earlier record',s['execution_records'][0]==record)
    ui.shot('review-before-restart.png');(ui.profile/'restart-before.json').write_text(json.dumps(s,ensure_ascii=False),encoding='utf-8');(ui.profile/'checks.json').write_text(json.dumps(ui.checks,ensure_ascii=False,indent=2),encoding='utf-8')


def after_restart(ui):
    before=json.loads((ui.profile/'restart-before.json').read_text(encoding='utf-8'))
    ui.checks=json.loads((ui.profile/'checks.json').read_text(encoding='utf-8'))
    ui.check('native restart keeps nutrition-name inventory readable','库存文件无法读取' not in ui.text())
    ui.check('native restart retains confirmed ledger and exact stock',ui.state()['foods']==before['foods'] and ui.state()['execution_records']==before['execution_records'])
    fixture(ui,trial((1,2)));estimate_fixture(ui,error='network unavailable');reset_calls(ui);ui.click('✦  方案');ui.click('生成 / 更新未确认三餐');time.sleep(1.2)
    ui.check('post-restart regeneration only requests unconfirmed slots',once(ui) and request(ui)['input']['slots']==[1,2])
    ui.check('post-restart generation never overwrites actual snapshot',ui.state()['execution_records']==before['execution_records'] and ui.state()['foods']==before['foods'])
    ui.shot('review-after-restart.png');(ui.profile/'checks.json').write_text(json.dumps(ui.checks,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True);p.add_argument('--port',type=int);p.add_argument('--prepare',action='store_true');p.add_argument('--restart',action='store_true');p.add_argument('--seed',type=Path);p.add_argument('--hub',type=Path);a=p.parse_args();profile=a.profile.resolve()
    if not profile.is_relative_to((APP/'.local-state').resolve()) or not profile.name.startswith('qa-'):p.error('isolated qa-* profile required')
    if a.prepare:seed(profile,a.seed,a.hub)
    elif a.restart:after_restart(DayUI(a.port,profile))
    else:exercise(DayUI(a.port,profile))
