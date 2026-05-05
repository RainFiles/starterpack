import discord
from discord.ext import commands
import time
import datetime
import random
import platform
import math
import asyncio
import os
import sys

# ─────────────────────────────────────────
#  CONFIG  –  replace the token below
# ─────────────────────────────────────────
TOKEN = "YOUR_BOT_TOKEN_HERE"
PREFIX = "!"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

START_TIME = time.time()

# ══════════════════════════════════════════
#  EVENTS
# ══════════════════════════════════════════

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name=f"{PREFIX}help | {len(bot.guilds)} servers"))
    print(f"✅  Logged in as {bot.user} ({bot.user.id})")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"⚠️ Missing argument. Try `{PREFIX}help {ctx.command}`")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"❌ Error: {error}")

# ══════════════════════════════════════════
#  ① UTILITY COMMANDS
# ══════════════════════════════════════════

@bot.command(name="uptime", help="Shows how long the bot has been running.")
async def uptime(ctx):
    elapsed = int(time.time() - START_TIME)
    h, r = divmod(elapsed, 3600)
    m, s = divmod(r, 60)
    embed = discord.Embed(title="⏱ Uptime", description=f"**{h}h {m}m {s}s**", color=0x5865F2)
    await ctx.send(embed=embed)


@bot.command(name="ping", help="Shows bot latency.")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Pong!", description=f"Latency: **{latency} ms**", color=0x57F287)
    await ctx.send(embed=embed)


@bot.command(name="time", help="Shows the current UTC time.")
async def time_cmd(ctx):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    embed = discord.Embed(title="🕐 Current Time", description=f"`{now}`", color=0xFEE75C)
    await ctx.send(embed=embed)


@bot.command(name="date", help="Shows today's date.")
async def date_cmd(ctx):
    now = datetime.datetime.utcnow().strftime("%A, %B %d %Y")
    embed = discord.Embed(title="📅 Today's Date", description=now, color=0xFEE75C)
    await ctx.send(embed=embed)


@bot.command(name="serverinfo", help="Shows info about this server.")
async def serverinfo(ctx):
    g = ctx.guild
    embed = discord.Embed(title=f"ℹ️ {g.name}", color=0x5865F2)
    embed.add_field(name="Owner", value=g.owner.mention)
    embed.add_field(name="Members", value=g.member_count)
    embed.add_field(name="Channels", value=len(g.channels))
    embed.add_field(name="Roles", value=len(g.roles))
    embed.add_field(name="Created", value=g.created_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Region", value=str(g.preferred_locale))
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
    await ctx.send(embed=embed)


@bot.command(name="userinfo", help="Shows info about a user. Usage: !userinfo [@user]")
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member}", color=member.color)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Nickname", value=member.nick or "None")
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Top Role", value=member.top_role.mention)
    embed.add_field(name="Bot", value="Yes" if member.bot else "No")
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="avatar", help="Shows a user's avatar. Usage: !avatar [@user]")
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"🖼️ {member.display_name}'s Avatar", color=0x5865F2)
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="botinfo", help="Shows info about the bot.")
async def botinfo(ctx):
    embed = discord.Embed(title="🤖 Bot Info", color=0x5865F2)
    embed.add_field(name="Name", value=str(bot.user))
    embed.add_field(name="Servers", value=len(bot.guilds))
    embed.add_field(name="Commands", value=len(bot.commands))
    embed.add_field(name="Python", value=platform.python_version())
    embed.add_field(name="discord.py", value=discord.__version__)
    embed.add_field(name="Prefix", value=PREFIX)
    await ctx.send(embed=embed)


@bot.command(name="membercount", help="Shows the server member count.")
async def membercount(ctx):
    embed = discord.Embed(
        title="👥 Member Count",
        description=f"**{ctx.guild.member_count}** members",
        color=0x57F287)
    await ctx.send(embed=embed)


