from zipfile import ZipFile
from xml.etree import ElementTree as ET
path = r"E:\学习\AI Job Hunt Assistant\简历模板.docx"
with ZipFile(path) as z:
    xml = z.read("word/document.xml")
root = ET.fromstring(xml)
ns = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
}
for i, tx in enumerate(root.findall('.//wps:txbxContent', ns), 1):
    texts = []
    for t in tx.iterfind('.//w:t', ns):
        if t.text and t.text.strip():
            texts.append(t.text.strip())
    if texts:
        print(f'BLOCK {i}')
        for item in texts[:12]:
            print(item)
        print('---')
