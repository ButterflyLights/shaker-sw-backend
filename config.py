import json

fn = "../config.json"

with open(fn) as f:
    configData = json.load(f)