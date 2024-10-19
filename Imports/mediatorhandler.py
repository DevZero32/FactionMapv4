import json
import time
import math
from random import choice
from Imports import classhandler,jsonhandler,adminhandler,armyhandler

class mediatorClass():
  def __init__(self,id):
    """
    Args:
      Id - Channel id of the battle channel
    """
    for data in getMediatorJson():
      if data["id"] == id:
        self.id = id
        self.attackingFaction = data["attackingFaction"]
        self.attackingFactionDeployments = data["attackingDeployments"]
        self.defendingFaction = data["defendingFaction"]
        self.defendingFactionDeployments = data["defendingDeployments"]
        self.region = data["region"]
        break

async def createChannel(interaction,client,battleInfo,mainguild=1074062206297178242):
  attackingGuild = client.get_guild(battleInfo.attackingFaction.guild)
  defendingGuild = client.get_guild(battleInfo.defendingFaction.guild)
  guild = client.get_guild(mainguild)
  # Channel creation
  category = guild.get_channel(1296537719555752076)
  channel = await guild.create_text_channel(f"{battleInfo.attackingFaction.name[0:5]}_V_{battleInfo.defendingFaction.name[0:5]}_R{battleInfo.region}", category=category)
  channel.position = len(category.text_channels)
  channel.topic = f"ATK:{battleInfo.attackingFaction.name} DEF:{battleInfo.defendingFaction.name}"
  #removing verified permissions
  await channel.set_permissions(target=guild.get_role(1100828097173000333),view_channel=False,read_messages=False,read_message_history=False)
  #removing unverified permissions
  await channel.set_permissions(target=guild.get_role(1100827903089971220),view_channel=False,read_messages=False,read_message_history=False)

  #mediator
  mediators = guild.get_role(1162115972124114975)
  mediator = choice(mediators.members)
  await channel.set_permissions(target=mediators,view_channel=True,read_messages=True,read_message_history=True,manage_messages=True)
  region = classhandler.regionClass(jsonhandler.getregionjson(),battleInfo.region)
  nearbyFactions = []
  for faction in jsonhandler.getfactionsjson():
    faction = classhandler.factionClass(faction["guild"],jsonhandler.getfactionsjson())

    for deployment in faction.deployments.raw:
      if deployment["region"] in region.neighbours or deployment["region"] == region.id:
        if deployment["name"] != battleInfo.attackingDeployment.name and deployment["name"] != battleInfo.defendingDeployment.name:
          deploymentName = deployment["name"]
          nearbyFactions.append(f"{faction.name} via `Deployment {deploymentName}`")
  if nearbyFactions == []:
    nearbyFactions = "None found"
  else: nearbyFactions = ", \n".join(nearbyFactions)
  msg = f"""
# Battle information:

{battleInfo.attackingFaction.name} Vs {battleInfo.defendingFaction.name}

{battleInfo.attackingFaction.name} has brought the following troops:
Deployment: {battleInfo.attackingDeployment.name}
Tier One: `{battleInfo.attackingDeployment.tierOne}`
Tier Two: `{battleInfo.attackingDeployment.tierTwo}`

{battleInfo.defendingFaction.name} has brought the following troops:
Deployment: {battleInfo.defendingDeployment.name}
Tier One: `{battleInfo.defendingDeployment.tierOne}`
Tier Two: `{battleInfo.defendingDeployment.tierTwo}`

Nearby factions that could assist:
{nearbyFactions}

Region building: `{region.building}`
*This affects the map chosen, your mediator will reveal the map to you.*

Terms will be selected by the mediator to ensure that the battle is fair and is controlled by the rules of faction map.

# Battle Rules

- Only commanders & Mediators may use global chat, only exception being at the end of the round. (soliders use `/team` whilst chatting)
- Only may the Mediator present the score, this is to prevent confusion.
- Mediators have the ability to decide when a round starts.
- Mediators have the ability to cancel a round due to cheating.
- Mediators must have access to admin commands on the private server where the battle is hosted.
- Battles are first to 5, unless a mediator adjusts this before in terms.
- Failing to comply with a mediator is an instant defeat.

# Preset Terms

Map: Given by Mediator
Rally size: determined by `/team` *total sizes*
Mercs: :x:
Pause time: :white_check_mark:

Time: Discussed and chosen by mediator to best accommodate everyone
Server: Discussed and chosen by mediator to best accommodate everyone

# Troops

Each team has its own rally size, with their own tiers of troops with their own counts. This limits the amount of troops per class you have:

** Tier One**
- Sappers
- Archers
- Light Infantry
- General Infantry

**Tier Two**
- Heavy Infantry
- Cavalry

The chosen mediator for this battle is {mediator.mention}
"""
  # Text too big
  if len(msg) >= 2000:
    await channel.send(msg)
  else:
    msgOne = f"""
# Battle information:

{battleInfo.attackingFaction.name} Vs {battleInfo.defendingFaction.name}

{battleInfo.attackingFaction.name} has brought the following troops:
Deployment: {battleInfo.attackingDeployment.name}
Tier One: `{battleInfo.attackingDeployment.tierOne}`
Tier Two: `{battleInfo.attackingDeployment.tierTwo}`

{battleInfo.defendingFaction.name} has brought the following troops:
Deployment: {battleInfo.defendingDeployment.name}
Tier One: `{battleInfo.defendingDeployment.tierOne}`
Tier Two: `{battleInfo.defendingDeployment.tierTwo}`

Nearby factions that could assist:
{nearbyFactions}
    """
    msgTwo = f"""
  # Battle Rules

- Only commanders & Mediators may use global chat, only exception being at the end of the round. (soliders use `/team` whilst chatting)
- Only may the Mediator present the score, this is to prevent confusion.
- Mediators have the ability to decide when a round starts.
- Mediators have the ability to cancel a round due to cheating.
- Mediators must have access to admin commands on the private server where the battle is hosted.
- Battles are first to 5, unless a mediator adjusts this before in terms.
- Failing to comply with a mediator is an instant defeat.

# Preset Terms

Map: Given by Mediator
Rally size: determined by `/team` *total sizes*
Mercs: :x:
Pause time: :white_check_mark:

Time: Discussed and chosen by mediator to best accommodate everyone
Server: Discussed and chosen by mediator to best accommodate everyone

# Troops

Each team has its own rally size, with their own tiers of troops with their own counts. This limits the amount of troops per class you have:

** Tier One**
- Sappers
- Archers
- Light Infantry
- General Infantry

**Tier Two**
- Heavy Infantry
- Cavalry

The chosen mediator for this battle is {mediator.mention}
  """
    await channel.send(msgOne)
    await channel.send(msgTwo)
  try:
    await channel.set_permissions(target=attackingGuild.owner,view_channel=True,read_messages=True,read_message_history=True)
    await channel.send(f"{attackingGuild.owner.mention}")
  except: await channel.send(f"`{battleInfo.attackingFaction.name}` owner couldnt be located, please find a representive.")
  try:
    await channel.set_permissions(target=defendingGuild.owner,view_channel=True,read_messages=True,read_message_history=True)
    await channel.send(f"{defendingGuild.owner.mention}")
  except: await channel.send(f"`{battleInfo.defendingFaction.name}` owner couldnt be located, please find a representive.")

  # === Adding Mediator Json ===
  addMediatorJson(channel.id,battleInfo.attackingFaction.guild,battleInfo.attackingDeployment.id,battleInfo.defendingFaction.guild,battleInfo.defendingDeployment.id,battleInfo.defendingDeployment.region)

