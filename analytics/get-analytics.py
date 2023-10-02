import json
ips = []
with open("amcs.json") as f:
	data = json.load(f)

for d in data["requests"]:
	if d["ip"] not in ips:
		ips.append(d["ip"])

print(" ".join(ips))
