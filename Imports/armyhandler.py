from Imports import jsonhandler ,factionshandler,classhandler,regionhandler,turnshandler,mediatorhandler,imagehandler,embedhandler
import asyncio
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

async def displaydeployments(interaction):
  factions = jsonhandler.getfactionsjson() # Retrieve the list of factions from the JSON file
  factionNames =  [indexFaction["name"] for indexFaction in factions] # Extract the names of all factions into a list

  if interaction.guild.name not in factionNames:
    embed = embedhandler.dangerEmbed(f"{interaction.guild.name} is not a faction","ensure that your faction is setup","Command denied")
    return await interaction.followup.send(embed=embed)

  faction = classhandler.factionClass(interaction.guild.id, jsonhandler.getfactionsjson())
  #Permission check
  member = interaction.user
  permissions = factionshandler.checkPermissions(interaction,member)
  if permissions["army"] == False: 
    embed = embedhandler.dangerEmbed("You lack permissions to access `/armies`","Ensure that you have permissions set","Command denied")
    return await interaction.followup.send(embed=embed)
  #Displaying deployments
  deployments = faction.deployments
  msg = ""

  if len(deployments.raw) == 0:
    embed = embedhandler.positiveEmbed("You have no armies",f"All deployments for {faction.name}","Deployments")
    return await interaction.followup.send(embed=embed)

  for deployment in deployments.raw:
    deployment = getDeploymentClass(faction,deployment["id"])
    turned = turnshandler.checkLogs(faction.guild,"deployments",deployment.id)
    battleBool = turnshandler.checkBattles(faction.guild,deployment.id)
    if battleBool: cooldownCondition = "**(In battle)**"
    elif not battleBool and turned: cooldownCondition = "**(Cooldown)**"
    else: cooldownCondition = ""
      
    msg += f"""
    **{deployment.name}**

    Location: {deployment.region}
    Tier one: {deployment.tierOne}
    Tier two: {deployment.tierTwo}

    Interacted: {turned} {cooldownCondition}
    Next interaction: <t:{deployment.nextTurn:.0f}:R>
    *Has the deployment been interacted or in battle.*

    """
  embed = embedhandler.positiveEmbed(msg,f"All deployments for {faction.name}","Deployments")
  return await interaction.followup.send(embed=embed)

async def formDeployment(interaction,region,name):
  factions = jsonhandler.getfactionsjson()

  if interaction.guild.name not in jsonhandler.get_faction_names():
    return (f"{interaction.guild.name} is not a faction")

  #Faction Permissions check
  faction = classhandler.factionClass(interaction.guild.id,factions)

  permissions = factionshandler.checkPermissions(interaction,interaction.user)
  if permissions["army"] == False:
    embed = embedhandler.dangerEmbed("You lack permissions to access `/armies`","Ensure that you have permissions set","Command denied")
    return await interaction.followup.send(embed=embed)
      
  #Region Check
  if regionhandler.regionOwnership(faction,region) == False: 
    file,embed = embedhandler.dangerEmbedFactionLogo(f"`Region {region}` is not owned by {faction.name}","Ensure that you have permissions set","Command denied",faction.guild)
    return await interaction.followup.send(embed=embed)

  region = classhandler.regionClass(jsonhandler.getregionjson(),region)

  if region.building not in ["Capital","Fort"]:
    file,embed = embedhandler.dangerEmbedFactionLogo("Deployments can only be formed at Capitals and Forts.","Find a region which is one of these","Command denied",faction.guild)
    return await interaction.followup.send(embed=embed,file=file)
  #Resource check
  if faction.resources.gold <= 49:
    file,embed = embedhandler.dangerEmbedFactionLogo(f"{faction.name} lacks enough gold to form a deployment","You need 50 gold to form","Command denied",faction.guild)
    return await interaction.followup.send(embed=embed,file=file)
  deployments = faction.deployments.raw
  names = [
    deployment["name"]
    for faction in factions
    if "deployments" in faction and isinstance(faction["deployments"], list)
    for deployment in faction["deployments"]
    if "name" in deployment
]
  if name in names: 
    file,embed = embedhandler.dangerEmbedFactionLogo("That name is already in use.","Pick a unique name","Command denied",faction.guild)
    return await interaction.followup.send(embed=embed,file=file)
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
  file,embed = embedhandler.positiveEmbedFactionLogo(f"Deployment formed at {region.id}", "Use the `/rally`command to rally to the deployment.","Deployment formed",faction.guild)
  return await interaction.followup.send(embed=embed,file=file)

