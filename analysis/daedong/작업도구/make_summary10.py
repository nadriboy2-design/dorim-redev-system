"""보고용 큰글씨 PPT에서 핵심 10장만 뽑아 요약10장 PPT를 만든다.
사용: python make_summary10.py   (먼저 build_report4.py report 로 보고용 PPT를 만든 뒤 실행)
환경변수 DAEDONG_ROOT 로 프로젝트 폴더를 바꿀 수 있다."""
import sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pptx import Presentation

ROOT = os.environ.get("DAEDONG_ROOT", r"C:\Users\cho\land\창원_대동백화점")
src = os.path.join(ROOT, "대동백화점_부지분할_검토보고_보고용_큰글씨_2026-11-12.pptx")
out = os.path.join(ROOT, "대동백화점_부지분할_검토보고_요약10장_2026-11-12.pptx")
want = ["대동백화점 부지", "검토 결론", "분할은 확정이 아닙니다", "아파트 진입로를 같이 씁니다",
        "분할하면 용적률이 넘을 수 있습니다", "백화점 부지는 현재 용적률도 받기 어렵습니다",
        "담보가 신탁으로 잡혀 있습니다", "리모델링 절차에서 지금 어디쯤인가",
        "제안서 분양가는 성산구 최상위 단지 수준입니다", "서면으로 확인할 5가지"]
p = Presentation(src)


def title(s):
    for sh in s.shapes:
        if sh.name == "Title":
            return sh.text_frame.text
    return ""


idx = {}
for i, s in enumerate(p.slides):
    t = title(s).replace("\n", " ")
    for w in want:
        if t.startswith(w) and w not in idx:
            idx[w] = i
assert len(idx) == 10, f"찾지 못한 슬라이드: {set(want) - set(idx)}"
keep = [idx[w] for w in want]
ids = p.slides._sldIdLst
for i, sid in enumerate(list(ids)):
    if i not in keep:
        p.part.drop_rel(sid.rId)
        ids.remove(sid)
for n, s in enumerate(p.slides, 1):  # 쪽번호 다시 매김
    for sh in s.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip().isdigit() and abs(sh.left / 914400 - 11.6) < 0.05:
            sh.text_frame.paragraphs[0].runs[0].text = str(n)
p.save(out)
print("saved", out, len(p.slides))
