#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#CamelJuno 🐪

import discord
import requests
import random
import json
import base64
import string
import time
from base64 import b16encode, b64decode
from cosmpy.protos.cosmwasm.wasm.v1.query_pb2 import (
    QuerySmartContractStateRequest,
    QuerySmartContractStateResponse,
)
from cosmpy.protos.cosmos.bank.v1beta1.query_pb2 import (
    QueryBalanceRequest,
    QueryBalanceResponse,
)
from datetime import date,datetime

client = discord.Client()

def request(path, data):
    payload = {
        "jsonrpc": "2.0",
        "id": genId(),
        "method": "abci_query",
        "params": {"path": None, "data": None, "prove": False},
    }
    payload["params"]["path"] = path
    payload["params"]["data"] = b16encode(data).decode("utf-8")
    a = requests.post('https://rpc-juno.itastakers.com/', json=payload)
    if a.status_code == 200:
      return a
    else:
      request(path,data)

def contract_query(path, contract_address, query_payload):
    query = QuerySmartContractStateRequest(
        address=contract_address, query_data=json.dumps(query_payload).encode('utf-8')
    )
    query_encoded = QuerySmartContractStateRequest.SerializeToString(query)
    resp = request(path, query_encoded)
    val = b64decode(resp.json()["result"]["response"]["value"])
    return json.loads(QuerySmartContractStateResponse.FromString(val).data.decode())

def bank_query(path,address):
    query = QueryBalanceRequest(
        address=address, denom="ujuno"
    )
    query_encoded = QueryBalanceRequest.SerializeToString(query)
    resp = request(path, query_encoded)
    val = b64decode(resp.json()["result"]["response"]["value"])
    return QueryBalanceResponse.FromString(val).balance.amount

def fetchTreasuryJuno():
  path = '/cosmos.bank.v1beta1.Query/Balance'
  address = 'juno1c5v6jkmre5xa9vf9aas6yxewc7aqmjy0rlkkyk4d88pnwuhclyhsrhhns6'
  return round(float(bank_query(path,address))/1000000,2)

def fetchTreasuryNeta():
  path = '/cosmwasm.wasm.v1.Query/SmartContractState'
  contract_address = 'juno168ctmpyppk90d34p3jjy658zf5a5l3w8wk35wht6ccqj4mr0yv8s4j5awr' #NETA Contract
  query_payload = {"balance":{"address":"juno1c5v6jkmre5xa9vf9aas6yxewc7aqmjy0rlkkyk4d88pnwuhclyhsrhhns6"}}
  return round(float(contract_query(path,contract_address,query_payload)['balance'])/1000000,2)

def fetchDAOStake():
    path = "/cosmwasm.wasm.v1.Query/SmartContractState"
    contract_address = "juno1a7x8aj7k38vnj9edrlymkerhrl5d4ud3makmqhx6vt3dhu0d824qh038zh" #DAO Staking Module
    query_payload = {"total_value":{}}
    return round(float(contract_query(path,contract_address,query_payload)['total'])/1000000,2)

