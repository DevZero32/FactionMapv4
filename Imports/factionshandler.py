from Imports import jsonhandler,classhandler,imagehandler,adminhandler
import discord
from discord.utils import get
"""
async def dualPrevent(interaction,client) -> bool:
    async def __mutualPermissions__(client: discord.client, userId: int, factionId: int):
        async def __getPermissions__(permissions,roleId):
            for role in permissions:
                if role["roleId"] == roleId:
                    print(role["rolePermissions"])
                    return role["rolePermissions"]

        guild = client.get_guild(factionId)
        member = await guild.fetch_member(userId)
        if member.guild_permissions.administrator and not await adminhandler.admincheck(member,client):
            return True

        roles = member.roles
        for role in roles:
            roleId = role.id
            try:
                faction = classhandler.factionClass(factionId,jsonhandler.getfactionsjson())
            except Exception:
                return False
            rolePermissions = await __getPermissions__(faction.permissions.raw,roleId)
            if any(rolePermissions.values()) and not await adminhandler.admincheck(member,client):
                return True
        return False

    factions = jsonhandler.getfactionsjson()
    guilds = [faction["guild"] for faction in factions]
    if interaction.guild.id not in guilds:
        return False
    # if faction
    user = interaction.user
    # permissions check
    if not any(checkPermissions(interaction,interaction.user).values()):
        return False
    mutuals = user.mutual_guilds
    for mutual in mutuals:
        if await __mutualPermissions__(client,user.id,mutual.id):
            return True
    return False
"""

async def associatefaction(interaction,link,client):
  member = interaction.user
  if not await adminhandler.admincheck(member,client): 
    return ("You require admin privlages to run this command.")

  link = link.split("/")[-1]
  guild = await client.fetch_invite(link)
  guild = guild.guild
  guildId = guild.id
  guildName = guild.name

  addfaction = await jsonhandler.add_verifiedfaction(interaction,guildName,guildId)
  if addfaction == False: return await interaction.response.send_message(f"`{guildName}` has already been added to verified factions.")
  return await interaction.response.send_message(f"`{guildName}` has been added to verified factions.")

# === HELPER ===
def getRolesPermissions(faction,roleId): #Faction being class
  roleAttrName = f"role_{roleId}" # Create the dynamic attribute name for role permissions
  rolePermissions = getattr(faction.permissions, roleAttrName, None) # Access attribute for role permissions using dynamic name
  return rolePermissions

def checkPermissions(interaction,member):
  faction = classhandler.factionClass(interaction.guild.id,jsonhandler.getfactionsjson())
  roles = member.roles
  permissions = {"army": False,"region": False, "faction": False, "trade": False}
  #admin bypass
  if interaction.user.guild_permissions.administrator:
    return {"army": True,"region": True, "faction": True, "trade": True}

  for role in roles:
    roleId = role.id
    rolePermissions = getRolesPermissions(faction,roleId)
    if rolePermissions != None:
      if rolePermissions.army == True: permissions["army"] = True
      if rolePermissions.region == True: permissions["region"] = True
      if rolePermissions.faction == True: permissions["faction"] = True
      if rolePermissions.trade == True: permissions["trade"] = True
  return permissions

# === PERMISSIONS ===