@bot.command(name="channelinfo", help="Shows info about the current channel.")
async def channelinfo(ctx):
    ch = ctx.channel
    embed = discord.Embed(title=f"📢 #{ch.name}", color=0x5865F2)
    embed.add_field(name="ID", value=ch.id)
    embed.add_field(name="Type", value=str(ch.type))
    embed.add_field(name="Created", value=ch.created_at.strftime("%Y-%m-%d"))
    if hasattr(ch, "topic") and ch.topic:
        embed.add_field(name="Topic", value=ch.topic, inline=False)
    await ctx.send(embed=embed)


# ══════════════════════════════════════════
#  ② FUN COMMANDS
# ══════════════════════════════════════════

@bot.command(name="roll", help="Roll dice. Usage: !roll [NdN] e.g. !roll 2d6")
async def roll(ctx, dice: str = "1d6"):
    try:
        num, sides = map(int, dice.lower().split("d"))
        if num < 1 or num > 100 or sides < 2 or sides > 1000:
            raise ValueError
        results = [random.randint(1, sides) for _ in range(num)]
        total = sum(results)
        embed = discord.Embed(title=f"🎲 Rolling {dice}", color=0xEB459E)
        embed.add_field(name="Results", value=" + ".join(map(str, results)))
        embed.add_field(name="Total", value=str(total))
        await ctx.send(embed=embed)
    except (ValueError, AttributeError):
        await ctx.send("⚠️ Invalid format. Use `!roll 2d6`")


@bot.command(name="coinflip", help="Flip a coin.")
async def coinflip(ctx):
    result = random.choice(["Heads 🪙", "Tails 🪙"])
    await ctx.send(f"**{result}**")


@bot.command(name="8ball", help="Ask the magic 8-ball. Usage: !8ball <question>")
async def eight_ball(ctx, *, question: str):
    responses = [
        "It is certain.", "Without a doubt.", "Yes, definitely.", "You may rely on it.",
        "As I see it, yes.", "Most likely.", "Outlook good.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Don't count on it.", "My reply is no.",
        "My sources say no.", "Outlook not so good.", "Very doubtful."
    ]
    embed = discord.Embed(title="🎱 Magic 8-Ball", color=0x5865F2)
    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name="Answer", value=random.choice(responses), inline=False)
    await ctx.send(embed=embed)


@bot.command(name="rps", help="Rock Paper Scissors. Usage: !rps <rock/paper/scissors>")
async def rps(ctx, choice: str):
    choices = ["rock", "paper", "scissors"]
    choice = choice.lower()
    if choice not in choices:
        return await ctx.send("⚠️ Choose rock, paper, or scissors.")
    bot_choice = random.choice(choices)
    icons = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
    if choice == bot_choice:
        result = "It's a tie!"
    elif (choice == "rock" and bot_choice == "scissors") or \
         (choice == "paper" and bot_choice == "rock") or \
         (choice == "scissors" and bot_choice == "paper"):
        result = "You win! 🎉"
    else:
        result = "Bot wins! 🤖"
    embed = discord.Embed(title="✂️ Rock Paper Scissors", color=0xEB459E)
    embed.add_field(name="You", value=f"{icons[choice]} {choice.capitalize()}")
    embed.add_field(name="Bot", value=f"{icons[bot_choice]} {bot_choice.capitalize()}")
    embed.add_field(name="Result", value=result, inline=False)
    await ctx.send(embed=embed)


@bot.command(name="choose", help="Randomly choose from options. Usage: !choose a | b | c")
async def choose(ctx, *, options: str):
    items = [o.strip() for o in options.split("|") if o.strip()]
    if len(items) < 2:
        return await ctx.send("⚠️ Provide at least 2 options separated by `|`.")
    chosen = random.choice(items)
    await ctx.send(f"🎯 I choose: **{chosen}**")


@bot.command(name="say", help="Makes the bot say something. Usage: !say <text>")
async def say(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(message)


@bot.command(name="reverse", help="Reverses text. Usage: !reverse <text>")
async def reverse(ctx, *, text: str):
    await ctx.send(text[::-1])


@bot.command(name="mock", help="Mocks text. Usage: !mock <text>")
async def mock(ctx, *, text: str):
    result = "".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))
    await ctx.send(result)


