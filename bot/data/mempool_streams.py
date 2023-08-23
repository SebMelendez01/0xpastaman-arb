import os
import json
import asyncio
import aioprocessing
import urllib.request 
from typing import List, Optional, Any
from web3 import  Web3, WebsocketProvider
from data.dex import DEX, CFMM_TYPE, TOKEN



from dotenv import load_dotenv

load_dotenv()
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')


class MempoolStream:
    def __init__(
            self, 
            ws_endpoint: str,
            publisher: Optional[aioprocessing.AioQueue] = None,

        ):
        with urllib.request.urlopen("https://unpkg.com/@uniswap/v2-periphery@1.1.0-beta.0/build/IUniswapV2Router02.json") as url:
            router_abi = json.load(url)["abi"]
        with urllib.request.urlopen("https://unpkg.com/@uniswap/v2-core@1.0.0/build/IUniswapV2Factory.json") as url:
            factory_abi = json.load(url)["abi"]
        with urllib.request.urlopen("https://gist.githubusercontent.com/veox/8800debbf56e24718f9f483e1e40c35c/raw/f853187315486225002ba56e5283c1dba0556e6f/erc20.abi.json") as url:
            self.erc20_abi = json.load(url)

        self.ws_endpoint = ws_endpoint
        self.web3 = Web3(WebsocketProvider(ws_endpoint))
        # Set Router
        self.router_addr = self.web3.to_checksum_address('0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D')
        self.router_contract = self.web3.eth.contract(address=self.router_addr, abi=router_abi)

        # Set Factory
        self.factory_addr = self.web3.to_checksum_address('0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f')
        self.factory_contract = self.web3.eth.contract(address=self.factory_addr, abi=factory_abi)
        self.publisher = publisher

        self.dex_list = []


    """
    1. Needs to redesign how a DexStream Adds a dex. It should be initialized to values of null
       or with USDC and USDT WETH pools and as the mempool see more tokens being used we can 
       call the add function such that a DEX is added and watched by the DexStream and the TokenStream
       https://ethereum.org/en/developers/docs/standards/tokens/erc-20/
    """
    def publish(self, data: Any):
        if self.publisher:
            self.publisher.put(data)

    # def get_token_data(self, address):
    #     if address not in self.token_list:
    #         self.num_tokens += 1
        
    #     address = self.web3.to_checksum_address(address)
    #     erc20 = self.web3.eth.contract(address=address, abi=self.erc20_abi)
    #     decimals = erc20.functions.decimals().call()
    #     symbol = erc20.functions.symbol().call()
    #     return {
    #         "global_index" : self.num_tokens,
    #         "symbol" : symbol,
    #         "decimals" : decimals,
    #         "address" : address
    #     }


    def handle_event(self, event):
        try:
            transaction = Web3.to_json(event).strip('"')
            transaction = self.web3.eth.get_transaction(transaction)
            to = transaction['to']

            if to == self.router_addr:
                input_data = transaction['input']
                decode = self.router_contract.decode_function_input(input_data)
                if "path" in decode[1]:
                    # print(decode[1]["path"])
                    if len(decode[1]["path"]) == 2: 
                        token0 = self.web3.to_checksum_address(decode[1]["path"][0])
                        token1 = self.web3.to_checksum_address(decode[1]["path"][1])
                        uniswapv2_addr = self.factory_contract.functions.getPair(
                            token0,
                            token1
                        ).call()
                        data = {
                            "type" : CFMM_TYPE.UNISWAPV2.value,
                            "tokens" : [
                                token0, 
                                token1
                            ],
                            "address" : uniswapv2_addr

                        }
                        # Send data to Dexstream to be added
                        if uniswapv2_addr not in self.dex_list and uniswapv2_addr != "0x0000000000000000000000000000000000000000":
                            self.dex_list.append(uniswapv2_addr)
                            print("publishing")

                            self.publish(data)
                    """
                    1. Take path addresses and build dex's dynamically
                    2. Need to redesign tokens structure as well as 
                    """

        except Exception as err:
            pass
            # print(f'error: {err}')
            

        # .find O(n)
        # .count O(n)
        # .__contains__([])
        # has_key()


    async def stream_txn_from_mempool(self):
        tx_filter = self.web3.eth.filter('pending')

        while True:
            for event in tx_filter.get_new_entries():
                self.handle_event(event)
            await asyncio.sleep(2)

    def main(self):
        # filter for pending transactions
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.gather(
                    self.stream_txn_from_mempool()))
        finally:
            loop.close()


if __name__ == '__main__':
    alchemy_ws = f"wss://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
   

    mempool = MempoolStream(alchemy_ws)
    mempool.main()







