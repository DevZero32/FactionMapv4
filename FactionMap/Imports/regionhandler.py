from Imports import jsonhandler,classhandler,factionshandler,turnshandler, imagehandler, armyhandler

def regionlookup(interaction, region,regions):
  if not (1 <= region <= len(regions)): return (f"Region must between 1 and {len(regions)}")
  region = classhandler.regionClass(jsonhandler.getregionjson(),region)
  
  if region.water == True: 
    landType = "Water" 
  else: landType = "Land"
  msg =(f""" 
  
# Region {region.id}

Faction: {region.owner}

Building: {region.building}
Resources: {", ".join(region.resources)}
Neighbours: {", ".join(str(neighbour) for neighbour in region.neighbours)}

LandType: {landType}
Biome: {region.biome}""")

  return msg

def build(interaction,regionId,building):
  
  #Check Permissions
  permissions = factionshandler.checkPermissions(interaction,interaction.user)
  if permissions["region"] == False: return "You lack permissions to build."
  region = classhandler.regionClass(jsonhandler.getregionjson(),regionId)
  if interaction.guild.name != region.owner: return "You must own this region to build on it"
  #Vers
  faction = classhandler.factionClass(region.owner,jsonhandler.getfactionsjson())
  
  #Turn handling
  if turnshandler.checkLogs(faction.name,"regions",region.id):
    return f"`Region {region.id}` has already been interacted with."
  
  resources = faction.resources
  building = building.name

  costs = {
    'Port': {'wood': 15, 'stone': 30, 'gold': 100,"iron":0},
    'Fort': {'wood': 10, 'stone': 40, 'gold': 175, 'iron': 20},
    'Village': {'wood': 25, 'stone': 25, 'gold': 100,"iron": 0}}
  costs = costs[building]
  #resource requirements
  if not (resources.wood >= costs["wood"] and resources.stone >= costs["stone"] and resources.gold >= costs["gold"] and resources.iron >= costs["iron"]): 
    return (f"You lack the necessary resources to build {building}.\nGold: {resources.gold}\nIron:{resources.iron}\nStone: {resources.stone}\nWood: {resources.wood}")
  #Land checks
  if building == "Port" and not any(classhandler.regionClass(jsonhandler.getregionjson(), neighbour).water for neighbour in region.neighbours): 
    return "Port must be built on land and near water."
  if region.building == "Capital": return f"{interaction.user.mention} THATS YOUR CAPITAL YOU NUMPTY!"
  if region.land == False: return (f"{building} must be built on land.")

  if region.building == building: return (f"{building} is already built at {region.id}")
  #Saving
  region.building = building
  resources.gold -= costs["gold"]
  resources.iron -= costs["iron"]
  resources.stone -= costs["stone"]
  resources.wood -= costs["wood"]

  resourcesDict = {'gold': resources.gold, 'iron': resources.iron, 'stone': resources.stone, 'wood': resources.wood, 'manpower': resources.manpower}
  jsonhandler.save_regions(jsonhandler.getregionjson(),region.id,faction.name,region.building)
  jsonhandler.save_factions(interaction.guild,jsonhandler.getfactionsjson(),interaction.guild.id,resourcesDict,faction.deployments.raw,faction.capital,faction.permissions.raw)
  turnshandler.logTurn(faction.name,"regions",region.id)
  imagehandler.assembleMap.cache_clear()
  return (f"{building} built at {region.id}")

def regionOwnership(faction,region):
  """
  Check if the specified faction owns the given region.

  Args:
    faction: An instance of factionClass representing the faction to check.
    region: An integer representing the region ID to check for ownership.

  Returns:
    True if the faction owns the region,
    False if the region is invalid,
    False if the region is not owned by said faction.
  """
  regions = jsonhandler.getregionjson()
  
  if not (1 <= region <= len(regions)): return False
  region = classhandler.regionClass(regions,region)
  if faction.name != region.owner: return False
  return True

def capital(interaction,regionId):
  # === Region Existance Check ====
  if not 0 < regionId <= len(jsonhandler.getregionjson()): return f"`Region {regionId}` is not a valid region."
  region = classhandler.regionClass(jsonhandler.getregionjson(),regionId)
  if region.water == True: return f"`Region {region.id}` You cannot occupy the ocean."
  # === Faction Existance Check ====
  factions = jsonhandler.getfactionsjson()
  if interaction.guild.id not in [faction["guild"] for faction in factions]:
    return f"{interaction.guild.name} is not a faction. please run `/setup` before setting up a capital."
  faction = classhandler.factionClass(interaction.guild.name,factions)
  
  #Check Permissions
  permissions = factionshandler.checkPermissions(interaction,interaction.user)
  if permissions["region"] == False : return "You lack permissions to build a capital."
  region = classhandler.regionClass(jsonhandler.getregionjson(),regionId)
  if region.owner != "None" and region.owner != faction.name: return f"`Region {region.id}` is occupied, please find another region."
  #Turn handling
  if turnshandler.checkLogs(faction.name,"regions",region.id):
    return f"`Region {region.id}` has already been interacted with."

  if faction.capital == 0 and len(faction.regions) == 0:
    capital = regionId
    regions = jsonhandler.getregionjson()
    jsonhandler.save_regions(regions,region.id,faction.name,"Capital")
    jsonhandler.save_factions(interaction.guild,factions,faction.guild,faction.resources.raw,faction.deployments.raw,capital,faction.permissions.raw)
    imagehandler.updateFactionBorders(faction.name)
    imagehandler.addBuilding(regionId)
    return f"`Faction {faction.name}` initated! Welcome to Faction Map!"
  else:
    if region.owner != faction.name: return "You must own this region to build here."
    resources = faction.resources
    building = "Capital"

    costs = {
      'Capital': {'wood': 25, 'stone': 30, 'gold': 500,"iron":15}}
    costs = costs[building]
    #resource requirements
    if not (resources.wood >= costs["wood"] and resources.stone >= costs["stone"] and resources.gold >= costs["gold"] and resources.iron >= costs["iron"]): 
      return (f"You lack the necessary resources to build {building}.\nGold: {resources.gold}\nIron:{resources.iron}\nStone: {resources.stone}\nWood: {resources.wood}")
    #Land checks
    if region.building == building: return (f"{building} is already built at {region.id}")
    #Saving
    region.building = building
    resources.gold -= costs["gold"]
    resources.iron -= costs["iron"]
    resources.stone -= costs["stone"]
    resources.wood -= costs["wood"]

    resourcesDict = {'gold': resources.gold, 'iron': resources.iron, 'stone': resources.stone, 'wood': resources.wood, 'manpower': resources.manpower}
    jsonhandler.save_regions(jsonhandler.getregionjson(),faction.capital,faction.name,"None")
    jsonhandler.save_regions(jsonhandler.getregionjson(),region.id,faction.name,region.building)
    jsonhandler.save_factions(interaction.guild,jsonhandler.getfactionsjson(),interaction.guild.id,resourcesDict,faction.deployments.raw,faction.capital,faction.permissions.raw)
    turnshandler.logTurn(faction.name,"regions",region.id)
    return (f"`{building}` built at `Region {region.id}`")