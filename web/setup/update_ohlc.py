from util.util import util
import pandas as pd
import yfinance as yf
import time, os, sys
import arrow
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


level = os.getenv('LEVEL') 

engine = create_engine(os.environ['DB'])
Session = sessionmaker(engine)
session = Session()

u = util()

tickers = pd.read_sql_table('yfinance_symbols', con=engine)

try:
    tickers = tickers[(tickers.loc[tickers['symbol'] == str(sys.argv[1])].index[0]+1):]
except:
    print("no ticker to start on provided")
    pass

for index, row in tickers.iterrows():
    try:
        time.sleep(1)
        current_tick_df = pd.read_sql_table(f"{row['symbol']}", con=engine)
        last_date_in_data = current_tick_df.iloc[-1]
        print(last_date_in_data['date'])
        print(row['symbol'])
        print(index)
        day = arrow.get(last_date_in_data['date']).format('YYYY-MM-DD')
        df = yf.download(
            tickers = f"{row['symbol']}",
            period = "6mo", # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            interval = "1d",  # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            group_by = 'ticker',
            auto_adjust = True,
            prepost = False,
            threads = True,
            proxy = None
        )
        
        df.reset_index(inplace=True)
        df.rename(str.lower, axis='columns', inplace=True)
        print("oi")
        df = df[(df.loc[df['date'] == day].index[0]+1):]
        print("oi")
        df.set_index('date', inplace=True)
        df.to_sql(f"{row['symbol']}", engine, if_exists='append')
        time.sleep(1)
    except Exception as ex:
        print(f"{type(ex).__name__} \n {ex.args}")
