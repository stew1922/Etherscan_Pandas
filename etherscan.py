# this file willl utilize API endpoints from the Ethereum block explorer Etherscan.io

import pandas as pd
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


# first endpoint is Accounts
class Accounts:

    # instantiate the class with the module identifier and what network to connect to (by defalut set to "main", aka mainnet)
    def __init__(self, module='account', network='main'):
        self.module = module
        self.url = networks[network]
    
    # function to get ether balance from a given address(es)
    def get_eth_balance(self, address, tag='latest', api_key=api_key):
        '''
        req'd:
        -address: if only single address balance is desired then the wallet address for the balance you wish to pull, str
                  if multiple address are desired then a list of the addresses to be pulled, list of strings
                  **IF multiple addresses passed, no more than 20 at one time

        optional:
        -tag: Etherscan.io predifined block parameter, either "earliest", "pending" or "latest"
                **set to "latest" by default
        '''
        
        # if a list of addresses is given, then call the multiple address endpoint, otherwise use the single address endpoint
        if type(address) == list:
            if len(address) > 20:
                raise Exception('No more than 20 addresses can be provided for a single call')
            address = ','.join(address)
            action = 'balancemulti'
        else:
            action = 'balance'

        # define the url from the instantiation
        url = self.url

        # define the params to be passed in the request
        params = {
            'module': self.module,
            'action': action,
            'address': address,
            'tag': tag,
            'apikey': api_key
        }

        # send the request
        res = requests.post(url, params=params).json()

        # return the info, converting wei into ETH
        if action == 'balance':
            return int(res['result'])*10**-18
        else:
            balances = {}
            for balance in res['result']:
                balances[balance['account']] = int(balance['balance'])*10**-18
            return balances

    # function to get a list of 'normal' txns by address
    def get_txns(self, address, kind, startblock=0, endblock=None, page=None, offset=None, sort='asc'):
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

        # define the  url from instansiation
        url = self.url

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
        res = requests.post(url, params).json()

        # return the info
        if res['message'] == 'No transactions found':
            return "No transactions found"
        else:
            return res['result']



