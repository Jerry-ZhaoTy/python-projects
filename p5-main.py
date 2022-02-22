# project: p5
# submitter: tzhao86
# partner: none
# hours: 6.0

from zipfile import ZipFile, ZIP_DEFLATED
from shapely.geometry import box
from io import TextIOWrapper
import matplotlib.pyplot as plt
import pandas as pd
import geopandas
import csv, json
import netaddr
import pyproj
import time
import sys
import re

# declare global variables
with open("ip2location.csv") as f:
    ip_csv = list(csv.reader(f))[1:]
index = 0

def ip_check(ip):
    start_time = time.time()
    ip_info = {}  
    int_ip = int(netaddr.IPAddress(ip))
    global index
    while index >= 0 and index < len(ip_csv):
        if int_ip < int(ip_csv[index][0]): index -= 1
        elif int_ip > int(ip_csv[index][1]): index += 1
        else:
            ip_info["ip"] = ip
            ip_info["int_ip"] = int_ip
            ip_info["region"] = ip_csv[index][3]
            ip_info["ms"] = (time.time() - start_time) * 1000
            break
    return ip_info

def rezip(src, dest):
    start_time = time.time()
    with ZipFile(src) as zf:
         with zf.open("rows.csv", "r") as f:
            rows = csv.reader(TextIOWrapper(f))
            header = next(rows)
            header.append("region")
            data = []
            for row in rows:
                ip = row[0]
                new_ip = []
                for digit in ip:
                    if digit.isalpha():
                        digit = '0'
                    new_ip.append(digit)
                new_ip = ''.join(new_ip)
                row[0] = new_ip
                data.append(row)
            data.sort()
            for row in data:
                ip_info = ip_check(row[0])
                row[0] = ip_info["int_ip"]
                row.append(ip_info["region"])
            data.sort()
            df = pd.DataFrame(data, columns=header)
    with ZipFile(dest, "w", compression=ZIP_DEFLATED) as zf:
        with zf.open("rows.csv", "w") as f:
            df.to_csv(f, index=False)

def zipcode_generator(zipFile):
    zipcode_list = set()
    regex_zipcode = re.compile(r'(\d{5})(-\d{4})?')
    with ZipFile(zipFile) as zf:
        filenames = list(map(lambda i: i.filename, filter(lambda j: "." in j.filename, zf.infolist())))
        for filename in filenames:
            with zf.open(filename) as f:
                for row in TextIOWrapper(f):
                    if re.findall(regex_zipcode, row) == []: continue
                    zipcode = re.findall(regex_zipcode, row)[0][0] + re.findall(regex_zipcode, row)[0][1]
                    zipcode_list.add(zipcode)
    for zipcode in zipcode_list:
        print(zipcode)

def geograph(ESPG_ID, svg_name):
    with ZipFile("server_log2.zip") as zf:
        with zf.open("rows.csv") as f:
            tiny_df = pd.read_csv(f)
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    world["region"] = world.apply(lambda x: len(tiny_df[tiny_df.region == x["name"]]), axis=1)
    world.loc[(world["region"] == 0), "color"] = "lightgray"
    world.loc[(0 < world["region"]) & (world["region"] <= 1000), "color"] = "orange"
    world.loc[(world["region"] >= 1000), "color"] = "red"
    crs = pyproj.CRS.from_epsg(ESPG_ID)
    window = box(crs.area_of_use.west, crs.area_of_use.south, crs.area_of_use.east, crs.area_of_use.north)
    result = world.intersection(window)
    result = result[~result.is_empty]
    plt.figure()
    result.to_crs(crs).plot(figsize=(8,8), color=world["color"]) 
    with open(svg_name, "w") as f:
        plt.savefig(f, format="svg")
    
def main():
    if len(sys.argv) < 2:
        print("usage: main.py <command> args...")
    elif sys.argv[1] == "ip_check":
        ips = sys.argv[2:]
        ip_info = []
        for ip in ips:
            ip_info.append(ip_check(ip))
        print(json.dumps(ip_info))
    elif sys.argv[1] == "region":
        rezip(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "zipcode":
        zipFile = sys.argv[2]
        zipcode_generator(zipFile)
    elif sys.argv[1] == "geo":
        ESPG_ID = sys.argv[2]
        svg_name = sys.argv[3]
        geograph(ESPG_ID, svg_name)
    else:
        print("unknown command: "+sys.argv[1])

if __name__ == '__main__':
     main()
