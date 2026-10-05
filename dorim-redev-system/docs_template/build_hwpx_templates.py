"""추진위원회 사무용 HWPX 양식 생성기.

실행: python build_hwpx_templates.py   (결과: ./hwpx/*.hwpx)
python-hwpx 로 기본 골격(secPr, 패키지)을 만들고, 서식(글자·문단·표 테두리)과
본문 XML 은 직접 주입한다. 양식 문구를 고치려면 아래 build_* 함수만 수정하면 된다.
"""
import sys
import io
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from lxml import etree
from hwpx.document import HwpxDocument

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = Path(__file__).parent / "hwpx"
HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"
NS = {"hp": HP}

ORG = "(가칭) 도림사거리 역세권 재개발 추진위원회"
PROJECT = "도림사거리 역세권 장기전세주택 재개발"
SITE = "서울특별시 영등포구 도림동 239-12 일원"

TEXT_W = 48190  # A4, 좌우 여백 20mm 기준 본문 폭(HWPUNIT)

# ── 서식 정의 ────────────────────────────────────────────────
# charPr: id -> (높이(1/100pt), 굵게, 글꼴id[0=돋움,1=바탕], 색)
CHARS = {
    "body": (7, 1100, False, 1, "#000000"),
    "title": (8, 2200, True, 0, "#000000"),
    "h1": (9, 1300, True, 0, "#000000"),
    "lab": (10, 1000, True, 0, "#000000"),
    "txt": (11, 1000, False, 1, "#000000"),
    "small": (12, 900, False, 1, "#555555"),
    "sub": (13, 1400, True, 0, "#000000"),
}
# paraPr: id -> (정렬, 왼쪽여백, 내어쓰기, 문단 앞, 문단 뒤, 줄간격%)
PARAS = {
    "title": (20, "CENTER", 0, 0, 0, 600, 130),
    "center": (21, "CENTER", 0, 0, 0, 0, 140),
    "body": (22, "JUSTIFY", 0, 0, 0, 0, 165),
    "h1": (23, "LEFT", 0, 0, 900, 300, 150),
    "item": (24, "JUSTIFY", 1000, -1000, 0, 0, 165),
    "item2": (25, "JUSTIFY", 2000, -1000, 0, 0, 165),
    "right": (26, "RIGHT", 0, 0, 0, 0, 165),
    "cellL": (27, "LEFT", 0, 0, 0, 0, 140),
    "cellC": (28, "CENTER", 0, 0, 0, 0, 140),
    "gap": (29, "LEFT", 0, 0, 0, 0, 60),
}
# borderFill: 3 = 흰 바탕 + 실선, 4 = 회색 음영 + 실선 (기본 문서에는 id 1~2 만 있음 → 연속 번호로 추가)
BF_PLAIN, BF_SHADE = 3, 4

_uid = [10000]


def uid():
    _uid[0] += 1
    return _uid[0]


def t(text):
    return escape(text)


def run(text, c):
    cid = CHARS[c][0]
    if text == "":
        return f'<hp:run charPrIDRef="{cid}"><hp:t /></hp:run>'
    return f'<hp:run charPrIDRef="{cid}"><hp:t>{t(text)}</hp:t></hp:run>'


def para(text, p="body", c="body", pagebreak=False):
    return (f'<hp:p id="{uid()}" paraPrIDRef="{PARAS[p][0]}" styleIDRef="0" '
            f'pageBreak="{1 if pagebreak else 0}" columnBreak="0" merged="0">{run(text, c)}</hp:p>')


def gap(n=1):
    return "".join(para("", "gap", "small") for _ in range(n))


class Cell:
    def __init__(self, text="", cs=1, rs=1, kind="txt", h=None):
        self.text, self.cs, self.rs, self.kind, self.h = text, cs, rs, kind, h


def L(text, **kw):  # 항목 라벨(회색, 가운데, 굵게)
    return Cell(text, kind="lab", **kw)


def X(text="", **kw):  # 내용(왼쪽 정렬)
    return Cell(text, kind="txt", **kw)


def C(text="", **kw):  # 내용(가운데 정렬)
    return Cell(text, kind="ctr", **kw)