async def disbandDeployment(interaction,name):
  factions = jsonhandler.getfactionsjson()
  # === Faction existance check ===
  if interaction.guild.name not in jsonhandler.get_faction_names():
    embed = embedhandler.dangerEmbed(f"{interaction.guild.name} is not a faction","")
    return await interaction.followup.send(embed=embed)

  #Faction Permissions check
  faction = classhandler.factionClass(interaction.guild.id,factions)

  permissions = factionshandler.checkPermissions(interaction,interaction.user)
  if permissions["army"] == False: 
    embed = embedhandler.dangerEmbed("You lack permissions to access `/disband`","Ensure that you have permissions set","Command denied")
    return await interaction.followup.send(embed=embed)
  # === Deployment existance check ===
  deployments = faction.deployments.raw

  if name not in [deployment["name"] for deployment in deployments]:
    embed = embedhandler.dangerEmbed(f"{name} is not a valid deployment","Ensure that you have the correct name","Command denied")
    return await interaction.followup.send(embed=embed)
 
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
        embed = embedhandler.dangerEmbed(f"`Deployment {deployment.name} cannot disband due to being in a battle.","Wait until the battle is over","Command denied")
        return await interaction.followup.send(embed=embed)
  # === removal ===
  for deployment in deployments:
    if deployment["name"] == name:
      region = classhandler.regionClass(jsonhandler.getregionjson(),deployment["region"])
      deployments.remove(deployment)
      break

  jsonhandler.save_factions(interaction.guild,jsonhandler.getfactionsjson(),interaction.guild.id,faction.resources.raw,deployments,faction.capital,faction.permissions.raw)
  if region.building == "None": imagehandler.assembleMap.cache_clear()
  embed = embedhandler.positiveEmbed(f"`Deployment {deployment['name']} has successfully disbanded","","Disbanded")
  return await interaction.followup.send(embed=embed)

