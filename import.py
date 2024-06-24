import os
import requests
import pandas as pd
import polars as pl
from db import DB


def banks() -> pl.DataFrame:
    url: str | None = os.environ.get("BANKS_URL", None)
    if url:
        resp = requests.get(url)
        df = pd.read_xml(resp.content, encoding="windows-1251", parser="etree")
        df.columns = ["id", "date_started", "short_name", "bik"]
    return pl.from_pandas(df)


def mcc() -> pl.DataFrame:
    df = pd.read_excel("downloads/mcc_codes.xlsx")
    df.columns = ["code", "descr", "full_descr"]
    df = pl.from_pandas(df).select(pl.col("code").cast(pl.Int32), pl.col("descr"))
    return df


db = DB()

banks_df = banks()
mcc_df = mcc()
db.insert(table="banks", df=banks_df)
db.insert(table="mcc", df=mcc_df)
