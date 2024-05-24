import json
from pathlib import Path
import os

def store_data(players, week, day):
	file_path = '2024/week' + str(week) + '/day' + str(day) + '.json'
	file_path = os.path.join(os.path.dirname(__file__), file_path)
	with open(file_path, 'x') as output:
		json.dump(players, output, indent=2)

def get_data(week, day):
	file_path = '2024/week' + str(week) + '/day' + str(day) + '.json'
	file_path = os.path.join(os.path.dirname(__file__), file_path)
	file = open(file_path, 'r')
	players = json.load(file)
	file.close()
	return players

def data_exists(week, day):
	file_path = '2024/week' + str(week) + '/day' + str(day) + '.json'
	file_path = Path(os.path.join(os.path.dirname(__file__), file_path))
	if file_path.exists():
		return True
	return False