@bot.command(name="emojify", help="Turns text into letter emojis. Usage: !emojify <text>")
async def emojify(ctx, *, text: str):
    result = ""
    for c in text.lower():
        if c.isalpha():
            result += f":regional_indicator_{c}: "
        elif c == " ":
            result += "  "
        else:
            result += c
    await ctx.send(result[:2000])


@bot.command(name="rate", help="Rates something out of 10. Usage: !rate <thing>")
async def rate(ctx, *, thing: str):
    score = random.randint(0, 10)
    bar = "█" * score + "░" * (10 - score)
    await ctx.send(f"I rate **{thing}** a **{score}/10**\n`[{bar}]`")


@bot.command(name="ship", help="Ship two users. Usage: !ship @user1 @user2")
async def ship(ctx, user1: discord.Member, user2: discord.Member):
    score = random.randint(0, 100)
    bar = "❤️" * (score // 10) + "🖤" * (10 - score // 10)
    await ctx.send(f"💘 **{user1.display_name}** + **{user2.display_name}**\n{bar} **{score}%** compatible!")


@bot.command(name="joke", help="Tells a random joke.")
async def joke(ctx):
    jokes = [
        ("Why don't scientists trust atoms?", "Because they make up everything!"),
        ("Why did the scarecrow win an award?", "Because he was outstanding in his field!"),
        ("I told my wife she should embrace her mistakes.", "She gave me a hug."),
        ("Why don't eggs tell jokes?", "They'd crack each other up."),
        ("What do you call a fake noodle?", "An impasta!"),
        ("Why can't you give Elsa a balloon?", "Because she'll let it go."),
        ("I'm reading a book about anti-gravity.", "It's impossible to put down!"),
        ("What do you call cheese that isn't yours?", "Nacho cheese."),
    ]
    setup, punchline = random.choice(jokes)
    embed = discord.Embed(title="😂 Joke", color=0xFEE75C)
    embed.add_field(name="Setup", value=setup, inline=False)
    embed.add_field(name="Punchline", value=f"||{punchline}||", inline=False)
    await ctx.send(embed=embed)


@bot.command(name="fact", help="Gives a random fun fact.")
async def fact(ctx):
    facts = [
        "Honey never spoils. Archaeologists found 3,000-year-old honey in Egyptian tombs.",
        "A group of flamingos is called a flamboyance.",
        "Octopuses have three hearts.",
        "The Eiffel Tower can be 15 cm taller during summer due to thermal expansion.",
        "Bananas are berries, but strawberries are not.",
        "Wombats produce cube-shaped poop.",
        "A day on Venus is longer than a year on Venus.",
        "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.",
        "The unicorn is Scotland's national animal.",
        "There are more possible iterations of a game of chess than atoms in the observable universe.",
    ]
    embed = discord.Embed(title="🧠 Fun Fact", description=random.choice(facts), color=0x57F287)
    await ctx.send(embed=embed)


@bot.command(name="roast", help="Roasts a user. Usage: !roast [@user]")
async def roast(ctx, member: discord.Member = None):
    member = member or ctx.author
    roasts = [
        "I'd roast you, but my mom said I'm not allowed to burn trash.",
        "You're not stupid — you just have bad luck thinking.",
        "I've seen better-looking faces on a clock.",
        "If brains were dynamite, you couldn't blow your hat off.",
        "You're proof that even evolution makes mistakes.",
    ]
    await ctx.send(f"{member.mention} {random.choice(roasts)}")


@bot.command(name="compliment", help="Compliments a user. Usage: !compliment [@user]")
async def compliment(ctx, member: discord.Member = None):
    member = member or ctx.author
    compliments = [
        "You have a smile that can light up the whole room!",
        "You're more fun than bubble wrap.",
        "You bring out the best in other people.",
        "You are genuinely one of a kind!",
        "Your creativity and imagination are truly inspiring.",
    ]
    await ctx.send(f"{member.mention} {random.choice(compliments)} 😊")


# ══════════════════════════════════════════
#  ③ MATH / NUMBER COMMANDS
# ══════════════════════════════════════════

@bot.command(name="calc", help="Evaluates a math expression. Usage: !calc 2+2")
async def calc(ctx, *, expression: str):
    try:
        # Safe eval — only allow math operations
        allowed = set("0123456789+-*/.() **")
        if not all(c in allowed for c in expression.replace(" ", "")):
            raise ValueError("Invalid characters")
        result = eval(expression, {"__builtins__": {}}, {})
        await ctx.send(f"🧮 `{expression}` = **{result}**")
    except Exception:
        await ctx.send("⚠️ Invalid expression.")


@bot.command(name="random", help="Random number between two values. Usage: !random 1 100")
async def random_num(ctx, low: int = 1, high: int = 100):
    if low >= high:
        return await ctx.send("⚠️ First number must be less than second.")
    await ctx.send(f"🎲 Random number between {low} and {high}: **{random.randint(low, high)}**")


@bot.command(name="sqrt", help="Square root of a number. Usage: !sqrt 144")
async def sqrt(ctx, number: float):
    if number < 0:
        return await ctx.send("⚠️ Cannot take square root of a negative number.")
    await ctx.send(f"√{number} = **{math.sqrt(number):.4f}**")


@bot.command(name="percentage", help="Percentage calculator. Usage: !percentage 25 200")
async def percentage(ctx, part: float, whole: float):
    if whole == 0:
        return await ctx.send("⚠️ Whole cannot be zero.")
    result = (part / whole) * 100
    await ctx.send(f"📊 {part} is **{result:.2f}%** of {whole}")


# ══════════════════════════════════════════
#  ④ MODERATION COMMANDS
# ══════════════════════════════════════════

@bot.command(name="kick", help="Kicks a member. Usage: !kick @user [reason]")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    embed = discord.Embed(title="👢 Member Kicked", color=0xED4245)
    embed.add_field(name="User", value=str(member))
    embed.add_field(name="Reason", value=reason)
    embed.add_field(name="Mod", value=str(ctx.author))
    await ctx.send(embed=embed)


@bot.command(name="ban", help="Bans a member. Usage: !ban @user [reason]")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    embed = discord.Embed(title="🔨 Member Banned", color=0xED4245)
    embed.add_field(name="User", value=str(member))
    embed.add_field(name="Reason", value=reason)
    embed.add_field(name="Mod", value=str(ctx.author))
    await ctx.send(embed=embed)


@bot.command(name="unban", help="Unbans a user. Usage: !unban user#0000")
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, user: str):
    bans = [ban_entry async for ban_entry in ctx.guild.bans()]
    for ban_entry in bans:
        if str(ban_entry.user) == user:
            await ctx.guild.unban(ban_entry.user)
            return await ctx.send(f"✅ Unbanned **{user}**")
    await ctx.send(f"⚠️ User `{user}` not found in ban list.")


