// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.13;

contract FlashLoanReceiver {
    /*
        Notes: 
        1. The below contract is an example of a golfed Aave Flashloan Contract
        2. There is no security implemented so using this in a mainnet MEV contract can be risky as anyone can access the below code 
        Assumptions:
        1. The contract has access to enough tokens to send premiums
        Optimizations:
        [X] switch mload to msize
        [X] send the calldata already formalized and use calldatacopy to effeciently place into memory
        [ ] Find effecient encoding of calldata to decrease size while keeping abstaction (is this possible, i.e. with a hash?) [Max gas to send calldata: 7232]
        [ ] Optimize default case and for loop
        [ ] Use Jumpi opcode
        [ ] Store3 i.e. store in a separate contract cheaper to read
        
        can you send a hash of the value to decrease the size of the calldata, and then unhash the value using the hash function? 
    */

    fallback() external payable {
        assembly {
            // You can only access teh fallback function if you're authorized
            // if iszero(eq(caller(), memUser)) {
                // Ohm (3, 3) makes your code more efficient
                // WGMI
                // revert(3, 3)
            // }

            // Arb should be saved in size contract code can save entire call data 
            let selector := shr(96, calldataload(0x0))
            switch selector
            case 0x7b5C526B7F8dfdff278b4a3e045083FBA4028790 {
                // Request Flashloan
                let b := msize() //adds a dup5
                let size := sub(calldatasize(), 0x14)
                calldatacopy(b, 0x14, size) // Where most of the gas is being used 
                let success := call(gas(), selector, 0, b, size, 0, 0) // Large gas call, Can I keep data as calldata instead of memory
            }
            default {
                // Execute Arb Here
                // ---             ---

                // Return funds with premium
                mstore (0x0, 0x095ea7b300000000000000000000000000000000000000000000000000000000)
                mstore (0x04, caller()) 
                let asset_loc := add(0x04, calldataload(0x04))
                let amounts_loc := add(0x24, calldataload(0x24))
                let premiums_loc := add(0x24, calldataload(0x44))
                let n := calldataload(asset_loc)
                asset_loc := add(0x20, asset_loc)
                
                for { let i := 0 } lt(i, n) { i := add(i, 1) } { 
                    mstore (0x24, add(calldataload(add(amounts_loc, mul(0x20, i))), calldataload(add(premiums_loc, mul(0x20,i))))) //we load then store is there away to just copy?
                    let success := call(gas(), calldataload(add(0xC4, mul(0x20, i))), 0, 0x0, 0x44, 0, 0)
                }
                mstore(0x0, true)
                return (0x0, 0x20)
            }
        }
    }
}

/*


// 0x920f5c84                                                          0x4
// 00000000000000000000000000000000000000000000000000000000000000a0    0x24    asset location
// 00000000000000000000000000000000000000000000000000000000000000e0    0x44    amount location
// 0000000000000000000000000000000000000000000000000000000000000120    0x64    premium location
// 0000000000000000000000008e4daaab32b37db32f3f21b1bd38160ef7511329    0x84    initiatior (address)
// 0000000000000000000000000000000000000000000000000000000000000160    0xA4    bytes location
// 0000000000000000000000000000000000000000000000000000000000000001    0xC4    assets.length
// 00000000000000000000000065afadd39029741b3b8f0756952c74678c9cec93    0xE4    asset[0]
// 0000000000000000000000000000000000000000000000000000000000000001    0x104   amounts.length
// 0000000000000000000000000000000000000000000000000000000000989680    0x124   amount[0]
// 0000000000000000000000000000000000000000000000000000000000000001    0x144   premiums.length
// 0000000000000000000000000000000000000000000000000000000000001388    0x164   premiums[0]
// 0000000000000000000000000000000000000000000000000000000000000000    0x184   bytes params

         0x920f5c84
0x04     00000000000000000000000000000000000000000000000000000000000000a0
0x24     0000000000000000000000000000000000000000000000000000000000000100
0x44     0000000000000000000000000000000000000000000000000000000000000160
0x64     000000000000000000000000d27ea43aeb637b096b4b0047d824bb7afc5d9501
0x84     00000000000000000000000000000000000000000000000000000000000001c0
0xA4     0000000000000000000000000000000000000000000000000000000000000002
0xC4     00000000000000000000000065afadd39029741b3b8f0756952c74678c9cec93
0xE4     00000000000000000000000065afadd39029741b3b8f0756952c74678c9cec93
0x104    0000000000000000000000000000000000000000000000000000000000000002
0x124    0000000000000000000000000000000000000000000000000000000000989680
0x144    0000000000000000000000000000000000000000000000000000000000989680
0x164    0000000000000000000000000000000000000000000000000000000000000002
0x184    0000000000000000000000000000000000000000000000000000000000001388
0x1A4    0000000000000000000000000000000000000000000000000000000000001388
0x1C4    0000000000000000000000000000000000000000000000000000000000000000

1. Deploy 
2. Fund 1 USDC to deployed contract
    220589. 441178
3. Call getFlashLoan from fallback
      [          20 bytes for pool address   ][ Call data for the next call]
    0x7b5C526B7F8dfdff278b4a3e045083FBA4028790
    
    -------- FLASHLOAN CALL DATA --------
    0xab9c4b5d
    000000000000000000000000[9d7f74d0c41e726ec95884e0e97fa6129e3b5e99]   Receiver
    00000000000000000000000000000000000000000000000000000000000000e0   Token Array Location
    0000000000000000000000000000000000000000000000000000000000000120   Amounts Array Location
    0000000000000000000000000000000000000000000000000000000000000160   Modes Array Location
    000000000000000000000000[9d7f74d0c41e726ec95884e0e97fa6129e3b5e99]   OnBehalfOf
    00000000000000000000000000000000000000000000000000000000000001a0   Params Location
    0000000000000000000000000000000000000000000000000000000000000000   Referral Code
    0000000000000000000000000000000000000000000000000000000000000001   Token Array Length
    00000000000000000000000065afadd39029741b3b8f0756952c74678c9cec93   Token[0]
    0000000000000000000000000000000000000000000000000000000000000001   Amounts Array length
    0000000000000000000000000000000000000000000000000000000000989680   Amount[0]
    0000000000000000000000000000000000000000000000000000000000000001   Modes Array Length
    0000000000000000000000000000000000000000000000000000000000000000   Modes[0]
    0000000000000000000000000000000000000000000000000000000000000000   Params


*/