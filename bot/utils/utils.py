import numpy as np
from functools import reduce

def get_price_data(contract):
    latestData = contract.functions.latestRoundData().call()
    return latestData[1] / 1E8

def pad_string32(s):
    return s.zfill(64)

# Can speed up by looking at the first element
def concat(l):
    if all(isinstance(x, str) for x in l):
        # Elements are strings
        mapper = lambda x: pad_string32(x[2:])  # don't apply hex  
    else:
        # Elements are integers
        mapper = lambda x: pad_string32(hex(x)[2:])   # keep hex
        
    reducer = lambda x, y: x + y
    res = reduce(reducer, map(mapper, l))
    return res

def build_calldata(token_array_addresses, flashloanArr):
    length = np.count_nonzero(flashloanArr)

    #Get deployed Address
    print('Deployed Address:')
    reciever = pad_string32(input()[2:])

    #Get locations
    token_location = 0xe0
    amounts_loc = token_location + (0x20 + 0x20 * (length))
    modes_loc = amounts_loc + (0x20 + 0x20 * (length))
    params_loc = modes_loc + (0x20 + 0x20 * (length))

    #Convert to Strings
    token_location = pad_string32(hex(token_location)[2:])
    amounts_loc = pad_string32(hex(amounts_loc)[2:])
    modes_loc = pad_string32(hex(modes_loc)[2:])
    params_loc = pad_string32(hex(params_loc)[2:])

    #Arrays
    array_lengths = pad_string32(hex(length)[2:])
    token_address = concat(token_array_addresses) ##Currently one value
    amount = concat(flashloanArr)

    mode  = "0000000000000000000000000000000000000000000000000000000000000000"
    modes = mode * length
    params = "0000000000000000000000000000000000000000000000000000000000000000"


    calldata = "0x7b5C526B7F8dfdff278b4a3e045083FBA4028790ab9c4b5d{}{}{}{}{}{}0000000000000000000000000000000000000000000000000000000000000000{}{}{}{}{}{}{}".format(
            reciever, 
            token_location,
            amounts_loc,
            modes_loc,
            reciever,
            params_loc,
            array_lengths,
            token_address,
            array_lengths,
            amount,
            array_lengths,
            modes,
            params
        )
    print(calldata)
