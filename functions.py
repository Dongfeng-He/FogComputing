import csv

def csvReader(filename):
    data = []
    with open(filename) as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            data.append(float(row[0]))
    return data


