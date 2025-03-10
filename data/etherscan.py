# this file willl utilize API endpoints from the Ethereum block explorer Etherscan.io
import pandas as pd
import numpy as np
from dotenv import load_dotenv
load_dotenv
import os
import requests

# pull in your API_KEY from .env file at or above this file level
api_key = os.getenv("ETHERSCAN_API_KEY")

# define the different network urls
networks = {
        'main': 'https://api.etherscan.io/api',
        'goerli': 'https://api-goerli.etherscan.io/api',
        'kovan': 'https://api-kovan.etherscan.io/api',
        'rinkeby': 'https://api-rinkeby.etherscan.io/api',
        'ropsten': 'https://api-ropsten.etherscan.io/api'
    }

# create a dictionary of known addresses
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
    'binance': '0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE',
    'airswap': '0x74de5d4fcbf63e00296fd95d33236b9794016631',
    'gemini': '0xd24400ae8BfEBb18cA49Be86258a3C749cf46853',
    'bittrex': '0xFBb1b73C4f0BDa4f67dcA266ce6Ef42f520fBB98'
}

# create a known addresses dictionary where the values become the keys so you can look up a label for a wallet
invert_known_addresses = {}
for add in known_addresses:
    invert_known_addresses[known_addresses[add].lower()] = add