def table(widths, rows, row_h=2300):
    """rows: Cell 리스트의 리스트(병합으로 가려지는 칸은 생략). 행 높이는 첫 Cell.h 또는 row_h."""
    nrows, ncols = len(rows), len(widths)
    occupied, placed, heights = set(), [], []
    for r, row in enumerate(rows):
        c = 0
        h = max((cell.h or 0) for cell in row) or row_h
        heights.append(h)
        for cell in row:
            while (r, c) in occupied:
                c += 1
            placed.append((r, c, cell))
            for rr in range(r, r + cell.rs):
                for cc in range(c, c + cell.cs):
                    occupied.add((rr, cc))
            c += cell.cs
        assert c <= ncols, f"행 {r}: 열 수 초과({c}>{ncols})"
    total_h = sum(heights)
    body = []
    for r in range(nrows):
        tcs = []
        for (rr, c, cell) in placed:
            if rr != r:
                continue
            lab = cell.kind == "lab"
            bf = BF_SHADE if lab else BF_PLAIN
            pc = "cellC" if cell.kind in ("lab", "ctr") else "cellL"
            cc = "lab" if lab else "txt"
            w = sum(widths[c:c + cell.cs])
            ch = sum(heights[r:r + cell.rs])
            paras = "".join(
                f'<hp:p id="{uid()}" paraPrIDRef="{PARAS[pc][0]}" styleIDRef="0" pageBreak="0" '
                f'columnBreak="0" merged="0">{run(line, cc)}</hp:p>'
                for line in (cell.text.split("\n") if cell.text else [""]))
            tcs.append(
                f'<hp:tc name="" header="0" hasMargin="1" protect="0" editable="0" dirty="0" borderFillIDRef="{bf}">'
                f'<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" '
                f'linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">'
                f'{paras}</hp:subList><hp:cellAddr colAddr="{c}" rowAddr="{r}" />'
                f'<hp:cellSpan colSpan="{cell.cs}" rowSpan="{cell.rs}" /><hp:cellSz width="{w}" height="{ch}" />'
                f'<hp:cellMargin left="425" right="425" top="170" bottom="170" /></hp:tc>')
        body.append("<hp:tr>" + "".join(tcs) + "</hp:tr>")
    return (
        f'<hp:p id="{uid()}" paraPrIDRef="{PARAS["cellL"][0]}" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
        f'<hp:run charPrIDRef="0"><hp:tbl id="{uid()}" zOrder="0" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" '
        f'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="0" rowCnt="{nrows}" '
        f'colCnt="{ncols}" cellSpacing="0" borderFillIDRef="{BF_PLAIN}" noAdjust="0">'
        f'<hp:sz width="{sum(widths)}" widthRelTo="ABSOLUTE" height="{total_h}" heightRelTo="ABSOLUTE" protect="0" />'
        f'<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" '
        f'vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0" />'
        f'<hp:outMargin left="0" right="0" top="0" bottom="0" /><hp:inMargin left="0" right="0" top="0" bottom="0" />'
        + "".join(body) + "</hp:tbl><hp:t /></hp:run></hp:p>")


# ── 헤더(서식) 주입 ──────────────────────────────────────────
def char_xml(cid, height, bold, font, color):
    return (
        f'<hh:charPr id="{cid}" height="{height}" textColor="{color}" shadeColor="none" useFontSpace="0" '
        f'useKerning="0" symMark="NONE" borderFillIDRef="2">'
        f'<hh:fontRef hangul="{font}" latin="{font}" hanja="{font}" japanese="{font}" other="{font}" symbol="{font}" user="{font}" />'
        '<hh:ratio hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100" />'
        '<hh:spacing hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0" />'
        '<hh:relSz hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100" />'
        '<hh:offset hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0" />'
        + ("<hh:bold />" if bold else "") +
        '<hh:underline type="NONE" shape="SOLID" color="#000000" /><hh:strikeout shape="NONE" color="#000000" />'
        '<hh:outline type="NONE" /><hh:shadow type="NONE" color="#C0C0C0" offsetX="10" offsetY="10" /></hh:charPr>')


def para_xml(pid, align, left, intent, prev, nxt, line):
    m = (f'<hh:margin><hc:intent value="{intent}" unit="HWPUNIT" /><hc:left value="{left}" unit="HWPUNIT" />'
         f'<hc:right value="0" unit="HWPUNIT" /><hc:prev value="{prev}" unit="HWPUNIT" />'
         f'<hc:next value="{nxt}" unit="HWPUNIT" /></hh:margin>'
         f'<hh:lineSpacing type="PERCENT" value="{line}" unit="HWPUNIT" />')
    return (
        f'<hh:paraPr id="{pid}" tabPrIDRef="0" condense="0" fontLineHeight="0" snapToGrid="1" suppressLineNumbers="0" '
        f'checked="0" textDir="LTR"><hh:align horizontal="{align}" vertical="BASELINE" />'
        '<hh:heading type="NONE" idRef="0" level="0" />'
        '<hh:breakSetting breakLatinWord="KEEP_WORD" breakNonLatinWord="BREAK_WORD" widowOrphan="0" keepWithNext="0" '
        'keepLines="0" pageBreakBefore="0" lineWrap="BREAK" /><hh:autoSpacing eAsianEng="0" eAsianNum="0" />'
        '<hp:switch><hp:case hp:required-namespace="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar">' + m +
        '</hp:case><hp:default>' + m + '</hp:default></hp:switch>'
        '<hh:border borderFillIDRef="2" offsetLeft="0" offsetRight="0" offsetTop="0" offsetBottom="0" '
        'connect="0" ignoreMargin="0" /></hh:paraPr>')


