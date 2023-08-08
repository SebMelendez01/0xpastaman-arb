from web3 import Web3
import os
from dotenv import load_dotenv
from addresses import ETHEREUM_TOKENS, ETHEREUM_POOLS, ETHEREUM_PRICE_AGGREGATORS, CHAINLINK_ABI

INFURA_API_KEY = os.getenv('INFURA_API_KEY')

def init_price_aggregators():
    price_aggregators = {}
    # infura_url = 'https://mainnet.infura.io/v3/{}'.format(INFURA_API_KEY)
    # web3 = Web3(Web3.HTTPProvider(infura_url))

    # for token in ETHEREUM_PRICE_AGGREGATORS:
    #     contract = web3.eth.contract(address=ETHEREUM_PRICE_AGGREGATORS[token][0], abi=CHAINLINK_ABI)
    #     price_aggregator[token] = contract

    return price_aggregators

def init_pools():
    pools = {}
    
    return pools