from fastapi import FastAPI
import math
import os
from sqlalchemy import create_engine
from typing import Dict
from sqlalchemy.orm import sessionmaker
from pprint import pprint
from fastapi.middleware.cors import CORSMiddleware


origins = [
    "https://eclect.us"
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

millnames = ['',' Thousand',' Million',' Billion',' Trillion'] 

engine = create_engine(os.environ['DB'], pool_recycle=600, pool_pre_ping=True)
Session = sessionmaker(engine)
session = Session()


@app.get("/supported-symbols")
def get_symbols() -> Dict:
    """
        returns all supported symbols with filing texts in the form:
        [
            { 'value': 'AAPL', 'label': 'AAPL, Apple inc.' },
            { 'value': 'AA', 'label': 'AA, American Airlines inc.' },
             ...
        ]
    """
    supported_symbols = []
    symbols = engine.execute('select symbol, shortname from supported_symbols;').fetchall()
    for symbol in symbols:
        supported_symbols.append({'value': symbol[0], 'label': f"{symbol[0]}, {symbol[1]}"})
    return supported_symbols

@app.get("/recents")
def get_recents( page: int = 1) -> Dict:
    """
        returns filing texts in the form:
        [  
          {
            "symbol": "BEN",
            "industry": "Asset Management",
            "country": "United States",
            "marketcap": "9 Billion",
            "shortname": "Franklin Resources, Inc.",
            "name": "0000038777-20-000138.txt",
            "date": "2020-07-28",
            "file_type": "10-Q",
            "daa_highlights": [
                {
                    "kmeans_i": 10,
                    "sentence_i": 159,
                    "sentence": "Impairments of intangible assets related to previous acquisitions decreased $9.3 million and $6.5 million for the three and nine months ended June 30, 2020.",
                    "good_or_bad": "bad"
                },
                {
                    "kmeans_i": 55,
                    "sentence_i": 31,
                    "sentence": "Our total AUM at June 30, 2020 was $622.8 billion, 10% lower than at September 30, 2019 and 13% lower than at June 30, 2019.",
                    "good_or_bad": "bad"
                }, ...
            ],
            "rf_highlights": [
                {
                    "kmeans_i": 43,
                    "sentence_i": 2,
                    "sentence": "Our Form 10 ‑ K for the fiscal year ended September 30, 2019 filed with the SEC includes a discussion of the risk factors identified by us, which are also included under the heading“ Risk Factors” in Item 2 of Part I of this Form 10-Q. Other than the risk factors set forth under the heading“ Important Additional Risks” in the Risk Factors in Item 2 of Part I of this Form 10-Q, which are incorporated herein by reference, there were no material changes from the Risk Factors as previously disclosed in our Form 10 ‑ K for the fiscal year ended September 30, 2019.",
                    "good_or_bad": "good"
                }
            ],
            "price_change_40_days": null
          },
           ...
        ]
    """
    
    filing_texts = []
    page = page - 1
    offset = page * 10
    try:
        filing_texts = engine.execute(f"select yf.symbol, yf.industry, yf.country, yf.marketcap,\
            yf.shortname, ft.name, ft.date, ft.cik, ft.file_type, ft.daa_highlights,\
            ft.rf_highlights,ft.price_change_5_days, ft.price_change_10_days, ft.price_change_20_days, ft.price_change_40_days\
                from yfinance_symbols yf, filing_texts ft where ft.yfinance_symbol_id = yf.id and (ft.daa_highlights is not null or ft.rf_highlights is not null)\
                    order by ft.date desc limit 10 offset {offset};").fetchall()
    except Exception as ex:
        print("symbols error")
        print(f"{type(ex).__name__} \n {ex.args}")
        return []
    result_list = add_to_output_highlights(filing_texts, [], [], False)
    return result_list

@app.get("/symbol/{symbol}")
def get_filings_for_symbol(symbol: str, page: int = 1) -> Dict:
    """
        returns filing texts in the form:
        [  
          {
            "symbol": "BEN",
            "industry": "Asset Management",
            "country": "United States",
            "marketcap": "9 Billion",
            "shortname": "Franklin Resources, Inc.",
            "name": "0000038777-20-000138.txt",
            "date": "2020-07-28",
            "file_type": "10-Q",
            "daa_highlights": [
                {
                    "kmeans_i": 10,
                    "sentence_i": 159,
                    "sentence": "Impairments of intangible assets related to previous acquisitions decreased $9.3 million and $6.5 million for the three and nine months ended June 30, 2020.",
                    "good_or_bad": "bad"
                },
                {
                    "kmeans_i": 55,
                    "sentence_i": 31,
                    "sentence": "Our total AUM at June 30, 2020 was $622.8 billion, 10% lower than at September 30, 2019 and 13% lower than at June 30, 2019.",
                    "good_or_bad": "bad"
                }, ...
            ],
            "rf_highlights": [
                {
                    "kmeans_i": 43,
                    "sentence_i": 2,
                    "sentence": "Our Form 10 ‑ K for the fiscal year ended September 30, 2019 filed with the SEC includes a discussion of the risk factors identified by us, which are also included under the heading“ Risk Factors” in Item 2 of Part I of this Form 10-Q. Other than the risk factors set forth under the heading“ Important Additional Risks” in the Risk Factors in Item 2 of Part I of this Form 10-Q, which are incorporated herein by reference, there were no material changes from the Risk Factors as previously disclosed in our Form 10 ‑ K for the fiscal year ended September 30, 2019.",
                    "good_or_bad": "good"
                }
            ],
            "price_change_40_days": null
          },
           ...
        ]
    """
    filing_texts = []
    page = page - 1
    offset = page * 40
    symbol = symbol.upper()
    try:
        filing_texts = engine.execute(f"select yf.symbol, yf.industry, yf.country, yf.marketcap,\
            yf.shortname, ft.name, ft.date, ft.file_type, ft.cik, ft.daa_highlights,\
            ft.rf_highlights, ft.price_change_5_days, ft.price_change_10_days, ft.price_change_20_days, ft.price_change_40_days\
                from yfinance_symbols yf, filing_texts ft where ft.yfinance_symbol_id = yf.id\
                    and yf.symbol='{symbol}' order by ft.date desc limit 10 offset {offset};").fetchall()
        industry = filing_texts[0]['industry']
        try:
            cluster_scores_daa = engine.execute(f"select cluster_scores from clusters_daa where yfinance_industry='{industry}'").fetchall()[0][0]
        except IndexError:
            cluster_scores_daa = []
        try:
            cluster_scores_rf = engine.execute(f"select cluster_scores from clusters_rf where yfinance_industry='{industry}'").fetchall()[0][0]
        except IndexError:
            cluster_scores_rf = []
    except Exception as ex:
        print(f"{type(ex).__name__} \n {ex.args}")
        return []
    result_list = add_to_output_highlights(filing_texts, cluster_scores_daa, cluster_scores_rf)
    return result_list

def millify(n):
    try:
        n = float(n)
        millidx = max(0,min(len(millnames)-1, int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
        return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
    except Exception as e_e:
        print('millify')
        print(e_e)

def add_to_output_highlights(filing_texts: list = [], cluster_scores_daa: list = [], cluster_scores_rf: list = [], include_empties: bool = True):
    result_list = []
    for filing_text in filing_texts:
        result = dict(filing_text)
        result['marketcap'] = millify(result['marketcap'])
        name = result['name'].replace(".txt", "")
        cik = result['cik'].lstrip("0")
        result['original_filing_link'] = f'https://www.sec.gov/Archives/edgar/data/{cik.lstrip("0")}/{name}/{name}-index.htm'
        result['financials_link'] = f'https://www.sec.gov/cgi-bin/viewer?action=view&cik={cik}&accession_number={name}&xbrl_type=v#'
        if include_empties == False:
            try:
                cluster_scores_daa = engine.execute(f"select cluster_scores from clusters_daa where yfinance_industry='{filing_text['industry']}'").fetchall()[0][0]
            except IndexError:
                cluster_scores_daa = []
            try:
                cluster_scores_rf = engine.execute(f"select cluster_scores from clusters_rf where yfinance_industry='{filing_text['industry']}'").fetchall()[0][0]
            except IndexError:
                cluster_scores_rf = []
        result['daa_highlights'] = filter_highlights('daa_highlights', cluster_scores_daa, result)
        result['rf_highlights'] = filter_highlights('rf_highlights', cluster_scores_rf, result)
        if include_empties:
            result_list.append(result)
        if (len(result['daa_highlights']) > 0 or len(result['rf_highlights']) > 0) and include_empties == False:
            result_list.append(result)
    return result_list

def filter_highlights(highlights_type: str, cluster_scores, result):
    top_start = 0
    bottom_start = -1
    highlights = []
    full_highlights = result.get(highlights_type)
    while full_highlights and len(highlights) <= 10 and top_start < len(full_highlights): #cluster scores are already sorted from good to bad
        top = cluster_scores[top_start]['index']
        bottom = cluster_scores[bottom_start]['index']
        for sentence in full_highlights:
            if sentence['kmeans_i'] in [top, bottom] and len(sentence['sentence'].split()) > 8:
                highlights.append(sentence)
        top_start += 1
        bottom_start -= 1
    return highlights