@bot.command(name="mute", help="Times out a member for N minutes. Usage: !mute @user 10 [reason]")
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int = 10, *, reason: str = "No reason"):
    until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
    await member.timeout(until, reason=reason)
    await ctx.send(f"🔇 **{member}** muted for **{minutes} minute(s)**. Reason: {reason}")


@bot.command(name="unmute", help="Removes timeout from a member. Usage: !unmute @user")
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 **{member}** has been unmuted.")


@bot.command(name="purge", help="Deletes messages. Usage: !purge 10")
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int = 5):
    if amount < 1 or amount > 100:
        return await ctx.send("⚠️ Amount must be between 1 and 100.")
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🗑️ Deleted **{len(deleted) - 1}** messages.")
    await asyncio.sleep(3)
    await msg.delete()


@bot.command(name="warn", help="Warns a member. Usage: !warn @user [reason]")
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason: str = "No reason"):
    embed = discord.Embed(title="⚠️ Warning Issued", color=0xFEE75C)
    embed.add_field(name="User", value=str(member))
    embed.add_field(name="Reason", value=reason)
    embed.add_field(name="Mod", value=str(ctx.author))
    try:
        await member.send(f"⚠️ You were warned in **{ctx.guild.name}** for: {reason}")
    except discord.Forbidden:
        pass
    await ctx.send(embed=embed)


