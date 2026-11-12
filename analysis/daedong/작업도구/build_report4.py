import sys, os, math
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree
from PIL import Image

ROOT = os.environ.get("DAEDONG_ROOT", r"C:\Users\cho\land\창원_대동백화점")  # 다른 PC에서는 환경변수 DAEDONG_ROOT 에 프로젝트 폴더 경로 지정
CR = os.path.join(ROOT, "증빙", "ev", "crops")
CR2 = os.path.join(ROOT, "증빙", "ev", "crops2")
MODE = sys.argv[1] if len(sys.argv) > 1 else "report"
FULL = (MODE == "full")
OUT = os.path.join(ROOT, "대동백화점_부지분할_검토보고_통합보고서_2026-11-12.pptx" if FULL
                   else "대동백화점_부지분할_검토보고_보고용_큰글씨_2026-11-12.pptx")
SEC = []
LAW = os.path.join(ROOT, "증빙", "법령")

BODY = "맑은 고딕"
HEAD = "바탕"
NUMF = "Cambria"

def C(h): return RGBColor.from_string(h)
CHAR, GOLD, BURG, PINK = C("3A3A3C"), C("C9A55C"), C("7A2338"), C("F8EFF1")
INK, MUTE, LABEL_BG, WHITE = C("262626"), C("857F76"), C("F5F3EF"), C("FFFFFF")
SUB = C("333333"); RED = C("C00000"); LIGHT = C("CFC9C0")
LINE = "DAD4CB"

# ---- 글자 크기 (세로 양식 대비 약 1.8배, 가로 화면용) ----
S_TITLE, S_SUB, S_BODY, S_BIG, S_CAP, S_SRC, S_FOOT = 30, 21, 20, 30, 15, 12, 12
X0, W0 = 0.5, 12.333
warnings = []

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
FOOT_NOTE = "'추정' 표시 수치는 가정 기반이며 확인이 필요합니다."


def cr(n): return os.path.join(CR, n)
def cr2(n): return os.path.join(CR2, n)


def est_lines(text, size, width_in):
    wpt = width_in * 72.0
    total = 0
    for para in text.split("\n"):
        w = sum(size * (1.0 if ord(ch) > 0x2E80 else 0.56) for ch in para)
        total += max(1, math.ceil(w / wpt)) if para else 1
    return total


def tb(slide, x, y, w, h, text, size=S_BODY, bold=False, color=INK, align=PP_ALIGN.LEFT,
       anchor=MSO_ANCHOR.TOP, font=BODY, name=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name: box.name = name
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = anchor
    paras = text if isinstance(text, list) else [text]
    need = 0
    for i, p in enumerate(paras):
        ptxt, popt = (p if isinstance(p, tuple) else (p, {}))
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = popt.get("align", align)
        runs = ptxt if isinstance(ptxt, list) else [(ptxt, {})]
        txt_all = ""
        for rt, ro in runs:
            r = para.add_run(); r.text = rt; txt_all += rt
            r.font.name = ro.get("font", popt.get("font", font))
            r.font.size = Pt(ro.get("size", popt.get("size", size)))
            r.font.bold = ro.get("bold", popt.get("bold", bold))
            r.font.color.rgb = ro.get("color", popt.get("color", color))
        if popt.get("space"): para.space_after = Pt(popt["space"])
        need += est_lines(txt_all, popt.get("size", size), w - 0.1) * popt.get("size", size) * 1.3 / 72
    if need > h + 0.08:
        warnings.append(f"OVERFLOW? '{str(paras[0])[:30]}' need {need:.2f} > {h:.2f}")
    return box


def rect(slide, x, y, w, h, fill, name=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid(); shp.fill.fore_color.rgb = fill
    shp.line.fill.background(); shp.shadow.inherit = False
    if name: shp.name = name
    return shp


def _border(cell, color=LINE, w=9525):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        for old in tcPr.findall(qn(tag)): tcPr.remove(old)
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        ln = etree.SubElement(tcPr, qn(tag), w=str(w), cap="flat", cmpd="sng", algn="ctr")
        sf = etree.SubElement(ln, qn("a:solidFill"))
        etree.SubElement(sf, qn("a:srgbClr"), val=color)
        etree.SubElement(ln, qn("a:prstDash"), val="solid")
    for tag in ("a:solidFill", "a:noFill"):
        for el in tcPr.findall(qn(tag)):
            tcPr.remove(el); tcPr.append(el)


def table(slide, x, y, col_w, rows, row_h=0.6, size=S_BODY, header=False, label_cols=(0,), name=None):
    nr, nc = len(rows), len(col_w)
    gf = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(sum(col_w)), Inches(row_h * nr))
    if name: gf.name = name
    tbl = gf.table
    tblPr = tbl._tbl.tblPr
    for a in ("firstRow", "bandRow", "firstCol", "lastRow", "lastCol", "bandCol"): tblPr.set(a, "0")
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is not None: sid.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"
    for j, w in enumerate(col_w): tbl.columns[j].width = Inches(w)
    for i in range(nr):
        tbl.rows[i].height = Inches(row_h)
        for j in range(nc):
            cell = tbl.cell(i, j)
            v = rows[i][j]
            txt, o = (v if isinstance(v, tuple) else (v, {}))
            is_head = header and i == 0
            is_label = (j in label_cols) and not is_head
            cell.fill.solid()
            cell.fill.fore_color.rgb = o.get("fill", CHAR if is_head else (LABEL_BG if is_label else WHITE))
            cell.margin_left = cell.margin_right = Inches(0.14)
            cell.margin_top = cell.margin_bottom = Inches(0.04)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame; tf.word_wrap = True
            lines = txt.split("\n")
            for k, ln in enumerate(lines):
                p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
                p.alignment = o.get("align", PP_ALIGN.CENTER if (is_head or is_label) else PP_ALIGN.LEFT)
                r = p.add_run(); r.text = ln
                r.font.name = o.get("font", BODY)
                r.font.size = Pt(o.get("size", size))
                r.font.bold = o.get("bold", True if (is_head or is_label) else False)
                r.font.color.rgb = o.get("color", WHITE if is_head else INK)
            _border(cell)
            wcol = col_w[j] - 0.28
            n = sum(est_lines(ln, o.get("size", size), wcol) for ln in lines)
            if n * o.get("size", size) * 1.3 / 72 + 0.08 > row_h + 0.02:
                warnings.append(f"TABLE ROW GROW? r{i}c{j} '{txt[:20]}' lines={n}")
    return y + row_h * nr


def picture(slide, path, x, y, w, h=None, name=None):
    im = Image.open(path)
    iw, ih = im.size
    sc = w / iw
    if h is not None and ih * sc > h: sc = h / ih
    pw, ph = iw * sc, ih * sc
    pic = slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(pw), Inches(ph))
    if name: pic.name = name
    pic.line.color.rgb = C(LINE)
    pic.line.width = Pt(1)
    return x, y, pw, ph


def cap(slide, x, y, w, text, align=PP_ALIGN.LEFT):
    tb(slide, x, y, w, 0.32, text, size=S_CAP, color=MUTE, align=align)