class Accounts:

    # instantiate the class with the module identifier and what network to connect to (by defalut set to "main", aka mainnet)
    def __init__(self, module='account', network='main'):
        self.module = module
        self.url = networks[network]
    
    # function to get ether balance from a given address(es)
    def get_eth_balance(self, address, tag='latest'):
        '''
        req'd:
        -address: if only single address balance is desired then the wallet address for the balance you wish to pull, str
                  if multiple address are desired then a list of the addresses to be pulled, list of strings
                  **IF multiple addresses passed, no more than 20 at one time

        optional:
        -tag: Etherscan.io predifined block parameter, either "earliest", "pending" or "latest"
                *set to "latest" by default
        '''
        
        # if a list of addresses is given, then call the multiple address endpoint, otherwise use the single address endpoint
        if type(address) == list:
            if len(address) > 20:
                raise Exception('No more than 20 addresses can be provided for a single call')
            address = ','.join(address)
            action = 'balancemulti'
        else:
            action = 'balance'

        # define the params to be passed in the request
        params = {
            'module': self.module,
            'action': action,
            'address': address,
            'tag': tag,
            'apikey': api_key
        }

        # send the request
        res = requests.post(self.url, params=params).json()

        # return the info, converting wei into ETH
        if action == 'balance':
            return int(res['result'])*10**-18
        else:
            balances = {}
            for balance in res['result']:
                balances[balance['account']] = int(balance['balance'])*10**-18
            return balances

    # function to a list of 'normal' or 'internal' txns by address
    def get_txns_by_address(self, address, kind, startblock=0, endblock=None, page=None, offset=None, sort='asc'):
        '''
        **NOTICE: This endpoint only returns a maximum of 10,000 records at one time.

        req'd:
        -address: wallet address for which you wish to pull normal transactions, type=str
        -kind: normal or internal, type=str

        optional:
        -startblock: the block you wish to beginning pulling from, type=int
            **DEFAULT = 0, aka the genesis block
        -endblock: the block you wish to stop pulling history at, type=int
            **DEFAULT = NONE, aka no end.  (Pro tip: to make faster search results, select a smaller startblock to endblock window)
        -page: page number, type=int
        -offset: number of transactions displayed per page, type=int
        -sort: sorting preference --> either 'asc' or 'desc', type=str
            **DEFAULT = 'asc'
        '''

        # determine the action to take depending on the kind
        if kind == 'normal':
            action = 'txlist'
        elif kind == 'internal':
            action = 'txlistinternal'
        else:
            raise Exception('"kind" must be either "normal" or "internal"')

        # define the parameters to be sent in the request
        params ={
            'module': self.module,
            'action': action,
            'address': address,
            'startblock': startblock,
            'endblock': endblock,
            'page': page,
            'offset': offset,
            'sort': sort,
            'apikey': api_key
        }

        # send the request
        res = requests.post(self.url, params).json()

        # return the info, first checking for a no transactions warning
        if res['message'] == 'No transactions found':
            print(f'WARNING: {res["message"]}')

        return res['result']

    # function to get a list of 'internal' txns by transaction hash
    def get_txns_by_hash(self, txn_hash):
        '''
        req'd:
        -txn_hash: transaction hash, str
        
        **NOTICE: the 'isError' field will return a 0 for successful txns and a 1 for rejected/cancelled txns
        '''

        # define the 'action' to send to the endpoint
        action = 'txlistinternal'

        # define the parameters to send in the request
        params = {
            'module': self.module,
            'action': action,
            'txhash': txn_hash,
            'apikey': api_key
        }

        # send the API request
        res = requests.post(self.url, params).json()

        # return the info, first checking for a no transactions warning
        if res['message'] == 'No transactions found':
            print(f'WARNING: {res["message"]}')

        return res['result']

    # function to get a list of 'internal' txns by block range
    def get_txns_by_block(self, startblock=0, endblock=None, page=None, offset=None, sort='asc'):
        '''
        **NOTICE: this will only return 10,000 records at one time, so it is suggested that your block window size account for this
        
        optional:
        -startblock: the first block to pull internal transactions from, type=int
            **DEFAULT = 0, aka the genesis block
        -endblock: the last block to pull internal transactions from, type=int
            **DEFAULT = None, aka no end (Pro tip: this will only pull in the first 10,000 records since that is the limit imposed by Etherscan)
        -page: the page number if pagination is enabled, type=int
            **DEFAULT = None, aka disabled
        -offset: the number of transaction displayed per page, type=int
            **NOTICE: only needs to be provided when pagination is turned on
        -sort: the sorting preference - either "asc" or "desc", type=str
            **DEFAULT = 'asc'
        '''

        # define the "action" for the API call
        action = 'txlistinternal'

        # define the paramaters to be used in the API call
        params = {
            'module': self.module,
            'action': action,
            'startblock': startblock,
            'endblock': endblock,
            'page': page,
            'offset': offset,
            'sort': sort,
            'apikey': api_key
        }

        # send the request
        res = requests.post(self.url, params).json()

        # return the info, first checking for a no transactions warning
        if res['message'] == 'No transactions found':
            print(f'WARNING: {res["message"]}')

        return res['result']

    # function to get erc20 token balance by wallet address
    def erc20_token_balance(self, contract_address, wallet_address=None, tag='latest'):
        '''
        req'd:
        -contract_address: the address for the erc20 token contract, type=str
        -wallet_address: the address for the wallet in which to check the balance, type=str

        optional:
        -tag: Etherscan.io predifined block parameter, either "earliest", "pending" or "latest"
            **DEFAULT = 'latest' 
        '''

        # define the action for the API call
        action = 'tokenbalance'

        # define the parameters for the request
        params = {
            'module': self.module,
            'action': action,
            'contractaddress': contract_address,
            'address': wallet_address,
            'tag': tag,
            'apikey': api_key
        }

        # make the request
        res = requests.post(self.url, params).json()

        # return the info
        if res['message'] == 'NOTOK':
            raise Exception(res['result'])
        else:
            return float(res['result']) * 10**-18

    # function to get a list of ERC20 token transfer events ***WARNING: this function only return 10000 records
    def erc20_transfer_history(self, contract_address, wallet_address=None, page=None, offset=None, startblock=0, endblock=None, sort='asc'):
        '''
        req'd:
        -contract_address: the address of the contract for which you wish to pull data, type=str

        optional:
        -wallet_address: and address of a wallet you wish to filter all transfer activity, type=str
        -page: page number if pagination in enabled, type=int
            **DEFAULT = None, aka disabled
        -offset: number of transactions to display per page, type=int
            **NOTICE: only needed when pagination is enabled
        -startblock: the block number from which to start your search, type=int
            **DEFAULT = 0, aka the genesis block
        -endblock: the block number from which to end your search, type=int
            **DEFAULT = None, aka no end and therefore all blocks
        -sort: the sorting preference - either 'asc' or 'desc', type=str
            **DEFAULT = 'asc'
        '''

        # define the action for the API call
        action = 'tokentx'
        
        # define the parameters for the API call
        params = {
            'module': self.module,
            'action': action,
            'contractaddress': contract_address,
            'address': wallet_address,
            'page': page,
            'offset': offset,
            'startblock': startblock,
            'endblock': endblock,
            'sort': sort,
            'apikey': api_key
        }

        # send the request
        res = requests.post(self.url, params).json()

        # return the info, first checking for a no transactions warning
        if res['message'] == 'No transactions found':
            raise Exception(f'WARNING: {res["message"]}')

        return res['result']

    # function to get a list of ERC721 token transfer events
    def erc721_transfer_history(self, contract_address, wallet_address=None, page=None, offset=None, startblock=0, endblock=None, sort='asc'):
        '''
        req'd:
        -contract_address: the address of the contract for which you wish to pull data, type=str

        optional:
        -wallet_address: and address of a wallet you wish to filter all transfer activity, type=str
        -page: page number if pagination in enabled, type=int
            **DEFAULT = None, aka disabled
        -offset: number of transactions to display per page, type=int
            **NOTICE: only needed when pagination is enabled
        -startblock: the block number from which to start your search, type=int
            **DEFAULT = 0, aka the genesis block
        -endblock: the block number from which to end your search, type=int
            **DEFAULT = None, aka no end and therefore all blocks
        -sort: the sorting preference - either 'asc' or 'desc', type=str
            **DEFAULT = 'asc'
        '''

        # define the action for the API call
        action = 'tokennfttx'
        
        # define the parameters for the API call
        params = {
            'module': self.module,
            'action': action,
            'contractaddress': contract_address,
            'address': wallet_address,
            'page': page,
            'offset': offset,
            'startblock': startblock,
            'endblock': endblock,
            'sort': sort,
            'apikey': api_key
        }

        # send the request
        res = requests.post(self.url, params).json()

        # return the info, first checking for a no transactions warning
        if res['message'] == 'No transactions found':
            print(f'WARNING: {res["message"]}')

        return res['result']

    # function to get a list of blocks mined by an address
    def mined_blocks(self, address, block_type='blocks', page=None, offset=None):
        '''
        Incomplete, needs to be written
        '''

        action = 'getminedblocks'

    # function to get historical Ether balance for a single address at a single block height -- NEEDS the pro API subscription
    def historical_ether_balance(self, address, block_num):
        '''
        Incomplete, needs to be written
        '''

        action = 'balancehistory'
    
    # function to a dataframe of 'normal' or 'internal' txns by address
    def get_txns_by_address_df(self, address, kind, startblock=0, endblock=None, page=None, offset=None, sort='asc'):

        # pull the history from the erc20_transfer_history() function
        history = self.get_txns_by_address(address, kind, startblock=0, endblock=None, page=None, offset=None, sort='asc')

        if len(history) == 0:
            return pd.DataFrame()

        # create the dataframe
        history_df = pd.DataFrame(history)

        # set the 'value' column to "float"
        history_df['value'] = history_df['value'].astype('float')

        # create a 'eth_fees' column to calculate the fees spent, in ETH
        if kind == 'normal':
            history_df['eth_fees'] = history_df['gasUsed'].astype('float') * (history_df['gasPrice'].astype('float') * 10**-18)
        else:
            history_df['eth_fees'] = 0

        # create a 'balance' column
        history_df['txn_value'] = np.where(
            history_df['to'] == str(address).lower(), 
            history_df['value'] - history_df['eth_fees'], 
            (history_df['value'] * -1) - history_df['eth_fees']
            )
        history_df['balance'] = history_df['txn_value'].cumsum()
        return history_df

    # function to return a pandas dataframe of an account and it's balance ***WARNING: this function only returns 10000 records
    def erc20_transfer_history_df(self, contract_address, wallet_address=None, page=None, offset=None, startblock=0, endblock=None, sort='asc'):

        # pull the history from the erc20_transfer_history() function
        history = self.erc20_transfer_history(contract_address, wallet_address, page, offset, startblock, endblock, sort)

        # create the dataframe
        history_df = pd.DataFrame(history)

        # set the 'value' column to "float"
        history_df['value'] = history_df['value'].astype('float')

        # create a 'eth_fees' column, in ETH
        history_df['eth_fees'] = history_df['gasUsed'].astype('float') * (history_df['gasPrice'].astype('float') * 10**-18)

        # create a 'balance' column
        history_df['txn_value'] = np.where(history_df['to'] == str(wallet_address).lower(), history_df['value'], history_df['value'] * -1)
        history_df['balance'] = history_df['txn_value'].cumsum()

        return history_df