@bot.command(name="slowmode", help="Sets channel slowmode. Usage: !slowmode 5 (seconds)")
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int = 0):
    await ctx.channel.edit(slowmode_delay=seconds)
    if seconds == 0:
        await ctx.send("✅ Slowmode **disabled**.")
    else:
        await ctx.send(f"✅ Slowmode set to **{seconds}s**.")


@bot.command(name="lock", help="Locks the current channel.")
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔒 Channel **locked**.")


@bot.command(name="unlock", help="Unlocks the current channel.")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔓 Channel **unlocked**.")


# ══════════════════════════════════════════
#  ⑤ ROLE / SERVER MANAGEMENT
# ══════════════════════════════════════════

@bot.command(name="addrole", help="Adds a role to a user. Usage: !addrole @user @role")
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"✅ Added **{role.name}** to **{member.display_name}**.")


@bot.command(name="removerole", help="Removes a role from a user. Usage: !removerole @user @role")
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"✅ Removed **{role.name}** from **{member.display_name}**.")


@bot.command(name="roleinfo", help="Shows info about a role. Usage: !roleinfo @role")
async def roleinfo(ctx, role: discord.Role):
    embed = discord.Embed(title=f"🏷️ Role: {role.name}", color=role.color)
    embed.add_field(name="ID", value=role.id)
    embed.add_field(name="Color", value=str(role.color))
    embed.add_field(name="Members", value=len(role.members))
    embed.add_field(name="Hoisted", value="Yes" if role.hoist else "No")
    embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No")
    embed.add_field(name="Created", value=role.created_at.strftime("%Y-%m-%d"))
    await ctx.send(embed=embed)


@bot.command(name="roles", help="Lists all server roles.")
async def roles(ctx):
    role_list = [r.mention for r in reversed(ctx.guild.roles) if r.name != "@everyone"]
    desc = " ".join(role_list) if role_list else "No roles."
    embed = discord.Embed(title=f"🏷️ Roles ({len(role_list)})", description=desc[:4096], color=0x5865F2)
    await ctx.send(embed=embed)


@bot.command(name="setnick", help="Sets a member's nickname. Usage: !setnick @user NewName")
@commands.has_permissions(manage_nicknames=True)
async def setnick(ctx, member: discord.Member, *, nickname: str):
    await member.edit(nick=nickname)
    await ctx.send(f"✅ Nickname changed to **{nickname}**.")


@bot.command(name="resetnick", help="Resets a member's nickname. Usage: !resetnick @user")
@commands.has_permissions(manage_nicknames=True)
async def resetnick(ctx, member: discord.Member):
    await member.edit(nick=None)
    await ctx.send(f"✅ Nickname reset for **{member.name}**.")


# ══════════════════════════════════════════
#  ⑥ POLL / EMBED TOOLS
# ══════════════════════════════════════════

@bot.command(name="poll", help="Creates a yes/no poll. Usage: !poll Is this cool?")
async def poll(ctx, *, question: str):
    embed = discord.Embed(title="📊 Poll", description=question, color=0x5865F2)
    embed.set_footer(text=f"Asked by {ctx.author.display_name}")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
    await ctx.message.delete()


@bot.command(name="announce", help="Sends an announcement embed. Usage: !announce <message>")
@commands.has_permissions(manage_messages=True)
async def announce(ctx, *, message: str):
    embed = discord.Embed(title="📣 Announcement", description=message, color=0xEB459E)
    embed.set_footer(text=f"From {ctx.author.display_name}")
    await ctx.send(embed=embed)
    await ctx.message.delete()


@bot.command(name="embed", help="Sends a custom embed. Usage: !embed Title | Description")
async def embed_cmd(ctx, *, content: str):
    parts = content.split("|", 1)
    title = parts[0].strip()
    desc = parts[1].strip() if len(parts) > 1 else ""
    embed = discord.Embed(title=title, description=desc, color=ctx.author.color)
    await ctx.send(embed=embed)


