import os
import json
import time
import logging
import datetime
import eth_abi
import eth_utils
import asyncio
import websockets
import aioprocessing
import urllib.request 

from typing import Dict, Optional, Any, List
from web3 import  Web3, WebsocketProvider
from data.dex import DEX, CFMM_TYPE, TOKEN
from data.utils import reconnecting_websocket_loop

from dotenv import load_dotenv

load_dotenv()
INFURA_API_KEY = os.getenv('INFURA_API_KEY')

    
class DexStream:
    """
    Takes a group of Dex's and streams changes in reserves to update the reserves on a specific dex
    1. Speed to compute update is important, use O(1) access time instead of iterating over an array of DEXs
    2. Once an update occures need to dynamically get price data for each token, might be easier instead
       of updated token price in each token, keep token data as global with each array and ping for price data
       every time we need the array, can use pipes to ping. 
    """

    def __init__(
            self,
            rpc_endpoint: str,
            ws_endpoint: str,
            publisher: Optional[aioprocessing.AioQueue] = None,
            subscriber: Optional[aioprocessing.AioQueue] = None,
            debug: bool = False
    ):
        
        self.dex_dict ={}
        self.token_list = {}
        self.num_tokens = 0

        self.rpc_endpoint = rpc_endpoint
        self.ws_endpoint = ws_endpoint
        self.publisher = publisher
        self.subscriber = subscriber
        self.web3 = Web3(WebsocketProvider(ws_endpoint))
        self.debug = debug

        with urllib.request.urlopen("https://gist.githubusercontent.com/veox/8800debbf56e24718f9f483e1e40c35c/raw/f853187315486225002ba56e5283c1dba0556e6f/erc20.abi.json") as url:
            self.erc20_abi = json.load(url)
    

    """
    Publish data to be executed with Julia code
    """
    def publish(self, data: Any):
        if self.publisher:
            self.publisher.put(data)

    """

    {
        source : dex | coinbase
        prices : []
        pools : [
            {
                pool : ([reserves], fee, [global_index])
                type : CFMM.Type.value
                Address : 0x...
            }
        ]
    }

    """
    def message_format(self):
        pools = []
        
        prices = {}

        for _, value in self.dex_dict.items():
            for token in value.tokens:
                prices[token.global_index - 1] = token.get_price() 
            data = {
                "pool" : (value.get_reserves(), value.fee, list(token.global_index for token in value.tokens)),
                "type" : value.type.value,
                "address" : value.address
            }
            pools.append(data)
        
        return {
            'source': 'dex',
            "pools" : pools,
            "prices" : prices,
            "time" : time.time()
        }


    """
    Create Tokens 
    """
    def create_token(self, address):
        if address in self.token_list:
            return self.token_list[address]
        self.num_tokens += 1
        address = self.web3.to_checksum_address(address)
        erc20 = self.web3.eth.contract(address=address, abi=self.erc20_abi)
        decimals = erc20.functions.decimals()
        symbol = erc20.functions.symbol()
        
        self.token_list[address] = TOKEN(symbol, address, self.num_tokens, decimals)
        return self.token_list[address]
        

    """
    **TO DO**
        1. Make code *starts with a "a" but forgetting name... I think
    """
    def add_dex(self, address:str, type:CFMM_TYPE, tokens:List[TOKEN]):
        with urllib.request.urlopen("https://unpkg.com/@uniswap/v2-core@1.0.0/build/IUniswapV2Pair.json") as url:
            uniswapV2_abi = json.load(url)["abi"]
        if type == CFMM_TYPE.UNISWAPV2:
            self.dex_dict[address] = DEX(uniswapV2_abi, type, address, .997, tokens)
            print("The length of the dictionary is {}".format(len(self.dex_dict)))


    def get_type(self, _type):
        if _type == CFMM_TYPE.UNISWAPV2.value:
            return CFMM_TYPE.UNISWAPV2
        elif _type == CFMM_TYPE.UNISWAPV3.value:
            return CFMM_TYPE.UNISWAPV3
        elif _type == CFMM_TYPE.BALENCER.value:
            return CFMM_TYPE.BALENCER
        elif _type == CFMM_TYPE.CURVE.value:
            return CFMM_TYPE.CURVE
        
    async def stream_dex_data(self):
        print("Started stream_dex_data")
        while True:
            try: 
                data = await self.subscriber.coro_get()
                print(json.dumps(data, indent=4))
                if data["address"] not in self.dex_dict:
                    tokens = list(map(lambda x: self.create_token(x), data["tokens"]))
                    self.add_dex(data["address"], self.get_type(data["type"]), tokens)
            except Exception as err:
                # pass
                print(f'error: {err}')

    """
    Once Dexes are added 
    """
    def handle_update_reserves(self, address, reserves):
        dex = self.dex_dict[address]
        for index, reserve in enumerate(reserves):
            reserves[index] = reserve / (10 ** dex.tokens[index].decimals)
        return self.dex_dict[address].update_reserves(reserves)

    async def stream_uniswap_v2_sync_events(self):
        sync_event_selector = self.web3.keccak(
            text='Sync(uint112,uint112)'
        ).hex()
        
        

        async with websockets.connect(self.ws_endpoint) as ws:
            subscription = {
                'json': '2.0',
                'id': 1,
                'method': 'eth_subscribe',
                'params': [
                    'logs',
                    {'topics': [sync_event_selector]}
                ]
            }

            await ws.send(json.dumps(subscription))
            _ = await ws.recv()
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=60 * 10)
                event = json.loads(msg)['params']['result']
                address = event['address'].lower()
                pools =  list(self.dex_dict.keys()) ## Will need to add Semaphores
                print(address)
                print(pools)
                if address in pools:
                    s = time.time()
                    data = eth_abi.decode(
                        ['uint112', 'uint112'],
                        eth_utils.decode_hex(event['data'])
                    )
                    """
                    Publish the data everytime there is a change in the reserves of 
                    a specific dex in a standard format do that is can be processed.

                    Bot processes data by consuming the queue and checking if the 
                    current message
                    """
                    if self.handle_update_reserves(address, list(map(int, data))):
                        
                        self.publish(self.message_format())#**TO DO** Create Standard Message Formate
                        # print("TO DO: SEND MESSAGE")
                    e = time.time()
                    if self.debug:
                        dbg_msg = self.dex_dict[address].debug_message()
                        print(f'{datetime.datetime.now()} {dbg_msg} -> Update took: {round((e - s), 6)} seconds')


        #https://docs.alchemy.com/reference/best-practices-for-using-websockets-in-web3
    