def managePermissions(interaction,role,army_permissions,region_permissions,faction_permissions,trade_permissions): #Add or edit a role & its permissons to the json
  if interaction.guild.name not in  jsonhandler.get_faction_names():
    return f"`Guild {interaction.guild.name}` Must be Setup first."

  
  for faction in jsonhandler.getfactionsjson():
    faction = classhandler.factionClass(faction["guild"],jsonhandler.getfactionsjson())
    if faction.name == interaction.guild.name:
      roleJson = {
          "roleId" : role.id,
          "rolePermissions": {
            "army": army_permissions,
            "region": region_permissions,
            "faction": faction_permissions,
            "trade": trade_permissions
          }
      }
      break

  try:
    ids =  [indexRole["roleId"] for indexRole in faction.permissions.raw]
  except UnboundLocalError: return f"`Guild {interaction.guild.name}` must be setup first; use `/setup`"
  # if in permissions add
  if role.id in ids:
    for indexRole in faction.permissions.raw:
      if indexRole["roleId"] == role.id:
        indexRole["rolePermissions"] = roleJson["rolePermissions"]
  # If not in permissions add
  else: faction.permissions.raw.append(roleJson)
  jsonhandler.save_factions(interaction.guild,jsonhandler.getfactionsjson(),interaction.guild_id,faction.resources.raw,faction.deployments.raw,faction.capital,faction.permissions.raw)
  
  msg = (f"""
 # {role.name}

**Army permissions**
`{army_permissions}`

**Region permissions**
`{region_permissions}`

**Faction permissions**
`{faction_permissions}`

**Trade permissions**
`{trade_permissions}`
""")
  return msg

def displayPermissions(interaction,factionId,client):
  factions = jsonhandler.getfactionsjson() # Retrieve the list of factions from the JSON file
  factionIds =  [indexFaction["guild"] for indexFaction in factions] # Extract the names of all factions into a list

  if factionId not in factionIds:
    return (f"{interaction.guild.name} is not a faction.") # Check if the provided factionName is valid

  faction = classhandler.factionClass(factionId,factions) # Initialize the faction class using the provided faction name and list of factions
  msg = """
  # Permissions""" # Start building the permissions message

  for role in faction.permissions.raw[:]:
    roleId = role["roleId"]

    roleName = get(interaction.guild.roles, id=roleId)  # Get the discord Role object from the roleId
    if roleName is not None:
      rolePermissions = getRolesPermissions(faction, roleId)
      if rolePermissions:
        msg += (f"""
  
  **{roleName.name}**
  
  -Army: {rolePermissions.army}
  -Region: {rolePermissions.region}
  -Faction: {rolePermissions.faction}
  -Trade: {rolePermissions.trade}""")

  return msg

