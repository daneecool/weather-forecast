import requests
import xml.etree.ElementTree as ET
from datetime import datetime

URL = "https://www.data.jma.go.jp/developer/xml/feed/extra.xml"

def extract_typhoon_entries():
    response = requests.get(URL)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    keywords = ["台風解析・予報情報", "台風の暴風域に入る確率"]
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    results = []

    for entry in root.findall('atom:entry', ns):
        title_elem = entry.find('atom:title', ns)
        if title_elem is not None and any(kw in title_elem.text for kw in keywords):
            updated_elem = entry.find('atom:updated', ns)
            link_elem = entry.find('atom:link', ns)
            data = {
                "title": title_elem.text,
                "updated": updated_elem.text if updated_elem is not None else None,
                "link": link_elem.attrib.get('href') if link_elem is not None else None
            }
            results.append(data)
    return results

if __name__ == "__main__":
    entries = extract_typhoon_entries()
    if entries:
        for entry in entries:
            print(f"Title: {entry['title']}")
            print(f"Updated: {entry['updated']}")
            print(f"Link: {entry['link']}\n")
    else:
        print("No matching typhoon entries found.")