async def rallyDeployment(interaction,infType,quantity,deploymentName):
  factions = jsonhandler.getfactionsjson()
  
  if interaction.guild.id not in [faction["guild"] for faction in factions]:
    embed = embedhandler.dangerEmbed(f"{interaction.guild.name} is not a faction","ensure that your faction is setup","Command denied")
    return await interaction.followup.send(embed=embed)
  
  #Permission check
  member = interaction.user
  permissions = factionshandler.checkPermissions(interaction,member)
  if permissions["army"] == False:
    embed = embedhandler.dangerEmbed("You lack permissions to access `/rally`","Ensure that you have permissions set","Command denied")
    return await interaction.followup.send(embed=embed)
  
  faction = classhandler.factionClass(interaction.guild.id,factions)
  deployments = faction.deployments
  #deployment existance check
  if deploymentName not in [deployment["name"] for deployment in deployments.raw]:
    embed = embedhandler.dangerEmbed(f"{deploymentName} is not a valid deployment","Ensure that you have the correct name","Command denied")
    return await interaction.followup.send(embed=embed)

  #getting deployment class
  for deployment in deployments.raw:
    if deployment["name"] == deploymentName:
      deploymentId = deployment["id"]
      break
  
  deployment = getDeploymentClass(faction,deploymentId)
  #location check
  region = classhandler.regionClass(jsonhandler.getregionjson(),deployment.region)
  if region.building not in ["Fort","Capital"]:
    embed = embedhandler.dangerEmbed(f"{deployment.name} must be located in a fort or capital to rally to.","Move the deployment to a region with a fort or capital","Command denied")
    return await interaction.followup.send(embed=embed)

  if region.owner != faction.guild:
    embed = embedhandler.dangerEmbed(f"{faction.name} must own the region to rally.","Move to a region which you own","Command denied")
    return await interaction.followup.send(embed=embed)
  #turn check
  if turnshandler.checkLogs(faction.guild,"deployments",deploymentId) == True:
    embed = embedhandler.dangerEmbed(f"{deployment.name} is currently on cooldown","Check `/armies` for when it will be next avaliable","Command denied")
    return await interaction.followup.send(embed=embed)
  if turnshandler.checkLogs(faction.guild,"regions",region.id) == True:
    embed = embedhandler.dangerEmbed(f"`Region {region.id}` is currently on cooldown","It will be avaliable next turn, check with `/Turn`","Command denied")
    return await interaction.followup.send(embed=embed)
  
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

  if resources.manpower < costs["manpower"]*quantity or resources.gold < costs["gold"]*quantity:
    embed = embedhandler.dangerEmbed(f"{faction.name} does not have enough resouces to rally {quantity} {infType}.","Ensure that you have enough resources, check your resources with `/overview`","Command denied")
    return await interaction.followup.send(embed=embed)

  #Army limiting
  deploymentSize = deployment.tierOne + deployment.tierTwo + quantity
  deploymentLimit = 50
  if deploymentSize > deploymentLimit:
    embed = embedhandler.dangerEmbed(f"Exceeds deployment limit of {deploymentLimit}","Ensure that you do not break this limit","Command denied")
    return await interaction.followup.send(embed=embed)
  
  deploymentsRaw = deployments.raw
  # Automatically find the formattedInfType and add to it accordingly
  for deploymentRaw in deploymentsRaw:
    if deploymentRaw["name"] == deploymentName:
      if formattedInfType == "tierOne":
        deploymentRaw["tierOne"] += quantity
      elif formattedInfType == "tierTwo":
        deploymentRaw["tierTwo"] += quantity
      else: 
        embed = embedhandler.dangerEmbed(f"Infantry Type({formatInfType}) is unrecognised, please notify <@604817657169969182>.","If you see this error message something has gone horribly wrong!`","Command denied")
        return await interaction.followup.send(embed=embed)

  #Taking resources
  gold = resources.gold - costs["gold"]*quantity
  manpower = resources.manpower - costs["manpower"]*quantity
  resourcesDict = {"gold": gold, "iron": resources.iron, "stone": resources.stone, "wood": resources.wood, "manpower": manpower}
  jsonhandler.save_factions(interaction.guild,factions,faction.guild,resourcesDict,deployments.raw,faction.capital,faction.permissions.raw)
  turnshandler.logTurn(faction.guild,"deployments",deploymentId,turnshandler.getTurns()["nextTurn"] - time.time())
  turnshandler.logTurn(faction.guild,"regions",region.id,turnshandler.getTurns()["nextTurn"] - time.time())
  embed = embedhandler.positiveEmbed(f"{deploymentName} has rallied {quantity} {infType.lower()}.","View your armies with `/armies`","Rally successfull")
  return await interaction.followup.send(embed=embed)

