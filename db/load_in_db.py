from app_files.data_check import *
from .db_connection import connect_sqla
import logging
from sqlalchemy import exc
import psycopg2
import datetime
import os

DATETIMENOW = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

LOG_NAME = f'data_insertion_{DATETIMENOW}.log'

LOG_DIR = os.environ['LOG_DIR']

ENGINE = connect_sqla()

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(filename=LOG_DIR+LOG_NAME,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')


def insert_in_table(df, table_name):
    # try to insert in given table the corrsponding data, catch any error the sql alchemy may throw, 
    try:
        df.to_sql(table_name, ENGINE, if_exists='append', index=False, method='multi')
    except exc.IntegrityError as e:
        logging.warning(f'/n/n Error in inserting db for table {table_name}. Detailed error: {e} /n/n')
        print("Duplicate data not inserted.: ")


def get_current_tables_data():
    # get all current csv read in data_check.py and map them to their corresponding tables
    unique_plans, num_un_pl, plandig_df = keep_unique_plans()
    datesdf = generate_pid_dates(plandig_df)
    cldf = load_clusters(unique_plans, num_un_pl)
    psdf = load_plan_sales(unique_plans)
    sdf = load_sales()
    fdf = load_forecast()

    mappings = {'plandigest': plandig_df, 'plandate': datesdf, 'plancluster': cldf, 'plansales': psdf, 'sales': sdf, 'forecast': fdf}
    return mappings


def insert_current_tables(mappings):
    # insert all the data in their corresponding tables
    for table_name, table_data in mappings.items():
        insert_in_table(table_data, table_name)
    


