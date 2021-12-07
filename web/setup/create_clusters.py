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
from util.models import ClustersDaa, ClustersQaq, ClustersRf

def clean(s):
    s = s.replace('_', '')
    return s


embedder = SentenceTransformer('/home/parrot/output/training_nli_vr25-fin_BERT-v1-2020-06-06_15-19-36')
#embedder = SentenceTransformer('/Users/cg/output/training_nli_vr25-fin_BERT-v1-2020-06-06_15-19-36')


engine = create_engine(os.environ['DB'], pool_recycle=600, pool_pre_ping=True)
Session = sessionmaker(engine)
session = Session()

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
    section = str(sys.argv[1])
    print('section', section)
    if section not in ['daa', 'qaq', 'rf']:
        print("section prob")
        quit()
    industry_to_start = str(sys.argv[2])
    print('Industry to start on', industry_to_start)
    tickers = tickers[(tickers.loc[tickers['industry'] == industry_to_start].index[0]):]
except:
    print("no start industry provided")

for index, row in tickers.iterrows():
    try:
        print(row['industry'])
        exists = engine.execute(f"select exists (select * from clusters_daa where yfinance_industry={row['industry']});").fetchall()
        if exists[0][0]:
            continue
        industry = row['industry']
        sql_string = f"select ft.price_change_40_days, ft.{sections_map[section]} from filing_texts ft, yfinance_symbols ys where ft.yfinance_symbol_id = ys.id and ys.industry='{row['industry']}' order by ys.industry;"
        print(sql_string)
        df = pd.read_sql(sql_string, con=engine)
        df = df[df[sections_map[section]] != 'NO_MATCH']
        df.dropna(subset=['price_change_40_days'], inplace=True)
        good_df = df[df['price_change_40_days'] > 0.00]
        bad_df = df[df['price_change_40_days'] < 0.00]
        good_corpus = []
        for index, row in good_df.iterrows():
            for sentence in split_into_sentences(row[sections_map[section]]):
                good_corpus.append(correct_spaces(clean(sentence)))
        bad_corpus = []
        for index, row in bad_df.iterrows():
            for sentence in split_into_sentences(row[sections_map[section]]):
                bad_corpus.append(correct_spaces(clean(sentence)))
        good_corpus = list(dict.fromkeys(good_corpus))
        bad_corpus = list(dict.fromkeys(bad_corpus))

        corpus = good_corpus + bad_corpus
        good_to_bad = len(good_corpus) / len(bad_corpus)
        corpus_embeddings = embedder.encode(corpus)

    # Perform kmean clustering
        num_clusters = 100
        print("clustering")
        clustering_model = KMeans(n_clusters=num_clusters)
        clustering_model.fit(corpus_embeddings)
        cluster_assignment = clustering_model.labels_
        print("clustered")

        clustered_sentences = [[] for i in range(num_clusters)]
        for sentence_id, cluster_id in enumerate(cluster_assignment):
            clustered_sentences[cluster_id].append(corpus[sentence_id])
    
        cluster_scores = []
        cluster_sents = []
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
            cluster_sents.append({ 'good_to_bad': g_to_b, 'sents': sents, 'index': i })
            cluster_scores.append({ 'good_to_bad': g_to_b, 'index': i })
        cluster_sents = sorted(cluster_sents, key=lambda item: item['good_to_bad'])
        cluster_scores = sorted(cluster_scores, key=lambda item: item['good_to_bad'])

        cluster_to_commit = models_map[section](
            yfinance_industry = industry,
            cluster_scores = cluster_scores,
            cluster_sents = cluster_sents,
            cluster_centers = clustering_model.cluster_centers_.tolist(),
            base_good_to_bad = good_to_bad,
                    )
        print("session committing")
        industry_file = industry.replace(' ', '_')
        try:
            session.add(cluster_to_commit)
            print("added")
            session.commit()
            dump(clustering_model, f"./models/{industry_file}_{section}.joblib")
            print("committed")
        except Exception as ex:
            print(f"{type(ex).__name__} \n {ex.args}")
            print("session problem")
            session.rollback()
            break
    except Exception as ex:
        print('main')
        print(f"{type(ex).__name__} \n {ex.args}")
