from dotenv import load_dotenv
load_dotenv()
import os
import coinmarketcapapi

# grab your coinmarketcap API key
api_key = os.getenv('CMC_API_KEY')

# CRYPTOCURRENCY endpoint
class Cryptocurrency:

    def __init__(self, symbol=None, cmc_id=None):
        self.symbol = symbol
        self.cmc_id = cmc_id

        self.cmc = coinmarketcapapi.CoinMarketCapAPI(api_key)

    
    def current_USD_price(self, cmc_id=None, symbol=None):
        cmc_id, symbol = self.cmc_id, self.symbol

        if cmc_id==None and symbol==None:
            raise Exception("Either the CMC ID or the symbol abbreviation must be provided.")
        elif cmc_id!=None:
            r = self.cmc.cryptocurrency_quotes_latest(id=self.cmc_id)
            price = r.data[str(self.cmc_id)]['quote']['USD']['price']
            if price is None:
                return 0
            else:
                return price
        else:
            r = self.cmc.cryptocurrency_quotes_latest(symbol=self.symbol)
            price = r.data[self.symbol]['quote']['USD']['price']
            if price is None:
                return 0
            else:
                return price

    def last_24h_price_change(self, cmc_id=None, symbol=None):
        cmc_id, symbol = self.cmc_id, self.symbol

        if cmc_id==None and symbol==None:
            raise Exception("Either the CMC ID or the symbol abbreviation must be provided.")
        elif cmc_id!=None:
            r = self.cmc.cryptocurrency_quotes_latest(id=self.cmc_id)
            price_chg = r.data[str(self.cmc_id)]['quote']['USD']['percent_change_24h']
            return price_chg
        else:
            r = self.cmc.cryptocurrency_quotes_latest(symbol=self.symbol)
            price_chg = r.data[self.symbol]['quote']['USD']['percent_change_24h']
            return price_chg

    def last_24h_volume(self, cmc_id=None, symbol=None):
        cmc_id, symbol = self.cmc_id, self.symbol

        if cmc_id==None and symbol==None:
            raise Exception("Either the CMC ID or the symbol abbreviation must be provided.")
        elif cmc_id!=None:
            r = self.cmc.cryptocurrency_quotes_latest(id=self.cmc_id)
            volume = r.data[str(self.cmc_id)]['quote']['USD']['volume_24h']
            return volume
        else:
            r = self.cmc.cryptocurrency_quotes_latest(symbol=self.symbol)
            volume = r.data[self.symbol]['quote']['USD']['volume_24h']
            return volume

    def last_24h_volume_change(self, cmc_id=None, symbol=None):
        cmc_id, symbol = self.cmc_id, self.symbol

        if cmc_id==None and symbol==None:
            raise Exception("Either the CMC ID or the symbol abbreviation must be provided.")
        elif cmc_id!=None:
            r = self.cmc.cryptocurrency_quotes_latest(id=self.cmc_id)
            volume_chg = r.data[str(self.cmc_id)]['quote']['USD']['volume_change_24h']
            return volume_chg
        else:
            r = self.cmc.cryptocurrency_quotes_latest(symbol=self.symbol)
            volume_chg = r.data[self.symbol]['quote']['USD']['volume_change_24h']
            return volume_chg

    def img_url(self, cmc_id=None, symbol=None):
        cmc_id, symbol = self.cmc_id, self.symbol

        if cmc_id==None and symbol==None:
            raise Exception("Either the CMC ID or the symbol abbreviation must be provided.")
        elif cmc_id!=None:
            r = self.cmc.cryptocurrency_info(id=self.cmc_id)
            img_url = r.data[str(self.cmc_id)]['logo']
            return img_url
        else:
            r = self.cmc.cryptocurrency_info(symbol=self.symbol)
            img_url = r.data[self.symbol]['logo']
            return img_url