class Contracts:

    # instantiate the class with the module identifier and what network to connect to (by defalut set to "main", aka mainnet)
    def __init__(self, module='contract', network='main'):
        self.module = module
        self.url = networks[network]

    # function to get contract ABI for a verified contract
    def get_abi(self, address):
        '''
        req'd:
        -address: address of the verified contract you would like the abi from, type=str
        '''

        # define the action for the API call
        action = 'getabi'

        # define the parameter for the request
        params = {
            'module': self.module,
            'action': action,
            'address': address,
            'apikey': api_key
        }

        # make the request
        res = requests.post(self.url, params).json()

        # return the info
        return res['result']

    # function to get contract source code for a verified contract
    def get_source(self, address):
        '''
        req'd:
        -address: address of the verified contract you would like the abi from, type=str
        '''

        # define the action for the API call
        action = 'getsourcecode'

        # define the parameter for the request
        params = {
            'module': self.module,
            'action': action,
            'address': address,
            'apikey': api_key
        }

        # make the request
        res = requests.post(self.url, params).json()

        # return the info
        return res['result']


class Transactions:

    # instantiate the class with the module identifier and what network to connect to (by defalut set to "main", aka mainnet)
    def __init__(self, module='transaction', network='main'):
        self.module = module
        self.url = networks[network]

    # function to check contract execution status
    def contract_execution_status(self, txn_hash):
        '''
        req'd:
        -txn_hash: the hash of the contract transaction you wish to check the status of, type=str
        '''

        # define the action for the API call
        action = 'getstatus'

        # define the parameters for the request
        params = {
            'module': self.module,
            'action': action,
            'txhash': txn_hash,
            'apikey': api_key
        }

        # make the request
        res = requests.post(self.url, params).json()

        # return the info
        return res['result']

    # function to check transaction receipt status
    def txn_receipt_status(self, txn_hash):
        '''
        req'd:
        -txn_hash: the hash of the contract transaction you wish to check the status of, type=str
        '''

        # define the action for the API call
        action = 'gettxreceiptstatus'

        # define the parameters for the request
        params = {
            'module': self.module,
            'action': action,
            'txhash': txn_hash,
            'apikey': api_key
        }

        # make the request
        res = requests.post(self.url, params).json()

        # return the info
        return res['result']

    # function to pull transaction history into a dataframe for a given token
    def erc20_txn_history(self, contract_address, file_path=None):
        '''
        req'd:
        -contract_address: the address of the token contract you'd like to pull history, type=str
        '''

        # instantiate the Accounts class
        # Accounts = Accounts()

        # we will use the erc20_transfer function from the Accounts class to build our dataframe
        # it is limited to 10,000 transactions per call so we will need to loop until we have pulled in all data
            ##for now the file location is going to be on this level and the file will be called chedda_history.csv
            ##in the future this will be deprecated and the user will need to choose the file location and the name
        # check first if there is a csv file in 'filepath', otherwise we will make one
        try:
            history = pd.read_csv(file_path)
        except Exception as e:
            if "No such file or directory" in str(e):
                history = pd.DataFrame(Accounts().erc20_transfer_history(contract_address))
                history.sort_values(by=['timeStamp'], axis=0, inplace=True, ignore_index=True)

        # find the last block of transactions
        last_block = history.iloc[-1]['blockNumber']

        # since we will use the last block to start pulling data, we must remove it from 'history' so we don't have any duplicates
        history = history[history['blockNumber'] != last_block]

        # since the maximum number of items returned from Etherscan is 10,000, run the loop until the length
        # of the returned items is less than 10,000
        history_total = history.copy()

        # be sure the timeStamp column is actually a datetime to be more human readable
        try:
            history_total.timeStamp = pd.to_datetime(history_total.timeStamp, utc=True, unit='s')
        except:
            history_total

        count = 0
        length = 10000
        while length == 10000:
            count += 1
            history = pd.DataFrame(Accounts().erc20_transfer_history(contract_address, startblock=last_block))
            history['timeStamp'] = pd.to_datetime(history['timeStamp'], utc=True, unit='s')
            length = len(history)
            history.sort_values(by=['timeStamp'], axis=0, inplace=True, ignore_index=True)
            last_block = history.iloc[-1]['blockNumber']
            history2 = history[history['blockNumber']!=last_block]
            if len(history) == 10000:
                history_total = pd.concat([history2, history_total], axis=0, join='inner')
            else:
                history_total = pd.concat([history, history_total], axis=0, join='inner')

        # be sure it is sorted in order by timeStamp
        history_total.sort_values(by=['blockNumber', 'timeStamp'], axis=0, ascending=[True, True], inplace=True, ignore_index=True)

        # make the 'value' column a floating point type in order to run calculations on it
        history_total['value'] = history_total['value'].astype('float')


        # write history_total to a csv if a file path was provided
        if file_path != None:
            history_total.to_csv(file_path)

        return history_total

    # function to create an dataframe and excel sheet of the full accounting of a particular wallet, including transactions and summary level of associated wallets
    def wallet_accounting(self, wallet, file_path, output_file_path=None):
        '''
        req'd:
        -wallet: the wallet address you want to analyze, type=str
        -file_path: the file location of the .csv file with the token's txn history
            NOTICE: Use 'erc20_txn_history' from this library and pandas 'pd.to_csv()' to easily create a .csv if you don't have one already
        
        optional:
        -output_file_path = the file location to output a tabulated excel sheet
        '''
    
        # the .csv that gets created from the above function is always in lower case
        wallet = str(wallet).lower()

        # add the wallet in question to the dictionary of known wallets
        invert_known_addresses[wallet] = 'this_wallet'

        # start with pulling in all erc20 txns from wallet and format the necessary columns
        wallet_erc20_history = pd.read_csv(file_path)
        wallet_erc20_history.blockNumber = wallet_erc20_history.blockNumber.astype('str')
        wallet_erc20_history.nonce = wallet_erc20_history.nonce.astype('float')
        wallet_erc20_history.gas = wallet_erc20_history.gas.astype('str')
        wallet_erc20_history.gasUsed = wallet_erc20_history.gasUsed.astype('str')
        wallet_erc20_history.cumulativeGasUsed = wallet_erc20_history.cumulativeGasUsed.astype('str')
        wallet_erc20_history.gasPrice = wallet_erc20_history.gasPrice.astype('str')
        wallet_erc20_history.confirmations = wallet_erc20_history.confirmations.astype('str')
        wallet_erc20_history.transactionIndex = wallet_erc20_history.transactionIndex.astype('str')
        wallet_erc20_history = wallet_erc20_history[((wallet_erc20_history['to'] == wallet) | (wallet_erc20_history['from'] == wallet))]
        wallet_erc20_history.timeStamp = pd.to_datetime(wallet_erc20_history.timeStamp, utc=True)
        wallet_erc20_history.value = wallet_erc20_history['value'].astype('float') * 10 ** (wallet_erc20_history.tokenDecimal.astype('float') * -1)
        wallet_erc20_history['eth_fees'] = wallet_erc20_history['gasUsed'].astype('float') * wallet_erc20_history['gasPrice'].astype('float') * 10**-18
        wallet_erc20_history['txn_value'] = np.where(wallet_erc20_history['to'] == wallet, wallet_erc20_history['value'], wallet_erc20_history['value'] * -1)
        wallet_erc20_history['balance'] = wallet_erc20_history['txn_value'].cumsum()
        wallet_erc20_history['to_label'] = ""
        wallet_erc20_history['from_label'] = ""
        for i in (wallet_erc20_history.index):
            if wallet_erc20_history.loc[i, 'to'] in invert_known_addresses:
                wallet_erc20_history.loc[i, 'to_label'] = invert_known_addresses[wallet_erc20_history['to'].loc[i]]

            if wallet_erc20_history.loc[i, 'from'] in invert_known_addresses:
                wallet_erc20_history.loc[i, 'from_label'] = invert_known_addresses[wallet_erc20_history['from'].loc[i]]

       # pull in the "normal" ETH txns and format the necessary columns
        wallet_normal = Accounts().get_txns_by_address_df(wallet, 'normal')
        if len(wallet_normal) != 0:
            wallet_normal.timeStamp = pd.to_datetime(wallet_normal.timeStamp, utc=True, unit='s')
            wallet_normal.value = wallet_normal.value.astype('float') * 10**-18
            wallet_normal.txn_value = wallet_normal.txn_value.astype('float') * 10**-18
            wallet_normal.balance = wallet_normal.balance.astype('float') * 10**-18
            wallet_normal.nonce = wallet_normal.nonce.astype('float')
            wallet_normal['to_label'] = ""
            wallet_normal['from_label'] = ""
            for i in (wallet_normal.index):
                if wallet_normal.loc[i, 'to'] in invert_known_addresses:
                    wallet_normal.loc[i, 'to_label'] = invert_known_addresses[wallet_normal['to'].loc[i]]

                if wallet_normal.loc[i, 'from'] in invert_known_addresses:
                    wallet_normal.loc[i, 'from_label'] = invert_known_addresses[wallet_normal['from'].loc[i]] 

       # pull in the "internal" ETH txns and format the necessary columns.
        wallet_internal = Accounts().get_txns_by_address_df(wallet, 'internal')
        if len(wallet_internal) != 0:
            wallet_internal.timeStamp = pd.to_datetime(wallet_internal.timeStamp, unit='s', utc=True)
            wallet_internal.value = wallet_internal.value.astype('float') * 10**-18
            wallet_internal.txn_value = wallet_internal.txn_value.astype('float') * 10**-18
            wallet_internal.balance = wallet_internal.balance.astype('float') * 10**-18
            wallet_internal['to_label'] = ""
            wallet_internal['from_label'] = ""
            for i in (wallet_internal.index):
                if wallet_internal.loc[i, 'to'] in invert_known_addresses:
                    wallet_internal.loc[i, 'to_label'] = invert_known_addresses[wallet_internal['to'].loc[i]]

                if wallet_internal.loc[i, 'from'] in invert_known_addresses:
                    wallet_internal.loc[i,'from_label'] = invert_known_addresses[wallet_internal['from'].loc[i]] 

        # merge the internal, normal and erc20 dataframes
        if len(wallet_normal) == 0 and len(wallet_internal) == 0:
            merged = pd.DataFrame()
        elif len(wallet_normal) > 0 and len(wallet_internal) == 0:
            merged = wallet_normal.copy()
        elif len(wallet_normal) == 0 and len(wallet_internal) > 0:
            merged = wallet_internal.copy()
        else:
            merged = pd.merge(wallet_internal, wallet_normal, how='outer')

        merged = pd.merge(wallet_erc20_history, merged, how='outer')
        merged.drop(columns=['balance', 'txn_value', 'Unnamed: 0'], inplace=True)

        merged.txreceipt_status = merged.txreceipt_status.astype('float')
        merged = merged.sort_values(['timeStamp', 'nonce', 'transactionIndex'], axis=0, ascending=True, ignore_index=True)
        merged = merged.reindex()

        merged['erc20_txn_value'] = np.where(
            merged['tokenName'] == "Chedda Token",
            np.where(
                merged['to'] == wallet,
                merged.value,
                merged.value * -1
                ), 0
        )

        merged['erc20_balance'] = merged.erc20_txn_value.cumsum()


        merged['eth_txn_value'] = np.where(
            merged['tokenName'] != "Chedda Token", 
            np.where(
                merged['to'] == wallet,
                merged.value,
                merged.value * -1
            ), 0
        )

        merged['eth_balance'] = 0
        for i in merged.index:
            # if it is the first txn, set the balance = to the txn_value
            if i == 0:
                merged.eth_balance = merged.loc[i, 'eth_txn_value']
            # if it is a mulitple part txn, the fee only needs to be accounted for once so don't subtract fees if it is not the first part of txn
            elif merged.loc[i, 'hash'] == merged.loc[i-1, 'hash'] and merged.loc[i-1, 'from'] == wallet:
                if merged.loc[i, 'txreceipt_status'] != 0:
                    merged.loc[i, 'eth_balance'] = merged.loc[i-1, 'eth_balance'] + merged.loc[i, 'eth_txn_value']
                else:
                    merged.loc[i, 'eth_balance'] = merged.loc[i-1, 'eth_balance']
            # only subtract fees if the sender is the wallet in question
            elif merged.loc[i, 'from'] == wallet:
                if merged.loc[i, 'txreceipt_status'] == 1:
                    merged.loc[i, 'eth_balance'] = merged.loc[i-1, 'eth_balance'] + merged.loc[i, 'eth_txn_value'] - merged.loc[i, 'eth_fees']
                else:
                    merged.loc[i, 'eth_balance'] = merged.loc[i-1, 'eth_balance'] - merged.loc[i, 'eth_fees']
            # this might be a redundant and unnecessary line
            else:
                merged.loc[i, 'eth_balance'] = merged.loc[i-1, 'eth_balance'] + merged.loc[i, 'eth_txn_value']

        # convert the timeStamp to an excel compatible format (no timezone)
        merged.timeStamp = merged.timeStamp.view('int64')/10**9
        merged.timeStamp = pd.to_datetime(merged.timeStamp, utc=False, unit='s')

        # create and associated wallets list along with the transaction summaries for each wallet
        sent_wallets = list(set(merged['to']))
        recieved_wallets = list(set(merged['from']))
        all_wallets = list(set(sent_wallets + recieved_wallets))

        # remove the wallet in question from the list
        all_wallets.remove(wallet)

        assoc = {}
        for wallet in all_wallets:
            if wallet in invert_known_addresses:
                assoc[invert_known_addresses[wallet]] = {
                    'eth_sent': abs(merged[merged['to'] == wallet]['eth_txn_value'].sum()), 
                    'eth_recieved': abs(merged[merged['from'] == wallet]['eth_txn_value'].sum()),
                    'eth_net': abs(merged[merged['from'] == wallet]['eth_txn_value'].sum()) - abs(merged[merged['to'] == wallet]['eth_txn_value'].sum()),
                    'erc20_sent': abs(merged[merged['to'] == wallet]['erc20_txn_value'].sum()),
                    'erc20_received': abs(merged[merged['from'] == wallet]['erc20_txn_value'].sum()),
                    'erc20_net': abs(merged[merged['from'] == wallet]['erc20_txn_value'].sum()) - abs(merged[merged['to'] == wallet]['erc20_txn_value'].sum())
                }
            else:
                assoc[wallet] = {
                    'eth_sent': abs(merged[merged['to'] == wallet]['eth_txn_value'].sum()), 
                    'eth_recieved': abs(merged[merged['from'] == wallet]['eth_txn_value'].sum()),
                    'eth_net': abs(merged[merged['from'] == wallet]['eth_txn_value'].sum()) - abs(merged[merged['to'] == wallet]['eth_txn_value'].sum()),
                    'erc20_sent': abs(merged[merged['to'] == wallet]['erc20_txn_value'].sum()),
                    'erc20_received': abs(merged[merged['from'] == wallet]['erc20_txn_value'].sum()),
                    'erc20_net': abs(merged[merged['from'] == wallet]['erc20_txn_value'].sum()) - abs(merged[merged['to'] == wallet]['erc20_txn_value'].sum())
                }

        assoc_df = pd.DataFrame(assoc).T

        # return the data
        if output_file_path == None:
            return assoc_df
        else:
            with pd.ExcelWriter(output_file_path) as writer:
                merged.to_excel(writer, sheet_name='Wallet History', freeze_panes=(1,0), index=False)
                assoc_df.to_excel(writer, sheet_name='Associated Wallet Summary', freeze_panes=(1,1))
                return assoc_df


