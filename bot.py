from webbrowser import get
import discord
from discord.ext import commands
import random
from pycardano import *
from blockfrost import BlockFrostApi, ApiError, ApiUrls
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()
blockfrost_key = os.getenv("BLOCK_FROST_KEY")
discord_key = os.getenv("DISCORD_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

def validator(addr, adaval):
    tries = 0
    while True:
        tries += 1
        api = BlockFrostApi(project_id=blockfrost_key, base_url=ApiUrls.mainnet.value)
        try:
            current_block = api.block_latest().height - 20
            saved_tx_ids = [tx for tx in api.address_transactions(addr, f"{current_block}:{0}")]
            if saved_tx_ids:
                for tx in saved_tx_ids:
                    utxos = api.transaction_utxos(tx.tx_hash)
                    for u in utxos.outputs:
                        if u.address == addr and u.amount[0].quantity == str(int(float(adaval) * 1000 * 1000)):
                            return True
            time.sleep(22)
            if tries >= 10:
                return False
        except ApiError:
            time.sleep(22)
            if tries >= 10:
                break

def checknfts(addr):
    api = BlockFrostApi(project_id=blockfrost_key, base_url=ApiUrls.mainnet.value)
    try:
        api_assets = api.address(addr).amount
        policy_id = ""
        nfts = [asset.unit[56:] for asset in api_assets if policy_id in asset.unit] #Remove POLICY_ID from string
        return len(nfts) >= 10
    except ApiError as e:
        print(e)

def append_data_to_json_file(filename, data):
    existing_data = json.load(open(filename, 'r')) if os.path.exists(filename) else []
    existing_data.update(data)
    json.dump(existing_data, open(filename, 'w'), indent=4)

@client.event
async def on_ready():
    print(f"Bot is connected {client.user}")

@client.command()
async def verify(ctx, arg):
    user_id = ctx.author.id
    verify = round(random.uniform(1.0, 2.0), 4)
    user_addr = arg
    await ctx.reply(f"Please send EXACTLY {verify} ADA to your address: {user_addr}")
    
    if validator(user_addr, verify):
        if checknfts(arg):
            append_data_to_json_file("./wallets.json", {str(user_id): arg})
            role = get(ctx.guild.roles, name='Special Role')
            await ctx.author.add_roles(role)
            await ctx.send("Wallet verified!")
        else:
            await ctx.reply("Not granted the role")
    else:
        await ctx.reply("Wallet not verified, try again.")

client.run(discord_key)
