import csv

def csvReader(filename):
    data = []
    with open(filename) as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            data.append(float(row[0]))
    return data

def unpack(data):
    left_index = 0
    number = 0
    unpacked_data = []
    for right_index in range(len(data)):
        if data[right_index] == "{":
            number += 1
        if data[right_index] == "}":
            number -= 1
            if number == 0:
                unpacked_data.append(data[left_index:right_index + 1])
                left_index = right_index + 1
                number = 0
    return unpacked_data