def _bf(bid, face):
    return (
        f'<hh:borderFill id="{bid}" threeD="0" shadow="0" centerLine="NONE" breakCellSeparateLine="0">'
        '<hh:slash type="NONE" Crooked="0" isCounter="0" /><hh:backSlash type="NONE" Crooked="0" isCounter="0" />'
        '<hh:leftBorder type="SOLID" width="0.12 mm" color="#000000" /><hh:rightBorder type="SOLID" width="0.12 mm" color="#000000" />'
        '<hh:topBorder type="SOLID" width="0.12 mm" color="#000000" /><hh:bottomBorder type="SOLID" width="0.12 mm" color="#000000" />'
        '<hh:diagonal type="SOLID" width="0.1 mm" color="#000000" />'
        f'<hc:fillBrush><hc:winBrush faceColor="{face}" hatchColor="#999999" alpha="0" /></hc:fillBrush></hh:borderFill>')


SHADE_BF = _bf(3, "#FFFFFF") + _bf(4, "#E7E6E6")


def patch_header(xml):
    import re

    def bump(tag, add_xml, n, xml):
        m = re.search(rf'<hh:{tag} itemCnt="(\d+)">', xml)
        old = int(m.group(1))
        xml = xml.replace(m.group(0), f'<hh:{tag} itemCnt="{old + n}">', 1)
        return xml.replace(f"</hh:{tag}>", add_xml + f"</hh:{tag}>", 1)

    xml = bump("borderFills", SHADE_BF, 2, xml)
    xml = bump("charProperties", "".join(char_xml(*v) for v in CHARS.values()), len(CHARS), xml)
    xml = bump("paraProperties", "".join(para_xml(*v) for v in PARAS.values()), len(PARAS), xml)
    return xml


# ── 파일 조립 ────────────────────────────────────────────────
def save_doc(name, body_xml, footer=ORG):
    OUT.mkdir(exist_ok=True)
    tmp = io.BytesIO()
    d = HwpxDocument.new()
    d.set_footer_text(footer)
    d.save_to_stream(tmp)
    zin = zipfile.ZipFile(io.BytesIO(tmp.getvalue()))

    sec = etree.fromstring(zin.read("Contents/section0.xml"))
    for ch in list(sec)[1:]:
        sec.remove(ch)
    pg = sec.find(".//hp:pagePr/hp:margin", NS)
    pg.set("left", "5669")
    pg.set("right", "5669")
    frag = etree.fromstring(f'<r xmlns:hp="{HP}">{body_xml}</r>')
    for ch in frag:
        sec.append(ch)
    sec_bytes = etree.tostring(sec, xml_declaration=True, encoding="UTF-8", standalone=True)

    path = OUT / f"{name}.hwpx"
    with zipfile.ZipFile(path, "w") as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "Contents/section0.xml":
                data = sec_bytes
            elif info.filename == "Contents/header.xml":
                data = patch_header(data.decode("utf-8")).encode("utf-8")
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = zipfile.ZIP_STORED if info.filename == "mimetype" else zipfile.ZIP_DEFLATED
            zout.writestr(zi, data)
    return path


def head_block(title, sub=None):
    s = para(ORG, "center", "sub")
    s += para(title, "title", "title")
    if sub:
        s += para(sub, "center", "small")
    return s


def sign_line(role="위원장"):
    return (para("20    년      월      일", "center", "body") + gap()
            + para(f"{ORG}", "right", "body")
            + para(f"{role}   ○ ○ ○   (인)", "right", "body"))


