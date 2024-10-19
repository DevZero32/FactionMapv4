import discord
from discord import app_commands
from discord.ext import commands
from Imports import jsonhandler, adminhandler, imagehandler,factionshandler,regionhandler,armyhandler,turnshandler,mediatorhandler,classhandler,economyHandler
import os
import asyncio

try:
  token = os.environ["TOKEN"]
except: token = "MTEwOTE3MzcxODQxNDAxNjUyMg.GpMnBO.c4lH5NQIErFktPpDzEDn9W6XH9DLeu-9RECFwg"
client = commands.Bot(command_prefix=" ",intents = discord.Intents.all())
global mainguild
mainguild = 1074062206297178242 #Faction Hub

@client.event
async def on_ready():
  print(f"{client.user} is now online.")
  try: print(f"{len(await client.tree.sync())} Commands Synced.")
  except Exception as e: print(f"Error with sync: {e}")
  await turnshandler.initialiseTurnSequence(client)

@client.tree.command(name="test",description = "This command is used for testing.")
async def Test(interaction:discord.Interaction):
  adminhandler.logInteraction(Test,interaction.user)
  latency = client.latency
  await interaction.response.send_message(f"Test Sucessful Ping:{latency}ms")
  
# === ARMY COMMANDS ===
@client.tree.command(name="armies",description = "Infomation on armies in your faction")
async def armies(interaction:discord.Interaction):
  adminhandler.logInteraction(armies,interaction.user)
  msg = await asyncio.to_thread(armyhandler.displaydeployments,interaction)
  
  await interaction.response.send_message(msg,ephemeral=True)

@client.tree.command(name="form",description = "Form an army to rally to")
async def form(interaction:discord.Interaction, region: int, name: str):
  adminhandler.logInteraction(form,interaction.user)

  msg = await asyncio.to_thread(armyhandler.formDeployment,interaction,region,name)
  await interaction.response.send_message(msg,ephemeral=True)
@client.tree.command(name="disband",description = "Disband an army.")
async def disband(interaction:discord.Interaction,name: str):
  adminhandler.logInteraction(disband,interaction.user)
  
  msg = await asyncio.to_thread(armyhandler.disbandDeployment,interaction,name)
  await interaction.response.send_message(msg,ephemeral=True)

@app_commands.describe(inf_type="Decide the type to rally. T1 cost: 50 Gold, 1 Manpower T2 cost: 150 gold, 3 manpower")
@app_commands.choices(inf_type=[
  discord.app_commands.Choice(name="Tier One",value=1),
  discord.app_commands.Choice(name="Tier Two",value=2)])
@client.tree.command(name="rally",description = "Rally to an army at a fort or the capital.")
async def rally(interaction:discord.Interaction, inf_type: discord.app_commands.Choice[int], quantity:int, deployment: str):
  adminhandler.logInteraction(rally,interaction.user)
  msg = await asyncio.to_thread(armyhandler.rallyDeployment,interaction,inf_type,quantity,deployment)
  
  await interaction.response.send_message(msg,ephemeral=True)

@client.tree.command(name="march",description = "March an army to a neighbouring reigion.")
@app_commands.describe(region="March a deployment to a nieghbouring region.")
@app_commands.describe(deployment="Enter the deploments name.")
async def march(interaction:discord.Interaction,deployment:str , region:int):
  adminhandler.logInteraction(march,interaction.user)
  msg = await asyncio.to_thread(armyhandler.marchDeployment,interaction,deployment,region)
  await interaction.response.send_message(msg,ephemeral=True)

@client.tree.command(name="attack",description = "Attack a deployment.")
async def attack(interaction:discord.Interaction, deployment:str , target:str): 
  adminhandler.logInteraction(attack,interaction.user)
  await interaction.response.defer()
  await armyhandler.attackDeployment(interaction,client,deployment,target)

@client.tree.command(name="occupy",description = "Occupy a region.")
async def occupy(interaction:discord.Interaction, region:int): 
  adminhandler.logInteraction(occupy,interaction.user)
  msg = await asyncio.to_thread(armyhandler.occupyRegion,interaction,client,region)
  try:
    await interaction.response.send_message(msg,ephemeral=True)
  except: await interaction.channel.send(msg)
  
@client.tree.command(name="scout",description = "Scout a region for deployments.")
async def scout(interaction:discord.Interaction, region:int): 
  adminhandler.logInteraction(scout,interaction.user)

  msg = await asyncio.to_thread(armyhandler.scoutRegion,interaction,region)
  await interaction.response.send_message(msg,ephemeral=True)

# === ECONOMY ===

@client.tree.command(name="trade",description="Send a trade request.")
async def trade(interaction:discord.Interaction):
  adminhandler.logInteraction(trade,interaction.user)
  await economyHandler.trade(interaction)

@client.tree.command(name="view_trades",description="List all trades in your faction.")
async def view_trades(interaction:discord.Interaction):
  adminhandler.logInteraction(view_trades,interaction.user)
  await economyHandler.viewTrades(interaction,client)

