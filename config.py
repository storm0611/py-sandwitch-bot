import os
import json
from dotenv import load_dotenv
load_dotenv()

from web3 import Web3

RPC_URL_WSS = os.environ.get('RPC_URL_WSS')
ABIs = {}
TOKENS = {
    'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
}
ROUTERS = {
    'UNISWAP_V2': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
}
# TEST_TX = "0x97378d2725344481e61186b2c0edf88efef421bb56ceb8a7177a7108591f0d5e"
TEST_TX = "0x757e7747629474974320e83904363cace061d444f4363f07dc8a652561c084d6"

w3 = Web3(Web3.WebsocketProvider(endpoint_uri=RPC_URL_WSS, websocket_timeout=60))

with open(file=os.path.join(os.getcwd(), 'abi', 'IUniswapV2Router02.json'), mode='r') as f:
    data = json.load(f)
    ABIs['UniswapV2Router02'] = data
    f.close()
with open(file=os.path.join(os.getcwd(), 'abi', 'IUniswapV2Pair.json'), mode='r') as f:
    data = json.load(f)
    ABIs['IUniswapV2Pair'] = data
    f.close()