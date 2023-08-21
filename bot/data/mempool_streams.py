import os
import json
import urllib.request 
import asyncio
from web3 import  Web3, WebsocketProvider


from dotenv import load_dotenv

load_dotenv()
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')


class MempoolStreams:
    def __init__(self, ws_endpoint: str):
        with urllib.request.urlopen("https://unpkg.com/@uniswap/v2-periphery@1.1.0-beta.0/build/IUniswapV2Router02.json") as url:
            router_abi = json.load(url)["abi"]
        with urllib.request.urlopen("https://unpkg.com/@uniswap/v2-core@1.0.0/build/IUniswapV2Factory.json") as url:
            factory_abi = json.load(url)["abi"]

        self.ws_endpoint = ws_endpoint
        self.web3 = Web3(WebsocketProvider(ws_endpoint))
        # Set Router
        self.router_addr = self.web3.to_checksum_address('0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D')
        self.router_contract = self.web3.eth.contract(address=self.router_addr, abi=router_abi)

        # Set Factory
        self.factory_addr = self.web3.to_checksum_address('0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f')
        self.factory_contract = self.web3.eth.contract(address=self.factory_addr, abi=factory_abi)

    """
    1. Needs to redesign how a DexStream Adds a dex. It should be initialized to values of null
       or with USDC and USDT WETH pools and as the mempool see more tokens being used we can 
       call the add function such that a DEX is added and watched by the DexStream and the TokenStream
       https://ethereum.org/en/developers/docs/standards/tokens/erc-20/
    """
    """
    Create Token
    """

    """
    Create Dex
    """

    """
    Add to TokenStream
    1. Need to redesign the token way a token steam adds a token. 
    """

    """
    Add to DexStream
    """


    def handle_event(self, event):
        try:
            # remove the quotes in the transaction hash
            transaction = Web3.to_json(event).strip('"')
            # use the transaction hash (that we removed the '"' from to get the details of the transaction
            transaction = self.web3.eth.get_transaction(transaction)
            # set the variable to the "to" address in the message
            to = transaction['to']
            # if the to address in the message is the router
            if to == self.router_addr:
                input_data = transaction['input']
                # print the transaction and its details
                decode = self.router_contract.decode_function_input(input_data)
                if "path" in decode[1]:
                    # print(decode[1]["path"])
                    if len(decode[1]["path"]) == 2: 
                        uniswapv2_addr = self.factory_contract.functions.getPair(
                            self.web3.to_checksum_address(decode[1]["path"][0]),
                            self.web3.to_checksum_address(decode[1]["path"][1])
                        ).call()

                        print(uniswapv2_addr)
                    """
                    1. Take path addresses and build dex's dynamically
                    2. Need to redesign tokens structure as well as 
                    """

        except Exception as err:
            # print(f'error: {err}')

            # print transactions with errors. Expect to see transactions people submitted with errors
            return
        # https://ethereum.org/en/developers/docs/standards/tokens/erc-20/
        # .find O(n)
        # .count O(n)
        # .__contains__([])
        # has_key()


    async def log_loop(self, event_filter, poll_interval):
        while True:
            for event in event_filter.get_new_entries():
                self.handle_event(event)
            await asyncio.sleep(poll_interval)


    def main(self):
        # filter for pending transactions
        tx_filter = self.web3.eth.filter('pending')
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.gather(
                    self.log_loop(tx_filter, 2)))
        finally:
            loop.close()


if __name__ == '__main__':
    alchemy_ws = "wss://eth-mainnet.g.alchemy.com/v2/PppCDUBPWTBBaiTelkanToh_5Kc4kuA0"
   

    mempool = MempoolStreams(alchemy_ws)
    mempool.main()



