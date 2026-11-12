import sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import fitz
from PIL import Image, ImageDraw
ROOT = r"C:\Users\cho\land\창원_대동백화점"
EV = os.path.join(ROOT, "증빙", "ev"); OUT = os.path.join(EV, "crops2"); os.makedirs(OUT, exist_ok=True)
SRC = r"C:\Users\cho\Documents\카카오톡 받은 파일"
RUST = (184, 58, 34)

def render(pdf, page, dpi):
    d = fitz.open(pdf); pm = d[page-1].get_pixmap(dpi=dpi)
    return Image.frombytes("RGB", (pm.width, pm.height), pm.samples)

def make(img, base, crop, boxes, name, target_w=2000, lw=4):
    """boxes/crop in base-pixel coords; output scaled so width = target_w; box line lw px at output scale"""
    x0, y0, x1, y1 = crop
    c = img.crop((x0, y0, x1, y1))
    s = target_w / c.width
    c = c.resize((target_w, int(c.height * s)), Image.LANCZOS)
    d = ImageDraw.Draw(c)
    for (a, b, e, f) in boxes:
        d.rectangle([(a-x0)*s, (b-y0)*s, (e-x0)*s, (f-y0)*s], outline=RUST, width=lw)
    c.save(os.path.join(OUT, name)); print(name, c.size)

split = os.path.join(SRC, "대동백화점 지번분할 검토자료.pdf")
intro = os.path.join(SRC, "대동백화점회사소개서.pdf")
rev = os.path.join(EV, "review.pdf")
p1 = render(split, 1, 110); p2 = render(split, 2, 110); p3 = render(split, 3, 110)

# 허가 동의율 (창원시 회신)
make(p1, 110, (150, 600, 780, 800), [(160, 652, 772, 738)], "city_consent.png")
# 의견요지 결론 (분리될 가능성이 높다)
make(p2, 110, (150, 210, 780, 300), [(452, 241, 774, 266), (166, 268, 306, 296)], "opinion_summary.png")
# 분필: 동의 못 얻으면 공유물분할소송 (의견서 라 항)
make(p2, 110, (150, 893, 780, 1003), [(164, 922, 774, 999)], "split_consent.png")
# 선례: 출입구 분리
make(p3, 110, (150, 318, 765, 466), [(284, 436, 400, 461)], "precedent_cell.png")
# 조건 4개 (두 쪽 이어 붙임, 박스 없음)
a = p2.crop((150, 1086, 780, 1138)); b = p3.crop((150, 146, 780, 194))
st = Image.new("RGB", (630, a.height + b.height), "white"); st.paste(a, (0, 0)); st.paste(b, (0, a.height))
st = st.resize((2000, int(st.height * 2000 / 630)), Image.LANCZOS); st.save(os.path.join(OUT, "conditions.png")); print("conditions", st.size)

# 소개서 12쪽: 부지 13,132㎡
i12 = render(intro, 12, 200)
s = 200/90
make(i12, 200, (int(410*s), int(225*s), int(955*s), int(605*s)), [(int(488*s), int(365*s), int(652*s), int(438*s))], "bldg_status.png", target_w=1400, lw=5)
# 소개서 19쪽: 위반건축물
i19 = render(intro, 19, 90*3)
s = 3
make(i19, 270, (int(420*s), int(455*s), int(842*s), int(592*s)), [(int(539*s), int(514*s), int(812*s), int(576*s))], "violation.png", target_w=1800)

# 대장 표제부 (이미 렌더된 bld_head.png, 원본 좌표)
bh = Image.open(os.path.join(ROOT, "증빙", "src", "bld_head.png")).convert("RGB")
make(bh, 1, (200, 232, 1135, 442), [(220, 244, 668, 298), (676, 368, 1119, 432)], "bld_far.png", target_w=1800, lw=5)

# 검토문서(review.pdf) 텍스트 검색으로 정확한 박스
d = fitz.open(rev)
def textbox(page, needles, pad=3):
    pg = d[page-1]; rs = []
    for n in needles:
        r = pg.search_for(n); rs += r
    return rs
DPI = 200; S = DPI/72
def rimg(page):
    pm = d[page-1].get_pixmap(dpi=DPI); return Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
# trust: 채무 구조 문단
pg3 = d[2]
r1 = pg3.search_for("실제 채무는"); r2 = pg3.search_for("444")
print("trust", r1, r2)
if r1 and r2:
    top = r1[0].y0; bot = max(r.y1 for r in r2)
    im = rimg(3)
    box = (r1[0].x0*S-10, top*S-8, 540*S, bot*S+8)
    hdr = pg3.search_for("채무 구조")
    y0 = (hdr[0].y0 - 6)*S if hdr else top*S-80
    crop = (int(60*S), int(y0), int(560*S), int(bot*S+30))
    # tight box on paragraph
    make(im, 1, crop, [box], "trust.png", target_w=1800, lw=4)
# profit table
pg8 = d[7]
ra = pg8.search_for("제안서 그대로"); rb = pg8.search_for("보수적 종합 (분양가")
print("profit", ra, rb)
im8 = rimg(8)
X0, X1 = 67*S, 535*S
boxes = []
if ra: boxes.append((X0, ra[0].y0*S-6, X1, ra[0].y1*S+8))
# 보수적 종합 row spans 2 lines
rc = pg8.search_for("2,500 만, 공사비 750")
if rb:
    y1 = (rc[0].y1 if rc else rb[0].y1+14)
    boxes.append((X0, rb[0].y0*S-6, X1, y1*S+8))
print(boxes)
# crop whole table region from header to the row after
hdr = pg8.search_for("시나리오")
last = pg8.search_for("공공기여 150")
yy0 = (hdr[0].y0 - 10)*S if hdr else 80*S
yy1 = (last[0].y1 + 10)*S if last else 380*S
make(im8, 1, (int(60*S), int(yy0), int(550*S), int(yy1)), boxes, "profit_table.png", target_w=1800, lw=4)
