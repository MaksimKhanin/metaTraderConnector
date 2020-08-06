# metaTraderConnector
The base connector to MetaTrader Terminal based on the terminal's python API. This the base class that will be used in creation new trading bots

Usage:

my_terminal = mt5_connector(server='MyBrokerOrDealerServer',
                             login=40927195,
                             password='pdfpfdpdf',
                             path="C:/metatrader/terminal64.exe",
                             timedelta=3)
                             
my_terminal.open_position("BUY", "EURUSD", filltype=1, lot=0.01, magic=4577)
last_positions = my_terminal.get_positions("EURUSD")[0]
my_terminal.close_position(last_positions, filltype=1)


