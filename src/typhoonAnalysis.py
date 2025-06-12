import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json

URL = "https://www.data.jma.go.jp/developer/xml/feed/extra.xml"

def extract_latest_typhoon_entries():
    response = requests.get(URL)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    keywords = [
        "台風解析・予報情報（５日予報）",
        "台風の暴風域に入る確率"
    ]
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    latest_entries = {}

    for entry in root.findall('atom:entry', ns):
        title_elem = entry.find('atom:title', ns)
        updated_elem = entry.find('atom:updated', ns)
        link_elem = entry.find('atom:link', ns)
        if title_elem is not None and updated_elem is not None:
            for kw in keywords:
                if kw in title_elem.text:
                    updated_time = datetime.fromisoformat(updated_elem.text.replace("Z", "+00:00"))
                    if (kw not in latest_entries) or (updated_time > latest_entries[kw]["updated"]):
                        latest_entries[kw] = {
                            "title": title_elem.text,
                            "updated": updated_time,
                            "link": link_elem.attrib.get('href') if link_elem is not None else None
                        }
    return latest_entries

def print_element_info(element, indent=0):
    # Print tag and text (if any)
    text = element.text.strip() if element.text else ""
    if text:
        print("  " * indent + f"{element.tag}: {text}")
    # Print attributes (if any)
    if element.attrib:
        print("  " * indent + f"{element.tag} attributes: {element.attrib}")
    # Recurse for children
    for child in element:
        print_element_info(child, indent + 1)

def element_to_dict(element):
    # Convert an Element and its children to a dictionary
    node = {}
    # Add attributes if present
    if element.attrib:
        node.update({f"@{k}": v for k, v in element.attrib.items()})
    # Add text if present
    text = (element.text or '').strip()
    if text:
        node["#text"] = text
    # Add children
    for child in element:
        child_dict = element_to_dict(child)
        if child.tag not in node:
            node[child.tag] = child_dict
        else:
            # If tag already exists, convert to list
            if not isinstance(node[child.tag], list):
                node[child.tag] = [node[child.tag]]
            node[child.tag].append(child_dict)
    return node

# Add this dictionary for translations
keyword_translations = {
    "台風解析・予報情報（５日予報）": "Typhoon analysis and forecast information (5-day forecast)",
    "台風の暴風域に入る確率": "Probability of entering the typhoon's storm zone"
}

def fetch_and_print_xml_details(link, keyword):
    try:
        resp = requests.get(link)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        # Convert XML to dict, then to JSON
        xml_dict = {root.tag: element_to_dict(root)}
        json_str = json.dumps(xml_dict, ensure_ascii=False, indent=2)
        # Use translation if available, else fallback to original keyword
        safe_keyword = keyword_translations.get(keyword, keyword)
        safe_keyword = safe_keyword.replace('/', '_').replace('（', '(').replace('）', ')')
        filename = f"{safe_keyword}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_str)
    except Exception as e:
        pass  # Optionally, you can log errors to a file if needed

if __name__ == "__main__":
    latest = extract_latest_typhoon_entries()
    if latest:
        for kw, entry in latest.items():
            fetch_and_print_xml_details(entry['link'], kw)