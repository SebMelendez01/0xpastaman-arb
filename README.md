# 0xpastaman-bot Overview
The goal of this project was to better understand the world of MEV specific arbitrage. This bot is not made to be put into production and compete in Arb opportunities. 

Now that we are past a disclaimer, lets get into it. This bot focuses on off-chain simulation for uniswap_v2 specifically solving the convex optimization problem of CFMMs. In order to compute if there is an opportunity two streams are set up, a `MempoolStream` and a `DexStream`, on a sub-process. Every time the reserve data is updated, i.e. `Sync(uint112,uint112)` event is detected, the main process computes if there is an opportunity.

The `TokenStream` is currently being fazed out for a more scalable `MempoolStream`.  The currently file for executing is `bot/execute.py`
## Current Problems
I have set up a mempool scraper but the transactions I am scraping are old and the pools that I am decoding from the mempool only have a single transaction. I need to get more up to date transactions from my mempool scraper. There may also be a blocking problem with how python works and setting up a `aioQueue` essentially a `pipe`. `.coro_get()` blocks as well as the websocket.[**TO DO LOOK INTO and see if it is a problem.**] Can set up a system test of and see if on of the aync streams is getting blocked. 
## Current Vunerablities
The bot currently does not take into account "poison tokens." Currently the transaction profit is not simulated on chain and therefore the bot risks submitting transactions to the network that will not be or were never valid. This can be fixed with the flashbots code by only calling `coinbase.transfer` if the transaction was profitable and everything succeeded. 
## Future Work and Next Steps
### Scaleing Option (CEX)
One way to scale is to do a little bit of upfront work and for a specific API/oracle get all of the tokens that can be queried for a specific price, then find all of the ERC20 addresses. Then use the factory address in order to get all of the viable pools. We can then create all of DEXs add the DEXs to the DEX stream and then we are able to ensure that each token price can be queried. This is less dynamic work and is more upfront. This would also create a significantly larger number of DEX's to run the simulation on and many of the pools we would be looking at would not actually contribute to finding an Arbitrage.
### **Scaling Option (MEMPOOL and CEX/Price Feed)**
#### CoinGeckoAPI
Updating the Framework: In order to scale the `DexStream` and `TokenStream` effeciently we need to dynaically get Dex's from the Mempool. We can do this by using a `filter` to look specifically for any `transaction` that interacts with the UniswapV2Router. We can then take the `path` function param and find all the paths that people are swaping through but calling the `FactoryV2` contract. We can then check if the token price exists on some API service, if it does we can add the tokens to both the `DexStream` and `TokenStream`.

Note: CoingeckoAPI doesn't allow me to get all to coins that I want. Need to figure out another solution. Instead of CoinGecko look  into [ANKR](https://www.ankr.com/docs/advanced-api/token-methods/#ankr_gettokenprice)

The bot currently does not scrape/listen to the mempool for DEX's/Tokens to add to the `DexStream` and `TokenStream`. The goal is to instead of using Coinbase API to get the token prices use CoinGeckoAPI as you can send the token address rather that the Ticker Symbol of the token. This will be more effecient and allow for the ability to get DEXs and tokens based on addresses rather than keeping a database to switch. If we are to use the CoinGeckoAPI although it would allow for us to get price data based on `address` we would need to poll for the data. Best way to do that is instead of set up a stream, every time reserves are updated we quickly request for all token prices async. If I go ahead with this I can turn the token stream into the Mempool stream. 

