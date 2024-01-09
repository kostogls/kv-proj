from .queries import define_queries
from .db_connection import connect_sqla
from sqlalchemy import text, exc
from pandas import DataFrame
import datetime
import logging
import os

engine = connect_sqla()
connection = engine.connect()

DATETIMENOW = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

LOG_NAME = f'executed_query_{DATETIMENOW}.log'

LOG_DIR = os.environ['LOG_DIR']

ENGINE = connect_sqla()

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(filename=LOG_DIR+LOG_NAME,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')


def run_queries():
    # take the queries dictionary, iterate it and try to execute the queries. instead log the error.
    queries_dict = define_queries()
    dict_of_results = {}

    for qn, query in queries_dict.items():
        try:
            res = connection.execute(text(query))
            dict_of_results[qn] = DataFrame(res.fetchall())
            dict_of_results[qn].columns = res.keys()
        except exc.ResourceClosedError as e:
            logging.warning(f'/n/n Error in query {qn}. Detailed error: {e} /n/n')

            continue
        


    # for qn, df in dict_of_results.items():
    #     print(df)
    return dict_of_results