async def victor(interaction,client,winningFaction,score):
  # === Permissions Check ===
  permission = await adminhandler.admincheck(interaction.user,client)
  if permission == False:
    return "You do not have permission to use this command."

  # === Channel Check ===
  mediatorJson = getMediatorJson()
  channelId = interaction.channel.id
  channelIds = [m["id"] for m in mediatorJson]
  if channelId not in channelIds:
    return f"This channel is not hosting terms for a battle." 
  # === Score Check ===
  if "-" not in score or not score.split("-")[0].isdigit() or not score.split("-")[1].isdigit():
    return "Score has not been formatted correctly;'Attackers-Defenders' (e.g., 5-1) "
  attackingScore = int(score.split("-")[0])
  defendingScore = int(score.split("-")[1])
  print(attackingScore,defendingScore)
  if not 0 <= attackingScore <= 5 or not 0 <= defendingScore <= 5:
    return "Score must range between 0-5."
  # === Get channel Class ===
  channelData = mediatorClass(channelId)
  winningFaction = winningFaction.name

  if winningFaction == "Attackers":
    winningFaction = channelData.attackingFaction
  elif winningFaction == "Defenders":
    winningFaction = channelData.defendingFaction
  else: return "An error has occured whilst trying to parse the winning faction."
  # Victory verifcation
  if (winningFaction == channelData.attackingFaction and attackingScore != 5) or (winningFaction == channelData.defendingFaction and defendingScore != 5):
    return "Victory data has been incorrectly entered; 'Attackers-Defenders' (e.g., 5-1) "
  
  # === Applying Attrition ===
  
  # == Attacking ==
  for deploymentData in channelData.attackingFactionDeployments:
    faction = classhandler.factionClass(deploymentData["faction"],jsonhandler.getfactionsjson())
    deployment = armyhandler.getDeploymentClass(faction,deploymentData["id"])
    try: Dpercentage = defendingScore/5
    except ZeroDivisionError: 
        Dpercentage = 0
    if Dpercentage != 0:
      tierOne = math.floor(deployment.tierOne*Dpercentage)
      tierTwo = math.floor(deployment.tierTwo*Dpercentage)
    else:  
        tierOne,tierTwo = deployment.tierOne,deployment.tierTwo
    
    deployments = faction.deployments.raw
    for deploymentIndex in deployments:
        if deploymentIndex["id"] == deploymentData["id"]:
            if Dpercentage == 1:
                deploymentName = deploymentIndex["name"]
                await interaction.channel.send(f"{deploymentName} has routed.")
                deployments.remove(deploymentIndex)
            else:
                deploymentIndex["region"] = channelData.region
                deploymentIndex["tierOne"] = tierOne
                deploymentIndex["tierTwo"] = tierTwo

            factionGuild = client.get_guild(faction.guild)
            jsonhandler.save_factions(factionGuild,jsonhandler.getfactionsjson(),faction.guild,faction.resources.raw,deployments,faction.capital,faction.permissions.raw)