The issue with not constantly checking the price is that arbs can be created from a change in reserve amount on a dex but also a change in the token price on a CEX. By only getting price data when reserves changes we miss an opportunity. 
#### MORALIS (CURRENT SOLUTION)
This API allows me to query based on token address nearly any ERC20 token. It would be reliant on someone elses system but it would allow me to have a finished product and scalable system much faster. 

    payload = {
        "tokens": [
            {
                "token_address": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-API-Key": "API-KEY"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)


Use the moralis API and update the token price whenever the reserves are updated for the tokens in that dex. 

The issue with this is I am completely reliant on another technology for token price updates that do not seem to be the most accurrate and from a real time feed. Example is ETH has been staying at a price of $1616.03 which is off the price the actual price of 2 dollars. The data is said to be being pulled from UniV3 so this is possible and not out of the range of possibility but something to note. The price feeds may not be real time. 

### **Scaling Option (MEMPOOL and DEX)**
The final option is to instead of update the token price data from a centralized source we do it from the DEX data, everytime a pools reserve price is updated we would update the price data for those 2 tokens. This would make the price data significantly more volitile and we would want to run it through a Kalman filter as the price of a token should be somewhere around the range of all of the token prices every time they are updated. Assuming markets have some sort of effeciency. 

To get the price of a token I may be able to use this and update it every time a tokens comes in. The issue is I wouldn't be able to calculate the pruce until I have 2 Transactions in the pool. I would need to create a staging and a final. This may also be good because it would limit the DEXs that I look at to only ones with more that 2 transactions. I can remove DEXs from the Stageing area every `n` seconds if another transaction as not come in, this would be a sort of built in filter for pools trading more volume: https://docs.uniswap.org/contracts/v2/concepts/core-concepts/oracles


### Current implemenation 
Pools are required to be build by the user. This is not scalable and as more code is added this will be fixed. The currently contract implementation is only golfed AAVE flashloan calls. Uniswap FlashCall is also another option. We are also currently only looking at UniV2
# NOTES: 
This repo is in developement and therefore this project is currently not made to be cloned as well as the readme is a culmination of notekeeping and thought process. 

### Useful Routing Problem Links
#
[Python Example](https://github.com/angeris/cfmm-routing-code/tree/master)\
[Paper](https://angeris.github.io/papers/cfmm-routing.pdf)\
[Julia Example](https://bcc-research.github.io/CFMMRouter.jl/dev/)

### YUL Hacks
#
[Advanced Solidity](https://github.com/androlo/solidity-workshop/blob/master/tutorials/2016-03-09-advanced-solidity-I.md)
### To Do

- [ ] Flashbots/submit to builder 
- [ ] Successful submission to flashbots only if the opportunity is profitable (costs more gas)
- [ ] `JUMPI` for execution path instead of `switch selector`
- [ ] Golfed swap code
- [ ] A way to save the swap code calldata for when the contract is called back `sstore2` Lib

### Building Call Data
**Initiate Falshloan Calldata**

    0x7b5C526B7F8dfdff278b4a3e045083FBA4028790
    0x0      0xab9c4b5d
    0x0      000000000000000000000000[9d7f74d0c41e726ec95884e0e97fa6129e3b5e99]      Receiver
    0x20     00000000000000000000000000000000000000000000000000000000000000e0        Token Array Location
    0x40     0000000000000000000000000000000000000000000000000000000000000120        Amounts Array Location
    0x60     0000000000000000000000000000000000000000000000000000000000000160        Modes Array Location
    0x80     000000000000000000000000[9d7f74d0c41e726ec95884e0e97fa6129e3b5e99]      OnBehalfOf
    0xA0     00000000000000000000000000000000000000000000000000000000000001a0        Params Location
    0xC0     0000000000000000000000000000000000000000000000000000000000000000        Referral Code

    0xE0     0000000000000000000000000000000000000000000000000000000000000001        Token Array Length
    0x100    00000000000000000000000065afadd39029741b3b8f0756952c74678c9cec93        Token[0]
    0x120    0000000000000000000000000000000000000000000000000000000000000001        Amounts Array length
    0x140    0000000000000000000000000000000000000000000000000000000000989680        Amount[0]
    0x160    0000000000000000000000000000000000000000000000000000000000000001        Modes Array Length
    0x180    0000000000000000000000000000000000000000000000000000000000000000        Modes[0]
    0x1A0    0000000000000000000000000000000000000000000000000000000000000000        Params

    Amounts Array Location = Token Array Location + [0x20 + 0x20 * (Token Array Length)]
    Modes Array Location = Amounts Array Location + [0x20 + 0x20 * (Amounts Array Length)]
    Params Location = Modes Array Location + [0x20 + 0x20 * (Modes Array Length)]

### Helpful Testing links
[Alchemy Faucet](https://goerlifaucet.com/)\
[Quicknode Faucet](https://faucet.quicknode.com/ethereum/goerli/?transactionHash=0xda0fd34031eb81579af97ac7858fac659b88c791e87261fff2dec35188ad6b2f)\
[Ethereum Gas Opcodes](https://github.com/wolflo/evm-opcodes/tree/main)\
[Decompile Contracts](https://ethervm.io/decompile)\
[Gas Savings Tips](https://hackmd.io/@gn56kcRBQc6mOi7LCgbv1g/rJez8O8st)\
[SStore 2](https://github.com/0xsequence/sstore2)\
[Is Zero Gas Savings](https://twitter.com/transmissions11/status/1474465495243898885)\
[Sandwich Bot](https://github.com/libevm/subway/blob/master/contracts/src/Sandwich.sol)\
[Get Amount Out](https://goerli.etherscan.io/address/0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D#readContract)\
[Get Pair](https://goerli.etherscan.io/address/0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f#readContract)\
[Flashloan Pool](https://goerli.etherscan.io/address/0x7b5C526B7F8dfdff278b4a3e045083FBA4028790#readProxyContract)\
[TEST](https://goerli.etherscan.io/tx/0x9b076a762acd75e5a2f8f15984fa2acb6bc11a0c211e14aa84f4f5ed6a42fba7)\
[Uniswap Deployment Addresses](https://docs.uniswap.org/contracts/v3/reference/deployments)\
[Defi liq. Monotoring](https://medium.com/intotheblock/a-practical-guide-to-monitoring-liquidation-risk-in-defi-lending-protocols-aae26c95e3b8)

[CFMM zero to one](https://medium.com/bollinger-investment-group/constant-function-market-makers-defis-zero-to-one-innovation-968f77022159)\
[L1 L2 Hueristics](https://web.stanford.edu/class/ee364b/lectures/l1_slides.pdf)\
[CFMM Routing](https://angeris.github.io/papers/cfmm-routing.pdf)\
[Julia Routing Library](https://bcc-research.github.io/CFMMRouter.jl/dev/examples/arbitrage/)\
[Python Routing Example - angeris](https://github.com/angeris/cfmm-routing-code/tree/master)\
[Flashbots Convex Opt.](https://www.youtube.com/watch?v=v9liLt12jN8)\
[Python CFMM Example](https://gist.githubusercontent.com/noxx3xxon/11fd224d7b99b78ee1e4a914bf0cbd22/raw/376a854183d4f2fc27e06058cfda2c5ea8e32efc/arbitrage.py)\
[Mathmatical Opt. DEXs](https://noxx.substack.com/p/dex-arbitrage-mathematical-optimisations)\

[All about Assembly](https://jeancvllr.medium.com/solidity-tutorial-all-about-assembly-5acdfefde05c)\
[All amout Memory](https://betterprogramming.pub/solidity-tutorial-all-about-memory-1e1696d71ee4)\
[All about Calldata](https://betterprogramming.pub/solidity-tutorial-all-about-calldata-aebbe998a5fc)\
[Deconstructing Sol Contract](https://medium.com/zeppelin-blog/deconstructing-a-solidity-contract-part-vi-the-swarm-hash-70f069e22aef)\
[Hashing Strings](https://medium.com/@kalexotsu/understanding-solidity-assembly-hashing-a-string-from-calldata-fbd2ece82263)\

[First Key to building MEV bots](https://medium.com/@solidquant/first-key-to-building-mev-bots-your-simulation-engine-c9c0420d2e1)\
[MEV Arb Bot](https://github.com/solidquant/whack-a-mole/tree/examples/strategy/dex_arb_base/data)\
[How I built an arb bot](https://medium.com/@solidquant/how-i-built-my-first-mev-arbitrage-bot-introducing-whack-a-mole-66d91657152e)\

### Ideas 
[Zero MEV](https://info.zeromev.org/terms#toxic-arbitrage)\
1. Create the oppotunity by looking through the mempool and building a bundle that creates a larger arb opportunity 




