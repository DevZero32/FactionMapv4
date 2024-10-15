import json
import asyncio
import time
from Imports import classhandler,jsonhandler,mediatorhandler,economyHandler
import discord
from discord import ui
from discord import app_commands
from discord.ext import commands

# === GET ===

def getTurns():
  """
  lastTurn = ["lastTurn"]
  nextTurn = ["nextTurn"]
  turns = ["turns"]
  """
  with open("Data/turns.json") as file:
      turns = json.load(file)
  return turns

# === UPDATE ===

def updateTurns(lastTurn,nextTurn):
   turns = getTurns()
   turns["lastTurn"] = lastTurn
   turns["nextTurn"] = nextTurn

   with open("Data/turns.json","w") as file:
      json.dump(turns, file, indent=4)

def addFactionTurn(factionId):
  turns = getTurns()

  factions = jsonhandler.getfactionsjson()
  factionInstance = classhandler.factionClass(factionId,factions) 
  factionDict ={
    "id": factionInstance.guild,
    "deployments": [],
    "regions": []
  }
  
  turns["turns"].append(factionDict)
  with open("Data/turns.json","w") as file:
    json.dump(turns, file, indent=4)

# === STARTUP ===


def resetTurns():
    factions = jsonhandler.getfactionsjson()
    turnsList = [] 

    for faction in factions:
        factionInstance = classhandler.factionClass(faction["guild"],factions) 
        factionDict ={
          "id": factionInstance.guild,
          "deployments": [],
          "regions": []
        }
        turnsList.append(factionDict)
    turnsJson = {
        "lastTurn": 0,
        "nextTurn": 1,
        "turns": turnsList   
    }
  
    with open("Data/turns.json","w") as file:
        json.dump(turnsJson, file, indent=4)

