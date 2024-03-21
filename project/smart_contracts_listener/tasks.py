import json
import logging

import requests
from django.db.models import Sum
from django.utils.timezone import now
from pytz import utc
from web3 import Web3
from datetime import datetime, timedelta

from project.celery import app
from project.smart_contracts_listener.models import TotalDistributionEvent

XAI_CONTRACT_ADDRESS = "0xaBE235136562a5C2B02557E1CaE7E8c85F2a5da0"
XAI_CONTRACT_ABI = '[{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bool","name":"value","type":"bool"}],"name":"AnyoneCanDistributeSet","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":true,"internalType":"address","name":"receiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Distributed","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint8","name":"version","type":"uint8"}],"name":"Initialized","type":"event"},{"anonymous":false,"inputs":[{"components":[{"internalType":"uint256","name":"share","type":"uint256"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"bool","name":"doCallback","type":"bool"}],"indexed":false,"internalType":"struct AIXTreasury.Receiver[]","name":"aixReceivers","type":"tuple[]"},{"components":[{"internalType":"uint256","name":"share","type":"uint256"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"bool","name":"doCallback","type":"bool"}],"indexed":false,"internalType":"struct AIXTreasury.Receiver[]","name":"ethReceivers","type":"tuple[]"}],"name":"ReceiversSet","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"previousAdminRole","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"newAdminRole","type":"bytes32"}],"name":"RoleAdminChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleGranted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleRevoked","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"aixAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"ethAmount","type":"uint256"}],"name":"TokensSwapped","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"inputAixAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"distributedAixAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"swappedEthAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"distributedEthAmount","type":"uint256"}],"name":"TotalDistribution","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"TransferETH","type":"event"},{"inputs":[],"name":"DEFAULT_ADMIN_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"DENOMINATOR","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"DISTRIBUTOR_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"aix","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"aixReceivers","outputs":[{"internalType":"uint256","name":"share","type":"uint256"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"bool","name":"doCallback","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"anyoneCanDistribute","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"minETHPerAIXPrice","type":"uint256"}],"name":"distribute","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"ethReceivers","outputs":[{"internalType":"uint256","name":"share","type":"uint256"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"bool","name":"doCallback","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"}],"name":"getRoleAdmin","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"grantRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"hasRole","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"contract IERC20","name":"_aix","type":"address"},{"internalType":"address","name":"_uniswapRouter","type":"address"},{"internalType":"address","name":"_weth","type":"address"},{"components":[{"internalType":"uint256","name":"share","type":"uint256"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"bool","name":"doCallback","type":"bool"}],"internalType":"struct AIXTreasury.Receiver[]","name":"_aixReceivers","type":"tuple[]"},{"components":[{"internalType":"uint256","name":"share","type":"uint256"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"bool","name":"doCallback","type":"bool"}],"internalType":"struct AIXTreasury.Receiver[]","name":"_ethReceivers","type":"tuple[]"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"renounceRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"revokeRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"value","type":"bool"}],"name":"setAnyoneCanDistribute","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"share","type":"uint256"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"bool","name":"doCallback","type":"bool"}],"internalType":"struct AIXTreasury.Receiver[]","name":"_aixReceivers","type":"tuple[]"},{"components":[{"internalType":"uint256","name":"share","type":"uint256"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"bool","name":"doCallback","type":"bool"}],"internalType":"struct AIXTreasury.Receiver[]","name":"_ethReceivers","type":"tuple[]"}],"name":"setReceivers","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalAixShares","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalEthShares","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"uniswapRouter","outputs":[{"internalType":"contract IUniswapV2Router02","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"weth","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"stateMutability":"payable","type":"receive"}]'
INFURA_URL = 'https://mainnet.infura.io/v3/fdca6548aa294127a74c4c2c88c8b6f6'
EVENT_NAME = 'TotalDistribution'
NUMBER_OF_LAST_BLOCKS = 24 * 60 * 6  # most frequent is new block each 10 seconds

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Load contract
contract = w3.eth.contract(address=XAI_CONTRACT_ADDRESS, abi=XAI_CONTRACT_ABI)

last_event = TotalDistributionEvent.objects.last()
event_filter = getattr(contract.events, EVENT_NAME).create_filter(
    fromBlock=w3.eth.block_number - NUMBER_OF_LAST_BLOCKS if last_event is None else last_event.block_id)


# Function to process event logs
def annotate_event_data(event_data):
    # print(prefix + ':', '\t', event)
    event_data['timestamp'] = w3.eth.get_block(event_data['blockNumber']).timestamp
    event_data['datetime'] = datetime.utcfromtimestamp(event_data['timestamp'])
    return event_data


events_data = [annotate_event_data(dict(event_data)) for event_data in event_filter.get_all_entries() if
               event_data['event'] == EVENT_NAME]

for event_data in events_data:
    event_time = datetime.utcfromtimestamp(event_data['timestamp']).replace(tzinfo=utc)
    if last_event is None or event_time > (last_event.created_at if last_event is None else now() - timedelta(days=1)):
        TotalDistributionEvent.objects.create_from_event_data(event_data)


@app.task
def write_new_events():
    logging.info(f'listening smart contract at {now()}')
    for event_data in event_filter.get_new_entries():
        TotalDistributionEvent.objects.create_from_event_data(annotate_event_data(event_data))


@app.task
def build_and_publish_report():
    logging.info(f'building report at {now()}')
    events_qs = TotalDistributionEvent.objects.filter(created_at__gt=now() - timedelta(days=1))
    first_tx_delta = now() - events_qs.first().created_at
    last_tx_delta = now() - events_qs.last().created_at
    report = f"Daily $AIX Stats:\n- First TX: {first_tx_delta.seconds // 3600 }h {first_tx_delta.seconds % 3600 // 60}m ago\n- Last TX: {last_tx_delta.seconds // 3600 }h {last_tx_delta.seconds % 3600 // 60}m ago\n- AIX processed: {events_qs.aggregate(Sum('input_aix_amount'))['input_aix_amount__sum']/10**18}\n- AIX distributed: {events_qs.aggregate(Sum('distributed_aix_amount'))['distributed_aix_amount__sum']/10**18}\n- ETH bought: {events_qs.aggregate(Sum('swapped_eth_amount'))['swapped_eth_amount__sum']/10**18}\n- ETH distributed: {events_qs.aggregate(Sum('distributed_eth_amount'))['distributed_eth_amount__sum']/10**18}"""
    logging.info(f'sending report at {now()}')
    payload = {
        "message": report,
        "endpoint_id": "89ccaa32-0364-4835-849c-be4543f4ff50"
    }

    logging.warning(payload)
    response = requests.post(
        'https://api.studylane.net/e9bc0d20-8fe9-4d7d-b242-3a719da8c211/external_message/',
        data=json.dumps(payload)
    )
    logging.warning(response.content)