class Stats:

    # instantiate the class with the module identifier and what network to connect to (by defalut set to "main", aka mainnet)
    def __init__(self, module='stats', network='main'):
        self.module = module
        self.url = networks[network]

    # function to get total supply of an ERC20 token
    def erc20_token_supply(self, contract_address):
        '''
        req'd:
        -contract_address: the address of the contract you which to pull the total supply, type=str
        '''

        # define the action for the API call
        action = 'tokensupply'

        # define the parameters for the request
        params = {
            'module': self.module,
            'action': action,
            'contractaddress': contract_address,
            'apikey': api_key
        }

        # make the request
        res = requests.post(self.url, params).json()

        # return the info
        return float(res['result']) * 10**-18

    # function to return total ether in circulation (excludes ETH2 staking rewards and EIP1559 burnt fees)
    def eth1_supply(self):

        # define the action for the api call
        action = 'ethsupply'

        # define the parameters for the request
        params = {
            'module': self.module,
            'action': action,
            'apikey': api_key
        }

        # make the request
        res = requests.post(self.url, params).json()

        # return the info in ETH, NOT wei (1 wei = 1 * 10^-18)
        return int(res['result']) * 10**-18

    # function to return total ether in circulation(includes ETH2 staking rewards and EIP 1559 burnt fees)
    def eth2_supply(self):

        # define the action for the api call
        action = 'ethsupply2'

        # define the parameters for the request
        params = {
            'module': self.module,
            'action': action,
            'apikey': api_key
        }

        # make the request
        res = requests.post(self.url, params).json()

        # return the info in ETH, NOT wei (1 wei = 1 * 10^-18)
        return int(res['result']) * 10**-18

    # function to get ether last price
    def eth_price(self):

        # define the action for the api call
        action = 'ethprice'

        # define the parameters for the request
        params = {
            'module': self.module,
            'action': action,
            'apikey': api_key
        }

        # make the request
        res = requests.post(self.url, params).json()

        # return the info in ETH, NOT wei (1 wei = 1 * 10^-18)
        return res['result']
