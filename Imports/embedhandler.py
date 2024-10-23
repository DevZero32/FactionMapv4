import discord
from discord import app_commands
from discord.ext import commands

def dangerEmbed(desc: str,footer: str,author: str) -> discord.Embed:
    embed = discord.Embed(
    color=discord.Color(int('eb3d47',16)),
    description=desc)
    embed.set_footer(text=footer)
    embed.set_author(name=author,icon_url="https://cdn.discordapp.com/attachments/763309644261097492/1143966731421896704/image.png?ex=66ba4c8a&is=66b8fb0a&hm=3a8bab4488268865b8094ca7b2a60e7ee406a651729634ebe3d7185a4c9277bc&")
    return embed

def dangerEmbedFactionLogo(desc: str,footer: str,author: str, factionId: int) -> discord.Embed:
    file = discord.File(f"Data/Logos/{factionId}.png",filename=f"{factionId}.png")
    iconUrl = f"attachment://{factionId}.png"

    embed = discord.Embed(
    color=discord.Color(int('eb3d47',16)),
    description=desc)
    embed.set_footer(text=footer)
    embed.set_author(name=author,icon_url=iconUrl)
    return [file,embed]

def positiveEmbedFactionLogo(desc: str,footer: str,author: str, factionId: int) -> discord.Embed:
    file = discord.File(f"Data/Logos/{factionId}.png",filename=f"{factionId}.png")
    iconUrl = f"attachment://{factionId}.png"

    embed = discord.Embed(color=discord.Color(int('eb3d47',16)),description=desc)
    embed.set_footer(text=footer)
    embed.set_author(name=author,icon_url=iconUrl)
    return [file,embed]

def positiveEmbed(desc: str,footer: str,author: str) -> discord.Embed:
    iconUrl = "https://cdn.discordapp.com/attachments/763309644261097492/1143966676661059635/image.png?ex=66c8243d&is=66c6d2bd&hm=880007a97a8c4ad1156d3e429073a4c0019d1fdbe426c43b28c2c038396bd8d3&"

    embed = discord.Embed(color=discord.Color(int('5865f2',16)),description=desc)
    embed.set_footer(text=footer)
    embed.set_author(name=author,icon_url=iconUrl)
    return embed