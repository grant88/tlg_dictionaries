import os
import pandas as pd
import polars as pl

class DB:
    def __init__(self) -> None:

        self.host = os.environ.get("DB_HOST", "localhost")
        self.port = os.environ.get("DB_PORT", "5432")
        self.dbname = os.environ.get("DB_NAME", "mydb")
        self.user = os.environ.get("DB_USER", "myuser")
        self.password = os.environ.get("DB_PASS", None)
        if self.password:
            self.uri = self.make_conn_uri()
            self.connection_string = self.make_conn_string()

    def make_conn_string(self) -> str:
        return f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password}"

    def make_conn_uri(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"

    def select(self, sql: str) -> pl.DataFrame:
        df = pl.read_database_uri(query=sql, uri=self.uri)
        return df
    
    def insert(self, table: str, df: pl.DataFrame, schema: str = "public") -> None:
        uri = self.uri
        if schema != "schema":
            uri += f"?currentSchema={schema}"
        df.write_database(table_name=table, connection=self.uri)
        return df