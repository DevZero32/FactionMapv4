import json
from datetime import datetime
import discord
from discord.ext import commands
client = commands.Bot(command_prefix="!",intents = discord.Intents.all())

async def admincheck(member,client,mainguild=1074062206297178242): #Are they an admin of Faction Hub
  guild = client.get_guild(mainguild)
  g_member= guild.get_member(member.id)
  try:
    g_member_roles= g_member.roles
  except: return False
  authorised_roles= [1074759071892254750,1074841275825659934,1074841283903893575,1074842096789377105,1162115972124114975]

  for role in g_member_roles:
    if role.id in authorised_roles:
      return True
  return False


def logInteraction(functionName,user): #Log a users interaction with a function
  with open("Data/log.json","r") as f:
    data = json.load(f)
  functionName = functionName.name
  
  currentDate = datetime.now()
  formattedDate = currentDate.strftime("%d/%m/%Y")
  formattedTime = currentDate.strftime("%H:%M:%S")

  eventInteraction = {
    "User:": user.name,
    "Function:": functionName,
    "Date": formattedDate,
    "Time": formattedTime
  }

  data.append(eventInteraction)
  
  with open("Data/log.json","w") as f:
    json.dump(data,f,indent=4)