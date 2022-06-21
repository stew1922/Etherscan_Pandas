import data.etherscan as eth
import data.cmc as cmc
import pandas as pd
import numpy as np

# instantiate the classes
accts = eth.Accounts()
txns = eth.Transactions()
stats = eth.Stats()

# define the CMC ID for CHEDDA
cmc_id=17645

# create a dictionary of known addresses
# NOTICE: the 'staking_farming_fee' wallet should no longer be being used, however you may see historical transactions being sent there
known_addresses = {
    'chedda_dead': '0x000000000000000000000000000000000000dead',
    'chedda_deployer': '0x763cfa5b0eb7bb2e54100010c5a8fc44d1dde714',
    'staking': '0x8d29e90625213f4eedbdc49e6358fdbf76b9ddd0',
    'chedda_contract': '0x16756EC1DEb89A2106C35E0B586a799D0A61837D',
    'chedda_marketing1': '0x9625088c654d26b9132feb52d37107ab898d19c6',
    'chedda_marketing2': '0xA0bd9f30daD7ea2a5daa5F93806966649950712D',
    'chedda_marketing3': '0xc17b1D72F07AE3f63c5484A8f0862763b581C6d9',
    'chedda_marketing4': '0x216E3DD4B71F2CAc69ae760809930d1B6574B2fF',
    'chedda_marketing5': '0xBD2d730CCaf5B4587c05A39b55Acff3D855ed336',
    'chedda_dev1': '0x625A181906e85e131eACE493F052b1166F1A443C',
    'chedda_dev2': '0x1D3E1ce1B7d9ae6e918357Ebc1aFD151b5ca5bA4',
    'chedda_dev3': '0x00F4DF21bc1A50bc06208F6A00D5D8F2bBc93Ae4',
    'chedda_dev4': '0x61Ff7eE1D9a7B8b7B68127c36475423cB08A2976',
    'presale_distributor?': '0x2336E0aF1AFc9D67bBfbc358a5b87A985C31f12b',
    'null': '0x0000000000000000000000000000000000000000',
    'usdc_farm': '0x48cfB650544b6628778a28d3a44a8dE5Ae0C1589',
    'eth_farm': '0x23F33C5F0887B385B971355006A18074771Ed50B',
    'uniswapV2': '0x32a505BF9dB617d23bF3EbaAc9aeF80cB24a828C',
    'uniswapV2_2': '0x7a250d5630b4cf539739df2c5dacb4c659f2488d',
    'uniswapV3': '0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45',
    'uniswapV3_2': '0x5a8bd8cdd4da5aebb783d2c67125be0df484eefe',
    'uniswap_usdc': '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc',
    'coinbase_swap': '0xe66B31678d6C16E9ebf358268a790B763C133750',
    'metamask_swap': '0x881d40237659c251811cec9c364ef91dc08d300c',
    'staking_farming_fee': '0x07d0cd787a7d92c0c27f36c315a7e74555c1ac92',
    '1inchV4': '0x1111111254fb6c44bAC0beD2854e76F90643097d',
    'wETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    'recovery_wallet': '0xf842351E23fBCE052769248b95dA238eEd698120',
    'coinbase1': '0x71660c4005ba85c37ccec55d0c4493e66fe775d3',
    'coinbase2': '0x503828976d22510aad0201ac7ec88293211d23da',
    'coinbase3': '0xddfabcdc4d8ffc6d5beaf154f18b778f892a0740',
    'coinbase4': '0x3cd751e6b0078be393132286c442345e5dc49699',
    'coinbase5': '0xb5d85cbf7cb3ee0d56b3bb207d5fc4b82f43f511',
    'coinbase6': '0xeb2629a2734e272bcc07bda959863f316f4bd4cf',
    'coinbase_commerce': '0xf6874c88757721a02f47592140905c4336dfbc61',
    'coinbase_commerce_contract': '0x881d4032abe4188e2237efcd27ab435e81fc6bb1',
    'coinbase_misc': '0xa090e606e30bd747d4e6245a1517ebe430f0057e',
    'binance': '0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE'
}

# create a known addresses dictionary where the values become the keys so you can look up a label for a wallet
invert_known_addresses = {}
for add in known_addresses:
    invert_known_addresses[known_addresses[add].lower()] = add

# update chedda txn history
def update_history():
    return txns.erc20_txn_history(known_addresses['chedda_contract'], './chedda_history.csv')

history = update_history()

# define some simple on-chain metrics:
# initially 100B tokens were created, then 50B were immediately burned
initial_supply = 100000000000
# current total supply comes from etherscan.io - includes everything except tokens sent to the null address
total_supply = float(stats.erc20_token_supply(known_addresses['chedda_contract']))
# the number of tokens burned by the devs
dev_burned_chedda = float(accts.erc20_token_balance(known_addresses['chedda_contract'], known_addresses['chedda_dead']))
# the number of tokens burned by transactions
txn_burned_chedda = history[history['to'] == known_addresses['null']].value.astype('float').sum() * 10**-18
# circulating supply are the total number of token on the market and in CHEDDA wallets
circulating_supply = initial_supply - dev_burned_chedda - txn_burned_chedda
# last 24 hours trading volume, $
last_24h_trading_volume = cmc.Cryptocurrency(cmc_id=cmc_id).last_24h_volume()
# last 24 hours volume % change
last_24h_volume_change = cmc.Cryptocurrency(cmc_id=cmc_id).last_24h_volume_change()
# current price of CHEDDA ($/CHEDDA)
current_price_USD = cmc.Cryptocurrency(cmc_id=cmc_id).current_USD_price()
# last 24 hours price change %
last_24h_price_change = cmc.Cryptocurrency(cmc_id=cmc_id).last_24h_price_change()
# current marketcap of CHEDDA
current_mc = circulating_supply * current_price_USD

# print off a list of chedda stats
def chedda_stats():
    stats = {
        'Initial Supply': f'{initial_supply: ,.0f}',
        'Supply burned by devs': f'{dev_burned_chedda: ,.0f}',
        'Supply burned by txns': f'{txn_burned_chedda: ,.0f}',
        'Total Supply burned': f'{txn_burned_chedda + dev_burned_chedda: ,.0f}',
        'Circulating Supply': f'{circulating_supply: ,.0f}',
        'Last 24hr Trading Volume': f'${last_24h_trading_volume: ,.0f}',
        'Current Price': f'${current_price_USD: ,.7f}',
        'Current Marketcap': f'${current_mc: ,.0f}'
    }

    return stats
