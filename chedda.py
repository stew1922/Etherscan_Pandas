import pandas as pd
from dotenv import load_dotenv
load_dotenv
import os


#be sure a .env file is saved with a parameter "API_KEY" with the appropriate key for your account with Etherscan.io
#pull in the API_KEY
api_key = os.getenv('API_KEY')

#create the connection to the Etherscan API
# eth = Etherscan(api_key)

##identify some key CHEDDA wallets/contracts:
#The CHEDDA "dead" wallet -- initial 50B token burn and then the addtional 1B token burn were here
chedda_dead = "0x000000000000000000000000000000000000dead"
#The CHEDDA deployer wallet
chedda_deployer = "0x763cfa5b0eb7bb2e54100010c5a8fc44d1dde714"
#The dev wallet (staking rewards are coming from here)
dev_wallet = "0x8d29e90625213f4eedbdc49e6358fdbf76b9ddd0"
#The contract address for CHEDDA
chedda_contract = "0x16756EC1DEb89A2106C35E0B586a799D0A61837D"
#The marketing wallet where 2% of all transactions go to cover marketing expenses
chedda_marketing = "0x9625088c654d26b9132feb52d37107ab898d19c6"
#The ETH null address - 1% of all transactions are sent here to be burned
null_address = "0x0000000000000000000000000000000000000000"

#define some simple on-chain metrics:
#initially 100B tokens were created, then 50B were immediately burned
initial_supply = 100000000000
#current total supply comes from etherscan.io - includes everything except tokens sent to the null address
total_supply = int(eth.get_total_supply_by_contract_address(chedda_contract)) * 10**-18
#the number of tokens burned by the devs
dev_burned_chedda = int(eth.get_acc_balance_by_token_and_contract_address(chedda_contract, chedda_dead)) * 10**-18
#the number of tokens burned by transactions
trans_burned_chedda = initial_supply - total_supply # for now until Etherscan fixes the balance issue on the null address
#circulating supply are the total number of token on the market and in CHEDDA wallets
circulating_supply = initial_supply - dev_burned_chedda - trans_burned_chedda

#create a function to automatically update CHEDDA_history.csv
def update_chedda_history(file="./CHEDDA_history.csv", rate_limit=5):
    
    # pull in the current history csv and create a pandas dataframe
    history = pd.read_csv("./CHEDDA_history.csv")

    # define the last time that is included in the csv
    last_time = history.iloc[-1].UnixTimestamp

    # utilizing Etherscan SDK, pull in new data starting from one nanasecond after the last time
    # loop through all data until it is current


