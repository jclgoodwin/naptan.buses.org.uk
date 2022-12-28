# import io
import shutil
# import tarfile
import requests
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    path = Path("naptan.xml")

    if not path.exists():
        url = "https://naptan.api.dft.gov.uk/v1/access-nodes"
        params = {"dataFormat": "xml"}
        response = requests.get(url, params, timeout=60, stream=True)
        print(response.headers)

        with path.open("wb") as open_file:
            for chunk in response.iter_content(chunk_size=102400):
                open_file.write(chunk)

    iterator = ET.iterparse(path)

    site_dir = Path("_site")
    if site_dir.exists():
        shutil.rmtree(site_dir)

    site_dir.mkdir()

    stops_dir = site_dir / "stops"
    stops_dir.mkdir()

    # tar_file_path = Path("github-pages.tar.gz")
    # if tar_file_path.exists():
    #     tar_file_path.unlink()
    # tar_file_path.touch()
    # tar_file = tarfile.open(tar_file_path, "w")

    for event, element in iterator:

        element.tag = element.tag.removeprefix("{http://www.naptan.org.uk/}")

        # if event == "start":
        #     # if element.tag == "{http://www.naptan.org.uk/}NaPTAN":
        #     #     modified_at = get_datetime(element.attrib["ModificationDateTime"])
        #     #     if modified_at == source.datetime:
        #     #         return

        #     #     source.datetime = modified_at

        if element.tag == "StopPoint":
            atco_code = element.findtext("AtcoCode")
            assert atco_code

            xml = ET.tostring(element)

            path = stops_dir / f"{atco_code}.xml"
            with path.open("wb") as open_file:
                open_file.write(xml)

            # tarinfo = tarfile.TarInfo(name=f"{atco_code}.xml")
            # tarinfo.size = len(xml)
    
            # tar_file.addfile(tarinfo, io.BytesIO(xml))

            element.clear()

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
