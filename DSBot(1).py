"""
This is a template for Project 1, Task 1 (Induced demand-supply)
"""

from enum import Enum
from fmclient import Agent, OrderSide, Order, OrderType

# Group details
GROUP_MEMBERS = {"796799": "Rishab Garg", "831865": "Kevin Xu", "834063" : "Austen McClernon"}


# ------ Add a variable called DS_REWARD_CHARGE -----
DS_REWARD_CHARGE = 500




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
        self._role = None
        self._bot_type = bot_type







    def role(self):
        return self._role

    def initialised(self):
        cash_info = self.holdings["cash"]["cash"]

        ##will get the information from market id.
        asset_info = None
        for market_id, market_holding in self.holdings["markets"].items():
            asset_info = market_holding["units"]

        if cash_info >0 :
            self._role = Role.BUYER

        if asset_info>0:
            self._role = Role.SELLER

        self.inform("my bot has a role of" + str(self._role))


        pass

    def order_accepted(self, order):
        pass

    def order_rejected(self, info, order):
        pass

    def received_order_book(self, order_book, market_id):
        pass

    def _print_trade_opportunity(self, other_order):
        self.inform("[" + str(self.role()) + str(other_order))

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
