import json
import asyncio
import time
from Imports import classhandler,jsonhandler,mediatorhandler

# === GET ===

def getTurns():
  """
  lastTurn = ["lastTurn"]
  nextTurn = ["nextTurn"]
  turns = ["turns]
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

def addFactionTurn(factionName):
  turns = getTurns()

  factions = jsonhandler.getfactionsjson()
  factionInstance = classhandler.factionClass(factionName,factions) 
  factionDict ={
    "name": factionInstance.name,
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
        factionInstance = classhandler.factionClass(faction["name"],factions) 
        factionDict ={
          "name": factionInstance.name,
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

async def initialiseTurnSequence():
  tickTime = time.time()
  hours = 3 * 3600
  
  async def turnSequence(currentTime, hours):
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
      factionId = faction["guild"]
      if factionId == factionGuildId:
        faction["capital"] = capital
        faction["deployments"] = deployments
        faction["resources"] = resources
        faction["permissions"] = permissions

    with open("Data/factions.json","w") as file:
      json.dump(factions,file,indent = 4)
      file.close()
  
  def distributeResources():
    factions = jsonhandler.getfactionsjson()
    for faction in factions:
      faction = classhandler.factionClass(faction["name"],factions)
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
      fortRegionsCount = len([regionId for regionId in faction.regions
                                if classhandler.regionClass(regions, regionId).building == 'Fort'])
      villageRegionsCount = len([regionId for regionId in faction.regions
        if classhandler.regionClass(regions, regionId).building == 'Village'])
      FortCost = 50
      gold -= (FortCost*fortRegionsCount)
      villageIncome = 20
      gold += (villageIncome*villageRegionsCount)

      resourcesDict = {'gold': gold, 'iron': iron, 'stone': stone, 'wood': wood, 'manpower': resources.manpower}
      save_factions(factions,faction.guild,resourcesDict,faction.deployments.raw,faction.capital,faction.permissions.raw)
      
  # === Run ====
  asyncio.create_task(turnSequence(tickTime, hours))

# === LOGGING ===

def logTurn(factionName, objectType, id):
    """
    Log a turn action for a specific faction.

    Args:
        factionName (str): The name of the faction to log the action for.
        objectType (str): The type of object to log ('deployments' or 'regions').
        id (int): The ID of the object related to the action.

    Updates the turns.json file with the logged action for the given faction.
    """
    turns = getTurns()
    for turnIndex in turns["turns"]:
        if turnIndex["name"] == factionName:
            turnIndex[objectType].append(id)
            break

    with open("Data/turns.json","w") as file:
        json.dump(turns, file, indent=4)
  

def checkLogs(factionName, objectType, id):
    """
    Check if a given ID is logged under a specific faction and object type.

    Args:
        factionName (str): The name of the faction to check within.
        objectType (str): The type of object to check for ('deployments' or 'regions').
        id (int): The ID of the object to verify against the logs.

    Returns:
        bool: True if the ID is found under the specified faction and object type, False otherwise.
    """
    factions = jsonhandler.getfactionsjson()
    for faction in factions:
      if faction["name"] == factionName:
        faction = classhandler.factionClass(factionName, factions)
        break
    if objectType == "deployments": #In battle check
      mediatorData = mediatorhandler.getMediatorJson()
      for channelData in mediatorData:
        channelData = mediatorhandler.mediatorClass(channelData["id"])
        allDeployments = channelData.attackingFactionDeployments + channelData.defendingFactionDeployments
        for data in allDeployments:
           if id == data["id"] and factionName == data["faction"]:
            return True
    if objectType == "regions":
      mediatorData = mediatorhandler.getMediatorJson()
      for channelData in mediatorData:
         if id == channelData["region"]:
            return True
    if objectType == "deployments":
      if id in faction.turns.deployments: return True
    elif objectType == "regions":
      if id in faction.turns.regions: return True
    return False