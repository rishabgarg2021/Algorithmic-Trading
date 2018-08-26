from fmclient import Agent
from fmclient import Order, OrderType, OrderSide, Holding

class Bot(Agent):



    def __init__(self, account, email, password, marketplace_id):
        name = "Simple_Bot"
        super().__init__(account,email,password,marketplace_id,name=name)
        self.description = "A bot learning to interact!"
        self._market_id = 539


    def initialised(self):
        pass

    def order_accepted(self, order):
        pass

    def order_rejected(self, info, order):
        pass

    def received_order_book(self, order_book, market_id):
        print("hehrhrhe")
        print(self._market_id)
        orders_count = 0
        for order in order_book:
            if order.mine:
                orders_count += 1
        if orders_count < 2:
            my_buy_order = Order(100, 1, OrderType.LIMIT, OrderSide.BUY, 539, ref="b1")
            print("my buy order is ",my_buy_order)

            self.send_order(my_buy_order)
        pass

    def received_completed_orders(self, orders, market_id=None):
        pass

    def received_holdings(self, holdings):
        pass


    def received_marketplace_info(self, marketplace_info):
        session_id= marketplace_info['session_id']
        if marketplace_info['status']:
            print("market place is active with session id = " + str(session_id))
        else:
            print("market is closed right now")

    def run(self):
        self.initialise()
        self.start()



if __name__ == "__main__":
    marketplace_id = 260
    fm_bot = Bot("bullish-delight", "r.garg2@student.unimelb.edu.au", "796799", marketplace_id)
    fm_bot.run()