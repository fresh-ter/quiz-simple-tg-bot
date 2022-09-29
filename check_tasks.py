import json

with open("tasks.json", "r") as f:
        tasks = json.load(f)

tasks = tasks['tasks']

for x in tasks:
	print("-----------------------------")
	print()
	print()
	print(x['text'])
	print()
	print()
	print("Answer:", x['answer'])
	print()
	print("-----------------------------")