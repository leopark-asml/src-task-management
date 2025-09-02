
from fastapi import FastAPI
import pyodbc
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

def get_connection():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

@app.get("/")
def root():
    return {"message": "API 서버 정상 작동 중"}

@app.get("/data")
def get_data():
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT TOP 10 * FROM your_table", conn)  # 실제 테이블 이름으로 변경
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}
