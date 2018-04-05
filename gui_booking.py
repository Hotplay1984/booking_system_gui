import sys
import datetime as dt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pandas as pd
from time import sleep
import dm

class Deal_Bottler(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.Sql_Conn = dm.Sql_Con()

        self.combo_side = QComboBox()
        self.line_code = QLineEdit()
        self.combo_name = QComboBox()
        self.spin_amt = QSpinBox()
        self.line_trade_price = QLineEdit()
        self.combo_portfolio = QComboBox()
        self.datedit_trade = QDateEdit()

        self.line_value = QLineEdit()
        self.line_id = QLineEdit()
        self.table_history = QTableWidget()
        self.status = QStatusBar()
        self.bt_update = QPushButton('Add Trade')

        self.df_basic_info = pd.DataFrame()
        self.df_trade_history = pd.DataFrame()
        self.df_update_info = pd.DataFrame()
        self.dict_name = {}
        self.portfolios = ['ptf001', ]

        self.weigit_setting()
        self.layout()

    def weigit_setting(self):
        self.status.showMessage('就绪')

        self.line_code.setEnabled(False)
        self.combo_name.setEditable(True)
        self.combo_name.currentIndexChanged.connect(self.search_code)

        self.datedit_trade.setDate(QDate.currentDate())
        self.combo_portfolio.addItems(self.portfolios)
        self.combo_side.addItems(['B', 'S'])

        self.spin_amt.setSingleStep(100)
        self.spin_amt.setMaximum(1000000)
        self.spin_amt.setMinimum(0)
        self.spin_amt.setValue(0)
        self.spin_amt.valueChanged.connect(self.calc_trade_value)

        self.line_value.setEnabled(False)
        self.line_id.setEnabled(False)

        self.bt_update.clicked.connect(self.add_trade)

        return

    def initialize(self):
        self.df_basic_info = self.Sql_Conn.get_basic_info()
        self.df_trade_history = self.Sql_Conn.get_trade_history()
        self.dict_name = {name:code for name, code in zip(self.df_basic_info['name'],
                                                          self.df_basic_info['code'])}
        self.combo_name.addItems(self.df_basic_info['name'].tolist())
        self.line_id.setText('')
        self.line_value.setText('')
        self.spin_amt.setValue(0)
        self.line_trade_price.setText('0')
        self.write_table()

        return

    def write_table(self):
        df = self.df_trade_history
        table = self.table_history
        table.clear()
        table.setRowCount(len(df))
        table.setColumnCount(len(df.columns.tolist()))
        table.setHorizontalHeaderLabels(df.columns.tolist())
        for col_n in range(table.columnCount()):
            for row_n in range(table.rowCount()):
                value = df.at[row_n, df.columns.tolist()[col_n]]
                table.setItem(row_n,
                              col_n,
                              QTableWidgetItem(str(value)))

    def search_code(self):
        name = self.combo_name.currentText()
        code = self.dict_name[name]
        self.line_code.setText(code)
        self.make_id()

    def calc_trade_value(self):
        amt = int(self.spin_amt.value())
        price = float(self.line_trade_price.text())
        value = amt * price
        self.line_value.setText(str(value))

    def make_id(self):
        current_date = dt.datetime.now().strftime('%Y%m%d')
        code = self.line_code.text()
        df = self.df_trade_history[self.df_trade_history['code']==code]
        try:
            df = df[df['trade_date']==current_date]
            num = len(df) + 1
        except:
            num = 1
        num_str = '0' + str(num) if num < 10 else str(num)
        id_str = current_date + code + num_str
        self.line_id.setText(id_str)

    def add_trade(self):
        trade_id = self.line_id.text()
        name = self.combo_name.currentText()
        code = self.line_code.text()
        amt = int(self.spin_amt.value())
        portfolio = self.combo_portfolio.currentText()
        side = self.combo_side.currentText()

        if side == 'S':
            if name not in self.df_trade_history['name'].tolist():
                self.status.showMessage('库存中没有这只股票')
                sleep(2)
                self.status.showMessage('就绪')
                return
            else:
                amt = -1 * amt

        try:
            trade_price = float(self.line_trade_price.text())
        except:
            self.status.showMessage('无效价格')
            sleep(2)
            self.status.showMessage('就绪')
        if len(str(trade_price)) > 0 and amt != 0:
            trade_date = self.datedit_trade.date().toString('yyyyMMdd')
            time_stp = dt.datetime.now()
            value_list = [trade_id, name, code, amt, trade_price,
                          trade_date, time_stp, portfolio, side]
            columns = self.df_trade_history.columns.tolist()
            df_tmp = pd.DataFrame([value_list], columns=columns)
            self.status.showMessage('传输中...')
            df_tmp.to_sql('trade_history',
                         self.Sql_Conn.engine,
                         schema='equity',
                         if_exists='append',
                         index=False)
            self.initialize()
            self.status.showMessage('就绪')
        else:
            self.status.showMessage('无效价格或数量')
            sleep(2)
            self.status.showMessage('就绪')


    def layout(self):

        main_frame = QFrame()
        main_form = QFormLayout()
        main_form.addRow('股票名称：', self.combo_name)
        main_form.addRow('股票代码：', self.line_code)
        main_form.addRow('买入/卖出：', self.combo_side)
        main_form.addRow('交易价格：', self.line_trade_price)
        main_form.addRow('数量：', self.spin_amt)
        main_form.addRow('交易日期：', self.datedit_trade)
        main_form.addRow('', QFrame())
        main_form.addRow('交易金额：', self.line_value)
        main_form.addRow('交易ID：', self.line_id)
        main_form.addWidget(self.bt_update)
        main_form.addRow(self.status)
        up_layout = QHBoxLayout()
        up_layout.addLayout(main_form)
        up_layout.addWidget(QFrame())
        main_frame.setLayout(up_layout)
        main_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)

        table_frame = QFrame()
        table_layout = QHBoxLayout()
        table_layout.addWidget(self.table_history)
        table_frame.setLayout(table_layout)
        table_frame.setFrameStyle(QFrame.Sunken|QFrame.StyledPanel)

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_frame)
        main_layout.addWidget(table_frame)
        self.setLayout(main_layout)

        self.initialize()

        return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Deal_Bottler()
    ex.show()
    sys.exit(app.exec_())