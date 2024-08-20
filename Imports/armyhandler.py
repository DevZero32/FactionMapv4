from Imports import jsonhandler ,factionshandler,classhandler,regionhandler,turnshandler,mediatorhandler,imagehandler
import time

def getDeploymentClass(faction, id):
  """
  Retrieve the deployment class for a given faction and deployment ID.

  Args:
    faction: An instance of the faction class.
    deployment: A dictionary containing deployment details.
    id: An integer representing the deployment ID.

  Returns:
    The deployment class associated with the given ID.
  """
  try:
    deployment = getattr(faction.deployments.armies, f"deployment_{id}")
    return deployment
  except: return None

def getDeploymentClassMethodTwo(faction,deployment,id):
  """
  Retrieve the deployment class for a given faction and deployment ID.

  Args:
    faction: An instance of the faction class.
    deployment: A dictionary containing deployment details.
    id: An integer representing the deployment ID.

  Returns:
    The deployment class associated with the given ID.
  """
  try: 
    id = deployment["id"]
    deployment = getattr(faction.deployments.armies, f"deployment_{id}")
    return deployment
  except: return None
def getDeployment(faction,roleId): #Faction being class
  AttrName = f"army_{roleId}" # Create the dynamic attribute name for role permissions
  deployment = getattr(faction.deployments, AttrName, None) # Access attribute for role permissions using dynamic name
  return deployment

def displaydeployments(interaction):
  factions = jsonhandler.getfactionsjson() # Retrieve the list of factions from the JSON file
  factionNames =  [indexFaction["name"] for indexFaction in factions] # Extract the names of all factions into a list

  if interaction.guild.name not in factionNames:
    return (f"{interaction.guild.name} is not a faction.") # Check if the provided factionName is valid

  faction = classhandler.factionClass(interaction.guild.id, jsonhandler.getfactionsjson())
  #Permission check
  member = interaction.user
  permissions = factionshandler.checkPermissions(interaction,member)
  if permissions["army"] == False: return "You lack permission to access deployments."

  #Displaying deployments
  deployments = faction.deployments
  msg = """ 
  # Deployments
  """

  if len(deployments.raw) == 0:
    return msg +(f"""

    {faction.name} currently has no deployments.""")

  for deployment in deployments.raw:
      deployment = getDeploymentClass(faction,deployment["id"])
      turned = turnshandler.checkLogs(faction.guild,"deployments",deployment.id)
      
      msg += f"""
**{deployment.name}**

Location: {deployment.region}
Teir one: {deployment.tierOne}
Teir two: {deployment.tierTwo}

Interacted: {turned}
*Has the deployment been interacted or in battle.*

"""
  return msg

def formDeployment(interaction,region,name):
  factions = jsonhandler.getfactionsjson()

  if interaction.guild.name not in jsonhandler.get_faction_names():
    return (f"{interaction.guild.name} is not a faction")

  #Faction Permissions check
  faction = classhandler.factionClass(interaction.guild.id,factions)

  permissions = factionshandler.checkPermissions(interaction,interaction.user)
  if permissions["army"] == False: return "You lack permissions to do this."
  # === Name Check ===
  #for faction in factions:
  #  factionI = classhandler.factionClass(faction["name"],factions)
  #  deploymentNames = [d["name"] for d in factionI.deployments.raw]
  #  if name in deploymentNames: return f"`Name {name}` is already taken."
      
  #Region Check
  if regionhandler.regionOwnership(faction,region) == False: return (f"`Region {region}` is not owned by `Faction {faction.name}` ")

  region = classhandler.regionClass(jsonhandler.getregionjson(),region)

  if region.building not in ["Capital","Fort"]:
    return "Deployments can only be formed at Capitals and Forts."
  #Resource check
  if faction.resources.gold <= 49:
    return (f"{faction.name} lack enough gold for make a deployment")

  deployments = faction.deployments.raw
  names = [deployment["name"] for deployment in deployments]
  if name in names: return "That name is already taken."
  try:
    highestId = 0
    for deplomentIndex in deployments:
      if deplomentIndex["id"] > highestId:
        highestId = deplomentIndex["id"]
    length = highestId
  except:
    length = 0
  newDeployment = {
      "id": length+1,
      "name": name,
      "region": region.id,
      "tierOne": 0,
      "tierTwo": 0
  }
  resources = faction.resources
  resourcesDict = {'gold': resources.gold - 50, 'iron': resources.iron, 'stone': resources.stone, 'wood': resources.wood, 'manpower': resources.manpower}
  deployments.append(newDeployment)
  jsonhandler.save_factions(interaction.guild,factions,faction.guild,resourcesDict,deployments,faction.capital,faction.permissions.raw)
  return (f"Deployment formed at {region.id}, Use the `/rally`command to rally to the deployment.")

