# dorim-redev-system/backend/seed_data.py
"""
조합원 명부 가데이터 생성 스크립트.
실행: python seed_data.py
"""
import pandas as pd
from pathlib import Path

DATA_DIR = Path("../data")
DATA_DIR.mkdir(exist_ok=True)

members = [
    {"member_id": 1001, "address": "서울 영등포구 도림동 239-12", "birth_date": "1955-03-15", "is_sale_target": True,  "rights_value": 185000000, "consent": True},
    {"member_id": 1002, "address": "서울 영등포구 도림동 239-14", "birth_date": "1962-07-22", "is_sale_target": True,  "rights_value": 220000000, "consent": True},
    {"member_id": 1003, "address": "서울 영등포구 도림동 239-16", "birth_date": "1948-11-08", "is_sale_target": False, "rights_value": 145000000, "consent": False},
    {"member_id": 1004, "address": "서울 영등포구 도림동 240-1",  "birth_date": "1971-02-14", "is_sale_target": True,  "rights_value": 198000000, "consent": True},
    {"member_id": 1005, "address": "서울 영등포구 도림동 240-3",  "birth_date": "1965-09-30", "is_sale_target": True,  "rights_value": 175000000, "consent": False},
    {"member_id": 1006, "address": "서울 영등포구 도림동 241-2",  "birth_date": "1953-06-18", "is_sale_target": True,  "rights_value": 210000000, "consent": True},
    {"member_id": 1007, "address": "서울 영등포구 도림동 241-5",  "birth_date": "1978-12-25", "is_sale_target": False, "rights_value": 130000000, "consent": False},
    {"member_id": 1008, "address": "서울 영등포구 도림동 242-1",  "birth_date": "1960-04-11", "is_sale_target": True,  "rights_value": 195000000, "consent": True},
    {"member_id": 1009, "address": "서울 영등포구 도림동 242-3",  "birth_date": "1967-08-07", "is_sale_target": True,  "rights_value": 168000000, "consent": True},
    {"member_id": 1010, "address": "서울 영등포구 도림동 243-2",  "birth_date": "1982-01-19", "is_sale_target": True,  "rights_value": 205000000, "consent": False},
    {"member_id": 1011, "address": "서울 영등포구 도림동 243-4",  "birth_date": "1950-10-05", "is_sale_target": False, "rights_value": 155000000, "consent": True},
    {"member_id": 1012, "address": "서울 영등포구 도림동 244-1",  "birth_date": "1974-03-28", "is_sale_target": True,  "rights_value": 182000000, "consent": False},
    {"member_id": 1013, "address": "서울 영등포구 도림동 244-6",  "birth_date": "1958-07-14", "is_sale_target": True,  "rights_value": 225000000, "consent": True},
    {"member_id": 1014, "address": "서울 영등포구 도림동 245-3",  "birth_date": "1945-12-01", "is_sale_target": False, "rights_value": 140000000, "consent": False},
    {"member_id": 1015, "address": "서울 영등포구 도림동 245-7",  "birth_date": "1969-05-22", "is_sale_target": True,  "rights_value": 190000000, "consent": True},
    {"member_id": 1016, "address": "서울 영등포구 도림동 246-1",  "birth_date": "1973-09-16", "is_sale_target": True,  "rights_value": 178000000, "consent": True},
    {"member_id": 1017, "address": "서울 영등포구 도림동 246-4",  "birth_date": "1956-02-09", "is_sale_target": False, "rights_value": 160000000, "consent": False},
    {"member_id": 1018, "address": "서울 영등포구 도림동 247-2",  "birth_date": "1980-11-30", "is_sale_target": True,  "rights_value": 215000000, "consent": True},
    {"member_id": 1019, "address": "서울 영등포구 도림동 247-8",  "birth_date": "1963-06-25", "is_sale_target": True,  "rights_value": 172000000, "consent": False},
    {"member_id": 1020, "address": "서울 영등포구 도림동 248-1",  "birth_date": "1970-04-03", "is_sale_target": True,  "rights_value": 200000000, "consent": True},
]

df = pd.DataFrame(members)
df.to_excel(DATA_DIR / "members.xlsx", index=False)
print(f"[SUCCESS] members.xlsx created: {len(df)} members")