def ev(slide, path, y, w, h, caption, x=X0):
    px, py, pw, ph = picture(slide, path, x, y, w, h)
    cap(slide, x, py + ph + 0.04, max(pw, 6.0), caption)
    return py + ph + 0.04 + 0.32 + 0.1


def subhead(slide, y, text, x=X0, w=None):
    rect(slide, x + 0.02, y + 0.15, 0.13, 0.13, BURG)
    tb(slide, x + 0.22, y, (w or W0) - 0.22, 0.42, text, size=S_SUB, bold=True, color=SUB, anchor=MSO_ANCHOR.MIDDLE)


def pingga(slide, y, lines, h=0.85, label="평 가"):
    """템플릿의 '평가' 박스: 자주색 라벨 + 연분홍 본문 + 금색 세로선."""
    rect(slide, X0, y, 1.3, h, BURG)
    tb(slide, X0, y, 1.3, h, label, size=22, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
       anchor=MSO_ANCHOR.MIDDLE, font=HEAD)
    rect(slide, X0 + 1.3, y, W0 - 1.3, h, PINK)
    rect(slide, X0 + 1.3, y, 0.04, h, GOLD)
    paras = [(l, {}) for l in lines] if isinstance(lines, list) else [(lines, {})]
    tb(slide, X0 + 1.5, y, W0 - 1.7, h, paras, size=S_BODY, color=INK, anchor=MSO_ANCHOR.MIDDLE)


def frame(slide, tag, title, lead, source):
    """상단 띠(헤더) + 하단 띠(푸터) + 섹션 제목줄 + 소제목."""
    n = len(prs.slides._sldIdLst)
    SEC.append((n, tag, title))
    rect(slide, 0, 0, 13.333, 0.8, CHAR, name="HeaderBand")
    rect(slide, 0, 0.8, 13.333, 0.04, GOLD)
    tb(slide, 6.0, 0.1, 6.55, 0.3, "상남동 44-1 · 대동백화점 부지 분할 검토", size=14, color=C("D9D4CC"), align=PP_ALIGN.RIGHT)
    tb(slide, 6.0, 0.37, 6.55, 0.4, "분할개발 제안 팩트체크 보고서", size=22, bold=True, color=WHITE, align=PP_ALIGN.RIGHT, font=HEAD)
    rect(slide, 12.7, 0.14, 0.03, 0.55, GOLD)
    # 푸터
    rect(slide, 0, 7.12, 13.333, 0.38, CHAR, name="FooterBand")
    rect(slide, 0, 7.12, 13.333, 0.02, GOLD)
    tb(slide, 0.4, 7.17, 10.5, 0.3, FOOT_NOTE, size=S_FOOT, color=LIGHT, anchor=MSO_ANCHOR.MIDDLE)
    tb(slide, 11.6, 7.15, 1.2, 0.33, str(n), size=16, bold=True, color=WHITE, align=PP_ALIGN.RIGHT, font=NUMF)
    # 섹션 제목줄
    bw = 1.25 if len(tag) > 2 else 0.8
    rect(slide, X0, 0.97, bw, 0.55, BURG)
    tb(slide, X0, 0.97, bw, 0.55, tag, size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
       anchor=MSO_ANCHOR.MIDDLE, font=HEAD if len(tag) > 2 else NUMF)
    tb(slide, X0 + bw + 0.2, 0.93, W0 - bw - 0.2, 0.62, title, size=S_TITLE, bold=True, color=INK,
       anchor=MSO_ANCHOR.MIDDLE, font=HEAD, name="Title")
    rect(slide, X0, 1.62, W0, 0.015, C(LINE))
    rect(slide, X0, 1.605, 1.3, 0.045, BURG)
    if lead:
        subhead(slide, 1.72, lead)
    if source:
        tb(slide, X0, 6.78, W0, 0.3, source, size=S_SRC, color=MUTE, name="Source")


def new(): return prs.slides.add_slide(BLANK)

R_ = {"color": RED, "bold": True}
CT = {"align": PP_ALIGN.CENTER}

# ===================== 1 표지 =====================
s = new()
rect(s, 0, 0, 13.333, 0.4, CHAR); rect(s, 0, 0.4, 13.333, 0.03, GOLD)
rect(s, 0, 7.1, 13.333, 0.4, CHAR); rect(s, 0, 7.07, 13.333, 0.03, GOLD)
tb(s, 0.9, 2.1, 7.2, 0.45, "경남 창원시 성산구 상남동 44-1  ·  분할개발 제안 검토", size=20, color=MUTE)
tb(s, 0.9, 2.65, 7.2, 1.9, "대동백화점 부지\n분할개발 제안 검토", size=46, bold=True, color=INK, font=HEAD, name="Title")
rect(s, 0.95, 4.75, 6.9, 0.025, C(LINE)); rect(s, 0.95, 4.735, 1.6, 0.05, BURG)
tb(s, 0.9, 4.98, 7.2, 0.4, "제안 확인  →  위험  →  증빙  →  서면 확인  →  회신", size=20, color=C("5F5A52"))
tb(s, 0.9, 5.55, 7.2, 0.45, "2026. 11. 12", size=24, bold=True, color=INK, font=NUMF)
tb(s, 0.9, 6.1, 7.2, 0.4, "대원홀딩스", size=22, bold=True, color=INK, font=HEAD)
tb(s, 0.9, 6.55, 7.4, 0.35, "투자 검토용 참고 자료 (감정평가서·법률·세무 의견 아님)", size=14, color=MUTE)
ph = Image.open(cr("site_photo.jpg"))
bx, by, bw_, bh_ = 8.55, 1.35, 4.2, 5.4
rect(s, bx - 0.08, by - 0.08, bw_ + 0.16, bh_ + 0.16, WHITE)
pic = s.shapes.add_picture(cr("site_photo.jpg"), Inches(bx), Inches(by), Inches(bw_), Inches(bh_))
ri, rb = ph.width / ph.height, bw_ / bh_
if ri > rb:
    keep = rb / ri; pic.crop_left = pic.crop_right = (1 - keep) / 2
else:
    keep = ri / rb; pic.crop_top = pic.crop_bottom = (1 - keep) / 2
pic.line.color.rgb = C(LINE); pic.line.width = Pt(1)
pic.name = "SitePhoto"

if FULL:
    s_toc = new()
    frame(s_toc, "목차", "목차", None, None)

# ===================== 2 검토 결론 =====================
s = new()
frame(s, "결론", "검토 결론", None, None)
cards = [("9가지", "확인된 위험", "서면 확인 전 참여 어려움"),
         ("250%", "조례 용적률 한도", "제안서는 349.67%"),
         ("–219억", "보수적 종합 수지", "제안서는 +587억 (낙관)"),
         ("444억", "신탁 우선수익권", "이자 21.4억 > 영업이익 5.1억")]