# == Defending ==
  for deploymentData in channelData.defendingFactionDeployments:
    faction = classhandler.factionClass(deploymentData["faction"],jsonhandler.getfactionsjson())
    deployment = armyhandler.getDeploymentClass(faction,deploymentData["id"])
    try: Apercentage = attackingScore/5
    except ZeroDivisionError: 
        Apercentage = 0
    if Apercentage != 0:
      tierOne = math.floor(deployment.tierOne*Apercentage)
      tierTwo = math.floor(deployment.tierTwo*Apercentage)
    else:  
        tierOne,tierTwo = deployment.tierOne,deployment.tierTwo

    deployments = faction.deployments.raw
    for deploymentIndex in deployments:
        if deploymentIndex["id"] == deploymentData["id"]:
            if Apercentage == 1:
                deploymentName = deploymentIndex["name"]
                await interaction.channel.send(f"{deploymentName} has routed.")
                deployments.remove(deploymentIndex)
            else:
                deploymentIndex["tierOne"] = tierOne
                deploymentIndex["tierTwo"] = tierTwo   
            factionGuild = client.get_guild(faction.guild)
            jsonhandler.save_factions(factionGuild,jsonhandler.getfactionsjson(),faction.guild,faction.resources.raw,deployments,faction.capital,faction.permissions.raw)

  msg = f"""
# BATTLE OUTCOME {score}!

{classhandler.factionClass(winningFaction,jsonhandler.getfactionsjson()).name} was victourious!

The attacking team suffered an attrition of {Dpercentage*100}%
The defending team suffered an attrition of {Apercentage*100}%
"""
  return msg

async def reinforce(interaction,client,factionName,deploymentName,side):
  # === Permissions Check ===
  permission = await adminhandler.admincheck(interaction.user,client)
  if permission == False:
    return "You do not have permission to use this command."

  # === Channel Check ===
  mediatorJson = getMediatorJson()
  channelId = interaction.channel.id
  channelIds = [m["id"] for m in mediatorJson]
  if channelId not in channelIds:
    return f"This channel is not hosting terms for a battle." 
  channelData = mediatorClass(channelId)
  # === Faction & Deployment Get ===
  for faction in jsonhandler.getfactionsjson():
    if factionName == faction["name"]:
      factionId = faction["guild"]
      break

  faction = classhandler.factionClass(factionId,jsonhandler.getfactionsjson())
  for deploymentIndex in faction.deployments.raw:
    if deploymentIndex["name"] == deploymentName: deploymentId = deploymentIndex["id"]
  try:
    deployment = armyhandler.getDeploymentClass(faction,deploymentId)
  except: return f"`Deployment {deploymentName}` could not be found."
  # === Pre Existance Check ===
  allDeployments = channelData.attackingFactionDeployments + channelData.defendingFactionDeployments
  for deploymentIndex in allDeployments:
    if deploymentIndex["faction"] == factionName and deploymentIndex["id"] == deployment.id:
      return f"`Deployment {deployment}` is already reinforcing."
  # === Nearby Check ===
  region = classhandler.regionClass(jsonhandler.getregionjson(),channelData.region)
  if deployment.region not in region.neighbours and deployment.region != region.id:
    return f"`Deployment {deployment.name}` is not nearby to reinforce"
  # Add to json data
  if side.name == "Attackers":
    attackers = channelData.attackingFactionDeployments
    attackers.append({"faction": faction.name,"id": deployment.id})
    saveMediatorJson(channelData.id,channelData.attackingFaction,attackers,channelData.defendingFaction,channelData.defendingFactionDeployments,channelData.region)
  elif side.name == "Defenders":
    defenders = channelData.defendingFactionDeployments
    defenders.append({"faction": faction.name,"id": deployment.id})
    saveMediatorJson(channelData.id,channelData.attackingFaction,channelData.attackingFactionDeployments,channelData.defendingFaction,defenders,channelData.region)
  else: return "An error has occured."
  return f"`Deployment {deployment.name}` has reinforced the {side.name}"