async def marchDeployment(client,interaction,deploymentName,regionId):
  # === Faction Existance Check ====
  factions = jsonhandler.getfactionsjson()
  if interaction.guild.id not in [faction["guild"] for faction in factions]:
    embed = embedhandler.dangerEmbed(f"{interaction.guild.name} is not a faction","ensure that your faction is setup","Command denied")
    return await interaction.followup.send(embed=embed)
  
  faction = classhandler.factionClass(interaction.guild.id,factions)
  # === Region Existance Check ====
  if not 0 < regionId <= len(jsonhandler.getregionjson()): return f"`Region {regionId}` is not a valid region."
  region = classhandler.regionClass(jsonhandler.getregionjson(),regionId)
  
  #  === Deployment Existance Check ====
  deployments = faction.deployments.raw

  if deploymentName not in [deployment["name"] for deployment in deployments]:
    embed = embedhandler.dangerEmbed(f"{deploymentName} is not a valid deployment","Ensure that you have the correct name","Command denied")
    return await interaction.followup.send(embed=embed)
  
  # === Permission Check ====
  member = interaction.user
  permissions = factionshandler.checkPermissions(interaction,member)
  if permissions["army"] == False:
    embed = embedhandler.dangerEmbed("You lack permissions to access `/armies`","Ensure that you have permissions set","Command denied")
    return await interaction.followup.send(embed=embed)

  # === Deployment Class ====

  for deployment in deployments:
    if deployment["name"] == deploymentName:
      deploymentRegion = classhandler.regionClass(jsonhandler.getregionjson(),deployment["region"])
      deployment = getDeploymentClass(faction,deployment["id"])
      break
  # === Troop size check ===
  if deployment.tierOne + deployment.tierTwo <= 0:
    embed = embedhandler.dangerEmbed(f"`Deployment {deployment.name}` has no infantry and cannot be marched.","Ensure that you have rallied to the deployment","Command denied")
    return await interaction.followup.send(embed=embed)

  # === Neighbour & Water Check ===
  if deployment.region not in region.neighbours:
    embed = embedhandler.dangerEmbed(f"`Region {region.id}` is not a nieghbour.","Check neigbouring regions with `/region_lookup`","Command denied")
    return await interaction.followup.send(embed=embed)

  elif region.water and (deploymentRegion.building not in ["Capital","Port"] and deploymentRegion.land == True):
    embed = embedhandler.dangerEmbed(f"To cross into the sea, You must do that a port or capital. `Region {deploymentRegion.id} is neither.`","Find a capital or port to access the sea","Command denied")
    return await interaction.followup.send(embed=embed)

  # === Turn Check ===
  if turnshandler.checkLogs(faction.guild,"deployments",deployment.id) == True:
    embed = embedhandler.dangerEmbed(f"{deployment.name} is currently on cooldown","Check `/armies` for when it will be next avaliable","Command denied")
    return await interaction.followup.send(embed=embed)
  # === Region attack'd check ===
  mediatorData = mediatorhandler.getMediatorJson()
  for channel in mediatorData:
    if region.id == channel["region"]:
        embed = embedhandler.dangerEmbed(f"You cannot march to `Region {region.id}` due to it being under attack.","","Command denied")
        return await interaction.followup.send(embed=embed)
  
  # === Applying change to deployments ===
  for deploymentIndex in deployments:
    if deploymentIndex["name"] == deployment.name:
      deploymentIndex["region"] = region.id
      break
  # === Saving & Logging Turn ===
  jsonhandler.save_factions(interaction.guild,factions,interaction.guild.id,faction.resources.raw,deployments,faction.capital,faction.permissions.raw)
  turnshandler.logTurn(faction.guild,"deployments",deployment.id,min(max(((deployment.tierOne + deployment.tierTwo)*600),3600*3),3600))
  if deploymentRegion.building == "None" or region.building == "None": imagehandler.assembleMap.cache_clear()
  embed = embedhandler.positiveEmbed(f"`Deployment {deployment.name}` has marched to `Region {region.id}`","View your armies with `/armies`","March successfull")
  await interaction.followup.send(embed=embed)
  try:
    if region.owner != faction.guild:
      regionOwner = client.get_guild(region.owner)
      regionFaction = classhandler.factionClass(factionId=region.owner,factions=factions)
      alertChannel = regionOwner.get_channel(regionFaction.alert)
      file,embed = embedhandler.dangerEmbedFactionLogo(f"{faction.name} has marched an army into `Region {region.id}`","Region tresspass alert",f"Region {region.id} entered",regionFaction.guild)
      await alertChannel.send(embed=embed,file=file)
  except Exception: pass

