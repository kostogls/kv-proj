import os
import pandas as pd
import warnings
import io
import datetime
import json
import os 

buffer = io.StringIO()

DATETIMENOW = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
DATA_DIR = os.environ["DATA_DIR"]
NUM_STORES = 30
REPORT_DIR = os.environ["REPORT_DIR"]

# add the dataframes info and "exploration" into report text, and maybe add warnings if something is wrong?? ESPECIALLY IF PRIMARY KEY IS EMPTY or not unique
# check the final dfs before putting them in the db for info -- if there are nulls 



def save_df_info(df, dfname, de=None):
    """
    save some csv basic info in a report file
    :param: df: the dataframe given to save its info
    :param: dfname: dataframe's name to save it in the report
    :param: de: save date info as well if they exist in the df
    """ 
    
    report_name = f'report{DATETIMENOW}.txt'

    df.info(buf=buffer)
    s = buffer.getvalue()
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

    with open(REPORT_DIR+report_name, "a", encoding="utf-8") as f:
        f.write(f"INFO for df: {dfname} loaded at {DATETIMENOW}")
        f.write(s)
        if de:
            f.write(de)
        f.write('\n\n-----------------------------------------\n\n')


def keep_unique_plans(file_prefix='plan_digest'):
    """
    :param file_prefixes: gets the repeating pattern of the file and read all the files starting with that prefix
    We need to read the digest files first, to remove any files that correspond to same plan periods but where
    extracted earlier in the process and save I/O cost. 
    :returns: un_pl: list with the unique pids of plans
    :returns: len(un_pl): how many unique pids there are
    :returns: plans_df: the result df for plan digest info
    """
    df = pd.DataFrame()
    files = [file for file in os.listdir(DATA_DIR) if file.startswith(file_prefix)]
    for file_name in files:
        file_path = os.path.join(DATA_DIR, file_name)
        with open(file_path, 'r') as file:

            content = pd.read_csv(file, names=['pid', 'timestamp', 'start_date', 'end_date', 'plan_descr'])
            
            df = pd.concat([df, content])

    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H%M%S')

    # Identify rows with duplicated values in plan_descr
    duplicates_mask = df.duplicated(subset=['plan_descr'], keep=False)

    non_duplicates_df = df[~duplicates_mask]
    duplicates_df = df[duplicates_mask].sort_values(by='timestamp', ascending=False)
    duplicates_df = duplicates_df.drop_duplicates(subset=['plan_descr'],keep='first')

    plans_df = pd.concat([non_duplicates_df, duplicates_df])
    plans_df['start_date'] = pd.to_datetime(plans_df['start_date'], format='%Y%m%d')
    plans_df['end_date'] = pd.to_datetime(plans_df['end_date'], format='%Y%m%d')

    save_df_info(plans_df, file_prefix)
    un_pl = list(plans_df.iloc[:,0])
    return un_pl, len(un_pl), plans_df


def generate_dates(row):
    # function to take a df row and generate all the dates in day frequency between two given dates (start - and date) 
    return pd.date_range(start=row['start_date'], end=row['end_date'], freq='D')


def generate_pid_dates(df):
    # function to generate a dataframe that has the pid and all the dates that exist between this plan's start and end date
    df_ = df.copy()
    df_['start_date'] = pd.to_datetime(df['start_date'], format='%Y%m%d')
    df_['end_date'] = pd.to_datetime(df['end_date'], format='%Y%m%d')

    df_['date'] = [pd.date_range(s, e, freq='d') for s, e in
                zip(pd.to_datetime(df['start_date']),
                    pd.to_datetime(df['end_date']))]

    result_df = df_.explode('date').drop(['start_date', 'end_date'], axis=1)
    result_df = result_df[['pid', 'date']]
    return result_df


def dates_exploration(df):
    # function to explore basic information about dates in a given df that contains such data types
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

    # Check the date range
    min_date = df['date'].min()
    max_date = df['date'].max()

    expected_dates = pd.date_range(start=min_date, end=max_date, freq='D').astype(str)
    missing_dates = expected_dates[~expected_dates.isin(df['date'])]
    
    duplicates_count = df.duplicated('date').sum()
    
    message = f"min_date: {min_date}, max_date: {max_date}, missing_dates: {missing_dates}, duplicates_count: {duplicates_count}" 
    return message

def load_forecast():
    # load the forecast csv data 
    filename = 'forecast.csv'
    df = pd.read_csv(DATA_DIR+filename, names=['date', 'item_id', 'store_id', 'forecast'])
    de = dates_exploration(df)
    save_df_info(df, filename, de)
    return df

def load_sales():
    # load the sales csv data 
    filename = 'sales.csv'
    df = pd.read_csv(DATA_DIR+filename, names=['date', 'item_id', 'store_id', 'sales'])
    de = dates_exploration(df)
    save_df_info(df, filename, de)
    return df

def merge_plan_files(unique_plans, name_prefix):
    """merge files that contain their pids in their names by reading all the csv with the corresponding unique plan in their names
    :param unique_plans: the unique_plans pid 
    :param name_prefix: the name of the given file before the pid (e.g. clusters, plan_sales)
    :returns: result df
    """
    df_list = []
    for plan in unique_plans:
        filename = name_prefix+plan+'.csv'
        file_path = os.path.join(DATA_DIR, filename)
        if 'sales' in filename:
            headers = ['pid', 'date', 'item_id', 'store_id', 'planned_sales']
        else:
            headers = ['pid', 'store_id', 'cluster_id', 'cluster_descr']
        df = pd.read_csv(file_path, names=headers)
        df_list.append(df)
    df = pd.concat(df_list, ignore_index=True)

    return df


def load_plan_sales(unique_plans):
    # load the sales csv data and merge all the unique plans together

    name_prefix = 'plan_sales_'
    df = merge_plan_files(unique_plans,name_prefix)
    # check basic info for the dataset
    # print(df.info())
    # print(df.describe())
    de = dates_exploration(df)
    save_df_info(df, name_prefix, de)

    return df


def load_clusters(unique_plans, num_un_pl):
    """
    load the clusters csv data and merge all the unique plans together
    :param: unique_plans: take the list with the unique pids
    :param: num_un_pl counter of how many unique plans exist in current data 
    :returns: result df 
    """
    name_prefix = 'plan_clusters_'
    df = merge_plan_files(unique_plans,name_prefix)

    # print(df.info())
    # print(df.describe())

    # one store appears one time in one pid
    if df.groupby(['pid', 'store_id']).ngroups != num_un_pl * NUM_STORES:
        warnings.warn('stores missing?')
    return df 

