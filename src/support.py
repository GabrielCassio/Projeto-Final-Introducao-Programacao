import csv

def import_csv_layout(path):
    terrain_map = []
    with open(path) as map:
        level = csv.reader(map, delimiter=',')
        for row in level:
            terrain_map.append(list(row))
    return terrain_map