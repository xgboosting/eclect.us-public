from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sec_edgar_downloader import Downloader
import pandas as pd
from tokenizer import split_into_sentences, correct_spaces
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from tokenizer import split_into_sentences, correct_spaces
import re, sys, os
import numpy as np
from pprint import pprint
from json import dumps, loads
from joblib import dump, load
import time
from util.models import ClustersDaa, ClustersRf, ClustersQaq, FilingText

embedder = SentenceTransformer('/home/parrot/output/training_nli_vr25-fin_BERT-v1-2020-06-06_15-19-36')
#embedder = SentenceTransformer('/home/c/output/training_nli_vr25-fin_BERT-v1-2020-06-06_15-19-36')


engine = create_engine(os.environ['DB'], pool_recycle=600, pool_pre_ping=True)
Session = sessionmaker(engine)
session = Session()

columns_map = {
    'daa': "daa_highlights",
    'rf': "rf_highlights",
    'qaq': "qaq_highlights" 
}

sections_map = {
    'daa': 'discussion_and_analysis',
    'rf': 'risk_factors',
    'qaq': 'quanitative_and_qualitative'
}

models_map = {
    'daa': ClustersDaa,
    'rf': ClustersRf,
    'qaq': ClustersQaq 
}

tickers = pd.read_sql('select distinct industry from yfinance_symbols order by industry;', con=engine)

try:
    industry_to_start = str(sys.argv[1])
    print('Industry to start on', industry_to_start)
    tickers = tickers[(tickers.loc[tickers['industry'] == industry_to_start].index[0]):]
except:
    print("no start industry provided")

def clean(s):
    s = s.replace('_', '')
    #s = s.replace('\x93', '')
    return s

for index, row in tickers.iterrows():
    industry = row['industry']
    industry_file = industry.replace(' ', '_')
    print(industry)
    for section in ['qaq', 'rf', 'daa']:
        print(section)
        query = f"select cluster_scores, base_good_to_bad from clusters_{section} where yfinance_industry='{industry}';"
        cluster = engine.execute(query, con=engine)
        c = cluster.fetchall()
        try:
            cluster_list = c[0][0]
        except:
            print(industry)
            print(section)
            print("cluster does not exist")
        x = [b['good_to_bad'] for b in cluster_list]
        a = np.array(x)
        good_cutoff = np.percentile(a, 90) # Change these around for more or less
        bad_cutoff = np.percentile(a, 10)
        good_indices = [l['index'] if l['good_to_bad'] > good_cutoff else None for l in cluster_list]
        bad_indices = [l['index'] if l['good_to_bad'] < bad_cutoff else None for l in cluster_list]
        symbol_query = f"select symbol from yfinance_symbols where industry='{industry}' order by symbol;"
        print(symbol_query)
        symbols = engine.execute(symbol_query, con=engine)
        symbols = symbols.fetchall()
        try:
            cluster_model = load(f"/home/parrot/eclect.us/web/setup/models/{industry_file}_{section}.joblib")
        except:
            continue
        #cluster_model = load(f"/home/c/eclect.us/web/setup/models/{industry_file}_{section}.joblib")
        for s in symbols:
            ticker = s[0]
            print(ticker)
            corpus = pd.read_sql(f"select ft.id, ft.price_change_40_days, yf.symbol, ft.date, ft.{sections_map[section]}, ft.name from yfinance_symbols yf, filing_texts ft where yf.id=ft.yfinance_symbol_id and yf.symbol='{ticker}' and ft.{sections_map[section]} != 'NO_MATCH' order by ft.date;", con=engine)
            #print(f"select ft.id, ft.price_change_40_days, yf.symbol, ft.date, ft.{sections_map[section]}, ft.name from yfinance_symbols yf, filing_texts ft where yf.id=ft.yfinance_symbol_id and yf.symbol='{ticker}' order by ft.date;")
            for corpus_index, corpus_row in corpus.iterrows():
                split_sents = []
                for sentence in split_into_sentences(corpus_row[sections_map[section]]):
                    split_sents.append(correct_spaces(clean(sentence)))
                embedded_split_sents = embedder.encode(split_sents)
                print(len(embedded_split_sents))
                try:
                    predictions = cluster_model.predict(embedded_split_sents)
                except:
                    print("no predictions")
                    predictions = []
                highlights = []
                for sentence_i, clustering_index in enumerate(predictions):
                    if clustering_index in good_indices:
                        highlights.append({ 'kmeans_i': int(clustering_index), 'sentence_i': int(sentence_i), 'sentence': split_sents[sentence_i], 'good_or_bad': 'good' })
                    if clustering_index in bad_indices:
                        highlights.append({ 'kmeans_i': int(clustering_index), 'sentence_i': int(sentence_i), 'sentence': split_sents[sentence_i], 'good_or_bad': 'bad' })
                session.query(FilingText).filter(FilingText.id==corpus_row['id']).update({ columns_map[section]: highlights })
                session.commit()
                print("session commited")
