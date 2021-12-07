from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData, Table, Date, Text, JSON, Numeric, ForeignKey, DateTime, Float
from sqlalchemy import create_engine
import datetime
import os

level = os.getenv('LEVEL') 

engine = create_engine(os.environ['DB'])

Base = declarative_base()
meta = MetaData()
meta.bind = engine
yfinance_symbols = Table('yfinance_symbols', meta, autoload=True, autoload_with=engine)

class CIKs(Base):
    __tablename__ = 'ciks'
    id = Column(String, primary_key=True)
    symbol = Column('symbol', String) 
    yfinance_symbol_id = Column('yfinance_symbol_id', Integer, ForeignKey(yfinance_symbols.c.id))
    
class FilingText(Base):
    __tablename__ = 'filing_texts'
    id = Column(Integer, primary_key=True)
    yfinance_symbol_id = Column('yfinance_symbol_id' ,Integer, ForeignKey(yfinance_symbols.c.id))
    date = Column('date', Date)
    file_type = Column('file_type', String)
    cik = Column('cik', String)
    name = Column('name', String, unique=True)
    discussion_and_analysis = Column('discussion_and_analysis', Text)
    quanitative_and_qualitative = Column('quanitative_and_qualitative', Text)
    risk_factors = Column('risk_factors', Text)
    daa_highlights = Column('daa_highlights', JSON, nullable=True)
    qaq_highlights = Column('qaq_highlights', JSON, nullable=True)
    rf_highlights = Column('rf_highlights', JSON, nullable=True)
    #financial_tables = Column('financial_tables', JSON)
    price_change_5_days = Column('price_change_5_days', Numeric(asdecimal=True, precision=10, scale=8), nullable=True)
    price_change_10_days = Column('price_change_10_days', Numeric(asdecimal=True, precision=10, scale=8), nullable=True)
    price_change_20_days = Column('price_change_20_days', Numeric(asdecimal=True, precision=10, scale=8), nullable=True)
    price_change_40_days = Column('price_change_40_days', Numeric(asdecimal=True, precision=10, scale=8), nullable=True)
    price_change_60_days = Column('price_change_60_days', Numeric(asdecimal=True, precision=10, scale=8), nullable=True)
    sma_diff_5_days = Column('sma_diff_5_days', Numeric(asdecimal=True, precision=10, scale=8), nullable=True)
    sma_diff_10_days = Column('sma_diff_10_days', Numeric(asdecimal=True, precision=10, scale=8), nullable=True)
    sma_diff_20_days = Column('sma_diff_20_days', Numeric(asdecimal=True, precision=10, scale=8), nullable=True)
    sma_diff_40_days = Column('sma_diff_40_days', Numeric(asdecimal=True, precision=10, scale=8), nullable=True)
    sma_diff_60_days = Column('sma_diff_60_days', Numeric(asdecimal=True, precision=10, scale=8), nullable=True)

class Clusters(Base):
    __tablename__ = 'clusters'
    id = Column(Integer, primary_key=True)
    yfinance_industry = Column('yfinance_industry', String)
    created = Column('created', Date, default=datetime.datetime.utcnow())
    cluster_scores = Column('cluster_scores', JSON)
    cluster_sents = Column('cluster_sents', JSON)
    cluster_centers = Column('cluster_centers', JSON)
    base_good_to_bad = Column('base_good_to_bad', Float)

class ClustersDaa(Base):
    __tablename__ = 'clusters_daa'
    id = Column(Integer, primary_key=True)
    yfinance_industry = Column('yfinance_industry', String)
    created = Column('created', Date, default=datetime.datetime.utcnow())
    cluster_scores = Column('cluster_scores', JSON)
    cluster_sents = Column('cluster_sents', JSON)
    cluster_centers = Column('cluster_centers', JSON)
    base_good_to_bad = Column('base_good_to_bad', Float)

class ClustersQaq(Base):
    __tablename__ = 'clusters_qaq'
    id = Column(Integer, primary_key=True)
    yfinance_industry = Column('yfinance_industry', String)
    created = Column('created', Date, default=datetime.datetime.utcnow())
    cluster_scores = Column('cluster_scores', JSON)
    cluster_sents = Column('cluster_sents', JSON)
    cluster_centers = Column('cluster_centers', JSON)
    base_good_to_bad = Column('base_good_to_bad', Float)

class ClustersRf(Base):
    __tablename__ = 'clusters_rf'
    id = Column(Integer, primary_key=True)
    yfinance_industry = Column('yfinance_industry', String)
    created = Column('created', Date, default=datetime.datetime.utcnow())
    cluster_scores = Column('cluster_scores', JSON)
    cluster_sents = Column('cluster_sents', JSON)
    cluster_centers = Column('cluster_centers', JSON)
    base_good_to_bad = Column('base_good_to_bad', Float)


Base.metadata.create_all(engine)
