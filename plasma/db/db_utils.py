import csv


def write_lod_to_csv(lod, csv_name):
    keys = lod[0].keys()
    with open(csv_name, 'w') as outfile:
        dw = csv.DictWriter(outfile, keys)
        dw.writeheader()
        dw.writerows(lod)