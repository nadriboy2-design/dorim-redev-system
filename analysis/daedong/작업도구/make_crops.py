import sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import fitz
from PIL import Image, ImageDraw

EV = r"C:\Users\cho\land\창원_대동백화점\증빙\ev"
OUT = os.path.join(EV, "crops")
os.makedirs(OUT, exist_ok=True)
SRC = r"C:\Users\cho\Documents\카카오톡 받은 파일"
RUST = (184, 58, 34)


def render(pdf, page, dpi):
    d = fitz.open(pdf)
    pm = d[page - 1].get_pixmap(dpi=dpi)
    img = Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
    return img


def crop(img, base_dpi, dpi, box, hls, name, width=6):
    s = dpi / base_dpi
    b = [int(v * s) for v in box]
    im = img.copy()
    dr = ImageDraw.Draw(im)
    for h in hls:
        hb = [int(v * s) for v in h]
        dr.rectangle(hb, outline=RUST, width=width)
    out = im.crop(b)
    p = os.path.join(OUT, name)
    out.save(p)
    print(name, out.size)


split = os.path.join(SRC, "대동백화점 지번분할 검토자료.pdf")
intro = os.path.join(SRC, "대동백화점회사소개서.pdf")
rev = os.path.join(EV, "review.pdf")
D = 170

# --- split pdf pages at base 110 dpi coords ---
p1 = render(split, 1, D)
crop(p1, 110, D, (135, 585, 775, 745), [(140, 660, 772, 728)], "city_consent.png")
p2 = render(split, 2, D)
crop(p2, 110, D, (135, 180, 775, 293), [(138, 238, 772, 291)], "opinion_summary.png")
cond_a = p2.crop((int(135 * D / 110), int(1082 * D / 110), int(775 * D / 110), int(1140 * D / 110)))
p3 = render(split, 3, D)
cond_b = p3.crop((int(135 * D / 110), int(145 * D / 110), int(775 * D / 110), int(195 * D / 110)))
w = max(cond_a.width, cond_b.width)
st = Image.new("RGB", (w, cond_a.height + cond_b.height), (255, 255, 255))
st.paste(cond_a, (0, 0)); st.paste(cond_b, (0, cond_a.height))
st.save(os.path.join(OUT, "conditions.png")); print("conditions.png", st.size)
crop(p3, 110, D, (150, 318, 765, 428), [(277, 348, 411, 418)], "precedent.png")

# --- intro pdf (base 90 dpi coords) ---
D2 = 200
i12 = render(intro, 12, D2)
crop(i12, 90, D2, (410, 225, 955, 605), [(488, 365, 652, 438)], "bldg_status.png")
i18 = render(intro, 18, 250)
i18.save(os.path.join(OUT, "_i18_full.png"))
i19 = render(intro, 19, D2)
crop(i19, 90, D2, (120, 440, 1000, 580), [(535, 522, 1000, 572)], "violation.png")

# --- review docx pages (base 90 dpi) ---
D3 = 160
r3 = render(rev, 3, D3)
crop(r3, 90, D3, (80, 400, 692, 500), [(82, 440, 690, 484)], "trust.png")
r8 = render(rev, 8, D3)
crop(r8, 90, D3, (80, 85, 672, 375), [(82, 130, 670, 162), (82, 270, 670, 335)], "profit_table.png")

# --- ordinance page 24 via text search ---
ord_pdf = r"C:\Users\cho\Downloads\창원시 도시계획 조례(경상남도 창원시조례)(제2260호)(20251114).pdf"
d = fitz.open(ord_pdf)
pg = d[23]
S = 200 / 72
pm = pg.get_pixmap(dpi=200)
im = Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
dr = ImageDraw.Draw(im)
r60 = pg.search_for("제60조(용도지역에서의 용적률)")
r60b = pg.search_for("별표 28과 같다")
r6 = pg.search_for("정비구역 또는 상업지역")
r6b = pg.search_for("⑥")
print("search", r60, r60b, r6, r6b)
for rs in (r60, r60b, r6):
    for r in rs:
        dr.rectangle([r.x0 * S - 4, r.y0 * S - 4, r.x1 * S + 4, r.y1 * S + 4], outline=RUST, width=6)
if r60:
    y0 = r60[0].y0 - 14
else:
    y0 = 240
last = r6[-1].y1 + 30 if r6 else 760
ordc = im.crop((int(40 * S), int(y0 * S), int(560 * S), int(last * S)))
ordc.save(os.path.join(OUT, "ordinance.png")); print("ordinance.png", ordc.size)

# --- field report photo from pptx ---
from pptx import Presentation
pr = Presentation(os.path.join(SRC, "대동백화점_개발검토_보고.pptx"))
sl = pr.slides[1]
for sh in sl.shapes:
    if sh.shape_type == 13:
        blob = sh.image.blob
        ext = sh.image.ext
        fp = os.path.join(OUT, "site_photo." + ext)
        open(fp, "wb").write(blob)
        print("photo", fp, Image.open(fp).size)

# field slides 6,7
for n, name, box, hl in [
    (7, "field_access.png", (80, 620, 1520, 795), []),
    (6, "field_price.png", (0, 0, 1600, 900), []),
]:
    im2 = Image.open(os.path.join(EV, "field", f"슬라이드{n}.PNG")).convert("RGB")
    im2.crop(box).save(os.path.join(OUT, name)); print(name)

oc = Image.open(os.path.join(OUT, "ordinance.png"))
A = oc.crop((0, 8, oc.width, 100)); B = oc.crop((0, 1325, oc.width, oc.height))
st = Image.new("RGB", (oc.width, A.height + B.height + 24), (255, 255, 255))
st.paste(A, (0, 0)); st.paste(B, (0, A.height + 24))
st.save(os.path.join(OUT, "ordinance_short.png")); print("ordinance_short", st.size)

crop(p3, 110, D, (270, 340, 418, 450), [(277, 348, 411, 440)], "precedent_cell.png", width=5)
i19b = render(intro, 19, 200)
crop(i19b, 90, 200, (520, 500, 1010, 582), [(535, 522, 1000, 574)], "violation2.png")