# ── 양식 1: 회의록 (추진위원회 / 주민총회 겸용) ───────────────
def build_minutes():
    w = [6500, 14000, 6500, 21190]
    b = head_block("제   회  회의록", "※ 회의 종류에 맞게 선택: 추진위원회(운영규정 제24~26조) / 주민총회(제20~23조)")
    b += gap()
    b += para("1. 회의 개요", "h1", "h1")
    b += table(w, [
        [L("회 의 명"), X("제   회 (□ 정기  □ 임시)   □ 추진위원회   □ 주민총회", cs=3)],
        [L("일    시"), X("20    년     월     일 (   )     :    ~     :   ", cs=3)],
        [L("장    소"), X("", cs=3)],
        [L("소집 절차"),
         X("□ 추진위원회: 개최 7일 전까지 통지서 송부 + 게시판 게시 (긴급 시 3일 전, 출석위원 2/3 이상 찬성)\n"
           "□ 주민총회: 개최 14일 전부터 게시판 게시 + 10일 전까지 등기우편 발송 (반송 시 1회 추가 발송)\n"
           "게시일: 20   .   .   .      발송일: 20   .   .   .      (□ 주민총회 개최는 사전 추진위 의결 완료)",
           cs=3, h=4600)],
        [L("추진위원회\n재적·출석"),
         X("재적위원(감사 포함)       명 / 출석       명\n(직접      명 · 서면      명)  ※ 대리 출석 불가, 감사는 의결권 없음", cs=3, h=3000)],
        [L("주민총회\n출석 현황"),
         X("추진위 구성 동의자       명 / 출석       명\n(직접      명 · 서면      명 · 대리(위임장)      명)", cs=3, h=3000)],
        [L("의 장"), X(""), L("서 기"), X("")],
        [L("의결정족수"),
         X("추진위원회: 재적위원 과반수 출석, 출석위원 과반수 찬성 (제26조①)\n"
           "주민총회: 동의자 과반수 출석, 출석자 과반수 찬성 (제22조①)\n"
           "□ 개의 정족수 충족  □ 미충족(재소집)  ※ 정관·규정으로 달리 정한 사항은 해당 기준 적용", cs=3, h=4200)],
    ])
    b += gap()
    b += para("2. 보고 사항", "h1", "h1")
    b += table([TEXT_W], [[X("1)\n2)", h=4200)]])
    b += gap()
    b += para("3. 안건 및 의결 결과", "h1", "h1", pagebreak=True)
    b += para("□ 통지된 안건에 한하여 의결함 (제20조⑥·제25조②)    □ 이해관계 위원(자신과 관련된 해임·계약·소송)은 해당 안건 의결 불참 확인",
              "body", "small")
    aw = [3000, 10000, 24190, 11000]
    rows = [[L("번호"), L("안 건"), L("주요 논의 및 결정 사항"), L("표결 결과")]]
    for i in range(1, 4):
        rows.append([C(f"제{i}호", h=5600), X(""), X(""),
                     X("□ 원안가결\n□ 수정가결\n□ 부결  □ 보류\n찬성   반대   기권  ")])
    b += table(aw, rows)
    b += gap()
    b += para("4. 기타 토의 및 차기 회의", "h1", "h1")
    b += table([6500, TEXT_W - 6500], [
        [L("기타 토의"), X("", h=4200)],
        [L("차기 회의"), X("20    년     월     일 (   )     :       장소:")],
    ])
    b += para("위와 같이 회의 결과를 기록하고, 아래와 같이 서명(날인)합니다.", "body", "body")
    b += table([10000, 8000, 20000, 10190], [
        [L("구 분"), L("성 명"), L("서명(날인)"), L("비 고")],
        [C("의 장", h=2800), X(""), X(""), X("")],
        [C("서 기(작성자)", h=2800), X(""), X(""), X("")],
        [C("서명 위원 1", h=2800), X(""), X(""), X("")],
        [C("서명 위원 2", h=2800), X(""), X(""), X("")],
    ])
    b += gap()
    b += table([8000, TEXT_W - 8000], [
        [L("첨부 서류"), X("□ 참석자 서명부  □ 소집 통지서(게시·발송 증빙 포함)  □ 서면결의서  □ 위임장 및 관계 증명서류\n"
                        "□ 회의 자료  □ 속기록·녹음·영상자료  □ 기타(          )", h=3200)],
        [L("공개 관리"), X("작성일: 20   .   .   .     공개일(작성 후 15일 이내): 20   .   .   .\n"
                        "공개 방법: □ 인터넷(홈페이지)  □ 사무소 비치  □ 게시판    ※ 주민등록번호 등 개인정보 제외", h=3200)],
    ])
    b += para("※ 추진위원회·주민총회 의사록은 운영규정 제35조에 따라 작성 후 15일 이내 공개하고, 토지등소유자의 서면 열람·복사 요청에는 "
              "15일 이내 응하며, 공개 목록은 분기 종료 다음 달 15일까지 서면 통지합니다. 조합설립인가일부터 30일 이내 조합에 인계합니다.",
              "body", "small")
    return b


