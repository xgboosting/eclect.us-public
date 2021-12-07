import pandas as pd
import yfinance as yf
import time, os
from util.util import util
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pprint import pprint

engine = create_engine(os.environ['DB'], pool_recycle=600, pool_pre_ping=True)
symbols = engine.execute("select symbol from yfinance_symbols;").fetchall()
supported_columns = engine.execute("SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'yfinance_symbols';").fetchall()
supported_columns = [c[0] for c in supported_columns]
symbols = [s[0] for s in symbols]
Session = sessionmaker(engine)
session = Session()

u = util()
stonks = u.getNasdaqTraded()

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

for index, row in stonks.iterrows():
    try:
        if row['Symbol'] in symbols:
            print('symbol in symbols')
            continue
        time.sleep(1)
        tick = yf.Ticker(row['Symbol'])
        tickDict = {}
        print("here")
        for key, value in tick.info.items():
            if hasNumbers(key) == False and tick.info['industry'] and key.lower() in supported_columns:
                tickDict[key.lower()] = [value]
        print("after tick industry")
        print("second here") 
        df1 = pd.DataFrame.from_dict(tickDict)
        df1.to_sql('yfinance_symbols', con=engine, if_exists='append')
        print(row['Symbol'])
        print("saved")
    except Exception as e_e:
        print('Main except')
        print(e_e)

session.commit()
#session.execute("ALTER TABLE yfinance_symbols ADD COLUMN ID SERIAL PRIMARY KEY;")
#session.commit()



tickers = pd.read_sql_table('yfinance_symbols', con=engine)
for index, row in tickers.iterrows():
    try:
        exists = engine.execute(f"select exists (select from information_schema.tables where table_name='{row['symbol']}');").fetchall()
        if exists[0][0]:
            print("table exists", row['symbol'])
            continue
        df = yf.download(
            tickers = f"{row['symbol']}",
            period = "10y", # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            interval = "1d",  # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            group_by = 'ticker',
            auto_adjust = True,
            prepost = False,
            threads = True,
            proxy = None
        )
        time.sleep(1)
        df.columns = map(str.lower, df.columns)
        df.index.name = 'date'
        df.to_sql(f"{row['symbol']}", engine)
    except Exception as e_e:
        print(e_e)


