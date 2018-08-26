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
DS_REWARD_CHARGE = 920




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

        #the market_id is updated in the initialize method.
        self._market_id = -1

        # It can be either Buyer or seller depending on cash or assets availaible at start
        self._role = None
        self.MAXIMUM = 10001
        self.MINIMUM= -1
        self._trade_opportunity = {"buy":{},"sell":{}}

        # Robot type can be either Market_Maker or Reactive.
        self._bot_type = bot_type
        self._waiting_for_server= False
        self.bid_counter = 0
        self.ask_counter = 0
    
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

        elif asset_info > 0:
            self._role  = Role.SELLER

        self.inform("my bot has a role of" + str(self._role))




    def order_accepted(self, order):


        self._waiting_for_server= False

        print("my order   has accepted",order)


    def order_rejected(self, info, order):
        self._waiting_for_server= False

        self.inform("my order ",order, " has rejected")
        print("my order  has rejected",order,info)
        # if OrderSide.BUY:
        #     self.bid_counter = 0
        # elif OrderSide.SELL:
        #     self.ask_counter = 0



    def received_order_book(self, order_book, market_id):
        print("role is ", self._role)
        print("id of market is ",self._market_id)

        #gets the trade_opportunity every time the order book is received from server.
        self._trade_opportunity = {"buy": {}, "sell": {}}

        #Order is defined as markert id: order object reference, type, Mine, Buy or Sell , Unit with price.

        for order  in order_book:

            if not order.mine:
                if(order._side == OrderSide.BUY):

                    if( order._id not  in  self._trade_opportunity['buy'].keys()):
                        self._trade_opportunity['buy'][order._id] = copy.deepcopy(order)

                if (order._side == OrderSide.SELL):

                    if ( order._id  not in self._trade_opportunity['sell'].keys()):
                        self._trade_opportunity['sell'][order._id] = copy.deepcopy(order)


        print("buy orders are :" ,self._trade_opportunity['buy'])
        print("sell orders are :" ,self._trade_opportunity['sell'])

        self._reactive(order_book)
        self._print_trade_opportunity(order_book)
        # self._marketmaker(order_book)





    def _reactive(self,other_order):
        
        
        print("cash with us is ", self.holdings['cash']['available_cash'])
        min_order_price = self.MAXIMUM
        place_buy_order = False

        #need to check the order placed was of us and make sure it doesn't place another order.
        for order in other_order:
            if(order.mine and order.side == OrderSide.BUY):
                place_buy_order = True


        #if we are buyer and any person who is selling a sell order which is less than DS_UTIL,
        #we will buy from it.
        #calculated the minimum order of sell and placed a buy order if it is less than the given amount.
        #also checked that we placed one order till the server gives the confirmation.
        if( self._role.value == (0,)):
            for (id,order) in self._trade_opportunity['sell'].items():
                if(order._price < min_order_price):
                    min_order_price = order._price

            if(min_order_price !=self.MAXIMUM and  not self._waiting_for_server
                    and not place_buy_order and
                    self.holdings['cash']['available_cash'] >= min_order_price
                    and DS_REWARD_CHARGE >= min_order_price):
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
        if (self._role.value == 1):
            for (id, order) in self._trade_opportunity['buy'].items():
                print("buy order is ", id, order)
                if (order._price > max_order_price):
                    max_order_price = order._price
            print("max order price to buy is ", max_order_price)

            if ( max_order_price!=self.MINIMUM and    not self._waiting_for_server and not place_sell_order
                    and self.holdings['markets'][self._market_id]['available_units']>0
                    and DS_REWARD_CHARGE <= max_order_price):
                place_sell_order = Order(max_order_price, 1, OrderType.LIMIT, OrderSide.SELL,
                                        self._market_id, ref="b1")

                self.send_order(place_sell_order)
                print("place this order of sell ", place_sell_order)
                self._waiting_for_server = True

    def _marketmaker(self, other_order):

        print("cash with us is ", self.holdings['cash']['available_cash'])

        if (self._role.value == 1 and self.ask_counter < 2): #seller
            place_sell_order = Order(DS_REWARD_CHARGE+5, 1, OrderType.LIMIT, OrderSide.SELL,
                                     self._market_id, ref="b1")
            self.send_order(place_sell_order)
            print("place this order of sell ", place_sell_order)

        if (self._role.value == (0,) and self.bid_counter < 2): # buyer
            place_buy_order = Order(DS_REWARD_CHARGE-5,
                                    1, OrderType.LIMIT, OrderSide.BUY, self._market_id, ref="s1")
            self.send_order(place_buy_order)
            print("place this order ", place_buy_order)

    def _print_trade_opportunity(self, other_order):
    #if i am buyer. anything whic# h has ask price less than my DS_REWARD, i will buy it.
        print("here")
        print(self._role.value)

        print(self._trade_opportunity)
        #defines the buyer
        if(self._role.value == (0,)):
            for (id, ord) in self._trade_opportunity['sell'].items():
                print("sell orders ")
                print(ord._price)

                if(ord._price <= DS_REWARD_CHARGE):

                    if(self.holdings['cash']['available_cash'] >= ord._price):
                        self.inform("[PROFITABLE TRADE] @ " + str(ord._price) )
                        print("[PROFITABLE TRADE] @ ", str(ord._price) )
                    if(self.holdings['cash']['available_cash'] < ord._price):
                        print("cash with us is ", self.holdings['cash']['available_cash'])

                        self.inform("[PROFITABLE TRADE] @ " + str(ord._price) , " but has insufficient cash")
                        print("[PROFITABLE TRADE] @ ",ord._price , " but has insufficient cash")
        #defines the seller
        if (self._role.value == 1):
            for (id, ord) in self._trade_opportunity['buy'].items():
                if (ord._price >= DS_REWARD_CHARGE):

                    if (self.holdings['markets'][self._market_id]['available_units'] >0):
                        print("[PROFITABLE TRADE] @ ", str(ord._price))
                        self.inform("[PROFITABLE TRADE] @ " + str(ord._price))

                    if (self.holdings['markets'][self._market_id]['available_units'] == 0 ):
                        print("[PROFITABLE TRADE] @ ", str(ord._price), " but has insufficient assets")
                        self.inform("[PROFITABLE TRADE] @ "+ str(ord._price), " but has insufficient assets")




        # for (id, ord) in self._trade_opportunity['sell'].items():
        #     print(id)
        #     print("sell of")
        #     print(ord)





        # self.inform("[" + str(self.role()) + str(other_order))


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
    MARKETPLACE_ID = 260  # replace this with the marketplace id
    bot_type= BotType.MARKET_MAKER
    ds_bot = DSBot(FM_ACCOUNT, FM_EMAIL, FM_PASSWORD, MARKETPLACE_ID,bot_type)
    ds_bot.run()