#TODO Quorum and Tally
# yesVotes = 
# noVotes = 
# noVetoVotes = 
# abstainVotes = 
# totalVotes = yesVotes + noVotes + noVetoVotes + abstainVotes
def fetchDAOProps():
  path = "/cosmwasm.wasm.v1.Query/SmartContractState"
  contract_address = "juno13z0mu9cyd0rj9cwr0hgwm9rxl8g9zwleqjg6pulcyypts26nua8qkzmlg0" #DAO Voting Module
  query_payload = {"reverse_proposals":{"limit":50}}
  proposalData = contract_query(path,contract_address,query_payload)['proposals']
  activeProposals = 0
  for i in proposalData:
    if i['status'] == 2:
      activeProposals = activeProposals + 1
  governanceData = ':scroll: `Active Proposals:` **'+str(activeProposals)+'**\n'
  if activeProposals > 0:
    for i in proposalData:
      if i['proposal']['status'] == 'open':
        propId = i['id']
        propTitle = i['proposal']['title']
        propDesc = i['proposal']['description']
        propExp = i['proposal']['expiration']['at_time']
        proposer = i['proposal']['proposer']
        governanceData = governanceData + '> ```Proposal #'+str(propId)+'```:notepad_spiral: `Title:` **'+str(propTitle)+'**\n> :ballot_box: `Vote:` **https://daodao.zone/dao/juno1c5v6jkmre5xa9vf9aas6yxewc7aqmjy0rlkkyk4d88pnwuhclyhsrhhns6/proposals/A'+str(propId)+'**\n> :writing_hand: `Description:` **'+propDesc+'**\n> :person_raising_hand: `Proposer: `**['+proposer+'](https://mintscan.io/juno/account/'+proposer+')**\n> :alarm_clock: `Voting End:` **'+datetime.fromtimestamp(int(propExp) // 1000000000).strftime('%m/%d/%Y %H:%M:%S')+' UTC**\n'
  return governanceData

def getNETA2JUNO():
  headers = {
    'Host': 'rpc-juno.itastakers.com',
    'Accept': '*/*'
  }
  jsonData = {"jsonrpc":"2.0","id":genId(),"method":"abci_query","params":{"path":"/cosmwasm.wasm.v1.Query/SmartContractState","data":"0a3f6a756e6f3165386e366368376d736b7334383765637a6e796561676d7a64356d6c327071397467656471743275363376726130713072396d71726a7936797312377b22746f6b656e325f666f725f746f6b656e315f7072696365223a7b22746f6b656e325f616d6f756e74223a2231303030303030227d7d","prove":False}}
  a = requests.post('https://rpc-juno.itastakers.com/',headers=headers,json=jsonData,timeout=20)
  if a.status_code == 200:
    a = round(float(base64.b64decode(json.loads(a.text)['result']['response']['value']).split('"token1_amount":"'.encode('utf-8'),1)[1].split('"}'.encode('utf-8'),1)[0])/1000000,2)
    return a
  else:
    getNETA2JUNO()

def getNETAOsmosis():
  headers = {
    'Host': 'api-osmosis.imperator.co',
  'Accept': 'application/json, text/plain, */*'
  }
  a = requests.get('https://api-osmosis.imperator.co/tokens/v2/NETA',headers=headers,timeout=20)
  if a.status_code == 200:
    a = json.loads(a.text)[0]
    return a
  else:
    getNETAOsmosis()

def getNETAPriceJunoOsmosis():
  headers = {
    'Host': 'api-osmosis.imperator.co',
    'Accept': 'application/json, text/plain, */*'
  }
  a = requests.get('https://api-osmosis.imperator.co/pools/v2/632',headers=headers,timeout=20)
  if a.status_code == 200:
    a = round(json.loads(a.text)[0]['price']/json.loads(a.text)[1]['price'],2)
    return a
  else:
    getNETAPriceJunoOsmosis()

def getNETALiquidityJunoSwap():
  headers = {
    'Host': 'rpc-juno.itastakers.com',
    'Accept': '*/*'
  }
  jsonData = {"jsonrpc":"2.0","id":genId(),"method":"abci_query","params":{"path":"/cosmwasm.wasm.v1.Query/SmartContractState","data":"0a3f6a756e6f3165386e366368376d736b7334383765637a6e796561676d7a64356d6c327071397467656471743275363376726130713072396d71726a79367973120b7b22696e666f223a7b7d7d","prove":False}}
  z = requests.post('https://rpc-juno.itastakers.com/',headers=headers,json=jsonData,timeout=20)
  if z.status_code == 200:
    a = float(base64.b64decode(json.loads(z.text)['result']['response']['value']).split('"token1_reserve":"'.encode('utf-8'),1)[1].split('"'.encode('utf-8'),1)[0])/1000000
    b = float(base64.b64decode(json.loads(z.text)['result']['response']['value']).split('"token2_reserve":"'.encode('utf-8'),1)[1].split('"'.encode('utf-8'),1)[0])/1000000
    return [a,b]
  else:
    getNETALiquidityJunoSwap()

def getJUNOGecko():
  headers = {
    'Host': 'api.coingecko.com',
    'Accept': '*/*'
  }
  a = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=juno-network',headers=headers,timeout=10)
  if a.status_code == 200:
    z = json.loads(a.text)[0]['current_price']
    if z == None:
      getJUNOGecko()
    else:
      return z
  else:
    getJUNOGecko()

def formatIt(hello):
  hello = int(hello)
  suffixes = ["", "K", "M", "B", "T"]
  hello = str("{:,}".format(hello))
  commas = 0
  x = 0
  while x < len(hello):
      if hello[x] == ',':
        commas += 1
      x += 1
  return hello.split(',')[0]+'.'+hello.split(',')[1][:-1] + suffixes[commas]

def genId():
  res = ''
  for i in range(12):
    res = res+random.choice(string.digits)
  return int(res)

@client.event
async def on_ready():
  print(f'You have logged in as {client}')
  message = await client.get_channel(channelID).fetch_message(messageID)
  while(True):
    try:
      NETASupply = 31886.6
      today = date.today().strftime("%B %d, %Y")
      NETA2JUNO = getNETA2JUNO()
      NETA2JUNOOsmosis = getNETAPriceJunoOsmosis()
      JunoSwapLiquidity = getNETALiquidityJunoSwap()
      OsmosisStats = getNETAOsmosis()
      NETAPriceJunoSwap = round(getJUNOGecko()*NETA2JUNO,2)
      NETAPriceOsmosis = round(OsmosisStats['price'],2)
      NETAMarketcap = formatIt(NETASupply*NETAPriceOsmosis)
      NETALiquidityOsmosis = formatIt(int(OsmosisStats['liquidity'])*2)
      NETALiquidityJunoSwap = formatIt(round(JunoSwapLiquidity[0]*getJUNOGecko()*2,2))
      airdropFile = open('HolderData.txt').readlines()
      originalHolders = airdropFile[0].strip()
      NETAHeld = airdropFile[1].strip()
      fullHeld = airdropFile[2].strip()
      DAOStake = fetchDAOStake()
      DAOStakePrct = round(DAOStake / NETASupply * 100,3)
      TreasuryJuno = fetchTreasuryJuno()
      TreasuryNeta = fetchTreasuryNeta()
      TreasuryUSD = round(TreasuryJuno * getJUNOGecko() + TreasuryNeta * NETAPriceJunoSwap,2)
      DAOPropData = fetchDAOProps()
      messageToBeSent = ':calendar: **'+today+'** :calendar:\n**__NETA Stats - Updates every 60 seconds__**\n\n'
      messageToBeSent = messageToBeSent+':moneybag: `Market Capitalization:` **$'+NETAMarketcap+'**\n'
      messageToBeSent = messageToBeSent+':briefcase: `Total Supply:` **'+str(NETASupply)+'**\n'
      messageToBeSent = messageToBeSent+'```Airdrop Eligible Address Stats```:trophy: `Holders > 0.1 NETA:` **'+str(originalHolders)+' / 5372**\n:gem: `Holds full amount or more:` **'+str(fullHeld)+' / '+str(originalHolders)+'**\n:shopping_cart: `Total NETA held:` **'+str(NETAHeld)+' / '+str(NETASupply)+'**\n'
      messageToBeSent = messageToBeSent+'```DAO Stats```:link: `URL:` **https://daodao.zone/dao/juno1c5v6jkmre5xa9vf9aas6yxewc7aqmjy0rlkkyk4d88pnwuhclyhsrhhns6**\n:closed_lock_with_key: `Total Bonded:` **'+str(DAOStake)+' NETA ('+str(DAOStakePrct)+'%)**\n:classical_building: `Treasury:` **$'+str(TreasuryUSD)+'**\n>> **'+str(TreasuryJuno)+' JUNO**\n>> **'+str(TreasuryNeta)+' NETA**\n'+DAOPropData
      messageToBeSent = messageToBeSent+'```JunoSwap Stats```:dollar: `Price:` **$'+str(NETAPriceJunoSwap)+'**\n:coin: `Price/Juno:` **'+str(round(NETA2JUNO,2))+' Juno'+'**\n:test_tube: `Total Liquidity:` **$'+str(NETALiquidityJunoSwap)+'**\n'
      messageToBeSent = messageToBeSent+'```Osmosis Stats```:dollar: `Price:` **$'+str(NETAPriceOsmosis)+'**\n:coin: `Price/Juno:` **'+str(NETA2JUNOOsmosis)+' Juno'+'**\n:test_tube: `Total Liquidity:` **$'+str(NETALiquidityOsmosis)+'**\n\n'
      messageToBeSent = messageToBeSent+'>>> ***Powered By <@340813726103896064>***'
      await message.edit(content=messageToBeSent,suppress=True)
      time.sleep(1)
      await message2.edit(content=messageToBeSent,suppress=True)
      print('Updated on: '+str(datetime.now().strftime("%H:%M:%S")))
      time.sleep(57)
    except:
      continue

channelID = 0
messageID = 0
BOT_TOKEN = 'PLACE_AUTH_TOKEN_HERE'
client.run(BOT_TOKEN)