async def initialiseTurnSequence(client):
  tickTime = time.time()
  hours = 3 * 3600
  #hours = 5
  async def turnSequence(currentTime, hours,client):
    currentTime = time.time()
    turns = getTurns()
    if turns["nextTurn"] < currentTime:  
      resetTurns()
      updateTurns(currentTime,currentTime+hours)
    
    while True:
      currentTime = time.time()
      nextTurn = getTurns()["nextTurn"]
      timeDif = nextTurn - currentTime
      await asyncio.sleep(timeDif)
      currentTime = time.time()
      resetTurns()
      distributeResources()
      await distributeTrades(client)
      updateTurns(currentTime,currentTime+hours)
  
  def save_factions(factions,factionGuildId,resources,deployments,capital,permissions):
    """
    guild -Being the discord object, held within interaction.guild
    factions -List of all the factions
    factionGuildId -Id of the save that is being updated/change
    [resources.raw,deployments,capital,permissions] data stored within the faction that can be changed.

    Saves faction data to json file Data/factions.json.
    """

    for faction in factions:
      if faction["guild"] == factionGuildId:
        faction["capital"] = capital
        faction["deployments"] = deployments
        faction["resources"] = resources
        faction["permissions"] = permissions

    with open("Data/factions.json","w") as file:
      json.dump(factions,file,indent = 4)
      file.close()

  async def distributeTrades(client):
    async def successNotify(offeringFactionId, receivingFactionId, client,tradeName):
      # Embed
      embed = discord.Embed(
        color=discord.Color(int('5865f2',16)),
        description=f"""Trade successful, view all trades with `/view_trades`"""
      )
      embed.set_footer(text="Trade occurs every turn.")
      embed.set_author(name=f"Trade {tradeName} successful",icon_url=f"https://cdn.discordapp.com/attachments/763309644261097492/1143966676661059635/image.png?ex=66baf53d&is=66b9a3bd&hm=7ebd69b2962ef32b2ecbcf59771a304dbd773c2d6e6a20f96458bc98cee77b83&")

      # Offering faction
      offeringFaction = classhandler.factionClass(offeringFactionId, jsonhandler.getfactionsjson())
      offeringGuild = client.get_guild(offeringFaction.guild)
      offeringAlertChannel = offeringGuild.get_channel(offeringFaction.alert)
      
      # Send the embed to the offering faction's alert channel
      await offeringAlertChannel.send(embed=embed)

      # Receiving faction
      receivingFaction = classhandler.factionClass(receivingFactionId, jsonhandler.getfactionsjson())
      receivingGuild = client.get_guild(receivingFaction.guild)
      receivingAlertChannel = receivingGuild.get_channel(receivingFaction.alert)
      
      # Send the embed to the receiving faction's alert channel
      await receivingAlertChannel.send(embed=embed)

    async def cancelNotify(offeringFactionId, receivingFactionId, client,tradeName,tradeId):
      # Embed
      embed = discord.Embed(
        color=discord.Color(int('eb3d47', 16)),
        description=f"A trade has been canceled due to a lack of resources on either side."
      )
      embed.set_footer(text="view all trades with `/view_trades`")
      embed.set_author(
          name=f"Trade {tradeName} canceled",
          icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&"
      )

      # Offering faction
      offeringFaction = classhandler.factionClass(offeringFactionId, jsonhandler.getfactionsjson())
      offeringGuild = client.get_guild(offeringFaction.guild)
      offeringAlertChannel = offeringGuild.get_channel(offeringFaction.alert)
      
      # Send the embed to the offering faction's alert channel
      await offeringAlertChannel.send(embed=embed)

      # Receiving faction
      receivingFaction = classhandler.factionClass(receivingFactionId, jsonhandler.getfactionsjson())
      receivingGuild = client.get_guild(receivingFaction.guild)
      receivingAlertChannel = receivingGuild.get_channel(receivingFaction.alert)
      
      # Send the embed to the receiving faction's alert channel
      await receivingAlertChannel.send(embed=embed)
      
      #cancel trade
      trades = economyHandler.getTrades()
      for trade in trades:
         if trade["id"] == tradeId:
            trades.remove(trade)
            break
      with open("Data\trades.json","w") as file:
         json.dump(trades,file,indent=4)

    for trade in economyHandler.getTrades():
      if trade["tradeAccepted"] == False:
        continue

      
      offeringFaction = classhandler.factionClass(trade["offeringFactionId"],jsonhandler.getfactionsjson())
      offeringResource = trade["offeringResource"]
      offeringQuanitity = trade["offeringQuantity"]
    
      receivingFaction = classhandler.factionClass(trade["receivingFactionId"],jsonhandler.getfactionsjson())
      receivingResource = trade["receivingResource"]
      receivingQuanitiy = trade["receivingQuantity"]

      if offeringFaction.resources.raw[offeringResource] < offeringQuanitity or receivingFaction.resources.raw[receivingResource] < receivingQuanitiy:
        await cancelNotify(offeringFaction.guild,receivingFaction.guild,client,trade["tradeName"])
        continue
      
      # do trade
      offeringFactionResources = offeringFaction.resources.raw
      receivingFactionResources = receivingFaction.resources.raw

      offeringFactionResources[receivingResource] + receivingQuanitiy
      offeringFactionResources[offeringResource] - offeringQuanitity

      receivingFactionResources[offeringResource] + offeringQuanitity
      receivingFactionResources[receivingResource] - receivingQuanitiy

      save_factions(jsonhandler.getfactionsjson(),offeringFaction.guild,offeringFactionResources,offeringFaction.deployments.raw,offeringFaction.capital,offeringFaction.permissions.raw)
      save_factions(jsonhandler.getfactionsjson(),receivingFaction.guild,receivingFactionResources,receivingFaction.deployments.raw,receivingFaction.capital,receivingFaction.permissions.raw)
      await successNotify(offeringFaction.guild,receivingFaction.guild,client,trade["tradeName"])

  def distributeResources():
    factions = jsonhandler.getfactionsjson()
    for faction in factions:
      faction = classhandler.factionClass(faction["guild"],factions)
      factionRegions = faction.regions
      
      resources = faction.resources
      gold, iron, stone, wood = resources.gold, resources.iron, resources.stone, resources.wood

      regions = jsonhandler.getregionjson()
      for indexRegion in factionRegions:
        region = classhandler.regionClass(regions,indexRegion)
        regionResources = region.resources
        #Giving the resources of the land
        if regionResources != None and region.building == "Village" or "Capital":
          for resource, amount in regionResources.items():
            if resource == "Wood":
                wood += amount
            elif resource == "Iron":
                iron += amount
            elif resource == "Stone":
                stone += amount
            elif resource == "Gold":
                gold += amount
            if region.building == "Capital":
              wood += 10
              iron += 5
              stone += 10
              capitalTax = 250
              gold += capitalTax
      
      # Count the number of regions with a fort
      fortRegionsCount = len([regionId for regionId in faction.regions if classhandler.regionClass(regions, regionId).building == 'Fort'])
      villageRegionsCount = len([regionId for regionId in faction.regions if classhandler.regionClass(regions, regionId).building == 'Village'])
      portRegionsCount = len([regionId for regionId in faction.regions if classhandler.regionClass(regions, regionId).building == 'Port'])
      PortCost = 10
      FortCost = 50
      gold -= (FortCost*fortRegionsCount)
      gold -= (PortCost*portRegionsCount)
      villageIncome = 20
      gold += (villageIncome*villageRegionsCount)

      resourcesDict = {'gold': gold, 'iron': iron, 'stone': stone, 'wood': wood, 'manpower': resources.manpower}
      save_factions(factions,faction.guild,resourcesDict,faction.deployments.raw,faction.capital,faction.permissions.raw)
      
  # === Run ====
  asyncio.create_task(turnSequence(tickTime, hours,client))

