from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sec_edgar_downloader import Downloader
from util.util import util
import pandas as pd
from util.models import FilingText
import arrow, os
u = util()
import os, re, shutil, sys
from bs4 import BeautifulSoup

print('Symbol to start on', str(sys.argv[1]))

level = os.getenv('LEVEL') 

#shutil.rmtree("./sec_edgar_filings")

#re.split(r'(?<=\.) ', text)

#TODO grab results from that api and put them in their own tables, match them with filings
#TODO NOW, finish this script get price 1,2,4,8,12 weeks from filing. Beggining on trading hours after published.
# Finish model file create table in DB

engine = create_engine(os.environ['DB'])
Session = sessionmaker(engine)
session = Session()
path = "."
dl = Downloader(path)

tickers = pd.read_sql_table('yfinance_symbols', con=engine)

try:
    tickers = tickers[(tickers.loc[tickers['symbol'] == str(sys.argv[1])].index[0]+1):]
except:
    print("no ticker to start on provided")
    pass
for index, row in tickers.iterrows():
    try:
        filing_texts_exists = engine.execute(f"select exists (select * from filing_texts where yfinance_symbol_id = {row['id']});").fetchall()
        if filing_texts_exists[0][0]:
            print(row['symbol'], "exists")
            continue
        print(f"Downloading {row['symbol']}")
        dl.get("10-K", row['symbol'], after_date="20150725")
        dl.get("10-Q", row['symbol'], after_date="20150725")
        print(f"Downloaded {row['symbol']}")
        kPath = f"{path}/sec_edgar_filings/{row['symbol']}/10-K"
        qPath = f"{path}/sec_edgar_filings/{row['symbol']}/10-Q"
        df = pd.read_sql_table(f"{row['symbol']}", engine)
        #df.set_index('Date', inplace=True)
        days = [5, 10, 20, 40, 60]
        for i in days:
            df[f"{i}_ma"] = df.iloc[:,4].rolling(window=i).mean()
            previous = df[f"{i}_ma"]
            df[f"percent_difference_from_{i}_ma"] = (df['close'] - df[f"{i}_ma"])/df[f"{i}_ma"]
            df.drop(columns=[f"{i}_ma"], inplace=True)

        if os.path.isdir(kPath):
            for filename in os.listdir(kPath):
                file = open(f"{kPath}/{filename}", "r")
                text = file.read()
                soup = BeautifulSoup(text, 'lxml')
                m = re.findall(r"(<ACCEPTANCE-DATETIME>)([0-9]+)", text)            
                arrow_time = time = arrow.get(m[0][1], 'YYYYMMDDHHmmss')
                print(row['symbol'])
                print(filename)
                print(kPath)
                print(arrow_time.format('YYYY-MM-DD'))
                print(df.columns)
                if int(arrow_time.format('HHmm')) <= 930:
                    _index = df[df['date'] == arrow_time.format('YYYY-MM-DD')].index[0] # trend we're in i.e. sma, and future prices diff
                    current_row = df.iloc[[_index]]
                else:
                    _index = df[df['date'] == arrow_time.format('YYYY-MM-DD')].index[0] + 1
                    current_row = df.iloc[[_index]]
                _5_days = _index + 5
                _10_days = _index + 10
                _20_days = _index + 20
                _40_days = _index + 40
                _60_days = _index + 60
                sma_diff_5_days = current_row["percent_difference_from_5_ma"].values[0]
                sma_diff_10_days = current_row["percent_difference_from_10_ma"].values[0]
                sma_diff_20_days = current_row["percent_difference_from_20_ma"].values[0]
                sma_diff_40_days = current_row["percent_difference_from_40_ma"].values[0]
                sma_diff_60_days = current_row["percent_difference_from_60_ma"].values[0]
                price_change_5_days = None
                price_change_10_days = None
                price_change_20_days = None
                price_change_40_days = None
                price_change_60_days = None
                try:
                    price_change_5_days = (df.iloc[[_5_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
                    price_change_10_days = (df.iloc[[_10_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
                    price_change_20_days = (df.iloc[[_20_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
                    price_change_40_days = (df.iloc[[_40_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
                    price_change_60_days = (df.iloc[[_60_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
                except Exception as ex:
                    print(f"{type(ex).__name__} \n {ex.args}")

                t = re.findall(r"(CENTRAL INDEX KEY:)([^;]*?)([a-zA-Z])", text)
                cik = re.findall(r"[0-9]+", t[0][1])
                print("extracting sections")
                analysis, quant, risk = u.extractSections(text)
                print("done")
                filing = FilingText(
                    yfinance_symbol_id=row['id'],
                    date= arrow_time.datetime,
                    file_type='10-k',
                    cik=cik[0],
                    name=filename,
                    discussion_and_analysis=analysis,
                    quanitative_and_qualitative=quant,
                    risk_factors=risk,
                    price_change_5_days=price_change_5_days,
                    price_change_10_days=price_change_10_days,
                    price_change_20_days=price_change_20_days,
                    price_change_40_days=price_change_40_days,
                    price_change_60_days=price_change_60_days,
                    sma_diff_5_days=sma_diff_5_days,
                    sma_diff_10_days=sma_diff_10_days,
                    sma_diff_20_days=sma_diff_20_days,
                    sma_diff_40_days=sma_diff_40_days,
                    sma_diff_60_days=sma_diff_60_days,
                )
                print("session commit")
                session.add(filing)
                session.commit()
                file.close()
                print("session committed")
        if os.path.isdir(qPath):
            for filename in os.listdir(qPath):
                file = open(f"{qPath}/{filename}", "r")
                text = file.read()
                soup = BeautifulSoup(text, 'lxml')
                m = re.findall(r"(<ACCEPTANCE-DATETIME>)([0-9]+)", text)            
                arrow_time = time = arrow.get(m[0][1], 'YYYYMMDDHHmmss')
                print(row['symbol'])
                print(filename)
                print(qPath)
                print(arrow_time.format('YYYY-MM-DD'))
                print(df.columns)
                if int(arrow_time.format('HHmm')) <= 930:
                    _index = df[df['date'] == arrow_time.format('YYYY-MM-DD')].index[0] # trend we're in i.e. sma, and future prices diff
                    current_row = df.iloc[[_index]]
                else:
                    _index = df[df['date'] == arrow_time.format('YYYY-MM-DD')].index[0] + 1
                    current_row = df.iloc[[_index]]
                _5_days = _index + 5
                _10_days = _index + 10
                _20_days = _index + 20
                _40_days = _index + 40
                _60_days = _index + 60
                sma_diff_5_days = current_row["percent_difference_from_5_ma"].values[0]
                sma_diff_10_days = current_row["percent_difference_from_10_ma"].values[0]
                sma_diff_20_days = current_row["percent_difference_from_20_ma"].values[0]
                sma_diff_40_days = current_row["percent_difference_from_40_ma"].values[0]
                sma_diff_60_days = current_row["percent_difference_from_60_ma"].values[0]
                price_change_5_days = None
                price_change_10_days = None
                price_change_20_days = None
                price_change_40_days = None
                price_change_60_days = None
                try:
                    price_change_5_days = (df.iloc[[_5_days]]['Close'].values[0] - current_row['Close'].values[0])/current_row['Close'].values[0]
                    price_change_10_days = (df.iloc[[_10_days]]['Close'].values[0] - current_row['Close'].values[0])/current_row['Close'].values[0]
                    price_change_20_days = (df.iloc[[_20_days]]['Close'].values[0] - current_row['Close'].values[0])/current_row['Close'].values[0]
                    price_change_40_days = (df.iloc[[_40_days]]['Close'].values[0] - current_row['Close'].values[0])/current_row['Close'].values[0]
                    price_change_60_days = (df.iloc[[_60_days]]['Close'].values[0] - current_row['Close'].values[0])/current_row['Close'].values[0]
                except Exception as ex:
                    print(f"{type(ex).__name__} \n {ex.args}")
                t = re.findall(r"(CENTRAL INDEX KEY:)([^;]*?)([a-zA-Z])", text)
                cik = re.findall(r"[0-9]+", t[0][1])
                print("extracting sections")
                analysis, quant, risk = u.extractSections(text)
                print("done")
                filing = FilingText(
                    yfinance_symbol_id=row['id'],
                    date= arrow_time.datetime,
                    file_type='10-q',
                    cik=cik[0],
                    name=filename,
                    discussion_and_analysis=analysis,
                    quanitative_and_qualitative=quant,
                    risk_factors=risk,
                    price_change_5_days=price_change_5_days,
                    price_change_10_days=price_change_10_days,
                    price_change_20_days=price_change_20_days,
                    price_change_40_days=price_change_40_days,
                    price_change_60_days=price_change_60_days,
                    sma_diff_5_days=sma_diff_5_days,
                    sma_diff_10_days=sma_diff_10_days,
                    sma_diff_20_days=sma_diff_20_days,
                    sma_diff_40_days=sma_diff_40_days,
                    sma_diff_60_days=sma_diff_60_days,
                )
                print("session commit")
                session.add(filing)
                session.commit()
                file.close()
                print("session committed")

            if os.path.isdir("./sec_edgar_filings"):
                shutil.rmtree("./sec_edgar_filings")
    except Exception as ex:
        print("#" * 20)
        try:
            if file:
                print("closing file")
                file.close()
        except Exception as e_e:
            print("file close fail")
        if os.path.isdir("./sec_edgar_filings"):
            shutil.rmtree("./sec_edgar_filings")
        print(f"{row['symbol']}")
        print(f"{type(ex).__name__} \n {ex.args}")
        session.rollback()
        print("#" * 20)
