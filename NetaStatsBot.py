#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#By CamelJuno 🐪

import discord
import requests
import random
import json
import base64
import string
import time
from datetime import date,datetime

client = discord.Client()

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
      NETAClaimed = 31886.6
      today = date.today().strftime("%B %d, %Y")
      NETA2JUNO = getNETA2JUNO()
      NETA2JUNOOsmosis = getNETAPriceJunoOsmosis()
      JunoSwapLiquidity = getNETALiquidityJunoSwap()
      OsmosisStats = getNETAOsmosis()
      NETAPriceJunoSwap = round(getJUNOGecko()*NETA2JUNO,2)
      NETAPriceOsmosis = round(OsmosisStats['price'],2)
      NETAMarketcap = formatIt(NETAClaimed*NETAPriceOsmosis)
      NETALiquidityOsmosis = formatIt(int(OsmosisStats['liquidity'])*2)
      NETALiquidityJunoSwap = formatIt(round(JunoSwapLiquidity[0]*getJUNOGecko()*2,2))
      airdropFile = open('HolderData.txt').readlines()
      originalHolders = airdropFile[0].strip()
      NETAHeld = airdropFile[1].strip()
      fullHeld = airdropFile[2].strip()
      messageToBeSent = ':calendar: **'+today+'** :calendar:\n**__NETA Stats - Updates every 60 seconds__**\n\n'
      messageToBeSent = messageToBeSent+':moneybag: `Market Capitalization:` **$'+NETAMarketcap+'**\n'
      messageToBeSent = messageToBeSent+':briefcase: `Total Supply:` **'+str(NETAClaimed)+'**\n'
      messageToBeSent = messageToBeSent+'```Airdrop Eligible Address Stats```:trophy: `Holders > 0.1 NETA:` **'+str(originalHolders)+' / 5372**\n:gem: `Holds full amount or more:` **'+str(fullHeld)+' / '+str(originalHolders)+'**\n:shopping_cart: `Total NETA held:` **'+str(NETAHeld)+' / '+str(NETAClaimed)+'**\n'
      messageToBeSent = messageToBeSent+'```DAO Stats```*Coming soon* :tm: \n'
      messageToBeSent = messageToBeSent+'```JunoSwap Stats```:dollar: `Price:` **$'+str(NETAPriceJunoSwap)+'**\n:coin: `Price/Juno:` **'+str(round(NETA2JUNO,2))+' Juno'+'**\n:test_tube: `Total Liquidity:` **$'+str(NETALiquidityJunoSwap)+'**\n'
      messageToBeSent = messageToBeSent+'```Osmosis Stats```:dollar: `Price:` **$'+str(NETAPriceOsmosis)+'**\n:coin: `Price/Juno:` **'+str(NETA2JUNOOsmosis)+' Juno'+'**\n:test_tube: `Total Liquidity:` **$'+str(NETALiquidityOsmosis)+'**\n\n'
      messageToBeSent = messageToBeSent+'>>> ***Powered By <@340813726103896064>***'
      await message.edit(content=messageToBeSent)
      print('Updated on: '+str(datetime.now().strftime("%H:%M:%S")))
      time.sleep(57)
    except:
      continue

channelID = 0
messageID = 0
BOT_TOKEN = 'PLACE_AUTH_TOKEN_HERE'
client.run(BOT_TOKEN)