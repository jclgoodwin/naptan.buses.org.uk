import json
from bng_latlon import OSGB36toWGS84
import shutil
import requests
import xml.etree.ElementTree as ET
from pathlib import Path


def download_naptan(path):
    url = "https://naptan.api.dft.gov.uk/v1/access-nodes"
    params = {"dataFormat": "xml"}

    # # for testing purposes, the full national dataset is a bit big
    # params["atcoAreaCodes"] = "030,290,639"

    response = requests.get(url, params, timeout=60, stream=True)
    print(response.headers)

    with path.open("wb") as open_file:
        for chunk in response.iter_content(chunk_size=102400):
            open_file.write(chunk)


def get_location(element):
    # print(ET.tostring(element))
    longitude = element.findtext("Translation/Longitude")
    latitude = element.findtext("Translation/Latitude")

    # if longitude is None:
    #     longitude = element.findtext("Longitude")
    #     latitude = element.findtext("Latitude")

    if longitude is not None:
        return (longitude, latitude)

    easting = int(element.findtext("Easting"))
    northing = int(element.findtext("Northing"))

    latitude, longitude = OSGB36toWGS84(easting, northing)

    return (longitude, latitude)


def get_element(element):
    # remove namespace crap to make our life easier
    element.tag = element.tag.removeprefix("{http://www.naptan.org.uk/}")
    return element


def get_stop(element):
    atco_code = element.findtext("AtcoCode")
    assert atco_code

    location = get_location(element.find("Place/Location"))

    element.clear()

    return (atco_code, location)


def main():
    path = Path("naptan.xml")

    if not path.exists():
        download_naptan(path)

    print("1")

    iterator = ET.iterparse(path)

    site_dir = Path("_site")
    if site_dir.exists():
        shutil.rmtree(site_dir)

    site_dir.mkdir()

    print("2")

    elements = (get_element(element) for _, element in iterator)
    stops = (element for element in elements if element.tag == "StopPoint")

    # data_frame = pandas.GeoDataFrame.from_features(
    #     get_stop(stops_dir, element) for element in stops
    # )

    # print(data_frame)

    stops = [get_stop(element) for element in stops]

    with open(site_dir / "stops.json", "w") as fp:
        json.dump(stops, fp)

    shutil.copy("index.html", site_dir)
    shutil.copy("js.js", site_dir)

    print("3")

    #     by_admin_area = {}

    #     with archive.open("Stops.csv") as open_file:
    #         csv_reader = csv.DictReader(
    #             io.TextIOWrapper(open_file, encoding='cp1252')
    #         )
    #         for item in csv_reader:
    #             if item['AdministrativeAreaCode'] in by_admin_area:
    #                 by_admin_area[item['AdministrativeAreaCode']].append(item)
    #             else:
    #                 by_admin_area[item['AdministrativeAreaCode']] = []

    # admin_areas = []
    # for key, items in by_admin_area.items():
    #     points = shapely.geometry.MultiPoint([(
    #         float(item["Longitude"]), float(item["Latitude"])
    #     ) for item in items if item['Status'] == "act"])

    #     admin_areas.append({
    #         "type": "Feature",
    #         "geometry": shapely.geometry.mapping(points.convex_hull)
    #     })

    # with open("admin-areas.json", "w") as fp:
    #     json.dump({"type": "FeatureCollection", "features": admin_areas}, fp)

    # # for admin_area in by_admin_area:
    # #     with open(f'admin-areas/{admin_area}.json', "w") as file:
    # #         json.dump(by_admin_area[admin_area], file)


if __name__ == "__main__":
    main()
