from zipfile import ZipFile
from xml.etree import ElementTree as ET
path = r"E:\学习\AI Job Hunt Assistant\简历模板.docx"
with ZipFile(path) as z:
    xml = z.read("word/document.xml")
root = ET.fromstring(xml)
ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
texts = []
for node in root.iterfind('.//w:t', ns):
    if node.text and node.text.strip():
        texts.append(node.text.strip())
for i, text in enumerate(texts[:220], 1):
    print(f"{i:03d}: {text}")
