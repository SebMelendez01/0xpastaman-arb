# NOTE: 
This repo is in developement and therefore this project is currently not made to be cloned as well as the readme is a culmination of notekeeping and thought process

### Useful Routing Problem Links
#
[Python Example](https://github.com/angeris/cfmm-routing-code/tree/master)\
[Paper](https://angeris.github.io/papers/cfmm-routing.pdf)\
[Julia Example](https://bcc-research.github.io/CFMMRouter.jl/dev/)

### YUL Hacks
#
[Advanced Solidity](https://github.com/androlo/solidity-workshop/blob/master/tutorials/2016-03-09-advanced-solidity-I.md)
### To Do
#
- [X] Understand Price Vector
- [ ] Async dex data aggregator
- [ ] Flashbots/Private Node 
- [ ] `JUMPI` for execution path instead of `switch selector`
- [ ] Golfed swap code
- [X] Return multiple tokens flashloan code

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