# ══════════════════════════════════════════
#  ⑦ SEARCH / LOOK UP
# ══════════════════════════════════════════

@bot.command(name="urban", help="Looks up a term on Urban Dictionary. Usage: !urban <term>")
async def urban(ctx, *, term: str):
    url = f"https://www.urbandictionary.com/define.php?term={term.replace(' ', '+')}"
    embed = discord.Embed(title=f"📖 Urban Dictionary: {term}",
                          description=f"[Click to view definition]({url})",
                          color=0xEB459E)
    await ctx.send(embed=embed)


@bot.command(name="wiki", help="Links to a Wikipedia article. Usage: !wiki <topic>")
async def wiki(ctx, *, topic: str):
    url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
    embed = discord.Embed(title=f"📚 Wikipedia: {topic}",
                          description=f"[Click to read article]({url})",
                          color=0x5865F2)
    await ctx.send(embed=embed)


@bot.command(name="google", help="Generates a Google search link. Usage: !google <query>")
async def google(ctx, *, query: str):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    await ctx.send(f"🔍 [Search Google for \"{query}\"]({url})")


@bot.command(name="youtube", help="Generates a YouTube search link. Usage: !youtube <query>")
async def youtube(ctx, *, query: str):
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    await ctx.send(f"▶️ [Search YouTube for \"{query}\"]({url})")


# ══════════════════════════════════════════
#  ⑧ MISC / EXTRA COMMANDS
# ══════════════════════════════════════════

@bot.command(name="afk", help="Sets your AFK status. Usage: !afk [reason]")
async def afk(ctx, *, reason: str = "AFK"):
    await ctx.send(f"💤 **{ctx.author.display_name}** is now AFK: {reason}")


@bot.command(name="remind", help="Reminds you after N seconds. Usage: !remind 30 Do homework")
async def remind(ctx, seconds: int, *, reminder: str):
    if seconds < 1 or seconds > 3600:
        return await ctx.send("⚠️ Please enter between 1 and 3600 seconds.")
    await ctx.send(f"⏰ I'll remind you in **{seconds}s**: {reminder}")
    await asyncio.sleep(seconds)
    await ctx.send(f"⏰ {ctx.author.mention} Reminder: **{reminder}**")


@bot.command(name="countdown", help="Counts down from N. Usage: !countdown 5")
async def countdown(ctx, n: int = 5):
    if n < 1 or n > 10:
        return await ctx.send("⚠️ Please choose between 1 and 10.")
    msg = await ctx.send(f"⏳ **{n}**")
    for i in range(n - 1, 0, -1):
        await asyncio.sleep(1)
        await msg.edit(content=f"⏳ **{i}**")
    await asyncio.sleep(1)
    await msg.edit(content="🚀 **Go!**")


@bot.command(name="tinyurl", help="Shortens a URL via TinyURL. Usage: !tinyurl <url>")
async def tinyurl(ctx, url: str):
    short = f"https://tinyurl.com/api-create.php?url={url}"
    await ctx.send(f"🔗 Short URL: {short}\n*(Note: open URL above in a browser to resolve)*")


@bot.command(name="color", help="Shows a color swatch. Usage: !color #FF5733 or !color 255 87 51")
async def color(ctx, *args):
    try:
        if len(args) == 1:
            hex_val = args[0].lstrip("#")
            r, g, b = int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16)
        elif len(args) == 3:
            r, g, b = int(args[0]), int(args[1]), int(args[2])
        else:
            raise ValueError
        color_int = (r << 16) + (g << 8) + b
        embed = discord.Embed(title="🎨 Color Info", color=color_int)
        embed.add_field(name="HEX", value=f"#{r:02X}{g:02X}{b:02X}")
        embed.add_field(name="RGB", value=f"rgb({r}, {g}, {b})")
        await ctx.send(embed=embed)
    except (ValueError, IndexError):
        await ctx.send("⚠️ Usage: `!color #FF5733` or `!color 255 87 51`")


