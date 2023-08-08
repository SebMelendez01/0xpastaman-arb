from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
INFURA_API_KEY = os.getenv('INFURA_API_KEY')


# Change this to use your own RPC URL
infura_url = 'https://mainnet.infura.io/v3/{}'.format(INFURA_API_KEY)
web3 = Web3(Web3.HTTPProvider(infura_url))
# AggregatorV3Interface ABI
abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
# Price Feed address
addr = '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419'

# Set up contract instance
contract = web3.eth.contract(address=addr, abi=abi)
# Make call to latestRoundData()
print(contract)
latestData = contract.functions.latestRoundData().call()
print(latestData)
#https://docs.chain.link/data-feeds/price-feeds/addresses

"""
1. load all the contracts at runtime for all assets then every so often query the feeds asynconously and
   and update using locks
"""

