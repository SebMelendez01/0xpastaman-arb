# import json
import sys
import json
# sys.path.append('../utils') 
sys.path.append('/Users/sebastianmelendez/Desktop/Projects/0xpastaman-bot/bot/data') 
# from utils import pad_string32, build_calldata, concat
from julia import Main
Main.include("../utils/utils.jl")
import requests

# import requests
 
# def fetch_data():
#     url = "https://rest.coinapi.io/v1/exchangerate/USDC/USD"
#     headers = {
#         "X-CoinAPI-Key": "6BA639D2-585E-4743-AE11-68FDD72EA22F" # Replace with your API key
#     }
#     response = requests.get(url, headers=headers)
#     return response.json()
 
# print(fetch_data())

# print(TOKENS)
# from addresses.ethereum import TOKENS as ETHEREUM_TOKENS
# from addresses.ethereum import POOLS as ETHEREUM_POOLS
"""
Notes:
Need to know: 
    1. Reserves
    2. Fee
    3. Tokens in that pool (as an index)
    4. Which Pool i.e. (0x0d4f...)
"""

"""
Test 1
"""
# print("TEST 1: ")
# ETH_USDT = ([17211.143709019695896738, 32095310.257553], .997, [1, 2])
# USDC_ETH = ([29114885.392256, 15654.757443890438424937], .997, [3, 1])
# DAI_USDC = ([10843872.083360015921060170, 10839678.889185], .997, [4, 3])
# PEPE_ETH = ([3550980725573.515105019682341127, 2835.342137754972254531], .997, [5, 1])
# types = [("ProductTwoCoin", 0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852), ("ProductTwoCoin", 0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc), ("ProductTwoCoin", 0xAE461cA67B15dc8dc81CE7615e0320dA1A9aB8D5), ("ProductTwoCoin", 0xA43fe16908251ee70EF74718545e4FE6C5cCEc9f)]
# pools = [ETH_USDT, USDC_ETH, DAI_USDC, PEPE_ETH]
# prices = [1876.56, .9997, 1, .9997, .000001343] 


# data = json.loads(Main.f(types , pools, prices))
# print(json.dumps(data, indent=4))

"""
Test 2
"""
# print("TEST 2: ")
# equal_pool = ([1e6, 1e6], 1, [1, 2])
# unequal_small_pool = ([1e3, 2e3], 1, [1, 2])
# weighted_pool = ([1e4, 2e4], [.4, .6], 1, [1, 2])
# types = [("ProductTwoCoin", 0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852), ("ProductTwoCoin", 0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc), ("GeometricMeanTwoCoin", 0xAE461cA67B15dc8dc81CE7615e0320dA1A9aB8D5),]
# pools = [unequal_small_pool, equal_pool, weighted_pool]
# prices = [1, 1] 

# data = json.loads(Main.f(types , pools, prices))
# print(json.dumps(data, indent=4))

"""
Test 3
"""
# print("TEST 3: ")
# pool1 = ([10, 5], .997, [1, 2])
# pool2 = ([1, 10], .997, [2, 3])
# pool3 = ([10, 50], .997, [3, 4])
# pool4 = ([20, 40], .997, [4, 3])
# types = [("ProductTwoCoin", "0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852"), ("ProductTwoCoin", "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"), ("ProductTwoCoin", "0xAE461cA67B15dc8dc81CE7615e0320dA1A9aB8D5"), ("ProductTwoCoin", "0xA43fe16908251ee70EF74718545e4FE6C5cCEc9f")]
# pools = [pool1, pool2, pool3, pool4]
# prices = [1, 10, 2, 3] 

# Main.f(types , pools, prices)
# data = json.loads(Main.f(types , pools, prices))
# print(json.dumps(data, indent=4))

"""
Build the calldata for the flashload
"""

# token_addresses = ["0x65afadd39029741b3b8f0756952c74678c9cec93", "0x2E8D98fd126a32362F2Bd8aA427E59a1ec63F780"]
# build_calldata(token_addresses, [10000000, 10000000])