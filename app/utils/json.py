from bson import json_util

def dumps(obj):
    return json_util.dumps(obj)

def loads(str):
    return json_util.loads(str)