@bot.command(name="ascii", help="Converts text to ASCII codes. Usage: !ascii Hello")
async def ascii_cmd(ctx, *, text: str):
    codes = " ".join(str(ord(c)) for c in text[:50])
    await ctx.send(f"🔢 ASCII: `{codes}`")


@bot.command(name="binary", help="Converts text to binary. Usage: !binary Hello")
async def binary(ctx, *, text: str):
    result = " ".join(format(ord(c), "08b") for c in text[:20])
    await ctx.send(f"💻 Binary:\n```{result}```")


@bot.command(name="timestamp", help="Converts a Unix timestamp. Usage: !timestamp 1714000000")
async def timestamp(ctx, unix: int):
    dt = datetime.datetime.utcfromtimestamp(unix).strftime("%Y-%m-%d %H:%M:%S UTC")
    await ctx.send(f"🕐 `{unix}` → **{dt}**")


@bot.command(name="invite", help="Generates a bot invite link.")
async def invite(ctx):
    url = discord.utils.oauth_url(bot.user.id, permissions=discord.Permissions(8))
    embed = discord.Embed(title="📨 Invite Me!",
                          description=f"[Click here to invite the bot]({url})",
                          color=0x57F287)
    await ctx.send(embed=embed)


@bot.command(name="github", help="Links to GitHub.")
async def github(ctx):
    await ctx.send("🐙 https://github.com")


@bot.command(name="status", help="Shows bot status summary.")
async def status(ctx):
    elapsed = int(time.time() - START_TIME)
    h, r = divmod(elapsed, 3600)
    m, s = divmod(r, 60)
    embed = discord.Embed(title="📊 Bot Status", color=0x57F287)
    embed.add_field(name="Uptime", value=f"{h}h {m}m {s}s")
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms")
    embed.add_field(name="Servers", value=len(bot.guilds))
    embed.add_field(name="Commands", value=len(bot.commands))
    await ctx.send(embed=embed)


# ══════════════════════════════════════════
#  ⑨ HELP COMMAND
# ══════════════════════════════════════════

@bot.command(name="help", help="Shows this help menu.")
async def help_cmd(ctx, command_name: str = None):
    if command_name:
        cmd = bot.get_command(command_name)
        if cmd:
            embed = discord.Embed(title=f"❓ {PREFIX}{cmd.name}", description=cmd.help, color=0x5865F2)
            return await ctx.send(embed=embed)
        else:
            return await ctx.send(f"⚠️ Command `{command_name}` not found.")

    categories = {
        "⏱ Utility": ["uptime", "ping", "time", "date", "serverinfo", "userinfo",
                       "avatar", "botinfo", "membercount", "channelinfo"],
        "🎉 Fun": ["roll", "coinflip", "8ball", "rps", "choose", "say", "reverse",
                   "mock", "emojify", "rate", "ship", "joke", "fact", "roast", "compliment"],
        "🧮 Math": ["calc", "random", "sqrt", "percentage"],
        "🛡 Moderation": ["kick", "ban", "unban", "mute", "unmute", "purge", "warn",
                          "slowmode", "lock", "unlock"],
        "🏷 Roles": ["addrole", "removerole", "roleinfo", "roles", "setnick", "resetnick"],
        "📢 Embeds": ["poll", "announce", "embed"],
        "🔍 Search": ["urban", "wiki", "google", "youtube"],
        "🔧 Misc": ["afk", "remind", "countdown", "tinyurl", "color", "ascii",
                    "binary", "timestamp", "invite", "github", "status"],
    }

    embed = discord.Embed(title=f"📖 Command List  ({len(bot.commands)} commands)",
                          description=f"Prefix: `{PREFIX}`  •  Use `{PREFIX}help <command>` for details",
                          color=0x5865F2)
    for cat, cmds in categories.items():
        embed.add_field(name=cat,
                        value=" ".join(f"`{PREFIX}{c}`" for c in cmds),
                        inline=False)
    await ctx.send(embed=embed)


# ══════════════════════════════════════════
#  RUN
# ══════════════════════════════════════════
if __name__ == "__main__":
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌  Please set your TOKEN in bot.py before running!")
        sys.exit(1)
    bot.run(TOKEN)
