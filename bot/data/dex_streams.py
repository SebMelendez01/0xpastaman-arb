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
from typing import Dict, Optional, Any
from web3 import  Web3, WebsocketProvider
from data.dex import DEX, CFMM_TYPE, TOKEN
from data.utils import reconnecting_websocket_loop

from dotenv import load_dotenv

load_dotenv()
INFURA_API_KEY = os.getenv('INFURA_API_KEY')

    



class DexStream:
    """
    Dex Streams aysnconously update the reserve data
    listen to sync even for specific dex contracts
    """

    def __init__(
            self,
            dex_dict: Dict[str, DEX],
            ws_endpoint: str,
            publisher: Optional[aioprocessing.AioQueue] = None,
            #  message_formatter: Callable = default_message_format,
            debug: bool = True
    ):
        self.dex_dict = dex_dict
        self.ws_endpoint = ws_endpoint
        self.publisher = publisher
        self.web3 = Web3(WebsocketProvider(ws_endpoint))
        self.debug = debug
    
    def publish(self, data: Any):
        if self.publisher:
            self.publisher.put(data)

    def handle_update_reserves(self, address, reserves):
        dex = self.dex_dict[address]
        for index, reserve in enumerate(reserves):
            reserves[index] = reserve / (10 ** dex.tokens[index].unit_conversion)
        return self.dex_dict[address].update_reserves(reserves)

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
        prices = [None] * 5 # NEED TO SET DYNAMICALLY
        for _, value in self.dex_dict.items():
            for token in value.tokens:
                prices[token.global_index - 1] = token.get_spot_price() 
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
    async def stream_uniswap_v2_sync_events(self):
        sync_event_selector = self.web3.keccak(
            text='Sync(uint112,uint112)'
        ).hex()
        pools =  list(self.dex_dict.keys())
        

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

