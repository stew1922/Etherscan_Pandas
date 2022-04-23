# this file willl utilize API endpoints from the Ethereum block explorer Etherscan.io
import pandas as pd
import numpy as np
from dotenv import load_dotenv
load_dotenv
import os
import json
import requests, urllib

# pull in your API_KEY from .env file at or above this file level
api_key = os.getenv("API_KEY")

# define the different network urls
networks = {
        'main': 'https://api.etherscan.io/api',
        'goerli': 'https://api-goerli.etherscan.io/api',
        'kovan': 'https://api-kovan.etherscan.io/api',
        'rinkeby': 'https://api-rinkeby.etherscan.io/api',
        'ropsten': 'https://api-ropsten.etherscan.io/api'
    }


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
            return int(res['result']) * 10**-18

    # function to get a list of ERC20 token transfer events
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
    
    # function to return a pandas dataframe of an account and it's balance
    def erc20_transfer_history_df(self, contract_address, wallet_address=None, page=None, offset=None, startblock=0, endblock=None, sort='asc'):

        # pull the history from the erc20_transfer_history() function
        history = self.erc20_transfer_history(contract_address, wallet_address, page, offset, startblock, endblock, sort)

        # create the dataframe
        history_df = pd.DataFrame(history)

        # set the 'value' column to "float"
        history_df['value'] = history_df['value'].astype('float')

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
    def erc20_txn_history(self, contract_address, file_path):
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

        count = 0
        length = 10000
        while length == 10000:
            count += 1
            history = pd.DataFrame(Accounts().erc20_transfer_history(contract_address, startblock=last_block))
            length = len(history)
            history.sort_values(by=['timeStamp'], axis=0, inplace=True, ignore_index=True)
            last_block = history.iloc[-1]['blockNumber']
            history2 = history[history['blockNumber']!=last_block]
            if len(history) == 10000:
                history_total = pd.concat([history2, history_total], axis=0)
            else:
                history_total = pd.concat([history, history_total], axis=0)

        # be sure it is sorted in order by timeStamp
        history_total.sort_values(by=['blockNumber', 'timeStamp'], axis=0, ascending=[True, True], inplace=True, ignore_index=True)

        # write history_total to a csv
        history_total.to_csv(file_path)

        return history_total

    # function to pull in associated wallets (sent or received tokens from these addresses)
    def associate_wallets(self, wallet, file_path):
        '''
        req'd:
        -wallet: the wallet address you want to analyze, type=str
        -file_path: the file location of the .csv file with the token's txn history
            NOTICE: Use 'erc20_txn_history' above and 'pd.to_csv()' to easily create a .csv if you don't have one already
        '''
    
        # the .csv that gets created from the above function is always in lower case
        wallet = str(wallet).lower()

        # read the csv
        history = pd.read_csv(file_path)

        # filter down the 'to' and 'from' columns to the desired wallet address
        fil = history[(history['to'] == wallet) | (history['from'] == wallet)]

        # create a list 'send' and 'receive' wallets with the amounts sent and received
        sent = list(set(fil['to'].values))
        receive = list(set(fil['from'].values))

        associations = {}
        sent_dict = {}
        received_dict = {}

        for assoc in sent:
            sent_dict[assoc] = fil[fil['to'] == assoc]['value'].astype('float').sum()*10**-18
        
        del sent_dict[wallet]

        for assoc in receive:
            received_dict[assoc] = fil[fil['from'] == assoc]['value'].astype('float').sum()*10**-18

        del received_dict[wallet]

        outs = sum(sent_dict.values())
        ins = sum(received_dict.values())
        balance = ins - outs
        
        associations = {
            'sent': sent_dict,
            'received': received_dict, 
            'current_balance': balance
        }


        return associations


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
        return int(res['result']) * 10**-18

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
