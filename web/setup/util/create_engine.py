from sqlalchemy import create_engine
db_string = "postgresql+psycopg2://eclectus:eclectus@localhost:5432/eclectus"
db = create_engine(db_string)
db.execute("CREATE TABLE IF NOT EXISTS films (title text, director text, year text)")