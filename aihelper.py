import discord
from discord.ext import commands
import google.generativeai as genai
import psutil
import platform
import asyncio
import signal
import sys
import os
from datetime import datetime, timedelta
#config:
DISCORD_TOKEN = 'token here`
ADMIN_ID = 1046003976727973910 <- type here own id for commands like .reset and .blacklist
GEMINI_KEYS = [
    'AIza key1', 'AIza key2',
    'AIza key3', 'AIza key4',
    'AIza key5', 'AIza key6',
    'AIza key7', 'AIza key8',
    'AIza key9'
]
#note: you can delete some keys strings if you want
AI_ASSISTANT_CHANNEL_ID = channelid with ai
LOG_CHANNELS = [channel for liveupdates.txt №1, channel for liveupdates.txt №2]
BLACKLIST_LOG_CHANNEL_ID = channelid for display blacklisted users
LIVE_UPDATES_FILE = "live_updates.txt"
current_key_index = 0
cleared_channels = set()

def get_full_knowledge():
    kb_content = ""
    if os.path.exists('agents.md'):
        with open('agents.md', 'r', encoding='utf-8') as f:
            kb_content += "--- CORE SERVER INFO ---\n" + f.read() + "\n"
    if os.path.exists(LIVE_UPDATES_FILE):
        with open(LIVE_UPDATES_FILE, 'r', encoding='utf-8') as f:
            kb_content += "\n--- LIVE RECENT UPDATES ---\n" + f.read()
    return kb_content if kb_content else "No knowledge base available."
def get_system_instruction():
    knowledge = get_full_knowledge()
    return f"""
You are the official AI Assistant for the TiRex Discord server. 
Your goal is to help users with TiRex info, Roblox scripting (Luau), and exploit scene news.
PERSONALITY:
Your owner is darknife. Speak as a knowledgeable friend—chill, concise, and helpful. 
You are an expert. Use <#ID> for redirects.
CONTEXT HANDLING (IMPORTANT):
You may be provided with a previous message for context. 
USE IT ONLY to understand what the user is talking about. 
DO NOT repeat the same phrasing, DO NOT get stuck in a loop, and DO NOT copy the style of the previous message if it's not needed. 
Always provide fresh, direct answers to the NEW input.
KNOWLEDGE BASE:
{knowledge}
"""

class TiRexBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=".", intents=intents)

    async def setup_hook(self):
        if platform.system() != "Windows":
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))

    async def shutdown(self):
        print("Shutting down...")
        channel = self.get_channel(AI_ASSISTANT_CHANNEL_ID)
        if channel:
            try:
                perms = channel.permissions_for(channel.guild.me)
                if perms.send_messages and perms.embed_links:
                    embed = discord.Embed(title="System Status", description="Disabled", color=discord.Color.red())
                    await channel.send(embed=embed)
            except: pass
        await self.close()
bot = TiRexBot()
def get_model():
    global current_key_index
    genai.configure(api_key=GEMINI_KEYS[current_key_index])
    return genai.GenerativeModel('gemini-flash-lite-latest')
async def safe_generate_content(prompt, history=None):
    global current_key_index
    retries = 5
    for i in range(retries):
        try:
            model = get_model()
            full_prompt = [get_system_instruction()]
            if history:
                full_prompt.append(f"--- REFERENCE CONTEXT (DO NOT LOOP/REPEAT THIS) ---\n{history}\n--- END OF REFERENCE ---")
            full_prompt.append(f"NEW USER INPUT: {prompt}")

            response = await asyncio.to_thread(model.generate_content, full_prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Key failed or error occurred: {e}")
            current_key_index = (current_key_index + 1) % len(GEMINI_KEYS)
            await asyncio.sleep(1 * (2**i))
    return None
@bot.command()
async def clear(ctx):
    """Clearing ai memory"""
    if ctx.author.id != ADMIN_ID: return
    cleared_channels.add(ctx.channel.id)
    await ctx.send("🧹 AI Context history cleared for this channel.")
@bot.group(invoke_without_command=True)
async def blacklist(ctx):
    if ctx.author.id != ADMIN_ID: return
    await ctx.send("Usage: `.blacklist add @user reason` or `.blacklist remove @user`")
@blacklist.command(name="add")
async def blacklist_add(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    if ctx.author.id != ADMIN_ID: return
    overwrite = ctx.channel.overwrites_for(member)
    overwrite.send_messages = False
    overwrite.create_public_threads = False
    overwrite.create_private_threads = False
    overwrite.send_messages_in_threads = False
    await ctx.channel.set_permissions(member, overwrite=overwrite)
    log_channel = bot.get_channel(BLACKLIST_LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"User {member.mention} has been added to the blacklist. Reason: {reason}")
    
    await ctx.send(f"✅ {member.display_name} added to blacklist.")
@blacklist.command(name="remove")
async def blacklist_remove(ctx, member: discord.Member):
    if ctx.author.id != ADMIN_ID: return
    await ctx.channel.set_permissions(member, overwrite=None)
    log_channel = bot.get_channel(BLACKLIST_LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"Участник {member.mention} has been removed from the blacklist")
    
    await ctx.send(f"✅ {member.display_name} removed from blacklist.")
@bot.command()
async def lock(ctx):
    if ctx.author.id != ADMIN_ID: return
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔒 Channel locked")
@bot.command()
async def unlock(ctx):
    if ctx.author.id != ADMIN_ID: return
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = None
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔓 Channel unlocked")
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 **Pong!** `{round(bot.latency * 1000)}ms`")
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(AI_ASSISTANT_CHANNEL_ID)
    if channel:
        try:
            perms = channel.permissions_for(channel.guild.me)
            if perms.send_messages and perms.embed_links:
                embed = discord.Embed(title="System Status", description="Enabled", color=discord.Color.green())
                await channel.send(embed=embed)
        except: pass
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.id in LOG_CHANNELS:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Channel <#{message.channel.id}> | {message.author.name}: {message.clean_content}\n"
        with open(LIVE_UPDATES_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
        return

    await bot.process_commands(message)
    if message.content.startswith(bot.command_prefix):
        return
    if message.channel.id == AI_ASSISTANT_CHANNEL_ID:
        async with message.channel.typing():
            history_context = ""
            should_use_history = message.channel.id not in cleared_channels
            if message.channel.id in cleared_channels:
                cleared_channels.remove(message.channel.id)
            if should_use_history:
                if message.reference and message.reference.message_id:
                    try:
                        ref_msg = await message.channel.fetch_message(message.reference.message_id)
                        history_context = f"User is replying to this:\n{ref_msg.author.name}: {ref_msg.clean_content}"
                    except: pass
                
                if not history_context:
                    try:
                        async for last_msg in message.channel.history(limit=10):
                            if last_msg.author == bot.user and last_msg.id != message.id:
                                if (datetime.now(last_msg.created_at.tzinfo) - last_msg.created_at).total_seconds() < 1800:
                                    history_context = f"Last bot message for context: {last_msg.clean_content}"
                                break
                    except: pass
            
            response = await safe_generate_content(message.content, history=history_context)
            if response:
                await message.reply(response[:2000])

if __name__ == "__main__":
    try:
        bot.run(DISCORD_TOKEN)
    except KeyboardInterrupt:
        asyncio.run(bot.shutdown())