def disbandDeployment(interaction,name):
  factions = jsonhandler.getfactionsjson()
  # === Faction existance check ===
  if interaction.guild.name not in jsonhandler.get_faction_names():
    return (f"{interaction.guild.name} is not a faction")

  #Faction Permissions check
  faction = classhandler.factionClass(interaction.guild.id,factions)

  permissions = factionshandler.checkPermissions(interaction,interaction.user)
  if permissions["army"] == False: return "You lack permissions to do this."
  # === Deployment existance check ===
  deployments = faction.deployments.raw

  if name not in [deployment["name"] for deployment in deployments]:
    return (f"{name} is not a valid deployment")
  # === Battle check ===
  def deploymentIdViaName(faction,deploymentName):
    deployments = faction.deployments.raw
    for deployment in deployments:
      if deployment["name"] == deploymentName:
        return deployment["id"]
  
  mediatorData = mediatorhandler.getMediatorJson()
  for battle in mediatorData:
    battle = mediatorhandler.mediatorClass(battle["id"])
    battleDeployments = battle.defendingFactionDeployments + battle.attackingFactionDeployments
    for battleDeployment in battleDeployments:
      if battleDeployment["faction"] == faction.name and battleDeployment["id"] == deploymentIdViaName(faction,name):
        return f"`Deployment {deployment.name} cannot disband due to being in a battle."

  # === removal ===
  for deployment in deployments:
    if deployment["name"] == name:
      region = classhandler.regionClass(jsonhandler.getregionjson(),deployment["region"])
      deployments.remove(deployment)
      break

  jsonhandler.save_factions(interaction.guild,jsonhandler.getfactionsjson(),interaction.guild.id,faction.resources.raw,deployments,faction.capital,faction.permissions.raw)
  if region.building == "None": imagehandler.assembleMap.cache_clear()
  return f"{name} has been disbanded."

def rallyDeployment(interaction,infType,quantity,deploymentName):
  factions = jsonhandler.getfactionsjson()
  
  if interaction.guild.id not in [faction["guild"] for faction in factions]:
    return f"{interaction.guild.name} is not a faction."
  
  #Permission check
  member = interaction.user
  permissions = factionshandler.checkPermissions(interaction,member)
  if permissions["army"] == False: return "You lack permission to access deployments."
  
  faction = classhandler.factionClass(interaction.guild.id,factions)
  deployments = faction.deployments
  #deployment existance check
  if deploymentName not in [deployment["name"] for deployment in deployments.raw]:
    return f"{deploymentName} is not a deployment."
  #getting deployment class
  for deployment in deployments.raw:
    if deployment["name"] == deploymentName:
      deploymentId = deployment["id"]
      break
  
  deployment = getDeploymentClass(faction,deploymentId)
  #location check
  region = classhandler.regionClass(jsonhandler.getregionjson(),deployment.region)
  if region.building not in ["Fort","Capital"]:
    return f"{deployment.name} must be located in a fort or capital to rally to."
  if region.owner != faction.name:
    return f"{faction.name} must own the region to rally."
  #turn check
  if turnshandler.checkLogs(faction.guild,"deployment",deploymentId) == True:
    return f"`{deployment.name}` has already been interacted with for this turn."
  if turnshandler.checkLogs(faction.guild,"regions",region.id) == True:
    return f"`Region {region.id}` has already been interacted with for this turn."
  
  #formatting inf type
  infType = infType.name
  
  formatInfType = lambda s: 'tier' + s.split(' ')[1].capitalize() #Switching the formating of the string to suit the json
  formattedInfType = formatInfType(infType)
  costs = {
    'tierOne': {'gold': 50,"manpower":1},
    'tierTwo': {'gold': 150,"manpower":3}}
  costs = costs[formatInfType(infType)]
  #resource check
  resources = faction.resources

  if resources.manpower < costs["manpower"]*quantity and resources.gold < costs["gold"]*quantity:
    return f"{faction.name} does not have enough resouces to rally {infType}."

  #Army limiting
  deploymentSize = deployment.tierOne + deployment.tierTwo + quantity
  deploymentLimit = 40
  if deploymentSize > deploymentLimit:
    return f"Exceeded deployment limit of {deploymentLimit}"
  deploymentsRaw = deployments.raw
  # Automatically find the formattedInfType and add to it accordingly
  for deploymentRaw in deploymentsRaw:
    if deploymentRaw["name"] == deploymentName:
      if formattedInfType == "tierOne":
        deploymentRaw["tierOne"] += quantity
      elif formattedInfType == "tierTwo":
        deploymentRaw["tierTwo"] += quantity
      else: return f"Infantry Type({formatInfType}) is unrecognised, please notify <@604817657169969182>."
  # === resource check ===
  if resources.gold < costs["gold"]*quantity or resources.manpower < costs["manpower"]*quantity:
    return f"`Faction {faction.name}` lacks enough resources for this rally."

  #Taking resources
  gold = resources.gold - costs["gold"]*quantity
  manpower = resources.manpower - costs["manpower"]*quantity
  resourcesDict = {"gold": gold, "iron": resources.iron, "stone": resources.stone, "wood": resources.wood, "manpower": manpower}
  jsonhandler.save_factions(interaction.guild,factions,faction.guild,resourcesDict,deployments.raw,faction.capital,faction.permissions.raw)
  turnshandler.logTurn(faction.guild,"deployments",deploymentId,turnshandler.getTurns()["nextTurn"] - time.time())
  turnshandler.logTurn(faction.guild,"regions",region.id,turnshandler.getTurns()["nextTurn"] - time.time())
  return f"{deploymentName} has rallied {quantity} {infType.lower()}."

