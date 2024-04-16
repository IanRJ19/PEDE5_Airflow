
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:dwh@localhost:3306/dwh")
connection = engine.connect()


with engine.begin() as connection:
    base = pd.read_sql_query(f"SELECT * FROM Base_Consolidada", con=connection)
    base.to_sql(name='TABLA_INFO', con=connection, if_exists='append', index=False)