# === LOGGING ===

def logTurn(factionId, objectType, objectId,duration):
    """
    Log a turn action for a specific faction.

    Args:
        factionId (str): The id of the faction to log the action for.
        objectType (str): The type of object to log ('deployments' or 'regions').
        objectId (int): The ID of the object related to the action.
        duration (int): The duration of the local turn

    Updates the turns.json file with the logged action for the given faction.
    """
    turns = getTurns()
    for turnIndex in turns["turns"]:
        if turnIndex["id"] == factionId:
            #existance handling
            for i in turnIndex[objectType]:
               if i["id"] == objectId:
                  i["lastTurn"] = time.time()
                  i["nextTurn"] = time.time() + duration

                  with open("Data/turns.json","w") as file:
                    json.dump(turns, file, indent=4)
                  break
            #normal conditions
            obj = {
               "id": objectId,
               "lastTurn": time.time(),
               "nextTurn": time.time() + duration
               }
            turnIndex[objectType].append(obj)
            break

    with open("Data/turns.json","w") as file:
        json.dump(turns, file, indent=4)
  

def checkLogs(factionId, objectType, objectId):
    """
    Check if a given ID is logged under a specific faction and object type.

    Args:
        factionName (str): The name of the faction to check within.
        objectType (str): The type of object to check for ('deployments' or 'regions').
        id (int): The ID of the object to verify against the logs.

    Returns:
        bool: True if the ID is found under the specified faction and object type, False otherwise.
    """
    faction = classhandler.factionClass(factionId, jsonhandler.getfactionsjson())
  
    if objectType == "deployments": #In battle check
      #check if in mediator
      mediatorData = mediatorhandler.getMediatorJson()
      for channelData in mediatorData:
        channelData = mediatorhandler.mediatorClass(channelData["id"])
        allDeployments = channelData.attackingFactionDeployments + channelData.defendingFactionDeployments
        for data in allDeployments:
           if objectId == data["id"] and factionId == data["faction"]:
            return True
      #check if already turned
      for i in faction.turns.deployments:
         if i["id"] == objectId:
            if i["nextTurn"] > time.time(): return True
    
    if objectType == "regions":
      #check if in mediator
      mediatorData = mediatorhandler.getMediatorJson()
      for channelData in mediatorData:
         if objectId == channelData["region"]:
            return True
      #check if already turned
      for i in faction.turns.regions:
         if i["id"] == objectId:
            if i["nextTurn"] > time.time(): return True

    return False