import urllib.request
from sqlalchemy import create_engine
import os
engine = create_engine(os.environ['DB'], pool_recycle=600, pool_pre_ping=True)


urllib.request.urlretrieve("https://www.sec.gov/include/ticker.txt", './ciks.txt')
ciks = open('./ciks.txt', 'r')


for line in ciks:
    print(line)
    line = line.split("\t")
    symbol = line[0].upper()
    cik = line[1].strip("\n")
    try:
        symbol_id = engine.execute(f"select id, symbol from yfinance_symbols where symbol = '{symbol}';").fetchall()[0][0]
    except:
        print("no symbol")
        continue
    try:
        engine.execute(f"insert into ciks (id, symbol, yfinance_symbol_id) values ('{cik}', '{symbol}', {symbol_id});")
    except:
        print("exists")
    print("inserted")
