import os
import sys
import json
import time
import getopt
import signal
import asyncio
import functools
import aioprocessing
import multiprocessing
from typing import Optional
from multiprocessing import Process

from addresses import UNISWAP_ABI
from data.dex_streams import DexStream
from data.token_streams import TokenStream
from data.dex import DEX, TOKEN, CFMM_TYPE
from data.utils import reconnecting_websocket_loop

from dotenv import load_dotenv


from julia import Main
Main.include("./utils/utils.jl")

load_dotenv()
INFURA_API_KEY = os.getenv('INFURA_API_KEY')

# def signal_handler(sig, frame):
#    
#     # get all active child processes
#     children = multiprocessing.active_children()
#     for child in children:
#         print(f"Killing Child Process: {child.pid}")
#         child.kill()
#     exit(0)
class SignalHandler:
    KEEP_PROCESSING = True
    def __init__(self, publisher: aioprocessing.AioQueue):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.publisher = publisher

    def exit_gracefully(self, signum, frame):
        print('Program Shutting Down! Please Wait.')
        children = multiprocessing.active_children()
        for child in children:
            print(f"Killing Child Process: {child.pid}")
            child.kill()
        self.publisher.put(None)
        self.KEEP_PROCESSING = False


def start_streams(_dex_stream:DexStream = None, _token_stream:TokenStream = None):
        streams = []
        token_stream = reconnecting_websocket_loop(
            _token_stream.stream_token_prices,
            tag='Token Stream'
        ) 
        # if _token_stream != None else None
        
        dex_stream = reconnecting_websocket_loop(
            _dex_stream.stream_uniswap_v2_sync_events,
            tag='Dex Stream'
        ) 
        # if _dex_stream != None else None
        streams.extend([asyncio.ensure_future(f) for f in [token_stream, dex_stream]])

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(streams))
        loop.close()
 

def setup_streams(publisher: aioprocessing.AioQueue, debug:bool):
    infura_ws = f"wss://mainnet.infura.io/ws/v3/{INFURA_API_KEY}"
    infura_rpc = f"https://mainnet.infura.io/v3/{INFURA_API_KEY}"

    ETH = TOKEN("ETH", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 1, 18)
    USDT = TOKEN ("USDT", "0xdAC17F958D2ee523a2206206994597C13D831ec7", 2, 6)
    USDC = TOKEN("USDC", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 3, 6)
    DAI = TOKEN ("DAI", "0x6B175474E89094C44Da98b954EedeAC495271d0F", 4, 18)
    AAVE = TOKEN ("AAVE", "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9", 5, 18)

    ETH_USDT = DEX(UNISWAP_ABI, CFMM_TYPE.UNISWAPV2, "0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852", ['ETH', 'USDT'], .997, [ETH, USDT], infura_rpc)
    USDC_ETH = DEX(UNISWAP_ABI, CFMM_TYPE.UNISWAPV2, "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc", ['USDC', 'ETH'], .997, [USDC, ETH], infura_rpc)
    DAI_USDC = DEX(UNISWAP_ABI, CFMM_TYPE.UNISWAPV2, "0xAE461cA67B15dc8dc81CE7615e0320dA1A9aB8D5", ['DAI', 'USDC'], .997, [DAI, USDC], infura_rpc)
    AAVE_ETH = DEX(UNISWAP_ABI, CFMM_TYPE.UNISWAPV2, "0xDFC14d2Af169B0D36C4EFF567Ada9b2E0CAE044f", ['AAVE', 'ETH'], .997, [AAVE, ETH], infura_rpc)
    
    dex_stream = DexStream(
        {
            ETH_USDT.get_address().lower(): ETH_USDT,
            USDC_ETH.get_address().lower(): USDC_ETH,
            DAI_USDC.get_address().lower(): DAI_USDC,
            AAVE_ETH.get_address().lower(): AAVE_ETH
        },
        infura_ws,
        publisher,
        debug=debug
    )

    token_stream = TokenStream(
        {
            "ETH": ETH, 
            "USDT": USDT,
            "USDC": USDC,
            "DAI": DAI,
            "AAVE": AAVE
        },
        'wss://ws-feed.exchange.coinbase.com',
        publisher
    )
    start_streams(dex_stream, token_stream)
     
async def consume(subscriber: aioprocessing.AioQueue, signal_handler: SignalHandler, debug:bool):
    while signal_handler.KEEP_PROCESSING:
        data = await subscriber.coro_get()
        if data is None:
            break
        if(data["source"] == "dex"):
            """
            Simulate the opportunity with Convex Opt. in Julia
            """
            trades = json.loads(Main.f(data["pools"], data["prices"]))
            e = time.time()
            if debug:
                print(f"Time to simulate opportunity: {round((e - data['time']), 4)} seconds")
            # print(json.dumps(trades, indent=4))
            # pprint.pprint(data)
        

async def main(argv):
    debug = False
    opts, _ = getopt.getopt(argv,"hv",["debug"])
    for opt, _ in opts:
        if opt == '-h':
            print ('add -v or --debug flag for debug messages ')
            sys.exit()
        elif opt in ("-v", "--debug"):
            debug = True
    
    queue = aioprocessing.AioQueue()
    signal_handler = SignalHandler(queue)

    # Create and start streams
    streams = Process(target=setup_streams, args=(queue, debug,))
    streams.start()

    # Set up Consumer
    await consume(queue, signal_handler, debug)
    
    # Wait for streams to shut down
    streams.join()
    sys.exit()

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1:]))
