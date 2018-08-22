"""
This is a template for Project 1, Task 1 (Induced demand-supply)
"""
import copy
from enum import Enum

import sys
from fmclient import Agent, OrderSide, Order, OrderType

# Group details
GROUP_MEMBERS = {"796799": "Rishab Garg", "831865": "Kevin Xu", "834063" : "Austen McClernon"}


# ------ Add a variable called DS_REWARD_CHARGE -----
DS_REWARD_CHARGE = 600




# Enum for the roles of the bot
class Role(Enum):
    BUYER = 0,
    SELLER = 1


# Let us define another enumeration to deal with the type of bot
class BotType(Enum):
    MARKET_MAKER = 0,
    REACTIVE = 1


class DSBot(Agent):
    # ------ Add an extra argument bot_type to the constructor -----
    def __init__(self, account, email, password, marketplace_id, bot_type):

        name = "H1Bot"
        super().__init__(account, email, password, marketplace_id,name)
        self._market_id = -1

        # It can be either Buyer or seller depending on cash or assets availaible at start
        self._role = None
        self.MAXIMUM = 10001
        self.MINIMUM= -1
        self._trade_opportunity = {"buy":{},"sell":{}}

        # Robot type can be either Market_Maker or Reactive.
        self._bot_type = bot_type
        self._waiting_for_server=False
    
    def role(self):
        return self._role

    def initialised(self):

        cash_info = self.holdings["cash"]["cash"]
        #self.holdings is a dictionary {cash:{'cash':,'available_cash':},markets:{id:{'units':,'ava_units:}}}
        ##will get the information from market id.
        asset_info = None
        for market_id, market_holding in self.holdings["markets"].items():
            self._market_id = market_id
            asset_info = market_holding["units"]

        if cash_info >0 :
            self._role = Role.BUYER

        if asset_info > 0:
            self._role  = Role.SELLER

        self.inform("my bot has a role of" + str(self._role))




    def order_accepted(self, order):
        self._waiting_for_server = False
        self.inform("my order ",order._id, " has accepted")
        print("my order ",order._id, " has accepted")

        pass

    def order_rejected(self, info, order):
        self._waiting_for_server = False
        self.inform("my order ",order._id, " has rejected")
        print("my order ",order._id, " has rejected")


        pass

    def received_order_book(self, order_book, market_id):

        print("id of market is ",self._market_id)
        id_order=[]

        #markert id: order object reference, type, Mine, Buy or Sell , Unit with price.
        for order  in order_book:
            id_order.append(order._id)
            if not order.mine:
                if(order._side == OrderSide.BUY):

                    if( order._id not  in  self._trade_opportunity['buy'].keys()):
                        self._trade_opportunity['buy'][order._id] = copy.deepcopy(order)

                if (order._side == OrderSide.SELL):

                    if ( order._id  not in self._trade_opportunity['sell'].keys()):
                        self._trade_opportunity['sell'][order._id] = copy.deepcopy(order)

        for id in self._trade_opportunity['buy'].keys():

            if id not in id_order:
                self._trade_opportunity['buy'].pop(id,None)

        for id in self._trade_opportunity['sell'].keys():
            if id not in id_order:
                self._trade_opportunity['sell'].pop(id,None)

     # self._print_trade_opportunity(order_book)
        print("buy orders are :" ,self._trade_opportunity['buy'])
        print("sell orders are :" ,self._trade_opportunity['sell'])

        self._reactive(order_book)


        pass
    def _reactive(self,other_order):
        
        
        print("cash with us is ", self.holdings['cash']['available_cash'])
        min_order_price = self.MAXIMUM
        place_buy_order = False

        for order in other_order:
            if(order.mine and order.side == OrderSide.Buy):
                place_buy_order = True

        print("value is  is " ,self._role.value)
        if( self._role.value == (0,)):
            for (id,order) in self._trade_opportunity['sell'].items():
                if(order._price < min_order_price):
                    min_order_price = order._price
            if(min_order_price !=self.MAXIMUM and  not self._waiting_for_server and not place_buy_order and self.holdings['cash']['available_cash'] >= min_order_price and DS_REWARD_CHARGE >= min_order_price):
                place_buy_order = Order(min_order_price,
                                1,OrderType.LIMIT,OrderSide.BUY,self._market_id,ref="b1")
                self.send_order(place_buy_order)
                print("place this order ",place_buy_order)
                self._waiting_for_server = True



        max_order_price = self.MINIMUM
        place_sell_order = False
        for order in other_order:
            if (order.mine and order.side == OrderSide.SELL):
                place_sell_order = True
        if (self._role.value == (1,)):
            for (id, order) in self._trade_opportunity['buy'].items():
                if (order._price > max_order_price):
                    max_order_price = order._price

            if ( max_order_price!=self.MINIMUM and    not self._waiting_for_server and not place_sell_order
                    and self.holdings['markets'][self._market_id]['available_units']>0
                    and DS_REWARD_CHARGE <= max_order_price):
                place_sell_order = Order(max_order_price, 1, OrderType.LIMIT, OrderSide.SELL,
                                        self._market_id, ref="b1")
                self.send_order(place_sell_order)
                print("place this order of sell ", place_sell_order)
                self._waiting_for_server = True




    def _print_trade_opportunity(self, other_order):
        # print(self._trade_opportunity)
        # for (id, ord) in self._trade_opportunity['buy'].items():
        #     print(id)
        #     print("buy of")
        #     print(ord)
        #
        # for (id, ord) in self._trade_opportunity['sell'].items():
        #     print(id)
        #     print("sell of")
        #     print(ord)





        # self.inform("[" + str(self.role()) + str(other_order))
        pass

    def received_completed_orders(self, orders, market_id=None):
        pass

    def received_holdings(self, holdings):


        pass

    def received_marketplace_info(self, marketplace_info):
        self.inform(marketplace_info['session_id'])
        pass

    def run(self):
        self.initialise()
        self.start()


if __name__ == "__main__":
    FM_ACCOUNT = "bullish-delight"
    FM_EMAIL = "r.garg2@student.unimelb.edu.au"
    FM_PASSWORD = "796799"
    MARKETPLACE_ID = 352  # replace this with the marketplace id
    bot_type= BotType.MARKET_MAKER
    ds_bot = DSBot(FM_ACCOUNT, FM_EMAIL, FM_PASSWORD, MARKETPLACE_ID,bot_type)
    ds_bot.run()