def marchDeployment(interaction,deploymentName,regionId):
  # === Faction Existance Check ====
  factions = jsonhandler.getfactionsjson()
  if interaction.guild.id not in [faction["guild"] for faction in factions]:
    return f"{interaction.guild.name} is not a faction."
  
  faction = classhandler.factionClass(interaction.guild.id,factions)
  # === Region Existance Check ====
  if not 0 < regionId <= len(jsonhandler.getregionjson()): return f"`Region {regionId}` is not a valid region."
  region = classhandler.regionClass(jsonhandler.getregionjson(),regionId)
  
  #  === Deployment Existance Check ====
  deployments = faction.deployments.raw

  if deploymentName not in [deployment["name"] for deployment in deployments]:
    return f"{deploymentName} is not a deployment."
  
  # === Permission Check ====
  member = interaction.user
  permissions = factionshandler.checkPermissions(interaction,member)
  if permissions["army"] == False: return "You lack permission to access deployments."

  # === Deployment Class ====

  for deployment in deployments:
    if deployment["name"] == deploymentName:
      deploymentRegion = classhandler.regionClass(jsonhandler.getregionjson(),deployment["region"])
      deployment = getDeploymentClass(faction,deployment["id"])
      break
  # === Troop size check ===
  if deployment.tierOne + deployment.tierTwo <= 0:
    return f"`Deployment {deployment.name}` has no infantry."

  # === Neighbour & Water Check ===
  if deployment.region not in region.neighbours:
    return f"`Region {region.id}` is not a nieghbour."
  elif region.water and (deploymentRegion.building != "Port" and deploymentRegion.land == True):
    return f"To cross into the sea, You must do that a port. `Region {deploymentRegion.id} is not a port.`"
  # === Turn Check ===
  if turnshandler.checkLogs(faction.guild,"deployments",deployment.id) == True:
    return f"`Deployment {deployment.name}` has already been interacted with this turn."
  # === Region attack'd check ===
  mediatorData = mediatorhandler.getMediatorJson()
  for channel in mediatorData:
    if region.id == channel["region"]:
        return f"You cannot march to `Region {region.id}` due to it being under attack."
  
  # === Applying change to deployments ===
  for deploymentIndex in deployments:
    if deploymentIndex["name"] == deployment.name:
      deploymentIndex["region"] = region.id
      break
  # === Saving & Logging Turn ===
  jsonhandler.save_factions(interaction.guild,factions,interaction.guild.id,faction.resources.raw,deployments,faction.capital,faction.permissions.raw)
  turnshandler.logTurn(faction.guild,"deployments",deployment.id,min(max(((deployment.tierOne + deployment.tierTwo)*600),3600*3),3600))
  if deploymentRegion.building == "None" or region.building == "None": imagehandler.assembleMap.cache_clear()
  return f"`Deployment {deployment.name}` has marched to `Region {region.id}`"

