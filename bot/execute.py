import os
import asyncio
import aioprocessing
from multiprocessing import Process
# from data import DEX, TOKEN, CFMM_TYPE, DexStream, TokenStream
from data.dex import DEX, TOKEN, CFMM_TYPE
from data.dex_streams import DexStream
from data.token_streams import TokenStream
from dotenv import load_dotenv
from addresses import UNISWAP_ABI

load_dotenv()
INFURA_API_KEY = os.getenv('INFURA_API_KEY')

async def main():
    print("TO DO")

if __name__ == '__main__':
    infura_ws = f"wss://mainnet.infura.io/ws/v3/{INFURA_API_KEY}"
    queue = aioprocessing.AioQueue()

    ETH = TOKEN("ETH", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 1, 18)
    USDT = TOKEN ("USDT", "0xdAC17F958D2ee523a2206206994597C13D831ec7", 2, 6)
    USDC = TOKEN("USDC", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 3, 6)
    DAI = TOKEN ("DAI", "0x6B175474E89094C44Da98b954EedeAC495271d0F", 4, 18)
    AAVE = TOKEN ("AAVE", "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9", 5, 18)

    ETH_USDT = DEX(UNISWAP_ABI, CFMM_TYPE.UNISWAPV2, "0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852", ['ETH', 'USDT'], .997, [ETH, USDT], infura_ws)
    USDC_ETH = DEX(UNISWAP_ABI, CFMM_TYPE.UNISWAPV2, "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc", ['USDC', 'ETH'], .997, [USDC, ETH], infura_ws)
    DAI_USDC = DEX(UNISWAP_ABI, CFMM_TYPE.UNISWAPV2, "0xAE461cA67B15dc8dc81CE7615e0320dA1A9aB8D5", ['DAI', 'USDC'], .997, [DAI, USDC], infura_ws)
    AAVE_ETH = DEX(UNISWAP_ABI, CFMM_TYPE.UNISWAPV2, "0xDFC14d2Af169B0D36C4EFF567Ada9b2E0CAE044f", ['AAVE', 'ETH'], .997, [AAVE, ETH], infura_ws)
    
    dex_stream = DexStream(
        {
            ETH_USDT.get_address().lower(): ETH_USDT,
            USDC_ETH.get_address().lower(): USDC_ETH,
            DAI_USDC.get_address().lower(): DAI_USDC,
            AAVE_ETH.get_address().lower(): AAVE_ETH
        },
        infura_ws,
        queue
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
        queue
    )
    # token_stream.start_streams()
    dex_stream.start_streams()
    # asyncio.run()

    # token0.update_stop_price(1.02334)
    # print(f"Token0 price:    {token0.get_spot_price()}")
    # print(f"token Stream price:    {token_stream.tokens['ETH'].get_spot_price()}")
    
    # dex.get_reserves()
    # dex.update_reserves([10000, 1242345])
    # dex.get_reserves()

    # asyncio.run()