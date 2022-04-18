import pandas as pd
import etherscan

## identify some key CHEDDA wallets/contracts:
# The CHEDDA "dead" wallet -- initial 50B token burn and then the addtional 1B token burn were here
chedda_dead = "0x000000000000000000000000000000000000dead"
# The CHEDDA deployer wallet
chedda_deployer = "0x763cfa5b0eb7bb2e54100010c5a8fc44d1dde714"
# The staking contract
staking = "0x8d29e90625213f4eedbdc49e6358fdbf76b9ddd0"
# The contract address for CHEDDA
chedda_contract = "0x16756EC1DEb89A2106C35E0B586a799D0A61837D"
# The marketing wallet where 2% of all transactions go to cover marketing expenses
chedda_marketing = "0x9625088c654d26b9132feb52d37107ab898d19c6"
# The ETH null address - 1% of all transactions are sent here to be burned
null_address = "0x0000000000000000000000000000000000000000"

# instantiate the classes
Accounts = etherscan.Accounts()
Stats = etherscan.Stats()

#define some simple on-chain metrics:
#initially 100B tokens were created, then 50B were immediately burned
initial_supply = 100000000000
#current total supply comes from etherscan.io - includes everything except tokens sent to the null address
total_supply = Stats.erc20_token_supply(chedda_contract)
#the number of tokens burned by the devs
dev_burned_chedda = Accounts.erc20_token_balance(chedda_contract, chedda_dead)
#the number of tokens burned by transactions
txn_burned_chedda = initial_supply - total_supply # for now until Etherscan fixes the balance issue on the null address
#circulating supply are the total number of token on the market and in CHEDDA wallets
circulating_supply = initial_supply - dev_burned_chedda - txn_burned_chedda



