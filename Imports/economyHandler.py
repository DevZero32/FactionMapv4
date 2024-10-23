from Imports import jsonhandler ,factionshandler,classhandler,regionhandler,turnshandler,mediatorhandler,imagehandler
import json
import discord
from discord import ui

class tradeRequestclass(discord.ui.View):
     def __init__(self,tradeId: int,offeringFaction: int,receivingFaction: int, *, timeout: float = None):
          super().__init__(timeout=timeout)
          self.tradeId = tradeId
          self.offeringFaction = offeringFaction
          self.receivingFaction = receivingFaction

     @discord.ui.button(label="Accept",style=discord.ButtonStyle.success)
     async def acceptTradeOffer(self,interaction: discord.Interaction,button:discord.ui.Button):
          
          #disabled check
          for item in self.children:
              if item.disabled == True:
                  return await interaction.response.send_message("This trade has already been settled.",ephemeral=True)

          
          # permission check
          if factionshandler.checkPermissions(interaction,interaction.user)["trade"] == False:
              if factionshandler.checkPermissions(interaction,interaction.user)["trade"] == False:
               embed = discord.Embed(
               color=discord.Color(int('eb3d47',16)),
               description="You lack the trade permission to use this.")
               embed.set_footer(text="use /set_permissions to set permissions")
               embed.set_author(name="Trade rejected",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
               return await interaction.response.send_message(embed=embed)
          # process
          updateTrade(self.tradeId,True)

          #Notify receiving faction
          embed = discord.Embed(
          color=discord.Color(int('5865f2',16)),
          description=f"""You have began a trade, view all trades with `/view_trades`""")
          embed.set_footer(text="Trade occurs every turn.")
          embed.set_author(name=f"Trade started",icon_url=f"https://cdn.discordapp.com/attachments/763309644261097492/1143966676661059635/image.png?ex=66baf53d&is=66b9a3bd&hm=7ebd69b2962ef32b2ecbcf59771a304dbd773c2d6e6a20f96458bc98cee77b83&")
          await interaction.response.send_message(embed=embed)
          
          #Notify offering faction

          embed = discord.Embed(
          color=discord.Color(int('5865f2',16)),
          description=f"You have began a trade, view all trades with `/view_trades`")
          embed.set_footer(text="Trade occurs every turn.")
          embed.set_author(name=f"Trade started",icon_url=f"https://cdn.discordapp.com/attachments/763309644261097492/1143966676661059635/image.png?ex=66baf53d&is=66b9a3bd&hm=7ebd69b2962ef32b2ecbcf59771a304dbd773c2d6e6a20f96458bc98cee77b83&")
          
          offeringFaction = classhandler.factionClass(self.offeringFaction,jsonhandler.getfactionsjson())
          offeringGuild = interaction.client.get_guild(offeringFaction.guild)
          alertChannel = offeringGuild.get_channel(offeringFaction.alert)

          await alertChannel.send(embed=embed)

          for item in self.children:
               item.disabled = True

          
    
     @discord.ui.button(label="Decline",style=discord.ButtonStyle.danger)
     async def declineTradeOffer(self,interaction: discord.Interaction,button:discord.ui.Button):
          #disabled check
          for item in self.children:
              if item.disabled == True:
                  return await interaction.response.send_message("This trade has already been settled.",ephemeral=True)
          
          # permission check
          if factionshandler.checkPermissions(interaction,interaction.user)["trade"] == False:
              if factionshandler.checkPermissions(interaction,interaction.user)["trade"] == False:
               embed = discord.Embed(
               color=discord.Color(int('eb3d47',16)),
               description="You lack the trade permission to use this.")
               embed.set_footer(text="use /set_permissions to set permissions")
               embed.set_author(name="Trade rejected",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
               return await interaction.response.send_message(embed=embed)

          #Notify receiving faction
          embed = discord.Embed(
          color=discord.Color(int('eb3d47',16)),
          description=f"You have declined trade, view all trades with `/view_trades`")
          embed.set_footer(text="Trade occurs every turn.")
          embed.set_author(name=f"Trade declined",icon_url=f"https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
          await interaction.response.send_message(embed=embed)
          
          #Notify offering faction

          embed = discord.Embed(
          color=discord.Color(int('eb3d47',16)),
          description=f"Trade has been declined, view all trades with `/view_trades`")
          embed.set_footer(text="Trade occurs every turn.")
          embed.set_author(name=f"Trade declined",icon_url=f"https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
          
          offeringFaction = classhandler.factionClass(self.offeringFaction,jsonhandler.getfactionsjson())
          offeringGuild = interaction.client.get_guild(offeringFaction.guild)
          alertChannel = offeringGuild.get_channel(offeringFaction.alert)

          await alertChannel.send(embed=embed)

          for item in self.children:
               item.disabled = True

class createTradeClass(discord.ui.Modal, title="Offer trade"):

   tradeName = ui.TextInput(
        label="Trade name",
        style=discord.TextStyle.short,
        required=True,
        placeholder="Name the trade offer")
   recevingFaction = ui.TextInput(
        label="To",
        style=discord.TextStyle.short,
        required=True,
        placeholder="Name the faction you wish to trade with")
   offeringResource = ui.TextInput(label="Offering resource",style=discord.TextStyle.short,required=True,placeholder="The resource you wish to trade forE.g 10 Gold")
   receivingResource = ui.TextInput(
        label="Receiving resource",
        style=discord.TextStyle.short,
        required=True,
        placeholder="What you want in return E.g 5 Iron"
   )

   async def on_submit(self, interaction: discord.Interaction):
     # Retrieve the input values
     tradeName = self.tradeName.value
     receivingFaction = self.recevingFaction.value
     offeringResource = self.offeringResource.value.lower()
     receivingResource = self.receivingResource.value.lower()

         
     #faction existance check
     if interaction.guild.id not in [i["guild"]for i in jsonhandler.getfactionsjson()]:
          embed = discord.Embed(
          color=discord.Color(int('eb3d47',16)),
          description="This server isn't a regocnised faction.")
          embed.set_footer(text="authorise to faction map before interacting")
          embed.set_author(name="Trade rejected",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
          return await interaction.response.send_message(embed=embed)

     #permissions check
     if factionshandler.checkPermissions(interaction,interaction.user)["trade"] == False:
          embed = discord.Embed(
          color=discord.Color(int('eb3d47',16)),
          description="You lack the trade permission to use this.")
          embed.set_footer(text="use /set_permissions to set permissions")
          embed.set_author(name="Trade rejected",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
          return await interaction.response.send_message(embed=embed)

     #receivingFaction check

     if receivingFaction not in jsonhandler.get_faction_names():
          embed = discord.Embed(
          color=discord.Color(int('eb3d47',16)),
          description="The faction you entered is not recognised.")
          embed.set_footer(text="Copy and paste the server name of the faction")
          embed.set_author(name="Trade rejected",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
          return await interaction.response.send_message(embed=embed)
     # faction name to id
     for faction in jsonhandler.getfactionsjson():
          if faction["name"] == receivingFaction: 
               receivingFaction = faction["guild"]
               break

     if interaction.guild.id == receivingFaction:
          embed = discord.Embed(
          color=discord.Color(int('eb3d47',16)),
          description="You cannot trade with yourself.")
          embed.set_footer(text="Copy and paste the server name of the faction")
          embed.set_author(name="Trade rejected",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
          return await interaction.response.send_message(embed=embed)
     
     # Validate resources
     resources = ["manpower", "gold", "iron", "stone", "wood"]
     
     if offeringResource.split(" ")[1] not in resources or receivingResource.split(" ")[1] not in resources:
          embed = discord.Embed(
          color=discord.Color(int('eb3d47',16)),
          description="Resources not recognized. Please enter valid resources.")
          embed.set_footer(text="Ensure that you enter one of the following: Manpower, Gold, Iron, Stone, Wood.")
          embed.set_author(name="Trade rejected",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
          return await interaction.response.send_message(embed=embed)
     # Validate Quantity
     try:
          offeringQuantity = int(offeringResource.split(" ")[0])
          receivingQuantity = int(receivingResource.split(" ")[0])
     except ValueError as e:
          embed = discord.Embed(
          color=discord.Color(int('eb3d47',16)),
          description=f"Error: {e}")
          embed.set_footer(text="Ensure that you enter numbers in quantity.")
          embed.set_author(name="Trade rejected",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
          return await interaction.response.send_message(embed=embed)
     
     # Enough resources check
     faction = classhandler.factionClass(interaction.guild.id,jsonhandler.getfactionsjson())
     if faction.resources.raw[offeringResource.split(" ")[1]] < offeringQuantity:
          embed = discord.Embed(color=discord.Color(int('eb3d47',16)),description=f"You lack enough resources for this trade")
          embed.set_footer(text="Consider your amount of resources.")
          embed.set_author(name="Trade rejected",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
          return await interaction.response.send_message(embed=embed)
     # send trade request
     receivingFaction = classhandler.factionClass(receivingFaction,jsonhandler.getfactionsjson())
     tradeId = createTrade(tradeName=tradeName,receivingFactionId=receivingFaction.guild,offeringFactionId=faction.guild,offeringResource=offeringResource.split(" ")[1],offeringQuanitiy=offeringQuantity,receivingResource=receivingResource.split(" ")[1],receivingQuanitiy=receivingQuantity)
     
     #trade request embed
     receivingGuild = interaction.client.get_guild(receivingFaction.guild)
     alertChannel = receivingGuild.get_channel(receivingFaction.alert)

     alertFile = discord.File(f"Data/Logos/{faction.guild}.png",filename=f"{faction.guild}.png")
     alertEmbed = discord.Embed(color=discord.Color(int('5865f2',16)),description=f"{offeringResource} for {receivingResource}")
     alertEmbed.set_footer(text=f"You will be receiving {offeringResource} for {receivingResource}.")
     alertEmbed.set_author(name=f"Trade request from {interaction.guild.name}",icon_url=f"attachment://{interaction.guild.id}.png")
     await alertChannel.send(embed=alertEmbed,view=tradeRequestclass(tradeId,interaction.guild.id,receivingFaction.guild),file=alertFile)

     #confirmation embed
     file = discord.File(f"Data/Logos/{receivingFaction.guild}.png",filename=f"{receivingFaction.guild}.png")
     embed = discord.Embed(color=discord.Color(int('5865f2',16)),description=f"""
Your trade request has been successfully sent to {receivingFaction.name}

Please note that the receiving faction must review and accept the request before the trade can be finalized.
Once accepted, the trade will automatically reoccur every turn until it is canceled by either faction. You will be notified once they respond.
     """)
     embed.set_footer(text=f"Your trade request has been sent to {receivingFaction.name}.")
     embed.set_author(name="Trade request sent",icon_url=f"attachment://{receivingFaction.guild}.png")
     return await interaction.response.send_message(embed=embed,file=file)
   
def createTrade(tradeName,receivingFactionId,offeringFactionId,offeringResource,offeringQuanitiy,receivingResource,receivingQuanitiy):
     trades = getTrades()
    
     if len(trades) == 0: 
       id = 1
     else: id = trades[-1]["id"]+1

     trade = {
       "tradeName": tradeName,
       "id": id,
        "offeringFactionId": offeringFactionId,
        "offeringResource": offeringResource,
        "offeringQuantity": offeringQuanitiy,
        "receivingFactionId": receivingFactionId,
        "receivingResource": receivingResource,
        "receivingQuantity": receivingQuanitiy,
        "tradeAccepted": False
     }
     trades.append(trade)

     with open("Data/trades.json","w") as file:
        json.dump(trades,file,indent = 4)
     return id

def updateTrade(tradeId: int,isAccepted: bool):
     """
     Args:
          TradeId -Int id to trade
          isAcceped -Bool

     Updates the status of the trade
     """
     trades = getTrades()

     for trade in trades:
         if trade["id"] == tradeId:
             trade["tradeAccepted"] = isAccepted
             break
     
     with open("Data/trades.json","w") as file:
        json.dump(trades,file,indent = 4)

def getTrades():
  """
  Gives Raw Json Data of trades.json
  """
  with open("Data/trades.json","r") as file:
    jsondata = json.loads(file.read())
  return jsondata

def getFactionTrades(guildId):
    """
    guildId: id of faction

    returns all of the trade instances where the faction is referanced
    """
    return [trade for trade in getTrades() if guildId in [trade["offeringFactionId"], trade["receivingFactionId"]]]

# === Commands ===
async def trade(interaction):
   # === Faction Existance Check ====
     factions = jsonhandler.getfactionsjson()
     if interaction.guild.id not in [faction["guild"] for faction in factions]:
          return await interaction.response.send_message(f"{interaction.guild.name} is not a faction. please run `/setup`.")
  
     #Check Permissions
     permissions = factionshandler.checkPermissions(interaction,interaction.user)
     if permissions["trade"] == False : return await interaction.response.send_message("You lack permissions to trade.")

     await interaction.response.send_modal(createTradeClass())

async def cancelTrade(interaction):
    # === Faction Existance Check ====
     factions = jsonhandler.getfactionsjson()
     if interaction.guild.id not in [faction["guild"] for faction in factions]:
          return await interaction.response.send_message(f"{interaction.guild.name} is not a faction. please run `/setup`.")
  
     #Check Permissions
     permissions = factionshandler.checkPermissions(interaction,interaction.user)
     if permissions["trade"] == False : return await interaction.response.send_message("You lack permissions to trade.")

     view = cancelTradeView(interaction)
     await interaction.response.send_message(view=view)

class cancelTradeView(discord.ui.View):
    def __init__(self, interaction, timeout: float = None):
        super().__init__(timeout=timeout)
        self.guildId = interaction.guild.id
        self.add_item(self.CancelTradeSelect(self.guildId))

    class CancelTradeSelect(discord.ui.Select):
        def __init__(self, guildId: int):
            # Create options from faction trades
            options = [
                discord.SelectOption(label=trade["tradeName"], value=trade["id"]) 
                for trade in getFactionTrades(guildId)
            ]

            # Initialize the Select component
            super().__init__(
                placeholder="Select the trade you wish to cancel.",
                options=options
            )

        async def callback(self, interaction: discord.Interaction):
            trades = getTrades()
            tradeId = int(self.values[0])
            # Find and remove the selected trade
            for trade in trades:
               if trade["id"] == tradeId:
                    trades.remove(trade)     

                    # Determine the other faction ID
                    if interaction.guild.id == trade["offeringFactionId"]:
                        otherFaction = trade["receivingFactionId"]
                    else:
                        otherFaction = trade["offeringFactionId"]

                    # Save the updated trades to the file
                    with open("Data/trades.json", "w") as file:
                        json.dump(trades, file, indent=4)

                    # Create an alert embed
                    embed = discord.Embed(
                        color=discord.Color(int('eb3d47', 16)),
                        description=f"Trade `{trade['tradeName']}` has been canceled, view all trades with `/view_trades`"
                    )
                    embed.set_footer(text="Trade occurs every turn.")
                    embed.set_author(
                        name="Trade canceled",
                        icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&"
                    )

                    # Send alert to the other faction
                    otherFactionObj = classhandler.factionClass(otherFaction, jsonhandler.getfactionsjson())
                    offeringGuild = interaction.client.get_guild(otherFactionObj.guild)
                    alertChannel = offeringGuild.get_channel(otherFactionObj.alert)
                    await alertChannel.send(embed=embed)

                    # Respond to the original interaction
                    await interaction.response.send_message(f"Trade `{trade['tradeName']}` has been canceled.")
                    break

async def viewTrades(interaction,client):
     #faction existance check
     if interaction.guild.id not in [i["guild"]for i in jsonhandler.getfactionsjson()]:
          embed = discord.Embed(
          color=discord.Color(int('eb3d47',16)),
          description="This server isn't a regocnised faction.")
          embed.set_footer(text="authorise to faction map before interacting")
          embed.set_author(name="Trade rejected",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
          return await interaction.response.send_message(embed=embed)
     #permisions
     if factionshandler.checkPermissions(interaction,interaction.user)["trade"] == False:
          embed = discord.Embed(
          color=discord.Color(int('eb3d47',16)),
          description="You lack the trade permission to use this.")
          embed.set_footer(text="use /set_permissions to set permissions")
          embed.set_author(name="Trade rejected",icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
          return await interaction.response.send_message(embed=embed)
    

     trades = getTrades()
     desc = ""

     for trade in trades:
          of = client.get_guild(trade["offeringFactionId"])
          rf = client.get_guild(trade["receivingFactionId"])
          if interaction.guild.id in [trade["offeringFactionId"],trade["receivingFactionId"]]:
              desc += f"""
**{trade["tradeName"]}**

{of.name} - {rf.name}
{trade["offeringQuantity"]} {trade["offeringResource"]} - {trade["receivingQuantity"]} {trade["receivingResource"]}
     """
     embed = discord.Embed(color=discord.Color(int('5865f2',16)),description=desc)
     embed.set_footer(text=f"All trades with reference to this faction.")
     embed.set_author(name="Trade Summary",icon_url=f"https://cdn.discordapp.com/attachments/763309644261097492/1143966676661059635/image.png?ex=66c8243d&is=66c6d2bd&hm=880007a97a8c4ad1156d3e429073a4c0019d1fdbe426c43b28c2c038396bd8d3&")
     await interaction.response.send_message(embed=embed,ephemeral=True)

