import os
import requests
import pandas as pd
import polars as pl
from db import DB

url = os.environ.get("BANKS_URL", None)
resp = requests.get(url)
df = pd.read_xml(resp.content, encoding='windows-1251', parser='etree')

print(len(df))

pl_df = pl.from_pandas(df)

db = DB()

db.insert(table='banks', df=pl_df)
