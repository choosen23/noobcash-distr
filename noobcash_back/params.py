import json

def getCapacity():
	with open("params.json", "r") as jsonFile:
	data = json.load(jsonFile)

	return int(data['capacity'])


def changeCapacity(new_capacity):
	with open("params.json", "r") as jsonFile:
	data = json.load(jsonFile)

	data['capacity'] = int(new_capacity)

	with open("params.json", "w") as jsonFile:
		json.dump(data, jsonFile)


def getDifficulty():
	with open("params.json", "r") as jsonFile:
	data = json.load(jsonFile)

	return int(data['difficulty'])