async def remove_reinforcement(interaction,client,factionName,deploymentName):
  # === Permissions Check ===
  permission = await adminhandler.admincheck(interaction.user,client)
  if permission == False:
    return "You do not have permission to use this command."

  # === Channel Check ===
  mediatorJson = getMediatorJson()
  channelId = interaction.channel.id
  channelIds = [m["id"] for m in mediatorJson]
  if channelId not in channelIds:
    return f"This channel is not hosting terms for a battle." 
  channelData = mediatorClass(channelId)
  # === Faction & Deployment Get ===
  for faction in jsonhandler.getfactionsjson():
    if factionName == faction["name"]:
      factionId = faction["guild"]
      break

  faction = classhandler.factionClass(factionId,jsonhandler.getfactionsjson())
  for deploymentIndex in faction.deployments.raw:
    if deploymentIndex["name"] == deploymentName: deploymentId = deploymentIndex["id"]
  try:
    deployment = armyhandler.getDeploymentClass(faction,deploymentId)
  except: return f"`Deployment {deploymentName}` could not be found."
  # If attacking deployment
  if deployment.id in [d["id"] for d in channelData.attackingFactionDeployments] and deployment.faction == factionName.name:
    deployments = channelData.attackingFactionDeployments
    for deploymentIndex in deployments:
      if deploymentIndex["id"] == deployment.id:
        deployments.remove(deploymentIndex)
        break
    saveMediatorJson(channelId,channelData.attackingFaction,deployments,channelData.defendingFaction,channelData.defendingFactionDeployments,channelData.region)
  # If defending deployment
  if deployment.id in [d["id"] for d in channelData.defendingFactionDeployments] and deployment.faction == factionName.name:
    deployments = channelData.defendingFactionDeployments
    for deploymentIndex in deployments:
      if deploymentIndex["id"] == deployment.id:
        deployments.remove(deploymentIndex)
        break
    saveMediatorJson(channelId,channelData.attackingFaction,channelData.attackingFactionDeployments,channelData.defendingFaction,deployments,channelData.region)
  return f"`Deployment {deploymentName}` has been removed from the battle."

def viewTeams(interaction):
# === Channel Check ===
  mediatorJson = getMediatorJson()
  channelId = interaction.channel.id
  channelIds = [m["id"] for m in mediatorJson]
  if channelId not in channelIds:
    return f"This channel is not hosting terms for a battle." 
  channelData = mediatorClass(channelId)
  
  attackingTotalTierOne = 0
  attackingTotalTierTwo = 0

  defendingTotalTierOne = 0
  defendingTotalTierTwo = 0
  msg = """
# Attacking Team
"""
  for attackingDeployment in channelData.attackingFactionDeployments:
    attackingFaction = classhandler.factionClass(attackingDeployment["faction"],jsonhandler.getfactionsjson())
    attackingDeployment = armyhandler.getDeploymentClass(attackingFaction,attackingDeployment["id"])
    
    attackingTotalTierOne += attackingDeployment.tierOne
    attackingTotalTierTwo += attackingDeployment.tierTwo
    msg+=f"""
Faction: {attackingFaction.name}

Tier One: {attackingDeployment.tierOne}
Tier Two: {attackingDeployment.tierTwo}

"""
  msg+= f"""
**Attacking Team Total**
Tier One: {attackingTotalTierOne}
Tier Two: {attackingTotalTierTwo}

# Defending Team
"""
  for defendingDeployment in channelData.defendingFactionDeployments:
    defendingFaction = classhandler.factionClass(defendingDeployment["faction"],jsonhandler.getfactionsjson())
    defendingDeployment = armyhandler.getDeploymentClass(defendingFaction,defendingDeployment["id"])
    
    defendingTotalTierOne += defendingDeployment.tierOne
    defendingTotalTierTwo += defendingDeployment.tierTwo
    msg+=f"""
Faction: {defendingFaction.name}

Tier One: {defendingDeployment.tierOne}
Tier Two: {defendingDeployment.tierTwo}

"""
  msg+= f"""
**Defending Team Total**
Tier One: {defendingTotalTierOne}
Tier Two: {defendingTotalTierTwo}

"""
  return msg