cw, gap = 2.95, 0.177
for i, (big, mid, small) in enumerate(cards):
    x = X0 + i * (cw + gap)
    rect(s, x, 1.85, cw, 1.75, CHAR); rect(s, x, 1.85, cw, 0.05, GOLD)
    tb(s, x, 1.98, cw, 0.7, big, size=36, bold=True, color=GOLD, align=PP_ALIGN.CENTER, font=HEAD, anchor=MSO_ANCHOR.MIDDLE)
    tb(s, x, 2.72, cw, 0.4, mid, size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tb(s, x, 3.12, cw, 0.4, small, size=14, color=C("BDB7AE"), align=PP_ALIGN.CENTER)
subhead(s, 3.8, "결론")
table(s, X0, 4.3, [1.5, 10.833], [
    ["결 론", ("선결조건이 서면으로 확인되기 전에는 참여가 어렵습니다.", R_)],
    ["근 거", "분할 불확정 · 진입로 겸용 · 용적률 초과 · 신탁 담보 · 조합 지연 · 시장가 적자"],
    ["요 청", "신탁원부, 분할선 도면, 용적률 계산서, 조합 동의율, 공사비·분양가 근거"],
], row_h=0.72, size=S_BODY)

# ===================== 3 위험 요약 =====================
s = new()
frame(s, "요약", "확인된 위험 9가지", None, None)
rows9 = [
    ["1", "분할은 확정이 아닙니다", "법률의견서도 \"가능성이 높다\"까지만"],
    ["2", "아파트 진입로를 같이 씁니다", "선례 상가는 출입구가 분리돼 있었음"],
    ["3", "분할하면 용적률이 넘을 수 있습니다", "대장 268.75% → 분할 후 약 294% (추정)"],
    ["4", "용적률 350%는 조례 한도 초과", "3종일반 조례 한도 250%"],
    ["5", "담보가 신탁으로 잡혀 있습니다", "우선수익권 444억 원"],
    ["6", "리모델링 조합 사업이 지연 중", "시공자 미선정, 동의율 확인 불가"],
    ["7", "시장가로 계산하면 적자입니다", "보수적 종합 –219억 원"],
    ["8", "인근 분양가가 더 낮습니다", "평당 2,300~2,700만 원"],
    ["9", "서류 속 숫자가 서로 다릅니다", "대지면적 4가지 · 위반건축물 기재"],
]
rows9 = [[(r[0], {"align": PP_ALIGN.CENTER, "font": NUMF, "size": 22}), (r[1], {"bold": True}), r[2]] for r in rows9]
table(s, X0, 1.85, [0.8, 5.5, 6.033], rows9, row_h=0.54, size=19, label_cols=(0,))

# ===================== 4 위험1 분할 확정 아님 =====================
s = new()
frame(s, "위험 1", "분할은 확정이 아닙니다", "법률의견서도 \"가능성이 높다\"까지만 말합니다",
      "출처: 법률사무소 율해 의견서 (2026-10-30) 1. 의견요지")
ny = ev(s, cr2("opinion_summary.png"), 2.2, W0, 1.9, "↑ 붉은 박스: \"분리될 가능성이 높다고 판단\"")
ny = table(s, X0, ny + 0.1, [3.0, 9.333], [
    ["의견서의 표현", "\"분리될 가능성이 높다\" (판단)"],
    ["확정 여부", ("확정이 아님 — 소송 결과에 따라 달라짐", R_)],
], row_h=0.6)
pingga(s, ny + 0.2, "의뢰인 문서도 조건부로만 말합니다.", h=0.7)

# ===================== 5 위험1 조건 =====================
s = new()
frame(s, "위험 1", "분할 조건 4개, 확인된 것은 0개", "의견서가 스스로 내건 조건입니다",
      "출처: 율해 의견서 \"인용의 조건\" · 현장보고 · 건축물대장 · 내부 검토 문서")
ny = ev(s, cr2("conditions.png"), 2.2, W0, 1.7, "↑ 의견서 1. 의견요지 바. (2쪽~3쪽 이어 붙임)")
table(s, X0, ny + 0.05, [6.4, 5.933], [
    ["① 출입·주차·소방에 필요하지 않을 것", ("진입로 겸용 — 충돌 소지", R_)],
    ["② 분할 후 건축법 57조 충족", ("용적률 초과 가능", R_)],
    ["③ 측량·감정으로 분할 부분 특정", "미확인"],
    ["④ 대지사용권·대지권 등기 정리 방안", "미확인"],
], row_h=0.52, size=19, label_cols=(0,))

# ===================== 6 위험1 분필 =====================
s = new()
frame(s, "위험 1", "분필은 조합 허가로 안 됩니다", "공유자 전원의 합의 또는 확정판결이 필요합니다",
      "출처: 율해 의견서 라. 리모델링과의 관계 · 민법 268·269조 · 집합건물법 8조")
ny = ev(s, cr2("split_consent.png"), 2.2, W0, 1.9, "↑ 붉은 박스: 동의를 못 얻으면 조합도 공유물분할소송으로 분리할 수밖에 없다")
table(s, X0, ny + 0.05, [3.4, 8.933], [
    ["① 소유권", "공유자 전원 합의 또는 판결"],
    ["② 신탁", "우선수익자(새마을금고) 동의 여부 확인 필요"],
    ["③ 분필 신청", "건축법 57조 심사 통과 (확정판결도 심사)"],
], row_h=0.62)

# ===================== 7 위험2 진입로 =====================
s = new()
frame(s, "위험 2", "아파트 진입로를 같이 씁니다", "선례의 상가는 출입구가 분리돼 있었습니다",
      "출처: 율해 의견서 선례표 (서울남부지법 2008가합24143) · 회사 현장보고 7쪽 (2026-11-09)")
ny = ev(s, cr2("precedent_cell.png"), 2.2, 7.2, 1.75, "↑ 선례표 \"사안\" 칸 (붉은 박스: 출입구도 분리됨)")
table(s, 8.2, 2.3, [1.5, 3.133], [
    ["선례", ("출입구 분리", {"bold": True})],
    ["이 건", ("진입로 겸용", R_)],
], row_h=0.75)
ev(s, cr("field_access.png"), ny + 0.1, W0, 1.7, "↑ 현장보고 7쪽: 백화점·메디컬센터를 지나 아파트로 들어가는 도로")

# ===================== 7-2 위험2 법적 부담 =====================
s = new()
frame(s, "위험 2", "진입로는 법정 기준과 통행권이 걸려 있습니다", "분할선을 어디에 긋느냐보다 진입로의 소유·관리가 먼저입니다",
      "출처: 주택건설기준규정 제25조(2017.7.1 시행본) · 건축법 제44조 · 민법 제220조 · 대법원 96다33433")
ny = table(s, X0, 2.2, [1.9, 6.0, 4.433], [
    ["진입도로 폭", "주택건설기준규정 제25조: 2천세대 이상은 폭 20m 이상 (신축 단지 기준, 현행 대조 필요)", "2,810세대 · 계획 3,230세대"],
    ["접도 의무", "건축법 제44조·시행령 제28조 ②: 연면적 2천㎡ 이상 건축물 대지는 6m 도로에 4m 이상 접해야 함", "백화점 연면적 34,608㎡ — 분할 후 각 필지 접도 확인 필요"],
    ["무상 통행권", "민법 제220조: 분할로 막힌 땅은 분할자 사이에서 무상 통행. 승계인에게는 인정 안 됨 (판례)", ("통행 폭은 \"일상생활 필요\" 범위 — 단지 차량·소방 보장 불확실", R_)],
], row_h=1.0, size=16, label_cols=(0,))
pingga(s, ny + 0.15, "진입로 귀속과 통행 보장이 서면으로 정해지지 않으면 분할은 진행할 수 없습니다.", h=0.8)

# ===================== 7-3 위험2 해결방안 =====================
s = new()
frame(s, "위험 2", "해결방안은 있으나 모두 합의가 필요합니다", "넷 중 하나로 정리해야 하며 어느 것도 혼자 정할 수 없습니다",
      "출처: 민법 제291조(지역권) · 건축법 제45조(도로 지정) 등 일반 법리 (적용 가능 여부는 전문가 확인 필요)")
ny = table(s, X0, 2.2, [2.9, 5.2, 4.233], [
    ["방안", "내용", "한계"],
    ["① 분할선 조정", "진입로 부분을 아파트 쪽 대지에 귀속", "백화점 대지 축소 · 접도 재검토"],
    ["② 통행·소방 지역권", "백화점 대지에 지역권 설정 후 등기", "공유자·신탁 수익자 동의 필요"],
    ["③ 도로 편입", "진입로를 시 도로로 지정 · 기부채납", "창원시 협의 · 시간과 비용"],
    ["④ 대체 진입로", "아파트 다른 면에서 새 진입로 개설", "부지 확보 여부 미확인"],
], row_h=0.66, size=17, header=True, label_cols=(0,))
pingga(s, ny + 0.15, "어느 방안이든 분할 합의 전에 서면 약정이 선행돼야 합니다.", h=0.75)

# ===================== 7-4 위험2 선결조건 =====================
s = new()
frame(s, "위험 2", "진입로 선결 확인 6가지", "이 확인이 끝나기 전에는 분할 논의가 시작될 수 없습니다",
      "출처: 내부 검토 문서 · 토지이음/도로대장 등 공적 자료로 확인 (확인 전까지 모두 미확인)")
table(s, X0, 2.2, [0.7, 6.0, 5.633], [
    [("1", {"align": PP_ALIGN.CENTER}), "진입로 부지의 필지·지목·소유자", "지적도·토지대장·등기부"],
    [("2", {"align": PP_ALIGN.CENTER}), "공도(시 도로) 여부", "창원시 도로대장 · 도로관리 부서"],
    [("3", {"align": PP_ALIGN.CENTER}), "폭·차로 수·소방차 진입 가능 여부", "현장 실측 (내일 방문)"],
    [("4", {"align": PP_ALIGN.CENTER}), "분할선 도면에서 진입로 귀속", "제안자에게 도면 서면 요청"],
    [("5", {"align": PP_ALIGN.CENTER}), "아파트의 다른 도로 접면 유무", "지적도 · 현장"],
    [("6", {"align": PP_ALIGN.CENTER}), "진입도로 기준의 리모델링 적용 여부", "창원시 주택 담당부서 질의"],
], row_h=0.66, size=18, label_cols=(0,))

# ===================== 8 위험3 용적률 =====================
s = new()
frame(s, "위험 3", "분할하면 용적률이 넘을 수 있습니다", "분할하면 아파트 쪽 대지가 줄어듭니다",
      "출처: 집합건축물대장 표제부 (2023-05-30 발급, 소개서 18쪽, 스캔 판독). 294%는 추정")
ny = ev(s, cr2("bld_far.png"), 2.2, W0, 2.2, "↑ 붉은 박스: 대지면적 113,000㎡ · 용적률 268.75%")
table(s, X0, ny + 0.1, [4.111, 4.111, 4.111], [
    [("현재 단지 (대장)", CT), ("분할 후 아파트 (추정)", CT), ("조례 한도 (별표 28)", CT)],
    [("268.75%", {"align": PP_ALIGN.CENTER, "size": S_BIG, "bold": True, "font": HEAD}),
     ("약 294%", {"align": PP_ALIGN.CENTER, "size": S_BIG, "bold": True, "color": RED, "font": HEAD}),
     ("250%", {"align": PP_ALIGN.CENTER, "size": S_BIG, "bold": True, "font": HEAD})],
], row_h=0.72, header=True, label_cols=())

# ===================== 9 조합 350% 근거 =====================
s = new()
frame(s, "위험 3", "조합 350%는 리모델링 증축으로 받을 수 있습니다", "현재 268% → 350%는 법정 증축 범위(30%) 안의 수치입니다",
      "출처: 조합 공고 06호 · 주택법 제2조25호·제66조 (법률 제21902호, 2027.3.9 시행본)")
ny = ev(s, cr("gonggo06_scale.png"), 2.2, W0, 1.25, "↑ 공고 06호 단지현황 (붉은 박스: 리모델링 전 268% → 후 350% 이내)")
ny = table(s, X0, ny + 0.05, [2.6, 9.733], [
    ["법 근거", "주택법 제2조 제25호 나목: 15년 경과 공동주택(대동아파트 해당, 담당자 확인)은 세대 전용면적 30%(85㎡ 미만 40%) 이내 증축 가능"],
    ["계산 (추정)", "268.75% × 1.3 ≈ 349.4%  →  조합 350% 이내와 일치"],
    ["판단", ("리모델링 특례로 350% 가능 — 단, 도시계획위원회 심의 통과 전제 (제66조 ⑥)", R_)],
], row_h=0.62, size=18)
pingga(s, ny + 0.15, "법정 용적률(250%)을 넘는 부분은 리모델링 증축 규정으로 허용되는 것입니다.", h=0.72)

# ===================== 10 위험4 백화점 =====================
s = new()
frame(s, "위험 4", "백화점 부지는 현재 용적률도 받기 어렵습니다", "리모델링이 아니므로 조례 한도 250%가 적용됩니다",
      "출처: 창원시 조례 [별표 28] · 국토계획법 제52조 (시행 2026.7.1) · 3종일반·지구단위 해당 미확인")
ny = ev(s, cr("byeolpyo28.png"), 2.2, W0, 1.75, "↑ 붉은 박스: 3종일반 250% (HWP 본문 발췌, 화면 캡처 아님)")
ny = table(s, X0, ny + 0.02, [4.111, 4.111, 4.111], [
    [("조례 한도", CT), ("현재 단지 (대장)", CT), ("제안서", CT)],
    [("250% 이하", {"align": PP_ALIGN.CENTER, "size": 26, "bold": True, "font": HEAD}),
     ("268.75%", {"align": PP_ALIGN.CENTER, "size": 26, "bold": True, "font": HEAD}),
     ("349.67%", {"align": PP_ALIGN.CENTER, "size": 26, "bold": True, "color": RED, "font": HEAD})],
], row_h=0.55, header=True, label_cols=())
pingga(s, ny + 0.12, ["신축은 리모델링 특례가 없어 현재 용적률 받기도 어렵습니다.",
                      "받으려면 지구단위계획(제52조)으로 종상향·용적률 완화가 필요 (불확실)."], h=0.95)

# ===================== 10-2 위험4 복리시설 증축 =====================
s = new()
frame(s, "위험 4", "조합에 들어가도 백화점 증축은 10%까지입니다", "복리시설은 아파트 세대와 증축 기준이 다릅니다",
      "출처: 주택법 시행령 별표 4 2.나 (2017.2.13 개정) · 공동주택관리법 시행령 별표 3 6호")
ny = table(s, X0, 2.2, [2.3, 5.9, 4.133], [
    ["대상 요건", "사용검사 10년 경과 · 공동주택과 동시에 리모델링 · 구조안전 인정", "조합 리모델링에 포함돼야 함 (미확인)"],
    ["증축 한도", ("기존 건축물 연면적 합계의 10분의 1 이내", R_), "34,608㎡ × 10% ≈ 3,460㎡ (추정)"],
    ["참고", "법 제2조 제25호 나목은 \"30% 이내, 대통령령 범위\" (2027.3.9 시행본)", "시행령 현행 수치 확인 필요"],
    ["리모델링이 아닌 증축", "시·군·구 건축위원회 심의 또는 사업계획승인 범위 (관리법 시행령 별표 3)", "행위허가 필요"],
], row_h=0.78, size=17, label_cols=(0,))
pingga(s, ny + 0.15, "백화점이 조합 리모델링에 들어가도 증축은 연면적의 10분의 1까지라 350%는 어렵습니다.", h=0.8)

# ===================== 11 위험5 신탁 =====================
s = new()
frame(s, "위험 5", "담보가 신탁으로 잡혀 있습니다", "근저당이 없어도 우선수익권이 444억 원입니다",
      "출처: 내부 검토 문서 \"채무 구조\" (등기부·감사보고서 인용, 2026-11-06). 신탁원부 원문 확인 필요")
ny = ev(s, cr2("trust.png"), 2.2, W0, 1.6, "↑ 붉은 박스: 신탁 우선수익권 기재")
ny = table(s, X0, ny + 0.05, [5.4, 6.933], [
    ["새마을금고 9곳 대출", "370억 원"],
    ["교보자산신탁 우선수익권", ("444억 원 (대출액의 120%)", R_)],
    ["연 이자 vs 영업이익", ("21.4억 원 > 5.1억 원", R_)],
], row_h=0.52, size=19)
pingga(s, ny + 0.12, "근저당은 2020-06-19 말소, 담보는 신탁으로 전환되었습니다.", h=0.62)

# ===================== 12 위험6 지연 =====================
s = new()
frame(s, "위험 6", "리모델링 조합 사업이 지연 중입니다", "허가 단계에서 동의를 다시 받아야 합니다",
      "출처: 율해 의견서 · 경남도민일보 (2026-02-22) · 창원시 회신 (2026-10-23) · 조합 공고 (2026-04-30)")
ny = table(s, X0, 2.2, [1.7, 6.4, 4.233], [
    ["시점", "진행 내용", "출처 · 상태"],
    ["2022-04", "조합설립인가", "율해 의견서 (인가서 미확인)"],
    ["2022-10", "우선협상대상자 지정", "조합 공고 (4년 경과)"],
    ["2026-02", ("도시계획심의 미통과", R_), "경남도민일보"],
    ["2026-04", "설계자·CM 업체 새로 모집", "조합 공고 06·08호"],
    ["현재", ("시공자 미선정 · 동의율 확인 불가", R_), "창원시 회신"],
], row_h=0.56, header=True, label_cols=(0,), size=19)
pingga(s, ny + 0.2, "조합 계획이 확정돼야 \"조합도 분할이 필요\"라는 논리가 성립합니다.", h=0.75)

# ===================== 12-2 위험6 사업시행절차 =====================
s = new()
frame(s, "위험 6", "리모델링 절차에서 지금 어디쯤인가", "도시계획심의 단계에서 멈춰 있습니다 (언론 보도 기준)",
      "출처: 리모델링 사업시행절차도 (사용자 제공, 출처 미상) · 세대수는 조합 공고 (추정)")
ny = table(s, X0, 2.2, [2.4, 5.9, 4.033], [
    ["단계", "내용 (제공 절차도 기준)", "이 건 진행 상황"],
    ["조합설립인가", "리모델링주택조합 설립", "2022-04 (인가서 미확인)"],
    ["1차 안전진단", "증축 가능 여부 판정 (주택법 제68조)", "결과 미확인"],
    [("도시계획심의", {"fill": PINK, "bold": True, "align": PP_ALIGN.CENTER}),
     ("50세대 이상 증가 시 도시계획위원회 심의\n지구단위 내 용적률 완화 시 사전 심의", {"fill": PINK}),
     ("2026-02 미통과 (현재 위치)", {"fill": PINK, "color": RED, "bold": True})],
    ["건축위원회 심의", "수직증축형이면 구조 적정성 검토 (제69조)", "해당 여부 미확인"],
    ["리모델링 허가", "제66조 허가 (30세대↑ 증가 시 제15조 승인)", ("동의율 불명 · 시공자 미선정", R_)],
    ["이주 ~ 준공", "이주·철거 → 2차 안전진단 → 착공 → 준공", "미도달"],
], row_h=0.5, size=16, header=True, label_cols=(0,))
pingga(s, ny + 0.2, "약 420세대 증가 계획(2,810→3,230, 추정)이라 도시계획심의가 필수입니다.", h=0.7)

# ===================== 13 위험6 허가 동의율 =====================
s = new()
frame(s, "위험 6", "허가 동의율은 전체 75%, 동별 50%", "조합설립 때와 기준이 다릅니다",
      "출처: 주택법 시행령 별표 4 1.나 (2017.2.13 개정) · 창원시 회신 (2026-10-23)")
ny = ev(s, cr2("city_consent.png"), 2.2, 7.4, 3.2, "↑ 붉은 박스: 허가 신청 시 동의 요건")
table(s, 8.3, 2.3, [2.2, 2.333], [
    ["조합설립", "전체 2/3\n동별 1/2"],
    ["허가 신청", ("전체 75%\n동별 50%", R_)],
    ["현재 동의율", ("확인 불가", R_)],
], row_h=0.95, size=19)
table(s, X0, max(ny, 5.55) + 0.05, [3.4, 8.933], [
    ["백화점 (복리시설)", "별동 비공유 복리시설은 권리변동이 없을 때만 동의 산정에서 제외 (별표 4)"],
], row_h=0.55, size=19)

# ===================== 14 위험6 시공자 =====================
s = new()
frame(s, "위험 6", "시공자도 아직 못 정했습니다", "조합이 설계자·CM 업체를 새로 뽑고 있습니다 (2026-04 공고)",
      "출처: 조합 공고 제2026-08호(CM)·제2026-06호(건축설계자), 마감 2026-05-11~14. 선정 결과 미확인")
table(s, X0, 2.2, [3.0], [["CM 공고 08호\n시공자 선정 지원"]], row_h=1.35, size=19)
picture(s, cr("gonggo08_cm.png"), 3.7, 2.2, 9.1, 1.35)
table(s, X0, 3.75, [3.0], [["설계자 공고 06호\n기존 계약 종료 전제"]], row_h=1.35, size=19)
picture(s, cr("gonggo06_end.png"), 3.7, 3.75, 9.1, 1.35)
cap(s, 3.7, 5.14, 9.1, "↑ 붉은 박스: 공고 해당 문구")
pingga(s, 5.7, "2022-10 우선협상대상자 지정 이후 4년이 지났습니다.", h=0.7)

# ===================== 15 위험7 수지 =====================
s = new()
frame(s, "위험 7", "시장가로 계산하면 적자입니다", "제안서 계산은 맞지만 가정이 시장보다 낙관적입니다",
      "출처: 내부 검토 문서 (제안서 구조 그대로 재계산, 추정)")
x, y, w, h = picture(s, cr2("profit_table.png"), X0, 2.2, 7.9, 4.0)
cap(s, X0, y + h + 0.03, 7.9, "↑ 붉은 박스: 제안서 그대로 / 보수적 종합")
table(s, 8.8, 2.2, [4.033], [[("제안서 그대로 (이익)", {"bold": True, "size": 19, "align": PP_ALIGN.CENTER})],
                             [("+587억 원", {"size": 34, "bold": True, "font": HEAD, "align": PP_ALIGN.CENTER})]], row_h=0.95, label_cols=())
table(s, 8.8, 4.3, [4.033], [[("보수적 종합 (이익)", {"bold": True, "size": 19, "fill": PINK, "align": PP_ALIGN.CENTER})],
                             [("–219억 원", {"size": 34, "bold": True, "color": RED, "fill": PINK, "font": HEAD, "align": PP_ALIGN.CENTER})]], row_h=0.95, label_cols=())

# ===================== 16 위험8 분양가 =====================
s = new()
frame(s, "위험 8", "인근 분양가가 더 낮습니다", "제안서는 평당 3,200만 원으로 가정했습니다",
      "출처: 회사 현장보고 6쪽 (2026-11-09), 현장 방문·관계자 전언 기준")
rect(s, X0, 2.2, 3.9, 1.7, CHAR); rect(s, X0, 2.2, 3.9, 0.05, GOLD)
tb(s, X0, 2.35, 3.9, 0.4, "제안서 분양가", size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
tb(s, X0, 2.85, 3.9, 0.8, "3,200만 원/평", size=30, bold=True, color=GOLD, align=PP_ALIGN.CENTER, font=HEAD, anchor=MSO_ANCHOR.MIDDLE)
rect(s, X0, 4.2, 3.9, 1.7, PINK); rect(s, X0, 4.2, 3.9, 0.05, BURG)
tb(s, X0, 4.35, 3.9, 0.4, "인근 분양가 (현장보고)", size=20, bold=True, color=BURG, align=PP_ALIGN.CENTER)
tb(s, X0, 4.85, 3.9, 0.8, "2,300~2,700\n만 원/평", size=28, bold=True, color=RED, align=PP_ALIGN.CENTER, font=HEAD, anchor=MSO_ANCHOR.MIDDLE)
ev(s, cr("field_price.png"), 2.2, 8.1, 4.1, "↑ 현장보고 6쪽 주변 분양 시장 (평당 분양가 붉은 글씨)", x=4.75)

# ===================== 16-2 위험8 실거래 비교 =====================
import json as _json
_S = _json.load(open(os.path.join(ROOT, "실거래", "summary84.json"), encoding="utf-8"))
def _eok(m): return f"{m/10000:.2f}억"
_big = [x for x in _S if x["n"] >= 10]
_small = [x for x in _S if x["n"] < 10]
s = new()
frame(s, "위험 8", "성산구 10년 이내 아파트 실거래 (84㎡형)", "주요 단지 평균 6.9~8.0억, 전용 평당 약 2,700~3,100만 원이 다수입니다",
      "출처: 국토교통부 실거래가 (API, 조회 2026-11-12) · 계약 2025-11~2026-11 · 전용 84~85㎡ · 취소 제외")
rows_ = [["단지 (동)", "준공", "건수", "평균", "전용 평당", "최근 거래 (거래일 · 금액 · 층)"]]
for x in _big:
    rows_.append([f"{x['apt']} ({x['dong']})", (x["year"], {"align": PP_ALIGN.CENTER}), (str(x["n"]), {"align": PP_ALIGN.CENTER}),
                  (_eok(x["avg"]), {"align": PP_ALIGN.RIGHT}), (f"{x['ppy']:,}만", {"align": PP_ALIGN.RIGHT}),
                  f"{x['last']} · {_eok(x['lamt'])} · {x['lfl']}층"])
table(s, X0, 2.15, [3.9, 0.8, 0.7, 1.4, 1.5, 4.033], rows_, row_h=0.4, size=15, header=True, label_cols=())

# ===================== 16-3 위험8 비교 평가 =====================
s = new()
frame(s, "위험 8", "제안서 분양가는 성산구 최상위 단지 수준입니다", "신축 입주 단지는 표본이 적어 참고로만 봅니다",
      "출처: 국토교통부 실거래가 (API, 조회 2026-11-12) · 34평형은 가정(전용 84㎡, 공급 약 112㎡) · 추정")
rows_ = [["신축 단지 (동)", "준공", "건수", "평균", "최저 ~ 최고"]]
for x in _small:
    rows_.append([f"{x['apt']} ({x['dong']})", (x["year"], {"align": PP_ALIGN.CENTER}), (str(x["n"]), {"align": PP_ALIGN.CENTER}),
                  (_eok(x["avg"]), {"align": PP_ALIGN.RIGHT}), (f"{_eok(x['mn'])} ~ {_eok(x['mx'])}", {"align": PP_ALIGN.RIGHT})])
ny = table(s, X0, 2.15, [4.8, 1.1, 1.1, 2.3, 3.033], rows_, row_h=0.46, size=16, header=True, label_cols=())
ny = table(s, X0, ny + 0.2, [4.0, 8.333], [
    ["제안서 가정 (3,200만 원/평)", ("34평형 기준 약 10.9억 원 (추정)", R_)],
    ["성산구 84㎡형 실거래", "다수 단지 6.9~8.0억 · 최고 평균 11.1억 (용지더샵레이크파크)"],
], row_h=0.58, size=17)
pingga(s, ny + 0.15, "제안서 분양가는 성산구에서 실거래가 가장 높은 용지 단지 수준의 가정입니다.", h=0.72)

# ===================== 17 위험9 면적 =====================
s = new()
frame(s, "위험 9", "서류 속 면적이 서로 다릅니다", "같은 백화점 대지가 네 가지 숫자로 나옵니다",
      "출처: 제안서 · 회사소개서 12쪽 · 등기 대지권 (내부 검토 문서 인용)")
table(s, X0, 2.2, [2.3, 2.9], [
    ["제안서", "9,900㎡"],
    ["제안서", "11,225㎡"],
    ["회사소개서", ("13,132㎡", R_)],
    ["등기 대지권", "15,320㎡"],
], row_h=0.85, size=24)
x, y, w, h = picture(s, cr2("bldg_status.png"), 6.0, 2.2, 6.8, 4.0)
cap(s, 6.0, y + h + 0.04, 6.8, "↑ 회사소개서 12쪽 (붉은 박스: 부지 13,132㎡)")

# ===================== 18 위험9 위반건축물 =====================
s = new()
frame(s, "위험 9", "위반건축물 기록이 있습니다", "1층 소매점 23.76㎡ 무단증축 (2017-04-24 기재)",
      "출처: 집합건축물대장 2쪽 변동사항 (2023-05-30 발급, 소개서 19쪽)")
ny = ev(s, cr2("violation.png"), 2.2, W0, 2.6, "↑ 붉은 박스: 위반건축물로 기재")
table(s, X0, ny + 0.05, [2.6, 9.733], [
    ["시정 여부", ("미확인", R_)],
    ["확인 방법", "성산구 건축허가과 문의 · 대장 재발급"],
], row_h=0.58)

# ===================== 19 서면 확인 =====================
s = new()
frame(s, "다음", "서면으로 확인할 5가지", "답변을 받은 뒤 다시 검토하겠습니다", "전체 요청 목록은 증빙자료_정리 파일 §7 (9개 항목)")
req = ["신탁원부 · 대출약정서", "분할선 도면 · 진입로 방안", "분할 후 용적률 계산서", "조합 동의율 · 심의 일정", "공사비 · 분양가 근거"]
table(s, X0, 2.25, [1.1, 11.233],
      [[(str(i + 1), {"align": PP_ALIGN.CENTER, "size": 26, "font": NUMF}), (t, {"size": 26, "bold": True})] for i, t in enumerate(req)],
      row_h=0.8, label_cols=(0,))

if FULL:
    def law(n): return os.path.join(LAW, n)

    def appx(title, lead, source, items, right_title="핵심 확인"):
        """items: [(image_path, caption, max_w, max_h)] 왼쪽에 세로로 쌓고, 오른쪽에 핵심 문구."""
        s_ = new()
        frame(s_, "부록", title, lead, source)
        y_ = 2.15
        for path, cp, mw, mh in items:
            _, py, pw, ph = picture(s_, path, X0, y_, mw, mh)
            cap(s_, X0, py + ph + 0.02, mw, cp)
            y_ = py + ph + 0.42
        return s_

    def points(s_, x, y, w, lines, h=None):
        h = h or min(4.4, 0.35 + 1.15 * len(lines))
        rect(s_, x, y, w, h, PINK); rect(s_, x, y, 0.05, h, GOLD)
        tb(s_, x + 0.2, y + 0.1, w - 0.35, h - 0.2, [(l, {"space": 8}) for l in lines], size=18, color=INK)

    s_ = appx("주택법 제2조 제25호 (리모델링 정의)", "증축 한도(30%·40%)와 복리시설 증축 규정의 원문입니다",
              "출처: 주택법 [시행 2027.3.9] 법률 제21902호 (국가법령정보센터 출력본, 사용자 제공)",
              [(law("a1_주택법2조25호.png"), "↑ 붉은 박스: 나목 증축 한도 · 입주자 공유가 아닌 복리시설 증축", 7.9, 4.3)])
    points(s_, 8.6, 2.15, 4.23, ["나목: 사용검사 15년 경과 공동주택은 세대 전용면적 30%(85㎡ 미만 40%) 이내 증축",
                                  "복리시설: 입주자 공유가 아니면 연면적 30% 이내, 대통령령 범위",
                                  "시행본이 2027.3.9라 현행본과 대조 필요"])

    s_ = appx("주택법 제66조 (리모델링의 허가 등)", "허가 요건과 도시계획위원회 심의(제6항)의 원문입니다",
              "출처: 주택법 [시행 2027.3.9] 법률 제21902호 (국가법령정보센터 출력본, 사용자 제공)",
              [(law("a2_주택법66조.png"), "↑ 붉은 박스: 제1항(허가) · 제6항(세대수 증가형 심의)", 7.2, 4.25)])
    points(s_, 8.6, 2.15, 4.23, ["제1항: 면적·세대수·동의 비율은 대통령령 기준에 따라 시장·군수·구청장 허가",
                                  "제6항: 세대수 증가형은 시·군·구 도시계획위원회 심의 필수",
                                  "시공자는 조합 총회에서 경쟁입찰로 선정 (제3·4항)"])

    s_ = appx("주택법 시행령 제13조 · 제75조", "수직증축 범위와 허가 신청·동의 철회의 원문입니다",
              "출처: 주택법 시행령 [시행 2026.9.8] 대통령령 제36657호 (국가법령정보센터 출력본, 사용자 제공)",
              [(law("a3a_시행령13조.png"), "↑ 제13조 (수직증축형 리모델링의 허용 요건)", 7.9, 1.75),
               (law("a3b_시행령75조.png"), "↑ 제75조 제3항: 허가신청서 제출 전까지 서면 동의 철회 가능", 7.9, 1.2)])
    points(s_, 8.6, 2.15, 4.23, ["제13조: 15층 이상 3개층, 14층 이하 2개층",
                                  "제75조 제1항: 허가기준은 별표 4",
                                  "제75조 제3항: 허가신청 전까지 동의 철회 가능 → 설립 때 동의가 그대로라고 볼 수 없음"])

    s_ = appx("주택법 시행령 별표 4 ① 동의비율", "조합 허가 신청의 동의율 원문입니다 (2017.2.13 개정)",
              "출처: 주택법 시행령 [별표 4] 공동주택 리모델링의 허가기준 (사용자 제공 PDF)",
              [(law("a5a_별표4_동의율.png"), "↑ 붉은 박스: 1. 동의비율 나. 리모델링주택조합의 경우", 7.0, 4.25)])
    points(s_, 8.0, 2.15, 4.83, ["주택단지 전체: 전체 구분소유자·의결권 각 75% 이상, 동별 각 50% 이상",
                                  "별동 비공유 복리시설 소유자는 권리변동이 없는 경우에 한해 산정에서 제외",
                                  "결의서에 설계 개요·공사비·비용분담 명세 필요"])

    s_ = appx("주택법 시행령 별표 4 ② 복리시설 증축", "백화점이 조합에 포함돼도 증축은 연면적 10분의 1입니다",
              "출처: 주택법 시행령 [별표 4] 2. 허용행위 나. (2017.2.13 개정, 사용자 제공 PDF)",
              [(law("a5b_별표4_복리시설증축.png"), "↑ 붉은 박스: 입주자 공유가 아닌 복리시설 등 (1쪽 하단 + 2쪽 상단 이어 붙임)", 7.9, 3.7)])
    points(s_, 8.6, 2.15, 4.23, ["사용검사 10년 이상 + 공동주택과 동시 리모델링 + 구조안전 인정",
                                  "증축은 기존 연면적 합계의 10분의 1 이내",
                                  "법 제2조 제25호 나목의 30%와 수치가 다름 → 현행 시행령 확인 필요"])

    s_ = appx("공동주택관리법 시행령 별표 3 (증축·증설)", "리모델링이 아닌 증축의 행위허가 기준 원문입니다",
              "출처: 공동주택관리법 시행령 [별표 3] 6. 증축·증설 (사용자 제공 PDF, 개정 2025.4.15)",
              [(law("a6_별표3_증축.png"), "↑ 붉은 박스: 가) 사업계획승인 범위 · 나) 건축위원회 심의 (표의 일부)", 6.4, 3.8)])
    points(s_, 7.3, 2.15, 5.53, ["입주자 공유가 아닌 복리시설 증축: 사업계획승인 범위이거나 시·군·구 건축위원회 심의를 거친 경우",
                                  "백화점이 입주자 공유 복리시설인지에 따라 적용이 달라짐 (미확인)"])

    s_ = appx("국토계획법 제52조 (지구단위계획의 내용)", "지구단위계획으로 용도지역 변경·용적률 완화를 정할 수 있는 근거입니다",
              "출처: 국토의 계획 및 이용에 관한 법률 [시행 2026.7.1] 법률 제21447호 (사용자 제공)",
              [(law("a4_국토계획법52조.png"), "↑ 붉은 박스: 제1항 제1호·제4호 · 제3항(완화 적용)", 7.0, 4.25)])
    points(s_, 7.9, 2.15, 4.93, ["제1항 제1호: 용도지역을 대통령령 범위에서 세분하거나 변경",
                                  "제1항 제4호: 건폐율·용적률·높이 한도",
                                  "제3항: 제76~78조 등을 대통령령 범위에서 완화 적용 가능",
                                  "대통령령 범위(시행령)는 미확인 → 종상향 가능 여부 불확실"])

    s_ = appx("창원시 도시계획 조례 [별표 28] 용적률", "3종일반주거지역 용적률 한도 250% (발췌)",
              "출처: 창원시 도시계획 조례 [별표 28] 본문을 옮긴 발췌 (HWP 원본, 한글 화면 캡처 아님)",
              [(os.path.join(CR, "byeolpyo28.png"), "↑ 붉은 박스: 제3종일반주거지역 250퍼센트", 7.9, 3.3)])
    points(s_, 8.6, 2.15, 4.23, ["3종일반 250%, 국토계획법 시행령 상한(300%)이 아니라 조례가 적용",
                                  "2025.11.14 제2260호 조례와 이 별표가 일치하는지는 미확인",
                                  "한글에서 연 화면 캡처로 교체하면 증빙력 상승"])

    s_ = new()
    frame(s_, "부록", "원문을 갖고 있지 않은 근거", "아래는 검색·요약 기준이며 원문 확인이 필요합니다", "출처: 공개 자료 검색 결과 (원문 미보유, 확인 필요)")
    table(s_, X0, 2.2, [3.3, 5.3, 3.733], [
        ["근거", "요지", "확인 방법"],
        ["주택건설기준 규정 제25조", "공동주택 진입도로: 2천세대 이상 폭 20m (2017.7.1 시행본 기준)", "wikisource 해당 문서 · 법제처 현행본 대조"],
        ["건축법 제44조 · 시행령 제28조", "연면적 2천㎡ 이상 건축물 대지는 6m 도로에 4m 이상 접함", "법제처 조문 확인"],
        ["민법 제220조", "분할로 막힌 땅의 무상 통행권 (분할자 사이)", "korea.legal/wiki/민법-제220조"],
        ["대법원 96다33433, 33440", "무상통행권은 승계인에게 인정되지 않음", "판결문 원문 확인"],
        ["서울남부지법 2008가합24143", "분할 선례 (상가 출입구 분리 사안)", "법률의견서 선례표 인용"],
    ], row_h=0.74, size=16, header=True, label_cols=(0,))

    s_ = new()
    frame(s_, "부록", "미확인·추가 확인 목록", "확인되기 전까지 본문의 해당 수치와 판단은 잠정입니다", "출처: 내부 검토 문서 (본문 각 슬라이드의 '미확인' 표시와 대응)")
    table(s_, X0, 2.15, [0.6, 6.3, 5.433], [
        ["#", "확인 항목", "확인 방법"],
        [("1", CT), "상남동 44-1 용도지역(3종일반 여부)·지구단위계획 해당", "토지이용계획확인서 · 창원시"],
        [("2", CT), "조합 현재 동의율 · 안전진단 · 설계자/CM/시공자 선정 결과", "조합 · 창원시 · 제안자 서면"],
        [("3", CT), "신탁원부 원문, 우선수익자 동의 가능성", "등기부 · 제안자 서면"],
        [("4", CT), "법령 현행본 대조 (시행본 · 복리시설 10%/30% · 시행령 범위)", "법제처 현행 조문"],
        [("5", CT), "진입로 부지 소유·공도 여부·폭 · 아파트 다른 접면", "지적도 · 도로대장 · 현장"],
        [("6", CT), "대장 확인: 대지·구역면적 불일치 · 백화점 연면적 · 공유 여부", "건축물대장 · 토지대장 재발급"],
        [("7", CT), "위반건축물 시정 여부 (23.76㎡ 무단증축)", "성산구 건축허가과"],
        [("8", CT), "조례 별표 28이 현행 제2260호와 일치하는지", "법제처 조례 PDF · 한글 캡처"],
        [("9", CT), "실거래: 분양권 제외, 공급면적 기준 평단가 (전용 기준만 산출)", "단지별 공급면적 · 분양권 API"],
    ], row_h=0.46, size=15, header=True, label_cols=(0,))

    # ---- 목차 채우기 ----
    SHORT = {"결론": "검토 결론", "요약": "위험 9가지 요약",
             "위험 1": "분할 확정 아님 · 조건 · 분필", "위험 2": "진입로: 법적 부담 · 해결 · 선결",
             "위험 3": "용적률 초과 · 조합 350% 근거", "위험 4": "조례 한도 · 복리시설 증축 10%",
             "위험 5": "신탁 우선수익권", "위험 6": "조합 지연 · 절차 · 동의율 · 시공자",
             "위험 7": "수지 적자", "위험 8": "분양가 · 성산구 실거래 비교",
             "위험 9": "면적 불일치 · 위반건축물", "다음": "서면 확인 5가지", "회신": "회신 문안",
             "부록": "법령 원문 · 확인 목록"}
    groups = []
    for n_, tag_, title_ in SEC:
        if tag_ == "목차":
            continue
        if groups and groups[-1][0] == tag_:
            groups[-1][2] = n_
        else:
            groups.append([tag_, n_, n_])
    half = (len(groups) + 1) // 2
    for k_, chunk in enumerate((groups[:half], groups[half:])):
        rows_ = [["구분", "내용", "쪽"]]
        for tag_, a_, b_ in chunk:
            rows_.append([tag_, SHORT.get(tag_, tag_), (f"{a_}" if a_ == b_ else f"{a_}~{b_}", CT)])
        table(s_toc, X0 + k_ * 6.3, 1.85, [1.1, 3.75, 1.2], rows_, row_h=0.55, size=15, header=True, label_cols=(0,))

prs.save(OUT)
print("saved", OUT, len(prs.slides._sldIdLst))
for w_ in warnings: print(w_)
