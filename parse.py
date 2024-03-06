from config import (
    ROUTERS,
    TOKENS
)
from utils import match
from eth_abi import abi
from config import w3
from config import ABIs

def parse_univ2_router_tx(tx):
    if ABIs.get('UniswapV2Router02', None) is None:
        print('UniswapV2Router02 ABI Not Found')
        return
    abi_types = ABIs.get('UniswapV2Router02')
    
    if not match(tx.get('to'), ROUTERS.get('UNISWAP_V2')):
        return None
    
    data = None
    try:
        data = w3.eth.contract(abi=abi_types).decode_function_input(tx.input)
        if 'swapExactETHForTokens' in data[0].fn_name:
            data = data[1]
            data['userAmountIn'] = tx.value
            return data
        elif 'swapExactTokensForTokens' in data[0].fn_name and match(data[1]['path'][0], TOKENS.get('WETH')):
            data = data[1]
            data['userAmountIn'] = data['amountIn']
            return data
    except Exception:
        return None
    return None
