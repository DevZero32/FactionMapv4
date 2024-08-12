import json
import discord
from Imports import turnshandler,classhandler
from discord.ext import commands
from functools import lru_cache

# -REGIONS-
def getregionjson():
  """
  Gives Raw Json Data of regions.json
  """
  with open("Data/regions.json","r") as file:
    jsondata = json.loads(file.read())
  return jsondata


def save_regions(Regions,id,owner,building):
  """
  Saves region data to json file Data/regions.json.
  """
  for Region in Regions:
    if Region["regionId"] == id:
      Region["regionOwner"] = owner
      Region["building"] = building
  with open("Data/regions.json","w") as file:
    json.dump(Regions,file,indent = 4)

# -FACTIONS-
def getfactionsjson():
  """
  Gives Raw Json Data of factions.Json
  """
  with open("Data/factions.json","r") as file:
    jsondata = json.loads(file.read())
    file.close()
  return jsondata

def save_factions(guild,factions,factionGuildId,resources,deployments,capital,permissions):
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
      faction["name"] = guild.name
      faction["capital"] = capital
      faction["deployments"] = deployments
      faction["resources"] = resources
      faction["permissions"] = permissions
      
  with open("Data/factions.json","w") as file:
    json.dump(factions,file,indent = 4)
    file.close()


def get_faction_names():
  """
  Retrieves a list of faction names from the factions JSON data.

  Returns:
      list: A list of faction names.
  """
  factions = getfactionsjson()
  faction_names = []
  for faction in factions:
    faction_names.append(faction["name"])
  return faction_names


def get_faction_info(faction_name):
  """
  Retrieves information for a specific faction based on the faction name.

  Args:
      faction_name (str): The name of the faction to retrieve information for.

  Returns:
      dict: A dictionary containing the faction's information, or None if not found.
  """
  factions = getfactionsjson()
  for faction in factions:
    if faction_name.name == faction["name"]:
      return faction
  return None

# -VERIFIED FACTIONS-

def getverifiedfactionsjson(): #Get the data of verified factions json data (Factions that are authorised to play faction map)
  with open("Data/verifiedfactions.json","r") as file:
    jsondata = json.loads(file.read())
    file.close()
  return jsondata

async def add_verifiedfaction(interaction,factionName,id): #Add a faction to verified faction json data
  factions = getverifiedfactionsjson()
  
  for faction in factions:
    if faction["guild"] == id or faction["name"] == factionName:
        existing_name = faction["name"]
        await interaction.response.send_message(f"This guild is already occupied; `{existing_name}`.")
        return "occupied"
  newfaction = {
      "name": factionName,
      "guild": id
  }
  factions.append(newfaction)
  with open("Data/verifiedfactions.json", "w") as file:
      json.dump(factions, file, indent=4)

async def remove_verifiedfaction(interaction,factionName,id):
  factions = getverifiedfactionsjson()

  with open("Data/verifiedfactions.json", "w") as file:
      json.dump(factions, file, indent=4)

# === Turn handleing + Setup ===
def updateAlert(guildId,AlertChannelId):
  factions = getfactionsjson()

  for faction in factions:
    factionId = faction["guild"]
    if factionId == guildId:
      faction["alert"] = AlertChannelId
      
  with open("Data/factions.json","w") as file:
    json.dump(factions,file,indent = 4)
    file.close()


async def setup_faction(name,guild_id,client,interaction,alertChannel):
  new_faction = {
    
        "name": name,
        "guild": guild_id,
        "alert": alertChannel,
        "capital": 0,
        "resources": {
            "gold": 500,
            "iron": 25,
            "stone": 50,
            "wood": 50,
            "manpower": 20
        },
        "deployments": [
        ],
        "permissions": [
        ]
    }
  factions = getfactionsjson()
  factions.append(new_faction)
  with open("Data/factions.json", "w") as file:
    json.dump(factions, file, indent=4)
  turnshandler.addFactionTurn(guild_id)

  embed = discord.Embed(
    color=discord.Color(int('5865f2',16)),
    description=f"""
You're almost ready to join the faction map!

Just set up your permissions using `/set_permissions`, and then you can choose your capital location with `/capital`.
"""
)
  faction = classhandler.factionClass(interaction.guild.id,getfactionsjson())

  file = discord.File(f"Data/Logos/{faction.guild}.png",filename=f"{faction.guild}.png")
  embed.set_author(name=f"{faction.name} Setup!",icon_url=f"attachment://{faction.guild}.png")
  return await interaction.response.send_message(embed=embed,file=file)