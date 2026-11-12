import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw, ImageFont
F = r"C:\Windows\Fonts\malgun.ttf"; FB = r"C:\Windows\Fonts\malgunbd.ttf"
RUST=(184,58,34)
lines=[("【별표 28】 용도지역에서의 용적률 (제60조 관련)",1),
("영 제85조제1항에 따라 지역에 따른 건축물의 용적률은 다음 각 호에서 정한 비율 이하로 하여야 한다.",0),
("3. 제1종일반주거지역 : 200퍼센트",0),
("4. 제2종일반주거지역 : 220퍼센트",0),
("5. 제3종일반주거지역 : 250퍼센트",2),
("6. 준주거지역 : 400퍼센트",0)]
W,H=2400,560
im=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(im)
y=20
for t,k in lines:
    f=ImageFont.truetype(FB if k else F, 54 if k==2 else 44)
    if k==2:
        d.rectangle([20,y-6,W-20,y+74],fill=(248,230,224),outline=RUST,width=6)
    d.text((40,y),t,font=f,fill=RUST if k==2 else (30,30,30))
    y+=88
im.save(r"C:\Users\cho\land\창원_대동백화점\증빙\ev\crops\byeolpyo28.png"); print(im.size)
