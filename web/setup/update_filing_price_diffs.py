from util.util import util
import pandas as pd
import yfinance as yf
import time, os
from util.models import FilingText
import arrow
from sqlalchemy import create_engine 
from sqlalchemy import or_
from sqlalchemy.orm import sessionmaker

level = os.getenv('LEVEL') 

engine = create_engine(os.environ['DB'], pool_recycle=600, pool_pre_ping=True)
Session = sessionmaker(engine)
session = Session()

yfinance_df = pd.read_sql_table("yfinance_symbols", engine)

u = util()

filing_texts = session.query(FilingText).filter(or_(FilingText.sma_diff_5_days==None, FilingText.sma_diff_10_days==None, FilingText.sma_diff_20_days==None,
 FilingText.sma_diff_40_days==None, FilingText.sma_diff_60_days==None, FilingText.price_change_5_days==None, FilingText.price_change_10_days==None,
 FilingText.price_change_20_days==None, FilingText.price_change_40_days==None, FilingText.price_change_60_days==None)).all()


for f in filing_texts:
    try:
        symbol = yfinance_df[yfinance_df['id'] == f.yfinance_symbol_id]['symbol'].values[0]
        df = pd.read_sql_table(f"{symbol}", engine)
        days = [5, 10, 20, 40, 60]
        for i in days:
            df[f"{i}_ma"] = df.iloc[:,4].rolling(window=i).mean()
            previous = df[f"{i}_ma"]
            df[f"percent_difference_from_{i}_ma"] = (df['close'] - df[f"{i}_ma"])/df[f"{i}_ma"]
            df.drop(columns=[f"{i}_ma"], inplace=True)
    except Exception as e:
        print("problem getting ohlc data")
    f.sma_diff_5_days = None
    f.sma_diff_10_days = None
    f.sma_diff_20_days = None
    f.sma_diff_40_days = None
    f.sma_diff_60_days = None
    f.price_change_5_days = None
    f.price_change_10_days = None
    f.price_change_20_days = None
    f.price_change_40_days = None
    f.price_change_60_days = None
    try:
        _index = df[df['date'] == str(f.date)].index[0] # trend we're in i.e. sma, and future prices diff
        current_row = df.iloc[[_index]]
    except Exception as ex:
        print(df['date'])
        print("date index probbbblleeemmmm")
        print(f"{type(ex).__name__} \n {ex.args}")
        continue
    try:
        _5_days = _index + 5
        _10_days = _index + 10
        _20_days = _index + 20
        _40_days = _index + 40
        _60_days = _index + 60
        f.sma_diff_5_days = current_row["percent_difference_from_5_ma"].values[0]
        f.sma_diff_10_days = current_row["percent_difference_from_10_ma"].values[0]
        f.sma_diff_20_days = current_row["percent_difference_from_20_ma"].values[0]
        f.sma_diff_40_days = current_row["percent_difference_from_40_ma"].values[0]
        f.sma_diff_60_days = current_row["percent_difference_from_60_ma"].values[0]
        f.price_change_5_days = (df.iloc[[_5_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
        f.price_change_10_days = (df.iloc[[_10_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
        f.price_change_20_days = (df.iloc[[_20_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
        f.price_change_40_days = (df.iloc[[_40_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
        f.price_change_60_days = (df.iloc[[_60_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
    except Exception as ex:
        print(f.date)
        print(f.price_change_5_days)
        print("ohlc data not found")
        print(f"{type(ex).__name__} \n {ex.args}")
    try:
        session.commit()
        print("session committed")
    except Exception as e:
        print("commit problem")
        session.rollback()

session.close()
    