async def attackDeployment(interaction, client, deploymentName, targetName):
  # === Faction Existence Check ===
  factions = jsonhandler.getfactionsjson()
  if interaction.guild.id not in [faction["guild"] for faction in factions]:
      return f"{interaction.guild.name} is not a faction."

  # === Permission Check ====
  member = interaction.user
  permissions = factionshandler.checkPermissions(interaction,member)
  if permissions["army"] == False: return "You lack permission to access deployments."

  # === Faction Retrieval ===
  def getFactionViaDeployment(deploymentName):
    factions = jsonhandler.getfactionsjson()
    for faction in factions:
      faction = classhandler.factionClass(faction["guild"],factions)
      deployments = faction.deployments.raw
      for deployment in deployments:
        if deployment["name"] == deploymentName: 
          return faction
    return False

  def deploymentIdViaName(faction,DeploymentName):
    deployments = faction.deployments.raw
    for deployment in deployments:
      if deployment["name"] == deploymentName:
        return deployment["id"]
  
  def deploymentViaName(faction,deploymentName):
    deployments = faction.deployments.raw
    for deployment in deployments:
      if deployment["name"] == deploymentName:
        return deployment
 
  attackingFaction = classhandler.factionClass(interaction.guild.id, factions)
  # === Deployment Existance Check ===
  attackingDeploymentFound = False
  for attackingDeployment in attackingFaction.deployments.raw:
    if attackingDeployment["name"] == deploymentName:
      attackingDeploymentFound = True
      break
  if attackingDeploymentFound == False:
    return f"{deploymentName} could not be found."
  attackingDeployment = getDeploymentClass(attackingFaction,deploymentIdViaName(attackingFaction,deploymentName))
  # === Turn check ===
  if turnshandler.checkLogs(attackingDeployment.faction,"deployments",attackingDeployment.id) == True:
    return f"`Deployment {attackingDeployment.name}` has been interacted with."
    
  
  # === Troop size check ===
  if not attackingDeployment.tierOne + attackingDeployment.tierTwo > 0:
    return f"`Deployment {deploymentName}` has no troops to attack with."

  defendingFaction = getFactionViaDeployment(targetName)
  if defendingFaction == False: return f"{targetName} could not be found."
  defendingDeployment = getDeploymentClassMethodTwo(defendingFaction,deploymentViaName(defendingFaction,targetName),deploymentIdViaName(defendingFaction,targetName))

  # === Nearby Check ===

  attackingDeploymentRegion = classhandler.regionClass(jsonhandler.getregionjson(),attackingDeployment.region)
  if defendingDeployment.region not in attackingDeploymentRegion.neighbours and defendingDeployment.region != attackingDeployment.region:
    return f"{targetName} is not close enough to be attacked."
  # === Battle pre existance check ===
  battleData = mediatorhandler.getMediatorJson()
  allDeployments = []
  for battle in battleData:
    battleInfo = mediatorhandler.mediatorClass(battle["id"])
    for attackingDeploymentIndex in battleInfo.attackingFactionDeployments:
        allDeployments.append(attackingDeploymentIndex)
    for defendingDeploymentIndex in battleInfo.defendingFactionDeployments:
        allDeployments.append(defendingDeploymentIndex)

  for deploymentIndex in allDeployments:
    deploymentFaction = classhandler.factionClass(deploymentIndex["faction"],factions)
    deploymentIndex = getDeploymentClass(deploymentFaction ,deploymentIndex["id"])
    if deploymentFaction.name == defendingDeployment.faction and deploymentIndex.id == defendingDeployment.id:
        return f"`Deployment {defendingDeployment.name}` is already in a battle"
  await interaction.response.send_message(f"`Deployment {deploymentName}` has begun a battle with `Enemy Deployment {targetName}`")

  # === Mediator Channel Creation ===
  class BattleInfoClass():
    def __init__(self,attackingFaction,attackingDeployment,defendingFaction,defendingDeployment):
      self.attackingFaction = attackingFaction
      self.attackingDeployment = attackingDeployment
      self.defendingFaction = defendingFaction
      self.defendingDeployment = defendingDeployment
      self.region = defendingDeployment.region
  battleInfo = BattleInfoClass(attackingFaction,attackingDeployment,defendingFaction,defendingDeployment)
  await mediatorhandler.createChannel(interaction, client,battleInfo)
 