async def attackDeployment(interaction, client, deploymentName, targetName):
  # === Faction Existence Check ===
  factions = jsonhandler.getfactionsjson()
  if interaction.guild.id not in [faction["guild"] for faction in factions]:
    embed = embedhandler.dangerEmbed(f"{interaction.guild.name} is not a faction","ensure that your faction is setup","Command denied")
    return await interaction.followup.send(embed=embed)

  # === Permission Check ====
  member = interaction.user
  permissions = factionshandler.checkPermissions(interaction,member)
  if permissions["army"] == False: 
    embed = embedhandler.dangerEmbed("You lack permissions to access `/armies`","Ensure that you have permissions set","Command denied")
    return await interaction.followup.send(embed=embed)

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
    embed = embedhandler.dangerEmbed(f"{deploymentName} could not be found.","To ensure you have to correct name: use `/armies`","Command denied")
    return await interaction.followup.send(embed=embed)

  attackingDeployment = getDeploymentClass(attackingFaction,deploymentIdViaName(attackingFaction,deploymentName))
  # === Turn check ===
  if turnshandler.checkLogs(attackingDeployment.guild,"deployments",attackingDeployment.id) == True:
    embed = embedhandler.dangerEmbed(f"{attackingDeployment.name} is currently on cooldown or is in a battle","Check `/armies` for when it will be next avaliable","Command denied")
    return await interaction.followup.send(embed=embed)
    
  
  # === Troop size check ===
  if not attackingDeployment.tierOne + attackingDeployment.tierTwo > 0:
    embed = embedhandler.dangerEmbed(f"`Deployment {deploymentName}` has no troops to attack with.","You need to rally before you can attack","Command denied")
    return await interaction.followup.send(embed=embed)

  defendingFaction = getFactionViaDeployment(targetName)
  if defendingFaction == False: 
    embed = embedhandler.dangerEmbed(f"{targetName} could not be found.","An easy to check if you have the correct army is with `/scout`","Command denied")
    return await interaction.followup.send(embed=embed)
  
  defendingDeployment = getDeploymentClassMethodTwo(defendingFaction,deploymentViaName(defendingFaction,targetName),deploymentIdViaName(defendingFaction,targetName))

  # === Same faction check ===
  if defendingDeployment.guild == attackingDeployment.guild:
    embed = embedhandler.dangerEmbed("You cannot attack yourself","","Command denied")
    return await interaction.followup.send(embed=embed)

  # === Nearby Check ===

  attackingDeploymentRegion = classhandler.regionClass(jsonhandler.getregionjson(),attackingDeployment.region)
  if defendingDeployment.region not in attackingDeploymentRegion.neighbours and defendingDeployment.region != attackingDeployment.region:
    embed = embedhandler.dangerEmbed(f"{targetName} is not close enough to be attacked.","An easy to check if you have the correct army is with `/scout`","Command denied")
    return await interaction.followup.send(embed=embed)
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
        embed = embedhandler.dangerEmbed(f"`Deployment {defendingDeployment.name}` is already in a battle","","Command denied")
        return await interaction.followup.send(embed=embed)
    
  embed = embedhandler.dangerEmbed(f"`Deployment {deploymentName}` has begun a battle with `Enemy Deployment {targetName}`","","Command denied")
  await interaction.followup.send(embed=embed)

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
 
