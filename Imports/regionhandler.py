from Imports import jsonhandler,classhandler,factionshandler,turnshandler, imagehandler, armyhandler,embedhandler
import time
import asyncio

async def regionlookup(interaction, region,regions):
  if not (1 <= region <= len(regions)): 
    embed = embedhandler.dangerEmbed(f"Region must between 1 and {len(regions)}","","Command denied")
    return interaction.followup.send(embed=embed)
  region = classhandler.regionClass(jsonhandler.getregionjson(),region)
  
  if region.water == True: 
    landType = "Water" 
  else: landType = "Land"

  regionOwner = "None"
  if region.owner != "None":
     regionOwner = classhandler.factionClass(region.owner,jsonhandler.getfactionsjson()).name

  msg =(f""" 
Faction: {regionOwner}

Building: {region.building}
Resources: {", ".join(region.resources)}
Neighbours: {", ".join(str(neighbour) for neighbour in region.neighbours)}

LandType: {landType}
Biome: {region.biome}

Interacted: {turnshandler.checkRegionInteraction(region.id)}
   """)
  embed = embedhandler.positiveEmbed(msg,"All relevant information",f"Region {region.id}")
  return await interaction.followup.send(embed=embed)

async def build(interaction,regionId,building):
  #Check Permissions
  permissions = factionshandler.checkPermissions(interaction,interaction.user)
  if permissions["region"] == False: 
    embed = embedhandler.dangerEmbed("You lack permissions to access `/build`","Ensure that you have permissions set","Command denied")
    return await interaction.followup.send(embed=embed)
  
  region = classhandler.regionClass(jsonhandler.getregionjson(),regionId)
  if interaction.guild.id != region.owner: 
    embed = embedhandler.dangerEmbed("You must own this region to build on it","Use occupy to take this region.","Command denied")
    return await interaction.followup.send(embed=embed)
  #Vers
  faction = classhandler.factionClass(region.owner,jsonhandler.getfactionsjson())
  
  #Turn handling
  if turnshandler.checkLogs(faction.guild,"regions",region.id):
    embed = embedhandler.dangerEmbed(f"`Region {region.id}` has already been interacted with.","Use `/turn` to find when it will be next avaiable","Command denied")
    return await interaction.followup.send(embed=embed)
  
  resources = faction.resources
  building = building.name

  costs = {
    'Port': {'wood': 15, 'stone': 30, 'gold': 100,"iron":0},
    'Fort': {'wood': 10, 'stone': 40, 'gold': 175, 'iron': 20},
    'Village': {'wood': 25, 'stone': 25, 'gold': 100,"iron": 0}}
  costs = costs[building]
  #resource requirements
  if not (resources.wood >= costs["wood"] and resources.stone >= costs["stone"] and resources.gold >= costs["gold"] and resources.iron >= costs["iron"]): 
    embed = embedhandler.dangerEmbed(f"You lack the necessary resources to build {building}.\nGold: {resources.gold}\nIron:{resources.iron}\nStone: {resources.stone}\nWood: {resources.wood}","","Command denied")
    return await interaction.followup.send(embed=embed)
  #Land checks
  if building == "Port" and not any(classhandler.regionClass(jsonhandler.getregionjson(), neighbour).water for neighbour in region.neighbours):
    embed = embedhandler.dangerEmbed("Port must be built on land and next to water","","Command denied")
    return await interaction.followup.send(embed=embed)
  if region.building == "Capital":
    embed = embedhandler.dangerEmbed(f"Attempted to replace Capital with {building}","If you wish to move your capital, use `/capital`","Command denied")
    return await interaction.followup.send(embed=embed)

  if region.land == False:
    embed = embedhandler.dangerEmbed(f"{building} must be built on land.","","Command denied")
    return await interaction.followup.send(embed=embed)

  if region.building == building:
    embed = embedhandler.dangerEmbed(f"{building} is already built at {region.id}","","Command denied")
    return await interaction.followup.send(embed=embed)

  #Saving
  region.building = building
  resources.gold -= costs["gold"]
  resources.iron -= costs["iron"]
  resources.stone -= costs["stone"]
  resources.wood -= costs["wood"]

  resourcesDict = {'gold': resources.gold, 'iron': resources.iron, 'stone': resources.stone, 'wood': resources.wood, 'manpower': resources.manpower}
  jsonhandler.save_regions(jsonhandler.getregionjson(),region.id,faction.guild,region.building)
  jsonhandler.save_factions(interaction.guild,jsonhandler.getfactionsjson(),interaction.guild.id,resourcesDict,faction.deployments.raw,faction.capital,faction.permissions.raw)
  turnshandler.logTurn(faction.guild,"regions",region.id,turnshandler.getTurns()["nextTurn"] - time.time())
  imagehandler.assembleMap.cache_clear()
  embed = embedhandler.positiveEmbed(f"{building} has been built at {region.id}","Map will be updating to display your new building",f"{building} built")
  return await interaction.followup.send(embed=embed)

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
  if faction.guild != region.owner: return False
  return True

