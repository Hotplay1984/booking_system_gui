import pandas as pd
import tushare as ts
import datetime as dt
from sql_conn import *
from pytz import timezone
from pandas.tseries.offsets import Day

source_db = 'postgresql'
username = 'postgres'
pwd = 'sunweiyao'
ip = '119.28.222.122'
port = 5432
db = 'quant'
engine = sql_engine(source_db=source_db,
                    username=username,
                    pwd=pwd,
                    ip=ip,
                    port=port,
                    db=db)

class Sql_Con():
    def __init__(self):
        source_db = 'postgresql'
        username = 'postgres'
        pwd = 'sunweiyao'
        ip = '119.28.222.122'
        port = 5432
        db = 'quant'
        self.engine = sql_engine(source_db=source_db,
                                username=username,
                                pwd=pwd,
                                ip=ip,
                                port=port,
                                db=db)

    def get_basic_info(self):
        sql_info = '''
        select code, name 
        from equity.stock_basic_info 
        '''
        return pd.read_sql_query(sql_info, self.engine)

    def get_trade_history(self):
        sql_trade = '''
        select *
        from equity.trade_history
        order by trade_date desc, time_stp desc 
        '''
        return pd.read_sql_query(sql_trade, self.engine)

