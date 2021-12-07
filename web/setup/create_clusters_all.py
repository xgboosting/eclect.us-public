from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sec_edgar_downloader import Downloader
import pandas as pd
from tokenizer import split_into_sentences, correct_spaces
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from tokenizer import split_into_sentences, correct_spaces
import re, sys, os
from joblib import dump, load
from util.models import Clusters
from datetime import datetime
from pytz import timezone  

us = timezone('US/Pacific')

def clean(s):
    s = s.replace('_', '')
    return s


embedder = SentenceTransformer('/home/parrot/output/training_nli_vr25-fin_BERT-v1-2020-06-06_15-19-36')
#embedder = SentenceTransformer('/Users/cg/output/training_nli_vr25-fin_BERT-v1-2020-06-06_15-19-36')


my_engine = create_engine(os.environ['SECOND_DB'], pool_recycle=600, pool_pre_ping=True)
engine = create_engine(os.environ['DB'], pool_recycle=600, pool_pre_ping=True)
Session = sessionmaker(engine)
session = Session()

try:
    sql_string = f"select ft.price_change_40_days, ft.discussion_and_analysis from filing_texts ft, yfinance_symbols ys where ft.yfinance_symbol_id = ys.id order by ys.industry;"
    print(sql_string, datetime.now(us))
    df = pd.read_sql(sql_string, con=my_engine)
    print("df read", datetime.now(us))
    df = df[df['discussion_and_analysis'] != 'NO_MATCH']
    df.dropna(subset=['price_change_40_days'], inplace=True)
    good_df = df[df['price_change_40_days'] > 0.0]
    bad_df = df[df['price_change_40_days'] < 0.0]
    good_corpus = []
    for index, row in good_df.iterrows():
        for sentence in split_into_sentences(row['discussion_and_analysis']):
            good_corpus.append(correct_spaces(clean(sentence)))
    bad_corpus = []
    for index, row in bad_df.iterrows():
        for sentence in split_into_sentences(row['discussion_and_analysis']):
            bad_corpus.append(correct_spaces(clean(sentence)))
    good_corpus = list(dict.fromkeys(good_corpus))
    bad_corpus = list(dict.fromkeys(bad_corpus))

    corpus = good_corpus + bad_corpus
    good_to_bad = len(good_corpus) / len(bad_corpus)
    print("embedding", datetime.now(us))
    corpus_embeddings = embedder.encode(corpus)
    print("embedding done", datetime.now(us))


# Perform kmean clustering
    num_clusters = 1000
    print("clustering", datetime.now(us))
    clustering_model = KMeans(n_clusters=num_clusters)
    clustering_model.fit(corpus_embeddings)
    cluster_assignment = clustering_model.labels_
    print("clustered", datetime.now(us))

    clustered_sentences = [[] for i in range(num_clusters)]
    for sentence_id, cluster_id in enumerate(cluster_assignment):
        clustered_sentences[cluster_id].append(corpus[sentence_id])
    
    cluster_scores = []
    for i, cluster in enumerate(clustered_sentences):
        g = 0
        b = 0
        sents = []
        for a in cluster:
            sents.append(a)
            if a in good_corpus:
                g += 1
            if a in bad_corpus:
                b += 1
        try:
            g_to_b = g/b
        except:
            g_to_b = good_to_bad
        cluster_scores.append({ 'good_to_bad': g_to_b, 'index': i })
    cluster_scores = sorted(cluster_scores, key=lambda item: item['good_to_bad'])

    print("commiting", datetime.now(us))
    cluster_to_commit = Clusters(
        yfinance_industry = 'all',
        cluster_scores = cluster_scores,
        cluster_sents = [],
        cluster_centers = clustering_model.cluster_centers_.tolist(),
        base_good_to_bad = good_to_bad,
                )
    print("session committing", datetime.now(us))
    try:
        session.add(cluster_to_commit)
        print("added")
        session.commit()
        dump(clustering_model, "../models/all.joblib")
        print("committed")
    except Exception as ex:
        print(f"{type(ex).__name__} \n {ex.args}")
        print("session problem")
        session.rollback()
except Exception as ex:
    print('main')
    print(f"{type(ex).__name__} \n {ex.args}")
