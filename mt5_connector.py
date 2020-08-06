import MetaTrader5 as mt5


class mt5_connector:

    def __init__(self, server, login, password, path, timedelta=3):

        self.server = server
        self.login = login
        self.password = password
        self.path = path
        self.timedelta = timedelta

        if not mt5.initialize(path=self.path, server=self.server, login=self.login, password=self.password):
            print("initialize() failed")
            return None
        mt5.shutdown()
        print(self.server, "initialize() success")

        self.symbols = {}
        symbols = self.perform_action(mt5.symbols_get)
        for each_symbol in symbols:
            symbol = each_symbol._asdict()
            sym_name = symbol['name']
            self.symbols[sym_name] = symbol

    def __enter__(self):
        """
        Открываем подключение к терминалу
        """
        # подключимся к MetaTrader 5
        if not mt5.initialize(path=self.path, server=self.server, login=self.login, password=self.password):
            print("initialize() failed")
            mt5.shutdown()

    def get_symbol_info(self, symbol):
        selected = self.perform_action(mt5.symbol_select, symbol)
        if not selected:
            print("Failed to select ", symbol, " on ", self.server)
        symbol_info = self.perform_action(mt5.symbol_info, symbol)
        if symbol_info == None:
            print(symbol, " info returned none from ", self.server, " connector")
        else:
            return symbol_info

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Закрываем подключение.
        """
        mt5.shutdown()
        if exc_val:
            raise ()

    def perform_action(self, func, *args, **kwargs):
        with self:
            return (func(*args, **kwargs))

    def mt5_action(fn):
        def wrapped(self, *args, **kwargs):
            if not mt5.initialize(path=self.path, server=self.server, login=self.login, password=self.password):
                print("initialize() failed")
                mt5.shutdown()
            return fn(self, *args, **kwargs)
            mt5.shutdown()

        return wrapped

    def get_positions(self, symbol):
        positions = self.perform_action(mt5.positions_get, symbol=symbol)
        if positions != None:
            return positions
        else:
            return ()

    def close_position(self, position, filltype=None):

        symbol = position.symbol
        position_id = position.ticket
        lot = position.volume

        if position.type == mt5.ORDER_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = self.get_tick(position.symbol).bid
        elif position.type == mt5.ORDER_TYPE_SELL:
            order_type = mt5.ORDER_TYPE_BUY
            price = self.get_tick(position.symbol).ask
        else:
            return

        filldict = {
            1: mt5.ORDER_FILLING_FOK,
            2: mt5.ORDER_FILLING_IOC,
            3: mt5.ORDER_FILLING_RETURN
        }

        if filltype is None:
            filltype = filldict[self.symbols[symbol]["filling_mode"]]

        deviation = 1

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "position": position_id,
            "deviation": deviation,
            #            "magic": 4577,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filltype
        }
        return self.order_send(request)

    def open_position(self, side, symbol, filltype=None, lot=0.01, magic=4577):

        if side == "BUY":
            order_type = mt5.ORDER_TYPE_BUY
            price = self.get_tick(symbol).ask
        elif side == "SELL":
            order_type = mt5.ORDER_TYPE_SELL
            price = self.get_tick(symbol).bid
        else:
            return

        filldict = {
            1: mt5.ORDER_FILLING_FOK,
            2: mt5.ORDER_FILLING_IOC,
            3: mt5.ORDER_FILLING_RETURN
        }

        if filltype is None:
            filltype = filldict[self.symbols[symbol]["filling_mode"]]

        deviation = 1

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "deviation": deviation,
            "magic": magic,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filltype
        }
        return self.order_send(request)

    @mt5_action
    def order_send(self, request):

        result = mt5.order_send(request)
        return result

    def get_tick(self, symbol):
        return self.perform_action(mt5.symbol_info_tick, symbol)