def occupyRegion(interaction,client,regionId):
  # === Faction Existence Check ===
  factions = jsonhandler.getfactionsjson()
  if interaction.guild.id not in [faction["guild"] for faction in factions]:
      return f"{interaction.guild.name} is not a faction."
  faction = classhandler.factionClass(interaction.guild.id,factions)
  # === Region Existance Check ====
  if not 0 < regionId <= len(jsonhandler.getregionjson()): return f"`Region {regionId}` is not a valid region."
  region = classhandler.regionClass(jsonhandler.getregionjson(),regionId)
  
  # === Region water check ===

  if region.water == True:
    return f"Cannot occupy `Region {region.id}` as its ocean."

  # === Permissions Check ===
  
  member = interaction.user
  permissions = factionshandler.checkPermissions(interaction,member)
  if permissions["army"] == False: return "You lack permission to access deployments."
  
  # === Deployment Locations Check ===

  if regionId not in [d["region"] for d in faction.deployments.raw]:
    return f"`Faction {faction.name}` doesnt have a deployment in the region to occupy the region."

  # === Attacking Faction Deployments turn check ===
  attackingDeploymentAva = False
  attackingAvaDeployments = []
  for deploymentIndex in faction.deployments.raw:
    if deploymentIndex["region"] != regionId:
      continue
    deploymentIndex = getDeploymentClass(faction,deploymentIndex["id"])
    if turnshandler.checkLogs(faction.guild,"deployments",deploymentIndex.id) == False:
      attackingDeploymentAva = True
      attackingAvaDeployments.append(deploymentIndex.id)

  if attackingDeploymentAva == False:
    return f"`Faction {faction.name}` all deployments in `region {region.id}` have been interacted with already."
  # === Region owner check ===
  if region.owner == faction.name:  
    return f"`Faction {faction.name}` already owns `Region {regionId}`"

  # === Region owner deployment presence === 
  if region.owner != "None":
    owningFaction = classhandler.factionClass(region.owner,factions)
    oFDR = [d["region"] for d in owningFaction.deployments.raw]
    deploymentPresent = regionId in oFDR 
  else:
    deploymentPresent = False
  
  if deploymentPresent == True:
    return f"`Faction {owningFaction.name}` has a deployment in the region preventing you from taking the region."
  
   # === Logging Turn ===
  for deploymentIndex in attackingAvaDeployments:
    turnshandler.logTurn(faction.guild,"deployments",deploymentIndex,turnshandler.getTurns()["nextTurn"] - time.time())

  # === Saving occupation
  
  if region.building == "Capital" and region.owner != "None": # removing the capital
    region.building = "None"
    def getFactionIdViaName(factionName):
        factions = jsonhandler.getfactionsjson()
        for faction in factions:
            if faction["name"] != factionName:
                continue
            return faction["guild"]
    # Removing old factions capital data
    oldFactionId = getFactionIdViaName(region.owner)
    oldFactionGuild = client.get_guild(oldFactionId)
    oldFaction = classhandler.factionClass(region.owner,jsonhandler.getfactionsjson())
    jsonhandler.save_factions(oldFactionGuild,jsonhandler.getfactionsjson(),oldFactionId,oldFaction.resources.raw,oldFaction.deployments.raw,0,oldFaction.permissions.raw)


  jsonhandler.save_regions(jsonhandler.getregionjson(),regionId,owner=faction.guild,building=region.building)
  imagehandler.assembleMap.cache_clear()
  imagehandler.updateFactionBorders(faction.id)
  return (f"`Faction {faction.name}` now owns `Region {regionId}`")

def scoutRegion(interaction,regionId):
  # === Faction Existence Check ===
  factions = jsonhandler.getfactionsjson()
  if interaction.guild.id not in [faction["guild"] for faction in factions]:
      return f"{interaction.guild.name} is not a faction."
  faction = classhandler.factionClass(interaction.guild.id,factions)
  # === Region Existance Check ====
  if not 0 < regionId <= len(jsonhandler.getregionjson()): return f"`Region {regionId}` is not a valid region."
  region = classhandler.regionClass(jsonhandler.getregionjson(),regionId)
  
  # === Permissions Check ===
  
  member = interaction.user
  permissions = factionshandler.checkPermissions(interaction,member)
  if permissions["army"] == False: return "You lack permission to access deployments."
  
  # === Deployment Locations Check ===

  deployments = faction.deployments.raw
  def nearbyCheck(deployments):
    for deployment in deployments:
      deployment = getDeploymentClass(faction,deployment["id"])
      deployment.region = classhandler.regionClass(jsonhandler.getregionjson(),deployment.region)
      area = deployment.region.neighbours
      area.append(deployment.region.id)
      if regionId in area:
        return True
    return False
  
  if not nearbyCheck(deployments):
    return f"`Faction {faction.name}` has no deployments nearby."
  
  # === Listing deployments in region ===
  header = f"""
# Deployments in `Region {regionId}`
 """
  found = False
  for faction in factions:
    faction = classhandler.factionClass(faction["guild"],factions)
    for deployment in faction.deployments.raw:
      deployment = getDeploymentClass(faction,deployment["id"])
      if deployment.region == regionId:
        found = True
        header += f"""
**{deployment.name}**

Teir one: {deployment.tierOne}
Teir two: {deployment.tierTwo}

"""
  if not found:
    header += "No Deployments Found"
  return header