# ── 양식 2: 추진위원회 소집 통지서 ───────────────────────────
def build_notice():
    b = head_block("제   회  추진위원회  개최 통지서")
    b += gap()
    b += table([8000, 17000, 8000, 15190], [
        [L("문서번호"), X("도림추진 제 20   -    호"), L("시행일자"), X("20    .    .    .")],
        [L("수    신"), X("추진위원 (감사 포함) 귀하", cs=3)],
        [L("제    목"), X("제   회 추진위원회 개최 알림", cs=3)],
    ])
    b += gap()
    b += para("1. 귀하의 건승과 댁내의 평안을 기원합니다.", "item", "body")
    b += para("2. 도림사거리 역세권 재개발 사업의 원활한 추진을 위하여 아래와 같이 추진위원회를 개최하오니, 참석하여 주시기 바랍니다.",
              "item", "body")
    b += gap()
    b += para("- 아   래 -", "center", "sub")
    b += gap()
    b += table([9000, TEXT_W - 9000], [
        [L("회 의 명"), X("제   회 (□ 정기  □ 임시)  추진위원회")],
        [L("일    시"), X("20    년     월     일 (   )     :    ")],
        [L("장    소"), X("")],
        [L("참석 대상"), X("추진위원 전원 (위원장·부위원장·추진위원·감사)")],
        [L("회의 안건"), X("제1호:\n제2호:\n제3호:\n※ 이 통지서에 기재한 안건에 한하여 의결할 수 있습니다.", h=5000)],
        [L("준 비 물"), X("신분증, 필기구")],
    ])
    b += gap()
    b += para("3. 부득이 참석하지 못하는 위원은 서면으로 출석하거나 의결권을 행사할 수 있습니다. 서면결의서를 회의 개최 전까지 제출하여 주시기 바랍니다. "
              "(추진위원회는 대리인 출석이 불가합니다.)", "item", "body")
    b += para("4. 소집 요건 확인:  □ 위원장 소집  □ 토지등소유자 1/10 이상 청구  □ 재적위원 1/3 이상 청구  □ 감사 소집  □ 긴급(3일 전 통지, 출석위원 2/3 이상 찬성 필요)",
              "item", "body")
    b += table([9000, TEXT_W - 9000], [
        [L("사무국 연락처"), X("전화:                 이메일:                 위치:")],
        [L("발송·게시 기록"), X("송부일: 20   .   .   .  (방법:          )   게시판 게시일: 20   .   .   .\n"
                           "※ 회의 개최 7일 전까지(긴급 시 3일 전) 송부·게시. 증빙(영수증·발송내역·게시 사진) 보관", h=3200)],
    ])
    b += gap()
    b += sign_line("위원장")
    return b


# ── 양식 3: 참석자 서명부 (추진위원회용 / 주민총회용) ────────
def build_signin_committee():
    b = head_block("추진위원회 참석자 서명부", "※ 추진위원회는 서면 출석은 인정되나 대리인 출석은 불가")
    b += gap()
    b += table([8000, 17000, 8000, 15190], [
        [L("회 의 명"), X("제   회 추진위원회", cs=3)],
        [L("일    시"), X("20    년     월     일 (   )     :    "), L("장    소"), X("")],
    ])
    b += gap()
    w = [3000, 8500, 8500, 10000, 12190, 6000]
    rows = [[L("번호"), L("성 명"), L("직 위"), L("출석 형태"), L("서명(날인)"), L("비 고")]]
    for i in range(1, 19):
        rows.append([C(str(i), h=2500), X(""), X(""), C("□직접  □서면"), X(""), X("")])
    b += table(w, rows, row_h=2500)
    b += gap()
    b += para("※ 직위: 위원장 / 부위원장 / 추진위원 / 감사(감사는 재적위원에 포함되나 의결권 없음). 비고란에 감사 표기.", "body", "small")
    b += para("※ 서명부의 개인정보는 출석 확인 및 정족수 산정 목적으로만 사용하며, 보관기간 경과 후 파기합니다.", "body", "small")
    return b


def build_signin_assembly():
    b = head_block("주민총회 참석자 서명부", "※ 서면결의는 출석으로 인정(총회 전일까지 도착), 대리인 출석은 위임장·관계 증명서류 필요")
    b += gap()
    b += table([8000, 17000, 8000, 15190], [
        [L("회 의 명"), X("제   회 주민총회", cs=3)],
        [L("일    시"), X("20    년     월     일 (   )     :    "), L("장    소"), X("")],
    ])
    b += gap()
    w = [2200, 5600, 7000, 10800, 5400, 3800, 9390, 4000]
    rows = [[L("번호"), L("토지등소유자\n성명"), L("소재지(동·호)"), L("출석 형태"), L("대리인\n성명"), L("관계"), L("서명(날인)"), L("비고")]]
    for i in range(1, 17):
        rows.append([C(str(i), h=2500), X(""), X(""), C("□직접 □서면 □대리"), X(""), X(""), X(""), X("")])
    b += table(w, rows, row_h=2500)
    b += gap()
    b += para("※ 대리인: 배우자·직계존비속·형제자매 중 성년자, 해외거주자의 대리인, 법인의 대리인(제13조②). 위임장 및 관계 증명서류를 제출해야 합니다.",
              "body", "small")
    b += para("※ 공유 소유자는 대표소유자 선임동의서에 따른 대표소유자가 서명합니다.", "body", "small")
    return b


