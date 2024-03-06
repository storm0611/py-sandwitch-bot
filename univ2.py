from eth_abi.packed import encode_packed
from config import (
    w3,
    ABIs
)
from utils import match

# Python implementation of https://github.com/Uniswap/uniswap-v2-periphery/blob/master/contracts/libraries/UniswapV2Library.sol#L17-L26
# We need "factory_address" and "init_code_hash" configuration to make it work in different environments (Uniswap, Sushiswap etc...)
class HashService:

    @staticmethod
    def for_uniswap():
        return HashService(
            factory_address='0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
            init_code_hash='0x96e8ac4277198ff8b6f785478aa9a39f403cb768dd02cbee326c3e7da348845f',
        )

    @staticmethod
    def for_pancake_swap():
        return HashService(
            factory_address='0xBCfCcbde45cE874adCB698cC183deBcF17952812',
            init_code_hash='0xd0d4c4cd0848c93cb4fd1f498d7013ee6bfb25783ea21593d5834f5d250ece66',
        )

    def __init__(self, factory_address: str, init_code_hash: str):
        self.init_code_hash = init_code_hash
        self.factory_address = factory_address

    def calculate_pair_adress(self, tokenA, tokenB):
        tokenA = w3.to_checksum_address(tokenA)
        tokenB = w3.to_checksum_address(tokenB)

        tokenA_hex = bytes.fromhex(tokenA[2:])
        tokenB_hex = bytes.fromhex(tokenB[2:])
        if tokenA_hex < tokenB_hex:
            token0 = tokenA
            token1 = tokenB
        else:
            token1 = tokenA
            token0 = tokenB
        b_salt = w3.keccak(encode_packed(['address', 'address'], [token0, token1]))

        pre = '0xff'
        b_pre = bytes.fromhex(pre[2:])
        b_address = bytes.fromhex(self.factory_address[2:])
        b_init_code = bytes.fromhex(self.init_code_hash[2:])
        b_result = w3.keccak(
            encode_packed(['bytes', 'bytes', 'bytes', 'bytes'], [b_pre, b_address, b_salt, b_init_code]))
        result_address = w3.to_checksum_address(b_result[12:].hex())
        return result_address, token0, token1

# Sorts tokens
def sort_tokens(token_a, token_b):
    return (token_a, token_b) if token_a < token_b else [token_b, token_a]

# Computes pair addresses off-chain
def get_address(token_a, token_b):
    token_a, token_b = sort_tokens(token_a, token_b)
    return HashService.for_uniswap().calculate_pair_adress(
        tokenA=token_a, tokenB=token_b
    )[0]
    
def get_reservers(addr, token_a, token_b):
    if ABIs.get('IUniswapV2Pair', None) is None:
        print('IUniswapV2Pair ABI Not Found')
        return 0, 0
    abi_types = ABIs.get('IUniswapV2Pair')
    try:
        pair_contract = w3.eth.contract(address=addr, abi=abi_types)
    except Exception:
        return 0, 0
    reserves = pair_contract.functions.getReserves().call()
    token0, token1 = sort_tokens(token_a, token_b)
    if match(token_a, token0):
        return reserves[0], reserves[1]
    else:
        return reserves[1], reserves[0]
    
def calc_reservers_given_out_supporting_on_fee(reserve_src, reserve_dst, amount_out):
    new_reserve_dst = reserve_dst - amount_out
    if new_reserve_dst < 0 or new_reserve_dst > reserve_dst:
        new_reserve_dst = 1
    
    numerator = reserve_src * amount_out * 1000
    denominator = new_reserve_dst * 997
    amount_in = numerator // denominator + 1
    
    new_reserve_src = reserve_src + amount_in
    if new_reserve_src < reserve_src:
        new_reserve_src = 2 ** 255 - 1
    
    return amount_in, new_reserve_src, new_reserve_dst