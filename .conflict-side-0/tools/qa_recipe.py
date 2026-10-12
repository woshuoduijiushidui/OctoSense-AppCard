"""Structured synthetic menu replies shared by current native suites."""
def steps(ids):
    return [dict(action='清洗',food_ids=list(ids),minutes=0),dict(action='充分煮熟',food_ids=list(ids),minutes=10)]


def menu(uses,title='水煮',slot=None):
    result=dict(title=title,uses=uses,steps=steps([u['food_id'] for u in uses]))
    if slot is not None:result['slot']=slot
    return result
