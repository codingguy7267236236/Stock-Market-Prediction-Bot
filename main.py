import nextcord
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
from nextcord.ext import commands,application_checks
from nextcord.utils import get
import os
from keep_alive import keep_alive
from stock import *

#variables
TOKEN = os.environ['TOKEN']
#logsId = os.environ['logs']

intents = nextcord.Intents().all()
intents.members=True
client=commands.Bot(command_prefix="!",intents=intents)


@client.event
async def on_ready():
  print("Bot online")
  await client.register_application_commands(Forecast)


@client.event
async def on_message(msg):
  if msg.author.id == client.user.id:
    return


server = [1091087983165325443]

#admin stuff
@client.slash_command(name="forecast", description="forecast stock price",
                      guild_ids=server,
                      dm_permission=False)
async def Forecast(ctx,ticker:str=nextcord.SlashOption(name="ticker",description="stock ticker",required=True)):
  await ctx.send("Processing....",ephemeral=True)
  ticker = ticker.upper()
  model1m = GetStock(ticker,"1m",7)
  model5m = GetStock(ticker,"5m",60)
  model15m = GetStock(ticker,"15m",60)
  model30m = GetStock(ticker,"30m",60)
  model1h = GetStock(ticker,"60m",90)
  model2h = GetStock(ticker,"90m",60)
  model1d = GetStock(ticker,"1d",150)
  #model1w = GetStock(ticker,"1wk",52)

  models = [model1m,model5m,model15m,model30m,model1h,model2h,model1d]

  desc = ""
  #charts and trains model
  for model in models:
    acc = model.Score()
    desc += f"**Model {model.period}** Accuracy **{acc*100}%**\n\n"

  embed = nextcord.Embed(title=f"Model Evaluation for {ticker} models",description=desc,color=0x00ff00)
  await ctx.send(embed=embed)
  
  prices = [models[0].data.iloc[-1]["Open"]]
  periods = ['Now']
  for model in models:
    fore = model.Forecast()
    prices.append(fore)
    periods.append(model.period)

  fp = models[0].Plot(periods,prices)
  await ctx.send(file=nextcord.File(fp))



@client.slash_command(name="chart", description="chart model eval",
                      guild_ids=server,
                      dm_permission=False)
async def Forecast(ctx,ticker:str=nextcord.SlashOption(name="ticker",description="stock ticker",required=True)):
  await ctx.send("Processing....",ephemeral=True)
  ticker = ticker.upper()
  model1m = GetStock(ticker,"1m",7)
  model5m = GetStock(ticker,"5m",60)
  model15m = GetStock(ticker,"15m",60)
  model30m = GetStock(ticker,"30m",60)
  model1h = GetStock(ticker,"60m",90)
  model2h = GetStock(ticker,"90m",60)
  model1d = GetStock(ticker,"1d",150)

  models = [model1m,model5m,model15m,model30m,model1h,model2h,model1d]

  for model in models:
    model.Chart()
  await ctx.send("View console",ephemeral=True)

#Run our webserver, this is what we will ping
keep_alive()

client.run(TOKEN)