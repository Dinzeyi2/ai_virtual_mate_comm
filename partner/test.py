import json
import os

a = False
with open('partner/config.json', "r", encoding="utf-8") as f:
    config = json.load(f)

print(config)