@client.tree.command(name="cancel_trade",description="Cancel a trade")
async def cancel_trades(interaction:discord.Interaction):
  adminhandler.logInteraction(view_trades,interaction.user)
  await economyHandler.cancelTrade(interaction)

# ===REGION ===

@client.tree.command(name="region_lookup", description=(f"Lookup a region. between 1 and {len(jsonhandler.getregionjson())}"))
@app_commands.describe(region="Region Selector")
async def regionlookup(interaction: discord.Interaction, region: int):
  adminhandler.logInteraction(regionlookup,interaction.user)
  
  msg = await asyncio.to_thread(regionhandler.regionlookup,interaction, region,jsonhandler.getregionjson())
  await interaction.response.send_message(msg)

@client.tree.command(name="build", description=("Build in a region"))
@app_commands.describe(region=(f"Region Selector. between 1 and {len(jsonhandler.getregionjson())}"))
@app_commands.describe(building="Select the building you want to build.")
@app_commands.choices(building=[
  discord.app_commands.Choice(name="Village",value=1),
  discord.app_commands.Choice(name="Port",value=2),
  discord.app_commands.Choice(name="Fort",value=3)
])
async def build(interaction: discord.Interaction, building: discord.app_commands.Choice[int], region: int):
  adminhandler.logInteraction(build,interaction.user)
  
  msg = await asyncio.to_thread(regionhandler.build,interaction,region,building)
  await interaction.response.send_message(msg)

# === FACTION ===
@client.tree.command(name="overview",description="Get an overview of your faction.")
async def overview(interaction:discord.Interaction):
  adminhandler.logInteraction(overview,interaction.user)
  await factionshandler.factionOverview(interaction)


@client.tree.command(name="setup",description="Establish your faction within faction map or update your factions logo.")
async def Setup(interaction:discord.Interaction,alert_channel: discord.TextChannel, logolink: str):
  adminhandler.logInteraction(Setup,interaction.user)
  await factionshandler.setup(interaction,client,logolink,alert_channel)


@client.tree.command(name="capital",description = "Set/Update your capital | Update Costs: 750 Gold, 20 Iron, 50 Stone, 50 Wood")
async def capital(interaction:discord.Interaction, region: int):
  adminhandler.logInteraction(capital,interaction.user)
  
  msg = await asyncio.to_thread(regionhandler.capital,interaction,region)
  await interaction.response.send_message(msg)


@client.tree.command(name="permissions",description = "Views all the roles with permissions.")
async def permissions (interaction:discord.Interaction):
  adminhandler.logInteraction(permissions,interaction.user)
  guild = interaction.guild
  name = guild.name
  
  msg = await asyncio.to_thread(factionshandler.displayPermissions,interaction,interaction.guild.id,client)
  await interaction.response.send_message(msg)


@client.tree.command(name="set_permissions",description = "Edit a roles permissions within Faction Map")
async def set_permissions(interaction:discord.Interaction, role: discord.Role, army_permissions: bool,region_permissions: bool,faction_permissions: bool,trade_permissions: bool ):
  adminhandler.logInteraction(set_permissions,interaction.user)
  if not interaction.user.guild_permissions.administrator: return await interaction.response.send_message("Access to administrator privileges is required for the requested action.")
  
  msg = await asyncio.to_thread(factionshandler.managePermissions,interaction,role,army_permissions,region_permissions,faction_permissions,trade_permissions)
  await interaction.response.send_message(msg)

# === MEDIATOR ===
@client.tree.command(name="teams",description="Used to view the teams and their size in a battle.")
async def teams(interaction:discord.Interaction):
  adminhandler.logInteraction(teams,interaction.user)
  msg = await asyncio.to_thread(mediatorhandler.viewTeams,interaction)
  await interaction.response.send_message(msg)

@client.tree.command(name="reinforce",description="Used by mediators to add reinforcements to the fight.")
@app_commands.choices(faction= [discord.app_commands.Choice(name=factionname, value=index) for index, factionname in enumerate(jsonhandler.get_faction_names())])
@app_commands.choices(side=[discord.app_commands.Choice(name="Attackers",value=1),discord.app_commands.Choice(name="Defenders",value=2)])
async def reinforce(interaction: discord.Interaction,faction: discord.app_commands.Choice[int], deployment: str, side: discord.app_commands.Choice[int]):
  adminhandler.logInteraction(reinforce,interaction.user)
  msg = await mediatorhandler.reinforce(interaction,client,faction,deployment,side)
  await interaction.response.send_message(msg)

@client.tree.command(name="remove_reinforcement",description="Used by mediators to remove a reinforcement from a fight.")
@app_commands.choices(faction=[discord.app_commands.Choice(name=factionname, value=index) for index, factionname in enumerate(jsonhandler.get_faction_names())])
async def remove_reinforcement(interaction:discord.Interaction,faction:discord.app_commands.Choice[int], deployment: str):
  adminhandler.logInteraction(remove_reinforcement,interaction.user)
  msg = await mediatorhandler.remove_reinforcement(interaction,client,faction,deployment)
  await interaction.response.send_message(msg)

