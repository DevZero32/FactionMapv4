from Imports import jsonhandler,classhandler,imagehandler,adminhandler
from discord.utils import get

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
  if addfaction == "occupied": return (f"`{guildName}` has already been added to verified factions.")
  return (f"`{guildName}` has been added to verified factions.")

# === HELPER ===
def getRolesPermissions(faction,roleId): #Faction being class
  roleAttrName = f"role_{roleId}" # Create the dynamic attribute name for role permissions
  rolePermissions = getattr(faction.permissions, roleAttrName, None) # Access attribute for role permissions using dynamic name
  return rolePermissions

def checkPermissions(interaction,member):
  faction = classhandler.factionClass(interaction.guild.name,jsonhandler.getfactionsjson())
  roles = member.roles
  permissions = {"army": False,"region": False, "faction": False, "trade": False}
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
    faction = classhandler.factionClass(faction["name"],jsonhandler.getfactionsjson())
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

def displayPermissions(interaction,factionName,client):
  factions = jsonhandler.getfactionsjson() # Retrieve the list of factions from the JSON file
  factionNames =  [indexFaction["name"] for indexFaction in factions] # Extract the names of all factions into a list

  if factionName not in factionNames:
    return (f"{factionName} is not a faction.") # Check if the provided factionName is valid

  faction = classhandler.factionClass(factionName,factions) # Initialize the faction class using the provided faction name and list of factions
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

async def setup(interaction,client,logolink):
  factions = jsonhandler.getfactionsjson()
  authorised_factions = jsonhandler.getverifiedfactionsjson()

  guild = interaction.guild
  guild_id = guild.id
  name = guild.name
  user = interaction.user
  
  if not user.guild_permissions.administrator: return ("Access to administrator privileges is required for the requested action.")
  # === Updating Logo ===
  for faction in factions:
    if guild_id == faction["guild"]:
      try:
        await imagehandler.save_image(logolink,guild_id)
        return (f"{name}'s logo has been updated!")
      except Exception as e:
        wolf = client.get_user(604817657169969182).mention
        return (f"""
    **An error has occured:**
Supported image formats: `.png, .jpg, .jpeg, .bmp`

```py
{e}

```
Contact {wolf} for futher assistance.
    """)
  
  list = []
  for authorised_faction in authorised_factions:
    list.append(authorised_faction["guild"])
  if guild_id not in list: return ("This server is not authorised for the use of faction map, to authorise vist: https://discord.com/channels/1074062206297178242/1104156000774275163/1106239922542743572")
  try:
    await imagehandler.save_image(logolink,guild_id)
  except Exception as e:
    wolf = client.get_user(604817657169969182).mention
    return (f"""
    **An error has occured:**
Supported image formats: `.png, .jpg, .jpeg, .bmp`

```py
{e}

```
Contact {wolf} for futher assistance.
    """)

  return await jsonhandler.setup_faction(name,guild_id,client,interaction)  
# === LOOKUP ===

def factionlookup(interaction,faction):

  faction = jsonhandler.get_faction_info(faction)
  faction = classhandler.factionClass(faction["name"],jsonhandler.getfactionsjson())
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
    if member in members: guilded.append(guild.name)
  sep = ", "
  return (f"**{member.display_name}**({member.name}) found in: `{sep.join(guilded)}`")