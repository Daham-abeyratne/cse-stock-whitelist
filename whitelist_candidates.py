import datetime
import json


# today = datetime.date.today()
# previous_day = today - datetime.timedelta(days=1)

today = '2026-01-16'
previous_day = "2026-01-17"

with open(f"{previous_day}.json") as f:
    prev_data = json.load(f)
with open(f'{today}.json') as f:
    today_data = json.load(f)


prev_stock_names = []
new_stock_names = []
for i in prev_data:
    prev_stock_names.append(i['symbol'])

for i in today_data:
    new_stock_names.append(i['symbol'])

whitelist_candidates = []

for stock in prev_stock_names:
    if stock in new_stock_names:
        whitelist_candidates.append(stock)
    else:
        continue

print(whitelist_candidates)

with open("whitelist_candidates.json","w") as f:
    json.dump(whitelist_candidates,f,indent=2)