import json
import asyncio
import websockets
import aioprocessing
from typing import Dict, Any, Optional
from data.dex import TOKEN
from data.utils import reconnecting_websocket_loop





class TokenStream:
    """
    Token Streams async update the price data of the tokens
    https://www.coinbase.com/settings/api
    https://help.coinbase.com/en/prime/trading-and-funding/supported-cryptocurrencies-and-trading-pairs
    https://api.exchange.coinbase.com/products/USDT-USD/ticker
    """
    def __init__(
            self, 
            tokens: Dict[str, TOKEN],
            ws_endpoint: str,
            publisher: Optional[aioprocessing.AioQueue] = None
    ):
        self.tokens = tokens
        self.ws_endpoint = ws_endpoint
        self.publisher = publisher

    def publish(self, data: Any):
        if self.publisher:
            self.publisher.put(data)

    def start_streams(self):
        streams = []
        token_stream = reconnecting_websocket_loop(
            self.stream_token_prices,
            tag='Token Stream'
        )
        streams.extend([asyncio.ensure_future(f) for f in [token_stream]])

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(streams))

    def create_product_ids(self, token: str):
        if(token != 'USDC'):
            return f"{token}-USD"
    
    async def stream_token_prices(self):
        product_ids = list(filter(lambda x: x != None, map(lambda x: f"{x}-USD" if x != 'USDC' else None, self.tokens.keys()))) 
        subscription = {
            "type": "subscribe",
            "channels": [
                {
                    "name": "ticker",
                    "product_ids": product_ids
                }
            ]
        }
        async with websockets.connect(self.ws_endpoint) as ws:
       
            await ws.send(json.dumps(subscription))
            _ = await ws.recv()

            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=60 * 10)
                price_data = json.loads(msg)
                symbol = price_data["product_id"].split("-")[0]
                spot = float(price_data["price"])
                if self.tokens[symbol].update_stop_price(spot):
                    print("TO DO: SEND MESSAGE")
                

if __name__ == "__main__":
    queue = aioprocessing.AioQueue()
    token0 = TOKEN("ETH", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 1, 18)
    token1 = TOKEN("USDT", "0xdAC17F958D2ee523a2206206994597C13D831ec7", 2, 6)
    tokenstream = TokenStream(
        {
            "ETH": token0, 
            "USDT": token1
        },
        'wss://ws-feed.exchange.coinbase.com',
        queue
    )
    
    asyncio.run(tokenstream.stream_token_prices())

#LP Trading
