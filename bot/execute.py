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
from data.mempool_streams import MempoolStream
from data.dex import DEX, TOKEN, CFMM_TYPE
from data.utils import reconnecting_websocket_loop

from dotenv import load_dotenv


from julia import Main
Main.include("./utils/utils.jl")

load_dotenv()
INFURA_API_KEY = os.getenv('INFURA_API_KEY')
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')


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


def start_streams(_dex_stream:DexStream = None, _mempool_stream:MempoolStream = None):
        streams = []
        mempool_stream = reconnecting_websocket_loop(
            _mempool_stream.stream_txn_from_mempool,
            tag='Mempool Stream'
        ) 
        dex_stream = reconnecting_websocket_loop(
            _dex_stream.stream_uniswap_v2_sync_events,
            tag='Dex Stream'
        ) 
        dex_data_stream = reconnecting_websocket_loop(
            _dex_stream.stream_dex_data,
            tag='Dex Data Stream'
        ) 

        # if _dex_stream != None else None
        streams.extend([asyncio.ensure_future(f) for f in [dex_stream, mempool_stream, dex_data_stream]]) #dex_stream, , 

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(streams))
        loop.close()
 

def setup_streams(publisher: aioprocessing.AioQueue, debug:bool):
    infura_ws = f"wss://mainnet.infura.io/ws/v3/{INFURA_API_KEY}"
    infura_rpc = f"https://mainnet.infura.io/v3/{INFURA_API_KEY}"
    alchemy_ws = f"wss://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

    mempool_to_dexstream = aioprocessing.AioQueue()

    mempool_stream = MempoolStream(
        alchemy_ws,
        mempool_to_dexstream
    )
    dex_stream = DexStream(
        infura_rpc,
        infura_ws,
        publisher,
        mempool_to_dexstream,
        debug=debug
    )

    start_streams(dex_stream, mempool_stream)
     
async def consume(subscriber: aioprocessing.AioQueue, signal_handler: SignalHandler, debug:bool):
    while signal_handler.KEEP_PROCESSING:
        data = await subscriber.coro_get()
        if data is None:
            break
        if(data["source"] == "dex"):
            """
            Simulate the opportunity with Convex Opt. in Julia
            """
            # trades = json.loads(Main.f(data["pools"], data["prices"]))
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
    
    
    dexstream_to_comsumer = aioprocessing.AioQueue()
    signal_handler = SignalHandler(dexstream_to_comsumer)

    # Create and start streams
    streams = Process(target=setup_streams, args=(dexstream_to_comsumer, debug,))
    streams.start()

    # Set up Consumer
    await consume(dexstream_to_comsumer, signal_handler, debug)
    
    # Wait for streams to shut down
    streams.join()
    sys.exit()

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1:]))