# ── 양식 4: 사업추진절차 안내 ────────────────────────────────
def build_process():
    b = head_block("재개발 사업 추진 절차 안내", "※ 법령·서울시 기준은 개정될 수 있으므로 확정 전 최신 내용을 확인하여 공지 (기준일: 2026.9.15. 생활법령 등)")
    b += gap()
    b += para("1. 사업 개요", "h1", "h1")
    b += table([9000, TEXT_W - 9000], [
        [L("사 업 명"), X(PROJECT)],
        [L("대 상 지"), X(SITE + "  (구역 면적 59,607.59㎡)")],
        [L("현재 단계"), X("서울시 사전검토회의 (정비구역 입안 초기)")],
        [L("적용 기준"), X("서울시 역세권 장기전세주택 건립 운영기준 (2026.3.6. 시행)")],
    ])
    b += gap()
    b += para("2. 유의 사항", "h1", "h1")
    b += para("○ 현재는 1단계(사전검토) 진행 중이며, 단계별 절차는 다음 쪽(별첨)과 같습니다. "
              "이후 단계는 사전검토 결과 및 주민 동의 현황에 따라 일정이 조정될 수 있습니다.", "item", "body")
    b += para("○ 해제 기한 유의(도시정비법 제20조): 정비구역 지정·고시 후 2년 내 추진위 승인 신청, 추진위 승인 후 2년 내 조합설립인가 신청, "
              "조합설립인가 후 3년 내 사업시행계획인가 신청을 하지 않으면 구역 해제 대상이 될 수 있습니다.", "item", "body")
    b += para("○ 동의율은 토지등소유자 수(및 토지면적) 기준이며, 정확한 산정 방식은 추진위원회 사무국 또는 관할 구청에 문의하시기 바랍니다.",
              "item", "body")
    b += gap()
    b += para("3. 문의처", "h1", "h1")
    b += table([9000, TEXT_W - 9000], [
        [L("추진위원회 사무국"), X("전화:                 이메일:                 방문:")],
        [L("관할 기관"), X("영등포구청 도시계획과·정비사업 담당 / 서울시 정비사업 정보몽땅 (cleanup.seoul.go.kr)")],
    ])
    b += gap()
    b += sign_line("위원장")
    b += para("별첨.  단계별 추진 절차", "h1", "h1", pagebreak=True)
    w = [2300, 6500, 15500, 9800, 7500, 6590]
    rows = [[L("순서"), L("단 계"), L("주요 내용"), L("동의·요건"), L("근 거"), L("진행 상태")]]
    steps = [
        ("사전검토", "서울시 사전검토회의", "정비구역 입안 신청, 주민 동의서 징구",
         "토지등소유자 40% 이상\n(역세권 운영기준)", "역세권 운영기준\n(2026.3.6.)"),
        ("정비구역\n지정", "입안·주민공람·심의·고시", "정비계획 수립, 구역 지정 고시\n(선심의제: 지정 요청 전까지 동의 50%)",
         "일반 재개발 선심의제\n50%(서울시 2025.7.)", "도시정비법 제16조"),
        ("추진위원회\n승인", "추진위원회 구성·구청장 승인", "위원장·감사 포함 5인 이상, 운영규정 작성\n(2025.12.4. 시행: 구역 지정 전 구성 가능)",
         "토지등소유자 과반수 동의\n(운영규정안 첨부 동의서)", "도시정비법 제31조\n운영규정 제2조"),
        ("추진위\n운영", "조합 설립 준비", "정비업체·설계자 선정, 정관 초안,\n동의서 징구, 분기별 자료 공개",
         "주민총회·추진위 의결\n(비용부담 업무는 사전 동의)", "도시정비법 제32조\n운영규정"),
        ("조합설립\n인가", "창립총회·인가 신청", "정관 확정, 임원 선출, 구청장 인가·등기",
         "토지등소유자 3/4 이상\n및 토지면적 1/2 이상", "도시정비법 제35조"),
        ("시공자\n선정", "시공사 입찰·선정", "조합설립인가 이후에만 가능\n(일반·지명경쟁, 총회 의결)", "총회 의결", "도시정비법 제29조\n(서울시 조례)"),
        ("사업시행\n인가", "사업시행계획 인가", "건축·교통·환경 심의,\n인가권자 60일 내 결정·고시",
         "총회 의결 (사업비 10% 이상\n증가 시 2/3 이상 찬성)", "도시정비법\n제45조·제50조"),
        ("관리처분\n인가", "관리처분계획 수립·인가", "분양신청, 30일 이상 공람, 총회 의결,\n인가(30일 내, 타당성 검증 시 60일)",
         "총회 의결\n(변경 시 사업비 증가 등 별도 요건)", "도시정비법\n제74조·제78조"),
        ("이주·철거\n착공·분양", "이주·철거·착공·분양", "분양공고(기한 개정 안내, 최신 확인)\n공사비 검증결과서 첨부 필요",
         "-", "도시정비법 제72조\n국토부 고시"),
        ("준공·\n이전고시", "준공인가·이전고시", "입주, 소유권 이전고시, 조합 청산", "-", "도시정비법"),
    ]
    for i, (a, b2, c, d2, e) in enumerate(steps, 1):
        rows.append([C(str(i), h=3000), C(a), X(b2 + "\n" + c), X(d2), X(e), C("□예정 □진행\n□완료")])
    b += table(w, rows)
    return b