@client.tree.command(name="victor",description = "Used by mediators to enter who won the battle")
@app_commands.describe(victorious="Enter the side that was victorious")
@app_commands.choices(victorious=[discord.app_commands.Choice(name="Attackers",value=1),discord.app_commands.Choice(name="Defenders",value=2)])
@app_commands.describe(score ="Provide the match score in the format 'Attackers-Defenders' (e.g., 5-1).")
async def victor(interaction:discord.Interaction, victorious: discord.app_commands.Choice[int],score: app_commands.Range[str,1,3]):
  adminhandler.logInteraction(victor,interaction.user)
  msg = await mediatorhandler.victor(interaction,client,victorious,score)
  await interaction.response.send_message(msg)

@client.tree.command(name="close",description="Close a battle channel.")
async def close(interaction:discord.Interaction):
  adminhandler.logInteraction(close,interaction.user)
  msg = await mediatorhandler.closeChannel(interaction,client)
  try:
    await interaction.response.send_message(msg)
  except: pass
# === ADMINSTRATOR ===

@client.tree.command(name="give_manpower",description = "Used by staff to enter a rally number as manpower increase.")
@app_commands.choices(faction= [discord.app_commands.Choice(name=factionname, value=index) for index, factionname in enumerate(jsonhandler.get_faction_names())])
async def give_manpower(interaction:discord.Interaction,faction: discord.app_commands.Choice[int], manpower: int):
  adminhandler.logInteraction(give_manpower,interaction.user)
  msg = await mediatorhandler.giveManpower(interaction,client,faction,manpower)
  await interaction.response.send_message(msg)


@client.tree.command(name="redraw",description = "This command should only be used if the map has been incorrectly drawn.")
async def redraw(interaction:discord.Interaction):
  adminhandler.logInteraction(redraw,interaction.user)

  member = interaction.user
  
  if not await adminhandler.admincheck(member,client): 
    await interaction.response.send_message("You require admin privlages to run this command.")
    return
  
  await interaction.response.defer()
  await asyncio.to_thread(imagehandler.redraw)
  await asyncio.to_thread(imagehandler.assembleMap)

  Embed = discord.Embed(
    colour=discord.Colour.blue(),
    description="Faction Map borders redrawn"
  )
  Embed.set_footer(text="Open in browser for full view")

  file = discord.File("Data/Map/Temp/mapOverview.png", filename="mapOverview.png")
  Embed.set_image(url="attachment://mapOverview.png")

  await interaction.followup.send(embed=Embed,file=file)

@client.tree.command(name="associate_faction",description = "Used to give a faction permission to use faction map.")
async def associatefaction(interaction:discord.Interaction,link: str):
  adminhandler.logInteraction(associatefaction,interaction.user)
  
  await factionshandler.associatefaction(interaction,link,client)
  # === MISC ===

@client.tree.command(name="user_lookup",description = "Lookup a user.") #Looks up a user, responds with the servers that they are in (that the bot is in as well)
async def userlookup(interaction:discord.Interaction,member: discord.Member):
  adminhandler.logInteraction(userlookup,interaction.user)
  msg = await factionshandler.userlookup(interaction,client,member)

  await interaction.response.send_message(msg)

@client.tree.command(name="faction_lookup",description = "Look up a faction.")
@app_commands.describe(faction="Faction Selector")
@app_commands.choices(faction= [discord.app_commands.Choice(name=factionname, value=index) for index, factionname in enumerate(jsonhandler.get_faction_names())])
async def factionlookup(interaction:discord.Interaction, faction: discord.app_commands.Choice[int]):
  adminhandler.logInteraction(factionlookup,interaction.user)
  msg = await asyncio.to_thread(factionshandler.factionlookup,interaction,faction)

  await interaction.response.send_message(msg)

@client.tree.command(name="map",description = "Display the current map.")
@app_commands.choices(mode=[discord.app_commands.Choice(name="Default",value=1),
discord.app_commands.Choice(name="Political",value=2),
discord.app_commands.Choice(name="Topography",value=3)])
async def map(interaction:discord.Interaction,mode: discord.app_commands.Choice[int]):
  adminhandler.logInteraction(map,interaction.user)
  await asyncio.to_thread(imagehandler.assembleMap)
  await interaction.response.defer()
  if mode.name == "Default":
    return await interaction.followup.send(file=discord.File(f"Data/Map/Temp/mapOverview.png"))
  mapFile = f"Data/Map/Temp/{(mode.name).lower()}Overview.png"
  await interaction.followup.send(file=discord.File(mapFile))
  
@client.tree.command(name="turn",description = "How long is left of the current turn")
async def turn(interaction:discord.Interaction):
  adminhandler.logInteraction(turn,interaction.user)
  nextTurnResult = await asyncio.to_thread(turnshandler.getTurns)
  nextTurn = nextTurnResult["nextTurn"]
  format = f"<t:{nextTurn:.0f}:t>,<t:{nextTurn:.0f}:R>"
  await interaction.response.send_message(f"Next turn is {format}")

# === RUN ===
#imagehandler.generateMasks()
#imagehandler.redraw()
client.run(token)