async def capital(interaction,regionId):
  # === Region Existance Check ====
  if not 0 < regionId <= len(jsonhandler.getregionjson()): return f"`Region {regionId}` is not a valid region."
  region = classhandler.regionClass(jsonhandler.getregionjson(),regionId)
  if region.water == True: 
    embed = embedhandler.dangerEmbed(f"`Region {region.id}` You cannot occupy the ocean.","Find land to occupy","Command denied")
    return await interaction.followup.send(embed)
  # === Faction Existance Check ====
  factions = jsonhandler.getfactionsjson()
  if interaction.guild.id not in [faction["guild"] for faction in factions]:
    embed = embedhandler.dangerEmbed(f"{interaction.guild.name} is not a faction. please run `/setup` before setting up a capital.","","Command denied")
    return await interaction.followup.send(embed=embed)
  faction = classhandler.factionClass(interaction.guild.id,factions)
  
  #Check Permissions
  permissions = factionshandler.checkPermissions(interaction,interaction.user)
  if permissions["region"] == False:
    embed = embedhandler.dangerEmbed("You lack permissions to build a capital.","Ensure that you have permissions set","Command denied")
    return await interaction.followup.send(embed=embed)

  region = classhandler.regionClass(jsonhandler.getregionjson(),regionId)
  if region.owner != "None" and region.owner != faction.guild: 
    embed = embedhandler.dangerEmbed(f"`Region {region.id}` is occupied, please find another region.","","Command denied")
    return await interaction.followup.send(embed=embed)
  #Turn handling
  if turnshandler.checkLogs(faction.guild,"regions",region.id):
    embed = embedhandler.dangerEmbed(f"`Region {region.id}` has already been interacted with.","Use `/turn` to find when it will be next avaiable","Command denied")
    return await interaction.followup.send(embed=embed)

  if faction.capital == 0 and len(faction.regions) == 0:
    capital = regionId
    regions = jsonhandler.getregionjson()
    jsonhandler.save_regions(regions,region.id,faction.guild,"Capital")
    jsonhandler.save_factions(interaction.guild,factions,faction.guild,faction.resources.raw,faction.deployments.raw,capital,faction.permissions.raw)
    await asyncio.wait_for(asyncio.to_thread(imagehandler.updateFactionBorders,faction.guild), timeout=360)
    await asyncio.to_thread(imagehandler.addBuilding,regionId)
    file,embed = embedhandler.positiveEmbedFactionLogo("Welcome to Faction Map!\n\nYou can now interact with the map.","Refer to the guides if you get stuck",f"{faction.name}` initated!",faction.guild)
    return await interaction.followup.send(embed=embed,file=file)
  else:
    if region.owner != faction.guild: 
      embed = embedhandler.dangerEmbed("You must own this region to build here.","","Command denied")
      return await interaction.followup.send(embed=embed)

    resources = faction.resources
    building = "Capital"

    costs = {
      'Capital': {'wood': 25, 'stone': 30, 'gold': 500,"iron":15}}
    costs = costs[building]
    #resource requirements
    if not (resources.wood >= costs["wood"] and resources.stone >= costs["stone"] and resources.gold >= costs["gold"] and resources.iron >= costs["iron"]): 
      embed = embedhandler.dangerEmbed(f"You lack the necessary resources to build {building}.\nGold: {resources.gold}\nIron:{resources.iron}\nStone: {resources.stone}\nWood: {resources.wood}","","Command denied")
      return await interaction.followup.send(embed=embed)
    #Land checks
    if region.building == building: 
      embed = embedhandler.dangerEmbed(f"{building} is already built at {region.id}","","Command denied")
      return await interaction.followup.send(embed=embed)
    #Saving
    region.building = building
    resources.gold -= costs["gold"]
    resources.iron -= costs["iron"]
    resources.stone -= costs["stone"]
    resources.wood -= costs["wood"]

    resourcesDict = {'gold': resources.gold, 'iron': resources.iron, 'stone': resources.stone, 'wood': resources.wood, 'manpower': resources.manpower}
    jsonhandler.save_regions(jsonhandler.getregionjson(),faction.capital,faction.guild,"None")
    jsonhandler.save_regions(jsonhandler.getregionjson(),region.id,faction.guild,region.building)
    jsonhandler.save_factions(interaction.guild,jsonhandler.getfactionsjson(),interaction.guild.id,resourcesDict,faction.deployments.raw,region.id,faction.permissions.raw)
    turnshandler.logTurn(faction.guild,"regions",region.id,turnshandler.getTurns()["nextTurn"] - time.time())
    imagehandler.assembleMap.cache_clear()
    embed = embedhandler.positiveEmbed(f"{building} has been built at {region.id}","Map will be updating to display your new building",f"{building} built")
    return await interaction.followup.send(embed=embed)