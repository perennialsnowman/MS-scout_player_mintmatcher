import requests
from web3 import Web3
import pandas as pd
import json

#########preset variables here#########
blockstart = 26200000
blockend = 26319340
api_key = '58NJMR8R28QMTIJRTTVWWZ2A38J4ZRH9FR' #for polygonscan
contract_address = '0x28F49Ba7b20CAD0a8256BE34484cF733B0f9a88F'
polygon_node = 'https://speedy-nodes-nyc.moralis.io/f7838987a14a3db5c6feed72/polygon/mainnet' #take your pick, I used a moralis speedy node
#######################################

mint_list = [] #create empty list
mint_final = []


pol_w3 = Web3(Web3.HTTPProvider(polygon_node)) #connect to the blockchain

#obtain abi (application binary interface) for player minting
abi_endpoint = "https://api.polygonscan.com/api?module=contract&action=getabi&address=0x28F49Ba7b20CAD0a8256BE34484cF733B0f9a88F&apikey=58NJMR8R28QMTIJRTTVWWZ2A38J4ZRH9FR"
abi = json.loads(requests.get(abi_endpoint).text)

params = dict(fromBlock = blockstart, toBlock = blockend, address = contract_address, topic0 = '0x3ac4fb5ff87d591c05622f261c3cce5182409bdc9704d5a721dd2da589a766e0', key = api_key) #the topic pertains to player minting

minttx_response = requests.get('https://api.polygonscan.com/api?module=logs&action=getLogs', params = params)

minttx = json.loads(minttx_response.text)
minttx = minttx["result"]

for entry in minttx:
    tx = pol_w3.eth.get_transaction(entry['transactionHash'])
    tx_output = pol_w3.eth.get_transaction_receipt(entry['transactionHash'])
    contract = pol_w3.eth.contract(address = tx["to"], abi = abi["result"]) #resolve the abi
    claim_log = contract.events.ScoutingClaimed().processReceipt(tx_output) #look at logs for scout claiming process
    scout_ID = claim_log[0]['args']['scoutId']

    player_IDs = claim_log[0]['args']['scouting'][7]
    for i in range(len(claim_log[0]['args']['scouting'][7])): #players returned as list in claim log - loop through list
        mint_dict_app = {"scoutID": scout_ID, "playerID": player_IDs[i], "transactionID": entry['transactionHash']}
        mint_list.append(mint_dict_app)

for entry in mint_list:
    scout_ID = entry['scoutID']
    player_ID = entry['playerID']
    tx_hash = entry['transactionID']
    params_scout = dict(scoutIds = scout_ID)
    scoutAPIjson = requests.get("https://api.metasoccer.com/scouts?", params = params_scout)
    scoutAPI = json.loads(scoutAPIjson.text)
    scout_OVR = scoutAPI[0]["overallKnowledge"]

    playerAPIjson = requests.get(f"https://api.metasoccer.com/players/{player_ID}")
    playerAPI = json.loads(playerAPIjson.text)
    player_pot_OVR = playerAPI["potential"]

    mint_final_app = {"scoutID": scout_ID, "scout_OVR": scout_OVR, "player_ID": player_ID, "player_pot": player_pot_OVR}
    print (mint_final_app)

    mint_final.append(mint_final_app)

mint_final_arr = pd.DataFrame(mint_final)
mint_final_arr.to_csv(f'mintvalues_bs{blockstart}_bf{blockend}.csv')