async def setup(interaction,client,logolink,alertChannel):
  factions = jsonhandler.getfactionsjson()
  authorised_factions = jsonhandler.getverifiedfactionsjson()

  guild = interaction.guild
  guild_id = guild.id
  name = guild.name
  user = interaction.user
  
  if not user.guild_permissions.administrator:
    embed = discord.Embed(
      color=discord.Color(int('eb3d47',16)),
      description="You lack permissions to access this."
    )
    embed.set_footer(text="You must be an admin to use this command.")
    embed.set_author(name="Access denied",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
    return await interaction.response.send_message(embed=embed)

  async def errorMsg(interaction):
    wolf = client.get_user(604817657169969182).mention
    embed = discord.Embed(
    color=discord.Color(int('eb3d47',16)),
    description=f"""
    **An error has occured:**
Supported image formats: `.png, .jpg, .jpeg, .bmp`

```py
{e}

```
Contact {wolf} for futher assistance.
    """)
    embed.set_footer(text="Ensure that your image is not corrupt & meets one of the format types.")
    embed.set_author(name="Access denied",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
    await interaction.response.send_message(embed=embed)

  # === Updating Logo ===
  for faction in factions:
    if guild_id == faction["guild"]:
      try:
        #save changes
        jsonhandler.updateAlert(guild_id,alertChannel.id)
        await imagehandler.save_image(logolink,guild_id)
        #notify channel
        embed = discord.Embed(
        color=discord.Color(int('5865f2',16)),
        description=f"All alerts will be sent here such as: Trades & border crossings")
        embed.set_author(name=f"{faction['name']} alerts sent here")
        await alertChannel.send(embed=embed)
        #embed
        embed = discord.Embed(
        color=discord.Color(int('5865f2',16)),
        description=f"Logo updated & alert channel assigned")
        file = discord.File(f'Data/Logos/{faction["guild"]}.png', filename=f'{faction["guild"]}.png')
        embed.set_author(name=f"{faction['name']} setup!",icon_url=f"attachment://{faction['guild']}.png")
        return await interaction.response.send_message(embed=embed,file=file)
      except Exception as e:
       return await errorMsg(interaction)
  
  list = [authorised_faction["guild"] for authorised_faction in authorised_factions]
  if guild_id not in list:
    embed = discord.Embed(
      color=discord.Color(int('eb3d47',16)),
      description="This server is not authorised for the use of faction map, to authorise vist: https://discord.com/channels/1074062206297178242/1104156000774275163/1106239922542743572."
    )
    embed.set_footer(text="Associate before attempting to setup your faction.")
    embed.set_author(name="Access denied",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
    return await interaction.response.send_message(embed=embed)
  try:
    await imagehandler.save_image(logolink,guild_id)
  except Exception as e:
       return await errorMsg(interaction)
  await jsonhandler.setup_faction(name,guild_id,client,interaction,alertChannel.id)
  
# === LOOKUP ===

def factionlookup(interaction,faction):

  faction = jsonhandler.get_faction_info(faction)
  faction = classhandler.factionClass(faction["guild"],jsonhandler.getfactionsjson())
  faction_info = (f"""
# **{faction.name}**

Capital:{faction.capital}
Deployments: {len(faction.deployments.raw)}

Manpower: {faction.resources.manpower}

Gold: {faction.resources.gold}
Iron: {faction.resources.iron}
Stone: {faction.resources.stone}
Wood: {faction.resources.wood}

*guild id {faction.guild}*
  """)
  return faction_info

async def userlookup(interaction,client,member):
  guilds = client.guilds
  guilded = []
  for guild in guilds:
    members = guild.members
    if member in members:guilded.append(guild.name)
      
  sep = ", "
  return (f"**{member.display_name}**({member.name}) found in: `{sep.join(guilded)}`")

async def factionOverview(interaction):
  # faction check
  if interaction.guild.name not in jsonhandler.get_faction_names():
    embed = discord.Embed(
      color=discord.Color(int('eb3d47',16)),
      description="This is not a faction."
    )
    embed.set_footer(text="To become a faction apply in faction hub `discord.gg/2nNFdp6Aje`")
    embed.set_author(name="Access denied",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
    return await interaction.response.send_message(embed=embed)

  #permissions check
  permissions = checkPermissions(interaction=interaction,member=interaction.user)

  if permissions["faction"] == False:
    #denied access
    embed = discord.Embed(
      color=discord.Color(int('eb3d47',16)),
      description="You lack permissions to access this."
    )
    embed.set_footer(text="Ensure that you have configured permissions before interacting with commands.")
    embed.set_author(name="Access denied",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
    return await interaction.response.send_message(embed=embed)

  #accepted
  faction = classhandler.factionClass(interaction.guild.id,jsonhandler.getfactionsjson())

  # buildings count
  inflow = 0
  outflow = 0

  for region in faction.regions:
    region = classhandler.regionClass(jsonhandler.getregionjson(),region)
    if region.building == "None":
      continue

    inflowDict = {"Capital":250,"Village":20}
    outflowDict = {"Fort":50 , "Port": 10}
    
    #inflow
    if region.building in inflowDict:
      inflow = inflow + inflowDict[region.building]

    elif region.building in outflowDict:
      outflow = outflow + outflowDict[region.building]
    

  embed = discord.Embed(
    color=discord.Color(int('5865f2',16)),
    description=f"""
## Financials                  
Inflow: {inflow}
Outflow: {outflow}
Trade: {"Coming soon"}
Revenue Per Turn: {inflow-outflow}
## Resources
- {faction.resources.manpower} Manpower
- {faction.resources.gold} Gold
- {faction.resources.iron} Iron
- {faction.resources.stone} Stone
- {faction.resources.wood} Wood
## Misc
Deployments: {len(faction.deployments.raw)}          
Regions controlled: {len(faction.regions)}

"""
)
  file = discord.File(f"Data/Logos/{faction.guild}.png",filename=f"{faction.guild}.png")
  embed.set_author(name=f"Overview of {faction.name}",icon_url=f"attachment://{faction.guild}.png")
  await interaction.response.send_message(embed=embed,file=file)

