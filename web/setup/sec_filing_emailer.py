import feedparser, arrow, os, sys, requests, re, math
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, Date
from json2html import *
from bs4 import BeautifulSoup
import numpy as np
import yfinance as yf
import pandas as pd
from util.util import util
from util.email import SendMail
from util.models import FilingText
import os
from tokenizer import split_into_sentences, correct_spaces
from joblib import dump, load
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

sections_map = {
    'daa': 'discussion_and_analysis',
    'rf': 'risk_factors',
    'qaq': 'quanitative_and_qualitative'
}

embedder = SentenceTransformer('/home/parrot/output/training_nli_vr25-fin_BERT-v1-2020-06-06_15-19-36')
#embedder = SentenceTransformer('/Users/cg/output/training_nli_vr25-fin_BERT-v1-2020-06-06_15-19-36')

keysToKeep = ['country', 'industry', 'regularMarketOpen', 'twoHundredDayAverage','averageDailyVolume10Day']

u = util()
companies_df = u.getNasdaqTraded()

engine = create_engine(os.environ['DB'], pool_recycle=600, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
session = Session()

def clean(s):
    s = s.replace('_', '')
    #s = s.replace('\x93', '')
    return s

def get_highlights(industry, symbol, sections_dict):
        industry_file = industry.replace(' ', '_')
        print("Getting highlights")
        print(industry)
        symbol = engine.execute(f"select symbol from yfinance_symbols where symbol='{symbol}' order by symbol;", con=engine)
        print(symbol)
        symbol = symbol.fetchall()[0][0]
        print(symbol)
        qaq_highlights = []
        daa_highlights = []
        rf_highlights = []
        for section in ['qaq', 'rf', 'daa']:
            print(section)
            query = f"select cluster_scores, base_good_to_bad from clusters_{section} where yfinance_industry='{industry}';"
            print(query)
            cluster = engine.execute(query, con=engine)
            print(cluster)
            c = cluster.fetchall()
            print(c)
            try:
                cluster_list = c[0][0]
            except Exception as e:
                print(e)
                continue
            print("cluster_list")
            x = [b['good_to_bad'] for b in cluster_list]
            a = np.array(x)
            good_cutoff = np.percentile(a, 90) # Change these around for more or less
            bad_cutoff = np.percentile(a, 10)
            good_indices = [l['index'] if l['good_to_bad'] > good_cutoff else None for l in cluster_list]
            bad_indices = [l['index'] if l['good_to_bad'] < bad_cutoff else None for l in cluster_list]
            cluster_model = load(f"/home/parrot/eclect.us/web/setup/models/{industry_file}_{section}.joblib")
            split_sents = []
            for sentence in split_into_sentences(sections_dict[section]):
                split_sents.append(correct_spaces(clean(sentence)))
            embedded_split_sents = embedder.encode(split_sents)
            predictions = cluster_model.predict(embedded_split_sents)
            highlights = []
            for sentence_i, clustering_index in enumerate(predictions):
                if clustering_index in good_indices:
                    highlights.append({ 'kmeans_i': int(clustering_index), 'sentence_i': int(sentence_i), 'sentence': split_sents[sentence_i], 'good_or_bad': 'good' })
                if clustering_index in bad_indices:
                    highlights.append({ 'kmeans_i': int(clustering_index), 'sentence_i': int(sentence_i), 'sentence': split_sents[sentence_i], 'good_or_bad': 'bad' })
            if section == 'qaq':
                qaq_highlights = highlights
            if section == 'rf':
                rf_highlights = highlights
            if section == 'daa':
                daa_highlights = highlights
        return qaq_highlights, rf_highlights, daa_highlights

yfinance_df = pd.read_sql_table("yfinance_symbols", engine)

names = [r.name for r in session.query(FilingText.name).order_by(FilingText.date.desc()).limit(500)]
formTypes = ['10-K', '10-Q']
url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=10-&company=&dateb=&owner=include&start=0&count=100&output=atom"
feed = feedparser.parse(url)
filing_list = []
company_names = []
for item in feed['items']:
    print("#" * 20)
    print(item['tags'][0]['term'])
    filename = re.findall(r"=([0-9\-]+)", item['id'])[0]
    filename = f"{filename}.txt"
    print(filename)
    if item['tags'][0]['term'] in formTypes and filename not in names:
        try:
            link = re.findall(r'(.+)-index', item['link'])
            link = link[0].strip()
            link = f"{link}.txt"
            cik = link.split("/")[6]
            print(cik)
            symbol = engine.execute(f"select yf.symbol, cik.yfinance_symbol_id, yf.industry, yf.marketcap from ciks cik, yfinance_symbols yf where cik.id = '{cik}' and yf.id = cik.yfinance_symbol_id;").fetchall()[0]
            if symbol is None:
                print("not found")
                continue
            print(symbol)
            print("#" * 20)
            #tick = yf.Ticker(symbol)
            try:
                if symbol[3] < 10000000:
                    print("under half billion")
                    continue
            except IndexError:
                print("yfinance data not found")
                print("under half billion most likely")
                continue
            print(f"{symbol} found, over half billion")
            df = pd.read_sql_table(symbol[0], engine)
            #df.set_index('Date', inplace=True)
            days = [5, 10, 20, 40, 60]
            for i in days:
                df[f"{i}_ma"] = df.iloc[:,4].rolling(window=i).mean()
                previous = df[f"{i}_ma"]
                df[f"percent_difference_from_{i}_ma"] = (df['close'] - df[f"{i}_ma"])/df[f"{i}_ma"]
                df.drop(columns=[f"{i}_ma"], inplace=True)
            print("sma created")
            text = u.getFiling(item['link'])
            soup = BeautifulSoup(text, 'lxml')
            m = re.findall(r"(<ACCEPTANCE-DATETIME>)([0-9]+)", text)            
            print(m)
            arrow_time = arrow.get(m[0][1], 'YYYYMMDDHHmmss')
            print(f"published {arrow_time.format()}")
            sma_diff_5_days = None
            sma_diff_10_days = None
            sma_diff_20_days = None
            sma_diff_40_days = None
            sma_diff_60_days = None
            price_change_5_days = None
            price_change_10_days = None
            price_change_20_days = None
            price_change_40_days = None
            price_change_60_days = None
            try:
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
                price_change_5_days = (df.iloc[[_5_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
                price_change_10_days = (df.iloc[[_10_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
                price_change_20_days = (df.iloc[[_20_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
                price_change_40_days = (df.iloc[[_40_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
                price_change_60_days = (df.iloc[[_60_days]]['close'].values[0] - current_row['close'].values[0])/current_row['close'].values[0]
            except Exception as ex:
                print("ohlc data not found")
                print(f"{type(ex).__name__} \n {ex.args}")

            t = re.findall(r"(CENTRAL INDEX KEY:)([^;]*?)([a-zA-Z])", text)
            cik = re.findall(r"[0-9]+", t[0][1])
            analysis, quant, risk = u.extractSections(text)
            sections_dict = {'qaq': quant, 'rf': risk, 'daa': analysis}
            print(symbol)
            qaq_highlights, rf_highlights, daa_highlights = get_highlights(symbol[2] ,symbol[0], sections_dict)

            print("tables extracted")
            filing = FilingText(
                yfinance_symbol_id=int(yfinance_df[yfinance_df['symbol'] == symbol[0]]['id'].values[0]),
                date= arrow_time.datetime,
                file_type=item['tags'][0]['term'],
                cik=cik[0],
                name=filename,
                discussion_and_analysis=analysis,
                quanitative_and_qualitative=quant,
                risk_factors=risk,
                qaq_highlights=qaq_highlights,
                rf_highlights=rf_highlights,
                daa_highlights=daa_highlights,
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
            session.add(filing)
            session.commit()
            print("committed")
            #### FOR EMAIL

            htmlTableJson = {}
            htmlTableJson['link'] = item['link']
            htmlTableJson['title'] = item['title']
            htmlTableJson['updated'] = item['updated']
            htmlTableJson['fileType'] = item['tags'][0]['term']
            htmlTableJson['market_cap'] = u.millify(symbol[3])
            htmlTableJson['symbol'] = symbol
            #for k in keysToKeep:
                #htmlTableJson[k] = tick.info[k]
            clean_rf_highlights = [rf['sentence'] for rf in rf_highlights]
            clean_daa_highlights = [daa['sentence'] for daa in daa_highlights]
            htmlTableJson['risk factors'] = clean_rf_highlights 
            htmlTableJson['discussion and analysis'] = clean_daa_highlights 
            content = json2html.convert(json=htmlTableJson)
            company_names.append(item['title'])
            filing_list.append(content)
        except Exception as ex:
            print('main')
            print(f"{type(ex).__name__} \n {ex.args}")
            session.rollback()
            
session.close()


if len(filing_list) > 0:
    SendMail().sendMail(filing_list, company_names)
else:
    print(filing_list)