# ── 양식 5: 주민 안내문 ──────────────────────────────────────
def build_resident_notice():
    b = head_block("[안내]  도림사거리 역세권 재개발", "")
    b += para("(  안내 제목을 입력하세요  )", "center", "sub")
    b += gap()
    b += para("토지등소유자 여러분께", "body", "sub")
    b += gap()
    b += para("안녕하십니까? 도림사거리 역세권 재개발 추진위원회입니다. "
              "평소 사업에 보내주시는 관심과 협조에 깊이 감사드립니다. 아래와 같이 안내드리오니 참고하여 주시기 바랍니다.",
              "body", "body")
    b += gap()
    b += para("1. 안내 내용", "h1", "h1")
    b += table([9000, TEXT_W - 9000], [
        [L("안내 사항"), X("", h=6000)],
        [L("일    시"), X("20    년     월     일 (   )     :    ")],
        [L("장    소"), X("")],
        [L("대    상"), X("도림동 239-12 일원 토지등소유자 (□ 전체  □ 해당자)")],
        [L("준 비 물"), X("")],
    ])
    b += gap()
    b += para("2. 유의 사항", "h1", "h1")
    b += para("○ 동의서·서류 제출 시 본인 확인(신분증)이 필요합니다.", "item", "body")
    b += para("○ 확정되지 않은 사업 일정·분담금 등 비공식 정보에 유의하시고, 추진위원회 공식 공지만 확인해 주세요.", "item", "body")
    b += para("○ 개인정보는 사업 추진 목적 외에 사용하지 않습니다.", "item", "body")
    b += gap()
    b += para("3. 문의처", "h1", "h1")
    b += table([9000, TEXT_W - 9000], [
        [L("추진위원회 사무국"), X("전화:                 이메일:                 방문:")],
    ])
    b += gap(2)
    b += sign_line("위원장")
    return b


# ── 양식 6: 주민총회 소집 공고(통지) ─────────────────────────
def build_assembly_notice():
    b = head_block("제   회  주민총회  소집 공고")
    b += gap()
    b += table([8000, 17000, 8000, 15190], [
        [L("문서번호"), X("도림추진 제 20   -    호"), L("시행일자"), X("20    .    .    .")],
        [L("수    신"), X("토지등소유자 귀하 (추진위원회 구성 동의자 및 미동의자 전원)", cs=3)],
        [L("제    목"), X("제   회 주민총회 개최 알림", cs=3)],
    ])
    b += gap()
    b += para("1. 도림사거리 역세권 재개발 추진위원회 운영규정 제20조에 따라 아래와 같이 주민총회를 개최하오니 참석하여 주시기 바랍니다.",
              "item", "body")
    b += gap()
    b += para("- 아   래 -", "center", "sub")
    b += gap()
    b += table([9000, TEXT_W - 9000], [
        [L("회 의 명"), X("제   회 (□ 정기  □ 임시)  주민총회")],
        [L("일    시"), X("20    년     월     일 (   )     :    ")],
        [L("장    소"), X("")],
        [L("회의 목적"), X("")],
        [L("회의 안건"), X("제1호:\n제2호:\n제3호:\n※ 통지한 안건에 한하여 의결할 수 있습니다.", h=5000)],
        [L("추진위 사전의결"), X("20    .    .    .  제   회 추진위원회에서 개최·안건 의결 (청구에 의한 소집은 해당 없음)")],
    ])
    b += gap()
    b += para("2. 참석·의결권 행사 방법", "h1", "h1")
    b += para("○ 직접 참석: 신분증을 지참하여 주시기 바랍니다.", "item", "body")
    b += para("○ 서면 결의: 안건별 의사를 표시한 서면결의서를 총회 전일까지 추진위원회에 도착하도록 제출 (서면 결의는 출석으로 봅니다).", "item", "body")
    b += para("○ 대리 출석: 위임장과 대리인 관계 증명서류를 제출 (대리인: 배우자·직계존비속·형제자매 중 성년자, 해외거주자의 대리인, 법인의 대리인).",
              "item", "body")
    b += gap()
    b += table([9000, TEXT_W - 9000], [
        [L("사무국 연락처"), X("전화:                 이메일:                 위치:")],
        [L("공고·발송 기록"), X("게시판 게시일(14일 전부터): 20   .   .   .      등기우편 발송일(10일 전까지): 20   .   .   .\n"
                           "반송분 재발송일: 20   .   .   .   (1회)    ※ 증빙 보관", h=3200)],
    ])
    b += gap()
    b += sign_line("위원장")
    return b


