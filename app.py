import os
import json
import asyncio
import contextlib
from websockets import connect
from dotenv import load_dotenv
load_dotenv()

from config import (
    w3,
    RPC_URL_WSS,
    ABIs,
    TOKENS,
    ROUTERS,
    TEST_TX
)
from utils import (
    match
)
from parse import (
    parse_univ2_router_tx
)
from univ2 import (
    get_address,
    get_reservers,
    calc_reservers_given_out_supporting_on_fee
)

            
async def main():
    # async with connect(RPC_URL_WSS) as ws:
    #     await ws.send('{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}')
    #     while True:
    #         with contextlib.suppress(Exception):
    #             message = await asyncio.wait_for(ws.recv(), timeout=15)
    #             response = json.loads(message)
    #             txHash = response['params']['result']
    #             tx = w3.eth.get_transaction(transaction_hash=txHash)
    #             if match(tx.get('to'), ROUTERS.get('UNISWAP_V2')):
    #                 return
    
    if not (tx := w3.eth.get_transaction(transaction_hash=TEST_TX)):
        return
    if not (router_data_decoded := parse_univ2_router_tx(tx=tx)):
        return
    token_src = router_data_decoded['path'][0]
    token_dst = router_data_decoded['path'][1]
    amount_out_min = router_data_decoded['amountOutMin']
    pair_address = get_address(token_a=token_src, token_b=token_dst)
    reserve_src, reserve_dst = get_reservers(addr=pair_address, token_a=token_src, token_b=token_dst)
    amount_in, new_rsv_src, new_rsv_dst = calc_reservers_given_out_supporting_on_fee(reserve_src=reserve_src, reserve_dst=reserve_dst, amount_out=amount_out_min)
    print(amount_in)
    
   

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()