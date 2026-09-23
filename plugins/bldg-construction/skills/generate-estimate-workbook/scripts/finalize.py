"""Recalculate through LibreOffice (caches formula results), then repair two things it breaks:
1. outlinePr summaryRight=0 (collapse button side for the sub-bid group)
2. merged ranges: LibreOffice writes the range perimeter onto EVERY cell inside the merge, so
   Excel draws lines through merged text. Every cell keeps only the edges on the perimeter.

    python finalize.py raw.xlsx out.xlsx
"""
import re, subprocess, sys, tempfile, zipfile, os
from openpyxl.utils import range_boundaries, get_column_letter

src, dst = sys.argv[1], sys.argv[2]

def outline(xml):
    if 'outlineLevel' not in xml or 'outlinePr' in xml: return xml
    if re.search(r"<sheetPr[^>]*/>", xml):
        return re.sub(r"<sheetPr([^>]*)/>", r'<sheetPr\1><outlinePr summaryBelow="1" summaryRight="0"/></sheetPr>', xml, count=1)
    if "<sheetPr" in xml:
        return re.sub(r"(<sheetPr[^>]*>)", r'\1<outlinePr summaryBelow="1" summaryRight="0"/>', xml, count=1)
    return xml

with tempfile.TemporaryDirectory() as td:
    subprocess.run(["soffice", "--headless", "--convert-to", "xlsx:Calc MS Excel 2007 XML", src, "--outdir", td], check=True, capture_output=True)
    zin = zipfile.ZipFile(os.path.join(td, os.path.basename(src)))
    files = {i.filename: zin.read(i.filename) for i in zin.infolist()}
    infos = zin.infolist()

st = files["xl/styles.xml"].decode()
bpre, brest = st.split("<borders", 1); bhead, bbody = brest.split(">", 1); bbody, bpost = bbody.split("</borders>", 1)
borders = re.findall(r"<border[ >].*?</border>|<border/>", bbody, re.S)
xpre, xrest = bpost.split("<cellXfs", 1); xhead, xbody = xrest.split(">", 1); xbody, xpost = xbody.split("</cellXfs>", 1)
xfs = re.findall(r"<xf [^>]*?/>|<xf [^>]*?>.*?</xf>", xbody, re.S)
bmemo, xmemo = {}, {}

def strip(bxml, keep):
    for side in ("left", "right", "top", "bottom"):
        if not keep[side]:
            bxml = re.sub(r"<%s(?: [^>]*)?(?:/>|>.*?</%s>)" % (side, side), "<%s/>" % side, bxml, count=1, flags=re.S)
    return bxml

def new_style(s, keep):
    k = (s, tuple(sorted(keep.items())))
    if k in xmemo: return xmemo[k]
    xf = xfs[s]; bid = int(re.search(r'borderId="(\d+)"', xf).group(1))
    nb = strip(borders[bid], keep)
    if nb not in bmemo:
        borders.append(nb); bmemo[nb] = len(borders) - 1
    nxf = re.sub(r'borderId="\d+"', 'borderId="%d"' % bmemo[nb], xf)
    if 'applyBorder' not in nxf: nxf = nxf.replace("<xf ", '<xf applyBorder="true" ', 1)
    xfs.append(nxf); xmemo[k] = len(xfs) - 1
    return xmemo[k]

fixed = 0
for name in list(files):
    if not name.startswith("xl/worksheets/sheet"): continue
    xml = outline(files[name].decode())
    for ref in re.findall(r'<mergeCell ref="([A-Z]+\d+:[A-Z]+\d+)"', xml):
        c1, r1, c2, r2 = range_boundaries(ref)
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                a = "%s%d" % (get_column_letter(c), r)
                m = re.search(r'<c r="%s"([^>]*?) s="(\d+)"' % a, xml)
                if not m: continue
                keep = {"left": c == c1, "right": c == c2, "top": r == r1, "bottom": r == r2}
                ns = new_style(int(m.group(2)), keep)
                xml = xml[:m.start()] + '<c r="%s"%s s="%d"' % (a, m.group(1), ns) + xml[m.end():]
                fixed += 1
    files[name] = xml.encode()

bhead = re.sub(r'count="\d+"', 'count="%d"' % len(borders), bhead)
xhead = re.sub(r'count="\d+"', 'count="%d"' % len(xfs), xhead)
files["xl/styles.xml"] = (bpre + "<borders" + bhead + ">" + "".join(borders) + "</borders>" + xpre +
                          "<cellXfs" + xhead + ">" + "".join(xfs) + "</cellXfs>" + xpost).encode()
with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
    for it in infos: z.writestr(it, files[it.filename])
print("finalized", dst, "| merged cells repaired:", fixed)