if __name__ == "__main__":
    uniswap_pair_abi = '[{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Burn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount0Out","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1Out","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Swap","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint112","name":"reserve0","type":"uint112"},{"indexed":false,"internalType":"uint112","name":"reserve1","type":"uint112"}],"name":"Sync","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":true,"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"MINIMUM_LIQUIDITY","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"burn","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_token0","type":"address"},{"internalType":"address","name":"_token1","type":"address"}],"name":"initialize","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"kLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"mint","outputs":[{"internalType":"uint256","name":"liquidity","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"price0CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"price1CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"skim","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount0Out","type":"uint256"},{"internalType":"uint256","name":"amount1Out","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"swap","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"sync","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]'
    infura_ws = f"wss://mainnet.infura.io/ws/v3/{INFURA_API_KEY}"
    token0 = TOKEN("ETH", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 1, 18)
    token1 = TOKEN ("USDT", "0xdAC17F958D2ee523a2206206994597C13D831ec7", 2, 6)

    dex = DEX(
        uniswap_pair_abi,
        CFMM_TYPE.UNISWAPV2,
        "0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852",
        ['ETH', 'USDT'],
        .997,
        [token0, token1]
    )
    dex_stream = DexStream(
        {"0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852".lower(): dex},
        infura_ws,
    )
    
    
    asyncio.run(dex_stream.stream_uniswap_v2_sync_events())