async def giveManpower(interaction,client,factionName,manpower):
 # === Permissions Check ===
  permission = await adminhandler.admincheck(interaction.user,client)
  if permission == False:
    return "You do not have permission to use this command." 
  
  #name to id
  for i in jsonhandler.getfactionsjson():
    if i["name"] == factionName.name:
      factionId = i["guild"]
      break

  faction = classhandler.factionClass(factionId,jsonhandler.getfactionsjson())
  factionManpower = faction.resources.manpower
  factionManpower += manpower
  resourcesDict = {"gold": faction.resources.gold,"iron": faction.resources.iron,"stone": faction.resources.stone,"wood": faction.resources.wood,"manpower": factionManpower}
  factionGuild = client.get_guild(faction.guild)
  jsonhandler.save_factions(factionGuild,jsonhandler.getfactionsjson(),faction.guild,resourcesDict,faction.deployments.raw,faction.capital,faction.permissions.raw)
  return f"`Faction {faction.name}` now has {factionManpower} manpower."

async def closeChannel(interaction,client):
# === Permissions Check ===
  permission = await adminhandler.admincheck(interaction.user,client)
  if permission == False:
    return "You do not have permission to use this command."

  # === Channel Check ===
  mediatorJson = getMediatorJson()
  channelId = interaction.channel.id
  channelIds = [m["id"] for m in mediatorJson]
  if channelId not in channelIds:
    return f"This channel is not hosting terms for a battle." 
  
  channel = interaction.guild.get_channel(channelId)
  await interaction.response.send_message("This channel is being deleted.")
  removeMediatorJson(channelId)
  time.sleep(1.5)
  await channel.delete()
  
def getMediatorJson():
  with open("Data/mediator.json","r") as file:
    jsondata = json.loads(file.read())
  return jsondata

def addMediatorJson(id,attackingFaction,attackingDeploymentId,defendingFaction,defendingDeploymentId,regionId):
  """
  Args:
    id - Channel id
    attackingFaction - Name of the attackingFaction
    defendingFaction - Name of defendingFaction
    regionId -Id of the region (defendingDeployment.region)
  """
  data = {
    "id": id,
    "attackingFaction": attackingFaction,
    "attackingDeployments": [],
    "defendingFaction": defendingFaction,
    "defendingDeployments": [],
    "region": regionId
    
  }
  data["attackingDeployments"].append({"faction": attackingFaction, "id": attackingDeploymentId})
  data["defendingDeployments"].append({"faction": defendingFaction, "id": defendingDeploymentId})
  mediatorJson = getMediatorJson()
  mediatorJson.append(data)
  with open("Data/mediator.json","w") as file:
    json.dump(mediatorJson,file,indent = 4)

def removeMediatorJson(id):
  """
  Args:
    Id -channel id of the battle channel
  """
  mediatorJson = getMediatorJson()
  for data in mediatorJson:
    if data["id"] == id:
      mediatorJson.remove(data)
      break
  
  with open("Data/mediator.json","w") as file:
    json.dump(mediatorJson,file,indent = 4)

def saveMediatorJson(id,attackingFaction,attackingDeployments,defendingFaction,defendingDeployments,regionId):
  """
  Args:
    id - Channel id
    attackingFaction - Name of the attackingFaction
    defendingFaction - Name of defendingFaction
    regionId -Id of the region (defendingDeployment.region)
  """

  mediatorJson = getMediatorJson()
  for data in mediatorJson:
    if data["id"] == id:
      data["attackingFaction"] = attackingFaction
      data["attackingDeployments"] = attackingDeployments
      data["defendingFaction"] = defendingFaction
      data["defendingDeployments"] = defendingDeployments
      break
  with open("Data/mediator.json","w") as file:
    json.dump(mediatorJson,file,indent = 4)
