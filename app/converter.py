import csv
import json

def csv_to_json(csv_file):
    data = []
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return json.dumps(data)