# ── 양식 7: 서면결의서 / 위임장 (주민총회용) ─────────────────
def build_proxy():
    b = head_block("주민총회  서면결의서 및 위임장", "※ 서면결의서는 총회 전일까지 추진위원회에 도착해야 합니다. (운영규정 제22조)")
    b += gap()
    b += para("1. 토지등소유자(위임인) 인적 사항", "h1", "h1")
    b += table([8000, 14000, 8000, 18190], [
        [L("성    명"), X(""), L("생년월일"), X("")],
        [L("주    소"), X("", cs=3)],
        [L("소유 물건"), X("도림동        번지   (토지      ㎡ / 건축물      ㎡ / 지분      )", cs=3)],
        [L("연 락 처"), X(""), L("공유 여부"), X("□ 단독  □ 공유(대표소유자 선임동의서 제출)")],
    ])
    b += gap()
    b += para("2. 제  회 주민총회 안건별 의결권 행사 (서면결의)", "h1", "h1")
    rows = [[L("안건"), L("안 건 명"), L("찬 성"), L("반 대"), L("기 권")]]
    for i in range(1, 4):
        rows.append([C(f"제{i}호", h=2400), X(""), C("□"), C("□"), C("□")])
    b += table([5000, 28190, 5000, 5000, 5000], rows)
    b += gap()
    b += para("3. 대리 출석 위임 (대리인이 출석하는 경우만 작성)", "h1", "h1")
    b += table([8000, 14000, 8000, 18190], [
        [L("대리인 성명"), X(""), L("관    계"), X("□ 배우자 □ 직계존비속 □ 형제자매 □ 해외거주자 대리인 □ 법인 대리인")],
        [L("대리인 주소"), X("", cs=3)],
        [L("위임 범위"), X("제  회 주민총회의 출석 및 의결권 행사 일체", cs=3)],
    ])
    b += gap()
    b += para("본인은 위 주민총회에서 위와 같이 의결권을 행사(또는 위임)하며, 이 서면의 내용이 사실임을 확인합니다.", "body", "body")
    b += gap()
    b += para("20    년      월      일", "center", "body")
    b += para("위임인(토지등소유자)   성명                    (서명 또는 인)", "right", "body")
    b += para("도림사거리 역세권 재개발 추진위원회 위원장 귀하", "body", "body")
    b += gap()
    b += table([8000, TEXT_W - 8000], [
        [L("제출 서류"), X("□ 신분증 사본  □ 대리인 신분증 사본  □ 관계 증명서류(가족관계증명서 등)  □ 해외거주·법인 대리 증빙", h=3200)],
        [L("접수 확인"), X("접수일시: 20   .   .   .     :       접수자:             (인)\n※ 총회 전일까지 도착분만 유효", h=3200)],
    ])
    b += para("※ 개인정보는 총회 의결정족수 확인 목적으로만 사용하며, 보관기간 경과 후 파기합니다.", "body", "small")
    return b


BUILDERS = [
    ("01_회의록(추진위원회_주민총회)", build_minutes),
    ("02_추진위원회_소집통지서", build_notice),
    ("03_추진위원회_참석자_서명부", build_signin_committee),
    ("04_사업추진절차_안내", build_process),
    ("05_주민_안내문", build_resident_notice),
    ("06_주민총회_소집공고", build_assembly_notice),
    ("07_주민총회_참석자_서명부", build_signin_assembly),
    ("08_주민총회_서면결의서_위임장", build_proxy),
]

if __name__ == "__main__":
    import shutil
    if OUT.exists():
        shutil.rmtree(OUT)
    for name, fn in BUILDERS:
        print("OK", save_doc(name, fn()))