async def occupyRegion(interaction,client,regionId):
  # === Faction Existence Check ===
  factions = jsonhandler.getfactionsjson()
  if interaction.guild.id not in [faction["guild"] for faction in factions]:
    embed = embedhandler.dangerEmbed(f"{interaction.guild.name} is not a faction","ensure that your faction is setup","Command denied")
    return await interaction.followup.send(embed=embed)
  
  faction = classhandler.factionClass(interaction.guild.id,factions)
  # === Region Existance Check ====
  if not 0 < regionId <= len(jsonhandler.getregionjson()): 
    embed = embedhandler.dangerEmbed(f"`Region {regionId}` is not a valid region.","","Command denied")
    return await interaction.followup.send(embed=embed)

  region = classhandler.regionClass(jsonhandler.getregionjson(),regionId)
  
  # === Region water check ===

  if region.water == True:
    embed = embedhandler.dangerEmbed(f"Cannot occupy `Region {region.id}` as its ocean.","Only land can be occupied","Command denied")
    return await interaction.followup.send(embed=embed)

  # === Permissions Check ===
  
  member = interaction.user
  permissions = factionshandler.checkPermissions(interaction,member)
  if permissions["army"] == False: 
    embed = embedhandler.dangerEmbed("You lack permissions to access `/armies`","Ensure that you have permissions set","Command denied")
    return await interaction.followup.send(embed=embed)
  
  # === Deployment Locations Check ===

  if regionId not in [d["region"] for d in faction.deployments.raw]:
    embed = embedhandler.dangerEmbed(f"`Faction {faction.name}` doesnt have a deployment in the region to occupy the region.","Ensure that you have army to occupy in the region","Command denied")
    return await interaction.followup.send(embed=embed)

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
    embed = embedhandler.dangerEmbed(f"`Faction {faction.name}` all deployments in `region {region.id}` have been interacted with already.","Ensure that you have army to occupy in the region","Command denied")
    return await interaction.followup.send(embed=embed)
  # === Region owner check ===
  if region.owner == faction.guild:
    embed = embedhandler.dangerEmbed(f"`Faction {faction.name}` already owns `Region {regionId}`","","Command denied")
    return await interaction.followup.send(embed=embed)

  # === Region owner deployment presence === 
  if region.owner != "None":
    owningFaction = classhandler.factionClass(region.owner,factions)
    oFDR = [d["region"] for d in owningFaction.deployments.raw]
    deploymentPresent = regionId in oFDR 
  else:
    deploymentPresent = False
  
  if deploymentPresent == True:
    embed = embedhandler.dangerEmbed(f"`Faction {owningFaction.name}` has a deployment in the region preventing you from taking the region.","You can destory the deployment using`/scout` & `/attack` ","Command denied")
    return await interaction.followup.send(embed=embed)
  
   # === Logging Turn ===
  for deploymentIndex in attackingAvaDeployments:
    turnshandler.logTurn(faction.guild,"deployments",deploymentIndex,turnshandler.getTurns()["nextTurn"] - time.time())

  # === Saving occupation
  
  if region.owner != "None": # old owner
    #remove capital
    if region.building == "Capital":
      region.building = "None"

    # Removing old factions capital data
    oldFactionGuild = client.get_guild(region.owner)
    oldFaction = classhandler.factionClass(region.owner,jsonhandler.getfactionsjson())
    await asyncio.to_thread(imagehandler.updateFactionBorders,oldFaction.guild)
    imagehandler.assembleMap.cache_clear()
    jsonhandler.save_factions(oldFactionGuild,jsonhandler.getfactionsjson(),region.owner,oldFaction.resources.raw,oldFaction.deployments.raw,0,oldFaction.permissions.raw)

    # Send alert to old faction
    try:
      oldFactionGuildObj = client.get_guild(oldFaction.guild)
      alertChannel = oldFactionGuildObj.get_channel(oldFaction.alert)
      file,embed = embedhandler.dangerEmbedFactionLogo(f"{faction.name} has taken `Region {region.id}`",f"You no longer control this region",f"Region {region.id} seized",oldFaction.guild)
      await alertChannel.send(embed=embed,file=file)
    except Exception: pass


  jsonhandler.save_regions(jsonhandler.getregionjson(),regionId,owner=faction.guild,building=region.building)
  imagehandler.assembleMap.cache_clear()
  await asyncio.to_thread(imagehandler.updateFactionBorders,faction.guild)
  embed = embedhandler.positiveEmbed(f"`Faction {faction.name}` now owns `Region {regionId}`","","Region Occupied")
  return await interaction.followup.send(embed=embed)

async def scoutRegion(interaction,regionId):
  # === Faction Existence Check ===
  factions = jsonhandler.getfactionsjson()
  if interaction.guild.id not in [faction["guild"] for faction in factions]:
    embed = embedhandler.dangerEmbed(f"{interaction.guild.name} is not a faction","ensure that your faction is setup","Command denied")
    return await interaction.followup.send(embed=embed)
  faction = classhandler.factionClass(interaction.guild.id,factions)
  # === Region Existance Check ====
  if not 0 < regionId <= len(jsonhandler.getregionjson()): 
    embed = embedhandler.dangerEmbed(f"`Region {regionId}` is not a valid region.","Please ensure that you have a valid region","Comamnd denied")
    return await interaction.followup.send(embed=embed)
  region = classhandler.regionClass(jsonhandler.getregionjson(),regionId)
  
  # === Permissions Check ===
  
  member = interaction.user
  permissions = factionshandler.checkPermissions(interaction,member)
  if permissions["army"] == False: 
    embed = embedhandler.dangerEmbed("You lack permissions to access `/armies`","Ensure that you have permissions set","Command denied")
    return await interaction.followup.send(embed=embed)
  
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
    embed = embedhandler.dangerEmbed(f"`Faction {faction.name}` has no deployments nearby.","Ensure that you have a deployment in a neighbouring region to scout","Command denied")
    return await interaction.followup.send(embed=embed)
  
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

Tier one: {deployment.tierOne}
Tier two: {deployment.tierTwo}

"""
  if not found:
    header += "No Deployments Found"
  embed = embedhandler.positiveEmbed(header,"",f"Deployments in ` Region {regionId}")
  return await interaction.followup.send(embed=embed)
