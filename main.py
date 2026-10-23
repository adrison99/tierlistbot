import os
import sqlite3
import datetime
import asyncio
import discord
from discord.ext import commands
from aiohttp import web

TRANSLATIONS = {
    "cs": {
        "no_perms": "❌ Na tento příkaz nemáš oprávnění!",
        "verified_success": "✅ Úspěšně verifikován Minecraft účet: **{ign}**",
        "kit_created": "✅ Kit **{kit}** byl úspěšně přidán do databáze.",
        "kit_exists": "⚠️ Kit **{kit}** již v databázi existuje.",
        "kit_removed": "🗑️ Kit **{kit}** byl odstraněn.",
        "tier_role_set": "✅ Pro kit **{kit}** a tier **{tier}** byla nastavená role **{role}**.",
        "result_room_set": "✅ Result místnost nastavena na {room}.",
        "helper_role_set": "✅ Helper role nastavena na {role}.",
        "queue_room_set": "✅ Fronta pro kit **{kit}** svázána s kanálem {room}.",
        "kit_cat_set": "✅ Pro kit **{kit}** byla nastavená kategorie **{cat}**.",
        "lang_set": "🌐 Jazyk serveru byl změněn na **Čeština**.",
        "cooldown_set": "⏳ Cooldown pro **{tipo}** úspěšně nastaven na **{time}**.",
        "cooldown_removed": "✅ Cooldown typu **{tipo}** pro kit **{kit}** byl hráči {player} úspěšně odstraněn.",
        "queue_opened": "✅ Fronta pro kit **{kit}** byla úspěšně otevřena v kanálu {room}!",
        "queue_closed": "🔒 Fronta pro kit **{kit}** byla uzavřena.",
        "cannot_close_active": "⚠️ Nemůžeš zavřít frontu, protože v ní stále probíhají testy!",
        "tester_joined": "✅ Úspěšně ses přidal jako aktivní tester pro kit **{kit}**.",
        "tester_left": "✅ Byl jsi odebrán z aktivních testerů pro kit **{kit}**.",
        "already_tester": "⚠️ Už jsi zapsán jako tester v této frontě!",
        "not_tester": "⚠️ Nejsi veden jako aktivní tester v této frontě.",
        "join_btn": "Join Queue",
        "leave_btn": "Leave Queue",
        "pull_btn": "Pull Player ⚔️",
        "queue_empty": "_Fronta je prázdná. Buď první!_",
        "no_testers": "_Žádní aktivní testeři._",
        "active_testers": "Aktivní Testeři",
        "queue_title": "📝 {kit} Waitlist",
        "queue_desc": "⏱️ Fronta se aktualizuje automaticky.\nPoužij tlačítka níže pro přidání nebo odebrání.",
        "closed_title": "🔒 {kit} Queue",
        "closed_desc": "Queue momentálně není otevřená. Počkej na Testera, který ji otevře.",
        "result_title": "📝 Výsledek tier testu – {kit}",
        "result_desc": "Tier test byl úspěšně dokončen pro frontu **{kit}**!",
        "result_sent": "✅ Výsledek byl úspěšně zaznamenán a tato místnost bude za chvíli smazána.",
        "test_started": "⚔️ Test začíná! Tester: {tester} | Hráč: {player}\nPo dokončení zadejte `/result` přímo v tomto kanálu.",
        "player_pulled": "✅ Hráč {player} byl vytažen do místnosti {room}!",
        "not_verified": "❌ Nemůžeš vstoupit do fronty, dokud se nepropojíš přes `/verify <minecraft ign>`!",
        "already_in_queue": "⚠️ Už jsi v této frontě!",
        "left_queue": "✅ Jsi venku z fronty.",
        "not_in_queue": "⚠️ Nejsi v této frontě."
    },
    "en-gb": {
        "no_perms": "❌ You do not have permission for this command!",
        "verified_success": "✅ Successfully verified Minecraft account: **{ign}**",
        "kit_created": "✅ Kit **{kit}** has been successfully added to the database.",
        "kit_exists": "⚠️ Kit **{kit}** already exists in the database.",
        "kit_removed": "🗑️ Kit **{kit}** was removed.",
        "tier_role_set": "✅ Role **{role}** set for kit **{kit}** and tier **{tier}**.",
        "result_room_set": "✅ Result channel set to {room}.",
        "helper_role_set": "✅ Helper role set to {role}.",
        "queue_room_set": "✅ Queue for kit **{kit}** bound to channel {room}.",
        "kit_cat_set": "✅ Category **{cat}** set for kit **{kit}**.",
        "lang_set": "🌐 Server language set to **English (British)**.",
        "cooldown_set": "⏳ Cooldown for **{tipo}** successfully set to **{time}**.",
        "cooldown_removed": "✅ Cooldown type **{tipo}** for kit **{kit}** successfully removed for player {player}.",
        "queue_opened": "✅ Queue for kit **{kit}** successfully opened in channel {room}!",
        "queue_closed": "🔒 Queue for kit **{kit}** has been closed.",
        "cannot_close_active": "⚠️ Cannot close queue while testing is ongoing!",
        "tester_joined": "✅ Successfully joined as active tester for kit **{kit}**.",
        "tester_left": "✅ Removed from active testers for kit **{kit}**.",
        "already_tester": "⚠️ You are already listed as a tester in this queue!",
        "not_tester": "⚠️ You are not listed as an active tester in this queue.",
        "join_btn": "Join Queue",
        "leave_btn": "Leave Queue",
        "pull_btn": "Pull Player ⚔️",
        "queue_empty": "_Queue is empty. Be the first!_",
        "no_testers": "_No active testers._",
        "active_testers": "Active Testers",
        "queue_title": "📝 {kit} Waitlist",
        "queue_desc": "⏱️ Queue updates automatically.\nUse buttons below to join or leave.",
        "closed_title": "🔒 {kit} Queue",
        "closed_desc": "Queue is currently closed. Wait for a Tester to open it.",
        "result_title": "📝 Tier Test Result – {kit}",
        "result_desc": "Tier test successfully completed for queue **{kit}**!",
        "result_sent": "✅ Result recorded, this channel will be deleted shortly.",
        "test_started": "⚔️ Test started! Tester: {tester} | Player: {player}\nWhen finished, use `/result` directly in this channel.",
        "player_pulled": "✅ Player {player} pulled to channel {room}!",
        "not_verified": "❌ You cannot join queue until verified via `/verify <minecraft ign>`!",
        "already_in_queue": "⚠️ You are already in this queue!",
        "left_queue": "✅ Left the queue.",
        "not_in_queue": "⚠️ You are not in this queue."
    }
}

def get_msg(guild_id: int, key: str, **kwargs) -> str:
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM server_settings WHERE guild_id = ?", (str(guild_id),))
    row = cursor.fetchone()
    conn.close()
    
    lang = row[0] if row and row[0] in TRANSLATIONS else "cs"
    dict_to_use = TRANSLATIONS.get(lang, TRANSLATIONS["cs"])
    msg = dict_to_use.get(key, TRANSLATIONS["cs"].get(key, ""))
    return msg.format(**kwargs)

def parse_cooldown(cd_str: str):
    days = 0
    hours = 0
    if not cd_str or cd_str == "0":
        return 0, 0
    cd_str = cd_str.strip().lower()
    if cd_str.endswith("d"):
        try: days = int(cd_str[:-1])
        except: pass
    elif cd_str.endswith("h"):
        try: hours = int(cd_str[:-1])
        except: pass
    else:
        try: days = int(cd_str)
        except: pass
    return days, hours

def init_db():
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS verified (discord_id TEXT PRIMARY KEY, minecraft_ign TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS kits (name TEXT PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tier_roles (kit TEXT, tier TEXT, role_id TEXT, PRIMARY KEY (kit, tier))")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS server_settings (
            guild_id TEXT PRIMARY KEY,
            result_room TEXT,
            helper_role TEXT,
            language TEXT DEFAULT 'cs',
            cooldown_lt TEXT DEFAULT '0',
            cooldown_ht TEXT DEFAULT '0',
            ht_ticket_room TEXT,
            turnaj_result_room TEXT
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS queue_rooms (kit TEXT PRIMARY KEY, channel_id TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS kit_categories (kit TEXT PRIMARY KEY, category_id TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS ht_ticket_categories (kit TEXT PRIMARY KEY, category_id TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS player_tiers (discord_id TEXT, kit TEXT, tier TEXT, PRIMARY KEY (discord_id, kit))")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_cooldowns (
            discord_id TEXT,
            kit TEXT,
            type TEXT,
            cooldown_until TEXT,
            PRIMARY KEY (discord_id, kit, type)
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS tester_monthly (discord_id TEXT, year_month TEXT, count INTEGER, PRIMARY KEY (discord_id, year_month))")
    cursor.execute("CREATE TABLE IF NOT EXISTS tester_overall (discord_id TEXT PRIMARY KEY, count INTEGER)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tournaments (
            kit TEXT PRIMARY KEY,
            tier TEXT,
            guild_id TEXT,
            category_id TEXT,
            signup_channel_id TEXT,
            end_time TEXT,
            groups_count INTEGER
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS tournament_signups (kit TEXT, discord_id TEXT, PRIMARY KEY (kit, discord_id))")
    conn.commit()
    conn.close()

init_db()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

VALID_TIERS = ["LT5", "HT5", "LT4", "HT4", "LT3", "HT3", "RLT2", "LT2", "RHT2", "HT2", "RLT1", "LT1", "RHT1", "HT1"]
HT_TIERS_ONLY = ["HT3", "HT2", "HT1"]
OWNER_IDS = [] 

async def has_helper_perms(ctx: discord.Interaction) -> bool:
    if ctx.user.id in OWNER_IDS or ctx.user.guild_permissions.administrator or ctx.guild.owner_id == ctx.user.id:
        return True
    
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT helper_role FROM server_settings WHERE guild_id = ?", (str(ctx.guild.id),))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0]:
        try:
            role_id = int(row[0])
            role = ctx.guild.get_role(role_id)
            if role and role in ctx.user.roles:
                return True
        except Exception:
            pass
            
    return False

async def kit_autocomplete(interaction: discord.Interaction, current: str):
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM kits")
    rows = cursor.fetchall()
    conn.close()
    kits = [row[0] for row in rows]
    return [discord.app_commands.Choice(name=kit, value=kit) for kit in kits if current.lower() in kit.lower()]

async def tier_autocomplete(interaction: discord.Interaction, current: str):
    return [discord.app_commands.Choice(name=tier, value=tier) for tier in VALID_TIERS if current.lower() in tier.lower()]

async def ht_tier_autocomplete(interaction: discord.Interaction, current: str):
    return [discord.app_commands.Choice(name=tier, value=tier) for tier in HT_TIERS_ONLY if current.lower() in tier.lower()]

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} je online!")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synchrováno {len(synced)} slash příkazů.")
    except Exception as e:
        print(f"❌ Chyba synchronizace: {e}")
    bot.loop.create_task(tournament_timer_loop())

# --- EDIT USER PŘÍKAZ ---
@bot.tree.command(name="edituser", description="Upraví profil hráče (Minecraft IGN nebo Tier pro konkrétní kit).")
@discord.app_commands.autocomplete(kit=kit_autocomplete, novy_tier=tier_autocomplete)
async def edituser(interaction: discord.Interaction, discord_hrac: discord.Member, nove_ign: str = None, kit: str = None, novy_tier: str = None):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

    if not nove_ign and not (kit and novy_tier):
        return await interaction.response.send_message("⚠️ Musíš zadat buď `nove_ign` nebo kombinaci `kit` + `novy_tier`!", ephemeral=True)

    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    response_parts = []

    # Změna Minecraft IGN
    if nove_ign:
        cursor.execute("INSERT OR REPLACE INTO verified (discord_id, minecraft_ign) VALUES (?, ?)", (str(discord_hrac.id), nove_ign))
        response_parts.append(f"🎮 IGN změněno na **{nove_ign}**")

    # Změna Tieru a udělení role
    if kit and novy_tier:
        t_clean = novy_tier.upper().replace("R", "")
        cursor.execute("INSERT OR REPLACE INTO player_tiers (discord_id, kit, tier) VALUES (?, ?, ?)", (str(discord_hrac.id), kit.lower(), t_clean))
        
        cursor.execute("SELECT role_id FROM tier_roles WHERE kit = ? AND tier = ?", (kit.lower(), t_clean))
        role_row = cursor.fetchone()
        if role_row and role_row[0]:
            role = interaction.guild.get_role(int(role_row[0]))
            if role:
                try:
                    await discord_hrac.add_roles(role)
                    response_parts.append(f"⚔️ Tier pro **{kit.capitalize()}** změněn na **{t_clean}** (Přidána role {role.name})")
                except:
                    response_parts.append(f"⚔️ Tier pro **{kit.capitalize()}** změněn na **{t_clean}** (Nepodařilo se dát roli)")
            else:
                response_parts.append(f"⚔️ Tier pro **{kit.capitalize()}** změněn na **{t_clean}**")
        else:
            response_parts.append(f"⚔️ Tier pro **{kit.capitalize()}** změněn na **{t_clean}**")

    conn.commit()
    conn.close()

    status_msg = "\n".join(response_parts)
    await interaction.response.send_message(f"✅ Úspěšně upraven profil pro {discord_hrac.mention}:\n{status_msg}", ephemeral=True)

# --- TURNAJOVÝ SYSTÉM ---
class TournamentSignupView(discord.ui.View):
    def __init__(self, kit: str):
        super().__init__(timeout=None)
        self.kit = kit

    @discord.ui.button(label="Přihlásit se", style=discord.ButtonStyle.success, emoji="✅", custom_id="tournament_signup_btn")
    async def signup_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        conn = sqlite3.connect("tierbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM tournament_signups WHERE kit = ? AND discord_id = ?", (self.kit.lower(), user_id))
        exists = cursor.fetchone()
        if exists:
            cursor.execute("DELETE FROM tournament_signups WHERE kit = ? AND discord_id = ?", (self.kit.lower(), user_id))
            conn.commit()
            conn.close()
            return await interaction.response.send_message("❌ Byl jsi odhlášen z turnaje.", ephemeral=True)
        
        cursor.execute("INSERT INTO tournament_signups (kit, discord_id) VALUES (?, ?)", (self.kit.lower(), user_id))
        conn.commit()
        conn.close()
        await interaction.response.send_message("✅ Úspěšně přihlášen do turnaje!", ephemeral=True)

async def close_and_draw_tournament(guild: discord.Guild, kit: str):
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT tier, category_id, signup_channel_id, groups_count FROM tournaments WHERE kit = ?", (kit.lower(),))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return
    
    tier, cat_id, signup_ch_id, groups_count = row
    cursor.execute("SELECT discord_id FROM tournament_signups WHERE kit = ?", (kit.lower(),))
    user_rows = cursor.fetchall()
    
    cursor.execute("DELETE FROM tournaments WHERE kit = ?", (kit.lower(),))
    cursor.execute("DELETE FROM tournament_signups WHERE kit = ?", (kit.lower(),))
    conn.commit()
    conn.close()

    players = [guild.get_member(int(r[0])) for r in user_rows if guild.get_member(int(r[0])) is not None]
    
    category = guild.get_channel(int(cat_id)) if cat_id else None
    signup_ch = guild.get_channel(int(signup_ch_id)) if signup_ch_id else None

    if signup_ch:
        try: await signup_ch.delete()
        except: pass

    if not players:
        if category:
            try: await category.delete()
            except: pass
        return

    import random
    import math
    random.shuffle(players)

    group_size = math.ceil(len(players) / groups_count) if groups_count > 0 else len(players)
    groups = []
    for i in range(0, len(players), group_size):
        groups.append(players[i:i + group_size])

    for idx, group_players in enumerate(groups, 1):
        group_channel_name = f"{kit.lower()}-skupina-{idx}"
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False)
        }
        for p in group_players:
            overwrites[p] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        group_ch = await guild.create_text_channel(
            name=group_channel_name,
            category=category if isinstance(category, discord.CategoryChannel) else None,
            overwrites=overwrites
        )

        mentions = " ".join([p.mention for p in group_players])
        
        matches_text = []
        for j in range(0, len(group_players) - 1, 2):
            matches_text.append(f"{group_players[j].mention} vs {group_players[j+1].mention}")
        if len(group_players) % 2 != 0:
            matches_text.append(f"{group_players[-1].mention} — čeká na soupeře (lichý počet)")

        players_list_text = "\n".join([f"{n+1}. {p.mention}" for n, p in enumerate(group_players)])
        matches_str = "\n".join(matches_text) if matches_text else "Žádné zápasy"

        embed = discord.Embed(
            title=f"🏆 Skupina {idx} — {kit.capitalize()} ({tier})",
            color=discord.Color.gold()
        )
        embed.add_field(name="Tier", value=tier, inline=False)
        embed.add_field(name="Hráči:", value=players_list_text, inline=False)
        embed.add_field(name="Zápasy (1v1):", value=matches_str, inline=False)
        embed.set_footer(text=f"Tester zapíše výsledky po dokončení zápasů pomocí /turnajresult.")

        await group_ch.send(content=mentions, embed=embed)

async def tournament_timer_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.datetime.now()
        conn = sqlite3.connect("tierbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT kit, guild_id, end_time FROM tournaments")
        rows = cursor.fetchall()
        conn.close()

        for kit, guild_id, end_time_str in rows:
            try:
                end_dt = datetime.datetime.fromisoformat(end_time_str)
                if now >= end_dt:
                    guild = bot.get_guild(int(guild_id))
                    if guild:
                        await close_and_draw_tournament(guild, kit)
            except Exception as e:
                print(f"Chyba v turnajovém timeru pro {kit}: {e}")

        await asyncio.sleep(30)

@bot.tree.command(name="createturnaj", description="Vytvoří nový turnaj pro daný kit a tier.")
@discord.app_commands.autocomplete(tier=ht_tier_autocomplete, kit=kit_autocomplete)
async def createturnaj(interaction: discord.Interaction, tier: str, kit: str, hodiny: int, skupiny: int):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

    guild = interaction.guild
    kit_key = kit.lower()
    t_clean = tier.upper().replace("R", "")

    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM tournaments WHERE kit = ?", (kit_key,))
    if cursor.fetchone():
        conn.close()
        return await interaction.response.send_message("❌ Pro tento kit již turnaj existuje! Použij nejprve `/deleteturnaj`.", ephemeral=True)

    lower_tier_map = {"HT3": "LT3", "HT2": "LT2", "HT1": "LT1"}
    target_lower_tier = lower_tier_map.get(t_clean, "LT3")

    cursor.execute("SELECT role_id FROM tier_roles WHERE kit = ? AND tier = ?", (kit_key, target_lower_tier))
    r_row = cursor.fetchone()
    conn.close()

    ping_role = guild.get_role(int(r_row[0])) if r_row and r_row[0] else None

    category_name = f"{t_clean}-{kit.capitalize()}-Turnaj"
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False)
    }
    if ping_role:
        overwrites[ping_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

    category = await guild.create_category(name=category_name, overwrites=overwrites)
    signup_ch = await guild.create_text_channel(name=f"{t_clean.lower()}-{kit.lower()}-signup", category=category)

    end_time = datetime.datetime.now() + datetime.timedelta(hours=hodiny)

    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tournaments (kit, tier, guild_id, category_id, signup_channel_id, end_time, groups_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (kit_key, t_clean, str(guild.id), str(category.id), str(signup_ch.id), end_time.isoformat(), skupiny))
    conn.commit()
    conn.close()

    embed = discord.Embed(
        title=f"🏆 {kit.capitalize()} TURNAJ — {t_clean}",
        description="Klikni na tlačítko ✅ pro přihlášení do turnaje!",
        color=discord.Color.gold()
    )
    embed.add_field(name="Kit", value=kit.capitalize(), inline=True)
    embed.add_field(name="Tier", value=t_clean, inline=True)
    embed.add_field(name="Skupin", value=str(skupiny), inline=True)
    embed.add_field(name="Deadline", value=f"<t:{int(end_time.timestamp())}:F> (za {hodiny} hodin)", inline=False)
    embed.set_footer(text=f"Vytvořil: {interaction.user.name}")

    content_ping = ping_role.mention if ping_role else "@everyone"
    view = TournamentSignupView(kit_key)
    await signup_ch.send(content=content_ping, embed=embed, view=view)

    await interaction.response.send_message(f"✅ Turnaj pro kit **{kit}** byl úspěšně vytvořen v kanálu {signup_ch.mention}!", ephemeral=True)

@bot.tree.command(name="deleteturnaj", description="Smaže probíhající turnaj a jeho místnosti.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def deleteturnaj(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

    kit_key = kit.lower()
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT category_id FROM tournaments WHERE kit = ?", (kit_key,))
    row = cursor.fetchone()
    cursor.execute("DELETE FROM tournaments WHERE kit = ?", (kit_key,))
    cursor.execute("DELETE FROM tournament_signups WHERE kit = ?", (kit_key,))
    conn.commit()
    conn.close()

    if row and row[0]:
        cat = interaction.guild.get_channel(int(row[0]))
        if cat and isinstance(cat, discord.CategoryChannel):
            for ch in cat.channels:
                try: await ch.delete()
                except: pass
            try: await cat.delete()
            except: pass

    await interaction.response.send_message(f"🗑️ Turnaj pro kit **{kit}** a jeho místnosti byly smazány.", ephemeral=True)

@bot.tree.command(name="turnajresultroomset", description="Nastaví místnost pro posílání výsledků turnajů.")
async def turnajresultroomset(interaction: discord.Interaction, roomka: discord.TextChannel):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO server_settings (guild_id, turnaj_result_room) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET turnaj_result_room = ?", (str(interaction.guild.id), str(roomka.id), str(roomka.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ Turnajová result místnost nastavena na {roomka.mention}.", ephemeral=True)

@bot.tree.command(name="turnajresult", description="Odešle výsledek turnaje a udělí role hráčům.")
@discord.app_commands.autocomplete(kit=kit_autocomplete, ziskany_tier=tier_autocomplete)
async def turnajresult(interaction: discord.Interaction, kit: str, ziskany_tier: str, hrac1: discord.Member, hrac2: discord.Member = None, hrac3: discord.Member = None):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

    hraci = [h for h in [hrac1, hrac2, hrac3] if h is not None]
    t_clean = ziskany_tier.upper().replace("R", "")
    kit_key = kit.lower()

    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT turnaj_result_room FROM server_settings WHERE guild_id = ?", (str(interaction.guild.id),))
    s_row = cursor.fetchone()
    cursor.execute("SELECT role_id FROM tier_roles WHERE kit = ? AND tier = ?", (kit_key, t_clean))
    role_row = cursor.fetchone()
    
    role = interaction.guild.get_role(int(role_row[0])) if role_row and role_row[0] else None

    ziskava_lines = []
    for h in hraci:
        cursor.execute("SELECT tier FROM player_tiers WHERE discord_id = ? AND kit = ?", (str(h.id), kit_key))
        p_row = cursor.fetchone()
        prev_tier = p_row[0] if p_row else "LT5"
        
        cursor.execute("INSERT OR REPLACE INTO player_tiers (discord_id, kit, tier) VALUES (?, ?, ?)", (str(h.id), kit_key, t_clean))
        
        if role:
            try: await h.add_roles(role)
            except: pass

        ziskava_lines.append(f"{h.mention} — {prev_tier} → {t_clean}")

    conn.commit()
    conn.close()

    embed = discord.Embed(
        title=f"🏆 {kit.capitalize()} TURNAJ",
        color=discord.Color.gold()
    )
    embed.add_field(name="Získává:", value="\n".join(ziskava_lines), inline=False)
    embed.set_footer(text=f"Zapisovatel: {interaction.user.name}")

    if s_row and s_row[0]:
        room = interaction.guild.get_channel(int(s_row[0]))
        if room:
            ping_content = f"<@&{role.id}>" if role else "@everyone"
            await room.send(content=ping_content, embed=embed)

    await interaction.response.send_message("✅ Výsledky turnaje byly úspěšně odeslány a role byly uděleny!", ephemeral=True)

# --- DATABÁZE A KOMPLETNÍ ZÁLOHA/OBNOVA ---
@bot.tree.command(name="databaseinfo", description="Vygeneruje textový kód pro zálohu nastavení, dat hráčů a statistik testerů.")
async def databaseinfo(interaction: discord.Interaction):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

    guild_id = str(interaction.guild.id)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()

    cursor.execute("SELECT result_room, helper_role, language, cooldown_lt, cooldown_ht, ht_ticket_room, turnaj_result_room FROM server_settings WHERE guild_id = ?", (guild_id,))
    settings = cursor.fetchone()

    cursor.execute("SELECT name FROM kits")
    kits = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT kit, tier, role_id FROM tier_roles")
    tier_roles = cursor.fetchall()

    cursor.execute("SELECT kit, channel_id FROM queue_rooms")
    queue_rooms = cursor.fetchall()

    cursor.execute("SELECT kit, category_id FROM kit_categories")
    kit_categories = cursor.fetchall()

    cursor.execute("SELECT kit, category_id FROM ht_ticket_categories")
    ht_ticket_categories = cursor.fetchall()

    cursor.execute("SELECT discord_id, minecraft_ign FROM verified")
    verified_users = cursor.fetchall()

    cursor.execute("SELECT discord_id, kit, tier FROM player_tiers")
    player_tiers = cursor.fetchall()

    cursor.execute("SELECT discord_id, kit, type, cooldown_until FROM player_cooldowns")
    player_cooldowns = cursor.fetchall()

    cursor.execute("SELECT discord_id, year_month, count FROM tester_monthly")
    tester_monthly = cursor.fetchall()

    cursor.execute("SELECT discord_id, count FROM tester_overall")
    tester_overall = cursor.fetchall()

    conn.close()

    lines = []
    if settings:
        result_room, helper_role, lang, cd_lt, cd_ht, ht_ticket_room, t_res_room = settings
        if lang: lines.append(f"lang:{lang}")
        if cd_lt and cd_lt != "0": lines.append(f"cdlt:{cd_lt}")
        if cd_ht and cd_ht != "0": lines.append(f"cdht:{cd_ht}")
        if result_room: lines.append(f"resultroom:{result_room}")
        if helper_role: lines.append(f"helperrole:{helper_role}")
        if ht_ticket_room: lines.append(f"htticketroom:{ht_ticket_room}")
        if t_res_room: lines.append(f"turnajresultroom:{t_res_room}")

    for kit in kits:
        lines.append(f"kit:{kit}")

    for kit, tier, role_id in tier_roles:
        lines.append(f"tierrole:{kit}|{tier}|{role_id}")

    for kit, channel_id in queue_rooms:
        lines.append(f"queueroom:{kit}|{channel_id}")

    for kit, category_id in kit_categories:
        lines.append(f"kitcat:{kit}|{category_id}")

    for kit, category_id in ht_ticket_categories:
        lines.append(f"htticketcat:{kit}|{category_id}")

    for d_id, ign in verified_users:
        lines.append(f"ver:{d_id}|{ign}")

    for d_id, kit, tier in player_tiers:
        lines.append(f"ptier:{d_id}|{kit}|{tier}")

    for d_id, kit, typ, until in player_cooldowns:
        lines.append(f"pcd:{d_id}|{kit}|{typ}|{until}")

    for d_id, ym, count in tester_monthly:
        lines.append(f"tmon:{d_id}|{ym}|{count}")

    for d_id, count in tester_overall:
        lines.append(f"tot:{d_id}|{count}")

    backup_text = ";;".join(lines)
    if not backup_text:
        return await interaction.response.send_message("⚠️ V databázi nejsou uložena žádná data k zálohování.", ephemeral=True)

    try:
        await interaction.user.send(f"📋 **Záloha databáze (zasetí do /database):**\n```text\n{backup_text}\n```")
        await interaction.response.send_message("✅ Kompletní záloha databáze ti byla odeslána do soukromých zpráv (DM).", ephemeral=True)
    except:
        await interaction.response.send_message(f"📋 **Záloha:**\n```text\n{backup_text}\n```", ephemeral=True)

@bot.tree.command(name="database", description="Hromadně obnoví nastavení a data ze záložního kódu.")
async def database(interaction: discord.Interaction, kod: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

    guild_id = str(interaction.guild.id)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()

    items = kod.split(";;")
    count = 0

    for item in items:
        if ":" not in item:
            continue
        key, val = item.split(":", 1)

        if key == "lang":
            cursor.execute("INSERT INTO server_settings (guild_id, language) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET language = ?", (guild_id, val, val))
            count += 1
        elif key == "cdlt":
            cursor.execute("INSERT INTO server_settings (guild_id, cooldown_lt) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET cooldown_lt = ?", (guild_id, val, val))
            count += 1
        elif key == "cdht":
            cursor.execute("INSERT INTO server_settings (guild_id, cooldown_ht) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET cooldown_ht = ?", (guild_id, val, val))
            count += 1
        elif key == "resultroom":
            cursor.execute("INSERT INTO server_settings (guild_id, result_room) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET result_room = ?", (guild_id, val, val))
            count += 1
        elif key == "helperrole":
            cursor.execute("INSERT INTO server_settings (guild_id, helper_role) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET helper_role = ?", (guild_id, val, val))
            count += 1
        elif key == "htticketroom":
            cursor.execute("INSERT INTO server_settings (guild_id, ht_ticket_room) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET ht_ticket_room = ?", (guild_id, val, val))
            count += 1
        elif key == "turnajresultroom":
            cursor.execute("INSERT INTO server_settings (guild_id, turnaj_result_room) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET turnaj_result_room = ?", (guild_id, val, val))
            count += 1
        elif key == "kit":
            cursor.execute("INSERT OR IGNORE INTO kits (name) VALUES (?)", (val.lower(),))
            count += 1
        elif key == "tierrole":
            parts = val.split("|")
            if len(parts) == 3:
                cursor.execute("INSERT OR REPLACE INTO tier_roles (kit, tier, role_id) VALUES (?, ?, ?)", (parts[0].lower(), parts[1], parts[2]))
                count += 1
        elif key == "queueroom":
            parts = val.split("|")
            if len(parts) == 2:
                cursor.execute("INSERT OR REPLACE INTO queue_rooms (kit, channel_id) VALUES (?, ?)", (parts[0].lower(), parts[1]))
                count += 1
        elif key == "kitcat":
            parts = val.split("|")
            if len(parts) == 2:
                cursor.execute("INSERT OR REPLACE INTO kit_categories (kit, category_id) VALUES (?, ?)", (parts[0].lower(), parts[1]))
                count += 1
        elif key == "htticketcat":
            parts = val.split("|")
            if len(parts) == 2:
                cursor.execute("INSERT OR REPLACE INTO ht_ticket_categories (kit, category_id) VALUES (?, ?)", (parts[0].lower(), parts[1]))
                count += 1
        elif key == "ver":
            parts = val.split("|")
            if len(parts) == 2:
                cursor.execute("INSERT OR REPLACE INTO verified (discord_id, minecraft_ign) VALUES (?, ?)", (parts[0], parts[1]))
                count += 1
        elif key == "ptier":
            parts = val.split("|")
            if len(parts) == 3:
                cursor.execute("INSERT OR REPLACE INTO player_tiers (discord_id, kit, tier) VALUES (?, ?, ?)", (parts[0], parts[1].lower(), parts[2]))
                count += 1
        elif key == "pcd":
            parts = val.split("|")
            if len(parts) == 4:
                cursor.execute("INSERT OR REPLACE INTO player_cooldowns (discord_id, kit, type, cooldown_until) VALUES (?, ?, ?, ?)", (parts[0], parts[1].lower(), parts[2], parts[3]))
                count += 1
        elif key == "tmon":
            parts = val.split("|")
            if len(parts) == 3:
                cursor.execute("INSERT OR REPLACE INTO tester_monthly (discord_id, year_month, count) VALUES (?, ?, ?)", (parts[0], parts[1], int(parts[2])))
                count += 1
        elif key == "tot":
            parts = val.split("|")
            if len(parts) == 2:
                cursor.execute("INSERT OR REPLACE INTO tester_overall (discord_id, count) VALUES (?, ?)", (parts[0], int(parts[1])))
                count += 1

    conn.commit()
    conn.close()

    await interaction.response.send_message(f"✅ Úspěšně obnoveno/nastaveno **{count}** položek z databázového kódu!", ephemeral=True)

# --- HT TICKET SYSTÉM ---
@bot.tree.command(name="hticketset", description="Nastaví místnost pro výběr HT ticketů.")
async def hticketset(interaction: discord.Interaction, roomka: discord.TextChannel):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO server_settings (guild_id, ht_ticket_room) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET ht_ticket_room = ?", (str(interaction.guild.id), str(roomka.id), str(roomka.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ HT ticket místnost nastavena na {roomka.mention}.", ephemeral=True)

@bot.tree.command(name="categorysetforhtticket", description="Nastaví kategorii pro vytvoření HT ticket místnosti pro daný kit.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def categorysetforhtticket(interaction: discord.Interaction, kit: str, kategorie: discord.CategoryChannel):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO ht_ticket_categories (kit, category_id) VALUES (?, ?)", (kit.lower(), str(kategorie.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ HT ticket kategorie pro kit **{kit}** byla nastavena na **{kategorie.name}**.", ephemeral=True)

class HTTicketKitSelect(discord.ui.Select):
    def __init__(self, kits):
        options = [discord.SelectOption(label=kit.capitalize(), value=kit) for kit in kits[:25]]
        super().__init__(placeholder="Vyber kit pro HT ticket...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        kit = self.values[0]
        user_id = str(interaction.user.id)

        conn = sqlite3.connect("tierbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT minecraft_ign FROM verified WHERE discord_id = ?", (user_id,))
        v_row = cursor.fetchone()
        if not v_row:
            conn.close()
            return await interaction.response.send_message("❌ Nejsi propojený! Použij nejprve `/verify`.", ephemeral=True)
        
        mc_ign = v_row[0]

        cursor.execute("SELECT tier FROM player_tiers WHERE discord_id = ? AND kit = ?", (user_id, kit.lower()))
        t_row = cursor.fetchone()
        
        cursor.execute("SELECT category_id FROM ht_ticket_categories WHERE kit = ?", (kit.lower(),))
        cat_row = cursor.fetchone()
        conn.close()

        current_tier = t_row[0] if t_row else "LT5"

        next_tier = "HT3"
        ct = current_tier.upper().replace("R", "")
        if "LT5" in ct: next_tier = "HT5"
        elif "HT5" in ct: next_tier = "LT4"
        elif "LT4" in ct: next_tier = "HT4"
        elif "HT4" in ct: next_tier = "LT3"
        elif "LT3" in ct: next_tier = "HT3"
        elif "HT3" in ct: next_tier = "LT2"
        elif "LT2" in ct: next_tier = "HT2"
        elif "HT2" in ct: next_tier = "LT1"
        elif "LT1" in ct: next_tier = "HT1"
        elif "HT1" in ct: next_tier = "HT1"

        channel_name = f"{mc_ign.lower()}-{next_tier.lower()}-{kit.lower()}"
        target_category = interaction.guild.get_channel(int(cat_row[0])) if cat_row and cat_row[0] else interaction.channel.category

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        
        conn = sqlite3.connect("tierbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT helper_role FROM server_settings WHERE guild_id = ?", (str(interaction.guild.id),))
        h_row = cursor.fetchone()
        conn.close()

        if h_row and h_row[0]:
            h_role = interaction.guild.get_role(int(h_row[0]))
            if h_role:
                overwrites[h_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        ticket_channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=target_category if isinstance(target_category, discord.CategoryChannel) else None,
            overwrites=overwrites
        )

        view = CloseTicketView()
        await ticket_channel.send(f"⚔️ HT Ticket otevřen pro {interaction.user.mention} na kit **{kit.capitalize()}** (Cílový tier: **{next_tier}**).\nPro uzavření ticketu použij tlačítko níže nebo `/close`.", view=view)
        await interaction.response.send_message(f"✅ Tvůj ticket byl vytvořen: {ticket_channel.mention}", ephemeral=True)

class HTTicketView(discord.ui.View):
    def __init__(self, kits):
        super().__init__(timeout=None)
        self.add_item(HTTicketKitSelect(kits))

@bot.tree.command(name="hticketsend", description="Ošle do nastavené místnosti zprávu pro vytvoření HT ticketu.")
async def hticketsend(interaction: discord.Interaction):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT ht_ticket_room FROM server_settings WHERE guild_id = ?", (str(interaction.guild.id),))
    row = cursor.fetchone()
    cursor.execute("SELECT name FROM kits")
    kits = [r[0] for r in cursor.fetchall()]
    conn.close()

    if not row or not row[0]:
        return await interaction.response.send_message("❌ Není nastavená místnost pro HT tickety! Použij `/hticketset`.", ephemeral=True)
    if not kits:
        return await interaction.response.send_message("❌ V databázi nejsou žádné kity!", ephemeral=True)

    target_channel = interaction.guild.get_channel(int(row[0]))
    if not target_channel:
        return await interaction.response.send_message("❌ Nastavený kanál nebyl nalezen.", ephemeral=True)

    embed = discord.Embed(
        title="⚔️ HT Tier Test Tickets",
        description="Zde můžeš požádat o test na **HT3+** kity.\n\n⚠️ **Pravidla:**\n- Netroluj tikety.\n- Vyber níže správný kit a systém ti automaticky založí místnost pro tvůj další vyšší tier.\n- Buď trpělivý.",
        color=discord.Color.gold()
    )
    
    view = HTTicketView(kits)
    await target_channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Zpráva pro vytváření HT ticketů byla úspěšně odeslána do vybrané místnosti.", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zavřít ticket 🔒", style=discord.ButtonStyle.danger, custom_id="close_ht_ticket")
    async def close_ticket_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await has_helper_perms(interaction):
            return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
        
        conn = sqlite3.connect("tierbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT cooldown_ht FROM server_settings WHERE guild_id = ?", (str(interaction.guild.id),))
        s_row = cursor.fetchone()

        parts = interaction.channel.name.split("-")
        if len(parts) >= 3:
            ign = parts[0]
            kit = parts[-1]
            cursor.execute("SELECT discord_id FROM verified WHERE minecraft_ign = ?", (ign,))
            u_row = cursor.fetchone()
            if u_row:
                discord_id = u_row[0]
                cd_setting = s_row[0] if s_row and s_row[0] else "0"
                days, hours = parse_cooldown(cd_setting)
                
                if days > 0 or hours > 0:
                    expiry = datetime.datetime.now() + datetime.timedelta(days=days, hours=hours)
                    cursor.execute("INSERT OR REPLACE INTO player_cooldowns (discord_id, kit, type, cooldown_until) VALUES (?, ?, ?, ?)", (discord_id, kit.lower(), "ht", expiry.isoformat()))
                    conn.commit()
        conn.close()

        await interaction.response.send_message("🔒 Ticket bude za chvíli smazán...", ephemeral=True)
        await asyncio.sleep(3)
        try:
            await interaction.channel.delete()
        except:
            pass

@bot.tree.command(name="close", description="Zavře aktuální ticket místnost.")
async def close(interaction: discord.Interaction):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT cooldown_ht FROM server_settings WHERE guild_id = ?", (str(interaction.guild.id),))
    s_row = cursor.fetchone()

    parts = interaction.channel.name.split("-")
    if len(parts) >= 3:
        ign = parts[0]
        kit = parts[-1]
        cursor.execute("SELECT discord_id FROM verified WHERE minecraft_ign = ?", (ign,))
        u_row = cursor.fetchone()
        if u_row:
            discord_id = u_row[0]
            cd_setting = s_row[0] if s_row and s_row[0] else "0"
            days, hours = parse_cooldown(cd_setting)
            
            if days > 0 or hours > 0:
                expiry = datetime.datetime.now() + datetime.timedelta(days=days, hours=hours)
                cursor.execute("INSERT OR REPLACE INTO player_cooldowns (discord_id, kit, type, cooldown_until) VALUES (?, ?, ?, ?)", (discord_id, kit.lower(), "ht", expiry.isoformat()))
                conn.commit()
    conn.close()

    await interaction.response.send_message("🔒 Ticket bude za chvíli smazán...", ephemeral=True)
    await asyncio.sleep(3)
    try:
        await interaction.channel.delete()
    except:
        pass

@bot.tree.command(name="add", description="Přidá uživateli přístup do aktuálního ticketu.")
async def add(interaction: discord.Interaction, user: discord.Member):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    
    try:
        await interaction.channel.set_permissions(user, view_channel=True, send_messages=True, read_message_history=True)
        await interaction.response.send_message(f"✅ Uživatel {user.mention} byl přidán do ticketu.", ephemeral=False)
    except Exception as e:
        await interaction.response.send_message(f"❌ Nepodařilo se přidat uživatele: {e}", ephemeral=True)

@bot.tree.command(name="remove", description="Odebere uživateli přístup z aktuálního ticketu.")
async def remove(interaction: discord.Interaction, user: discord.Member):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    
    try:
        await interaction.channel.set_permissions(user, overwrite=None)
        await interaction.response.send_message(f"✅ Uživateli {user.mention} byl odebrán přístup z ticketu.", ephemeral=False)
    except Exception as e:
        await interaction.response.send_message(f"❌ Nepodařilo se odebrat uživatele: {e}", ephemeral=True)

# --- TESTER LEADERBOARD ---
@bot.tree.command(name="testerleaderboard", description="Zobrazí žebříček testerů.")
@discord.app_commands.choices(obdobi=[
    discord.app_commands.Choice(name="Tento měsíc", value="tentomesic"),
    discord.app_commands.Choice(name="Minulý měsíc", value="minulymesic"),
    discord.app_commands.Choice(name="Celkově", value="celkove")
])
async def testerleaderboard(interaction: discord.Interaction, obdobi: str):
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    
    now = datetime.datetime.now()
    if obdobi == "tentomesic":
        target_month = now.strftime("%Y-%m")
        title = "🏆 TOP testeři tento měsíc"
        cursor.execute("SELECT discord_id, count FROM tester_monthly WHERE year_month = ? ORDER BY count DESC LIMIT 10", (target_month,))
    elif obdobi == "minulymesic":
        first_day = now.replace(day=1)
        last_month_dt = first_day - datetime.timedelta(days=1)
        target_month = last_month_dt.strftime("%Y-%m")
        title = "🏆 TOP testeři minulý měsíc"
        cursor.execute("SELECT discord_id, count FROM tester_monthly WHERE year_month = ? ORDER BY count DESC LIMIT 10", (target_month,))
    else:
        title = "🏆 TOP testeři celkově"
        cursor.execute("SELECT discord_id, count FROM tester_overall ORDER BY count DESC LIMIT 10")
        
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return await interaction.response.send_message("✨ Žádné záznamy v leaderboardu.", ephemeral=True)
        
    desc_lines = []
    for i, (d_id, count) in enumerate(rows, 1):
        desc_lines.append(f"{i}. <@{d_id}>: {count} testů")
        
    embed = discord.Embed(
        title=title,
        description="\n".join(desc_lines),
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- OSTATNÍ PŘÍKAZY ---
@bot.tree.command(name="language", description="Změní jazyk bota pro tento server.")
@discord.app_commands.choices(jazyk=[
    discord.app_commands.Choice(name="🇨🇿 Čeština", value="cs"),
    discord.app_commands.Choice(name="🇬🇧 English (British)", value="en-gb"),
    discord.app_commands.Choice(name="🇺🇸 English (American)", value="en-us"),
    discord.app_commands.Choice(name="🇸🇰 Slovenčina", value="sk"),
    discord.app_commands.Choice(name="🇩🇪 Deutsch", value="de"),
    discord.app_commands.Choice(name="🇫🇷 Français", value="fr"),
    discord.app_commands.Choice(name="🇷🇺 Русский", value="ru"),
    discord.app_commands.Choice(name="🇮🇹 Italiano", value="it"),
    discord.app_commands.Choice(name="🇪🇸 Español", value="es")
])
async def language(interaction: discord.Interaction, jazyk: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO server_settings (guild_id, language) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET language = ?", (str(interaction.guild.id), jazyk, jazyk))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "lang_set"), ephemeral=True)

@bot.tree.command(name="cooldownset", description="Nastaví globální cooldown pro LT nebo HT tiery.")
@discord.app_commands.choices(typ=[discord.app_commands.Choice(name="LT", value="lt"), discord.app_commands.Choice(name="HT", value="ht")])
async def cooldownset(interaction: discord.Interaction, typ: str, cas: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    column = "cooldown_lt" if typ == "lt" else "cooldown_ht"
    cursor.execute(f"INSERT INTO server_settings (guild_id, {column}) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET {column} = ?", (str(interaction.guild.id), cas, cas))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "cooldown_set", tipo=typ.upper(), time=cas), ephemeral=True)

@bot.tree.command(name="removecooldown", description="Odstraní cooldown hráči podle výběru.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
@discord.app_commands.choices(typ=[discord.app_commands.Choice(name="LT", value="lt"), discord.app_commands.Choice(name="HT", value="ht")])
async def removecooldown(interaction: discord.Interaction, kit: str, discord_hrac: discord.Member, typ: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM player_cooldowns WHERE discord_id = ? AND kit = ? AND type = ?", (str(discord_hrac.id), kit.lower(), typ.lower()))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "cooldown_removed", tipo=typ.upper(), kit=kit, player=discord_hrac.mention), ephemeral=True)

@bot.tree.command(name="cooldown", description="Zobrazí všechny aktivní cooldowny daného hráče.")
async def cooldown(interaction: discord.Interaction, player: discord.Member):
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT kit, type, cooldown_until FROM player_cooldowns WHERE discord_id = ?", (str(player.id),))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return await interaction.response.send_message(f"✨ Uživatel {player.mention} nemá žádné aktivní cooldowny.", ephemeral=True)
        
    lt_lines = []
    ht_lines = []
    now = datetime.datetime.now()
    
    for kit, typ, until_str in rows:
        try:
            dt = datetime.datetime.fromisoformat(until_str)
            if now < dt:
                time_left = dt.strftime('%d.%m.%Y %H:%M')
                line = f"**{kit.capitalize()}:** {time_left}"
                if typ.lower() == "lt":
                    lt_lines.append(line)
                else:
                    ht_lines.append(line)
        except:
            pass
            
    desc_parts = []
    if lt_lines:
        desc_parts.append("__**LT Cooldowny**__")
        desc_parts.extend(lt_lines)
    if ht_lines:
        if desc_parts: desc_parts.append("")
        desc_parts.append("__**HT Cooldowny**__")
        desc_parts.extend(ht_lines)
        
    if not desc_parts:
        return await interaction.response.send_message(f"✨ Uživatel {player.mention} nemá žádné aktivní cooldowny.", ephemeral=True)
        
    embed = discord.Embed(
        title=f"⏳ Cooldowny pro hráče {player.display_name}",
        description="\n".join(desc_parts),
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="verify", description="Propojí tvůj Discord účet s Minecraft IGN.")
async def verify(interaction: discord.Interaction, minecraft_ign: str):
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO verified (discord_id, minecraft_ign) VALUES (?, ?)", (str(interaction.user.id), minecraft_ign))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "verified_success", ign=minecraft_ign), ephemeral=True)

@bot.tree.command(name="createkit", description="Přidá nový kit do databáze.")
async def createkit(interaction: discord.Interaction, jmeno_kitu: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO kits (name) VALUES (?)", (jmeno_kitu.lower(),))
        conn.commit()
        await interaction.response.send_message(get_msg(interaction.guild.id, "kit_created", kit=jmeno_kitu), ephemeral=True)
    except sqlite3.IntegrityError:
        await interaction.response.send_message(get_msg(interaction.guild.id, "kit_exists", kit=jmeno_kitu), ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(name="removekit", description="Odstraní kit z databáze.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def removekit(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kits WHERE name = ?", (kit.lower(),))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "kit_removed", kit=kit), ephemeral=True)

@bot.tree.command(name="tieroleset", description="Nastaví roli pro daný kit a tier.")
@discord.app_commands.autocomplete(kit=kit_autocomplete, tier=tier_autocomplete)
async def tieroleset(interaction: discord.Interaction, kit: str, tier: str, role: discord.Role):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO tier_roles (kit, tier, role_id) VALUES (?, ?, ?)", (kit.lower(), tier, str(role.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "tier_role_set", kit=kit, tier=tier, role=role.name), ephemeral=True)

@bot.tree.command(name="resultroomset", description="Nastaví místnost pro posílání výsledků.")
async def resultroomset(interaction: discord.Interaction, discord_roomka: discord.TextChannel):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO server_settings (guild_id, result_room) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET result_room = ?", (str(interaction.guild.id), str(discord_roomka.id), str(discord_roomka.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "result_room_set", room=discord_roomka.mention), ephemeral=True)

@bot.tree.command(name="helperoleset", description="Nastaví roli pro používání bota.")
async def helperoleset(interaction: discord.Interaction, role: discord.Role):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO server_settings (guild_id, helper_role) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET helper_role = ?", (str(interaction.guild.id), str(role.id), str(role.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "helper_role_set", role=role.mention), ephemeral=True)

@bot.tree.command(name="queueroomset", description="Nastaví textový kanál pro frontu daného kitu.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def queueroomset(interaction: discord.Interaction, discord_roomka: discord.TextChannel, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO queue_rooms (kit, channel_id) VALUES (?, ?)", (kit.lower(), str(discord_roomka.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "queue_room_set", kit=kit, room=discord_roomka.mention), ephemeral=True)

@bot.tree.command(name="kitcategoryset", description="Nastaví kategorii pro vygenerování testovací místnosti.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def kitcategoryset(interaction: discord.Interaction, kit: str, kategorie: discord.CategoryChannel):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO kit_categories (kit, category_id) VALUES (?, ?)", (kit.lower(), str(kategorie.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "kit_cat_set", kit=kit, cat=kategorie.name), ephemeral=True)

QUEUES = {}

class QueueView(discord.ui.View):
    def __init__(self, kit_name: str, guild_id: int):
        super().__init__(timeout=None)
        self.kit_name = kit_name
        self.guild_id = guild_id
        self.children[0].label = get_msg(guild_id, "join_btn")
        self.children[1].label = get_msg(guild_id, "leave_btn")
        self.children[2].label = get_msg(guild_id, "pull_btn")

    @discord.ui.button(style=discord.ButtonStyle.primary, custom_id="join_queue")
    async def join_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = sqlite3.connect("tierbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT minecraft_ign FROM verified WHERE discord_id = ?", (str(interaction.user.id),))
        row = cursor.fetchone()
        cursor.execute("SELECT cooldown_until FROM player_cooldowns WHERE discord_id = ? AND kit = ?", (str(interaction.user.id), self.kit_name.lower()))
        cd_row = cursor.fetchone()
        conn.close()

        if cd_row and cd_row[0]:
            try:
                cd_time = datetime.datetime.fromisoformat(cd_row[0])
                if datetime.datetime.now() < cd_time:
                    return await interaction.response.send_message(f"⏳ Cooldown aktivní do **{cd_time.strftime('%d.%m.%Y %H:%M')}**!", ephemeral=True)
            except:
                pass

        if not row:
            return await interaction.response.send_message(get_msg(interaction.guild.id, "not_verified"), ephemeral=True)

        if self.kit_name not in QUEUES:
            QUEUES[self.kit_name] = {"players": [], "testers": []}

        if interaction.user.id in QUEUES[self.kit_name]["players"]:
            return await interaction.response.send_message(get_msg(interaction.guild.id, "already_in_queue"), ephemeral=True)

        QUEUES[self.kit_name]["players"].append(interaction.user.id)
        await interaction.response.send_message("✅", ephemeral=True)
        await update_queue_message(interaction.channel, self.kit_name, interaction.guild.id)

    @discord.ui.button(style=discord.ButtonStyle.danger, custom_id="leave_queue")
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.kit_name in QUEUES and interaction.user.id in QUEUES[self.kit_name]["players"]:
            QUEUES[self.kit_name]["players"].remove(interaction.user.id)
            await interaction.response.send_message(get_msg(interaction.guild.id, "left_queue"), ephemeral=True)
            await update_queue_message(interaction.channel, self.kit_name, interaction.guild.id)
        else:
            await interaction.response.send_message(get_msg(interaction.guild.id, "not_in_queue"), ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.success, custom_id="pull_player")
    async def pull_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await has_helper_perms(interaction):
            return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

        if self.kit_name not in QUEUES or not QUEUES[self.kit_name]["players"]:
            return await interaction.response.send_message(get_msg(interaction.guild.id, "queue_empty"), ephemeral=True)

        conn = sqlite3.connect("tierbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT category_id FROM kit_categories WHERE kit = ?", (self.kit_name.lower(),))
        cat_row = cursor.fetchone()
        
        player_id = QUEUES[self.kit_name]["players"][0]
        cursor.execute("SELECT minecraft_ign FROM verified WHERE discord_id = ?", (str(player_id),))
        ign_row = cursor.fetchone()
        conn.close()

        player = interaction.guild.get_member(player_id)
        if not player:
            QUEUES[self.kit_name]["players"].pop(0)
            return await interaction.response.send_message("⚠️ Hráč již není na serveru.", ephemeral=True)

        mc_ign = ign_row[0] if ign_row else player.name
        target_category = interaction.guild.get_channel(int(cat_row[0])) if cat_row and cat_row[0] else None

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            player: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        test_channel = await interaction.guild.create_text_channel(
            name=f"{mc_ign.lower()}-test",
            category=target_category if isinstance(target_category, discord.CategoryChannel) else interaction.channel.category,
            overwrites=overwrites
        )

        QUEUES[self.kit_name]["players"].pop(0)
        if interaction.user.id not in QUEUES[self.kit_name]["testers"]:
            QUEUES[self.kit_name]["testers"].append(interaction.user.id)

        await update_queue_message(interaction.channel, self.kit_name, interaction.guild.id)
        await test_channel.send(get_msg(interaction.guild.id, "test_started", tester=interaction.user.mention, player=player.mention))
        await interaction.response.send_message(get_msg(interaction.guild.id, "player_pulled", player=player.mention, room=test_channel.mention), ephemeral=True)

def get_queue_embed(kit_name: str, guild_id: int):
    data = QUEUES.get(kit_name, {"players": [], "testers": []})
    players_list = data["players"]
    testers_list = data["testers"]

    players_str = "\n".join([f"{i+1}. <@{pid}>" for i, pid in enumerate(players_list)]) if players_list else get_msg(guild_id, "queue_empty")
    testers_str = "\n".join([f"{i+1}. <@{tid}>" for i, tid in enumerate(testers_list)]) if testers_list else get_msg(guild_id, "no_testers")

    embed = discord.Embed(
        title=get_msg(guild_id, "queue_title", kit=kit_name.capitalize()),
        description=f"{get_msg(guild_id, 'queue_desc')}\n\n**Fronta:**\n{players_str}\n\n**{get_msg(guild_id, 'active_testers')}:**\n{testers_str}",
        color=discord.Color.blue()
    )
    return embed

async def update_queue_message(channel, kit_name, guild_id):
    embed = get_queue_embed(kit_name, guild_id)
    async for message in channel.history(limit=10):
        if message.author == bot.user and message.embeds:
            await message.edit(embed=embed, view=QueueView(kit_name, guild_id))
            return
    await channel.send(embed=embed, view=QueueView(kit_name, guild_id))

@bot.tree.command(name="openqueue", description="Otevře queue pro daný kit.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def openqueue(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id FROM queue_rooms WHERE kit = ?", (kit.lower(),))
    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        return await interaction.response.send_message(f"❌ Pro kit **{kit}** není nastavena queue místnost!", ephemeral=True)

    target_channel = interaction.guild.get_channel(int(row[0]))
    if not target_channel:
        return await interaction.response.send_message("❌ Kanál nebyl nalezen.", ephemeral=True)

    try:
        async for message in target_channel.history(limit=50):
            if message.author == bot.user:
                await message.delete()
    except Exception as e:
        print(f"Nelze smazat staré zprávy: {e}")

    QUEUES[kit.lower()] = {"players": [], "testers": []}
    embed = get_queue_embed(kit.lower(), interaction.guild.id)
    
    await target_channel.send(content="@everyone", embed=embed, view=QueueView(kit.lower(), interaction.guild.id))
    await interaction.response.send_message(get_msg(interaction.guild.id, "queue_opened", kit=kit, room=target_channel.mention), ephemeral=True)

@bot.tree.command(name="closequeue", description="Zavře frontu pro daný kit.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def closequeue(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

    kit_key = kit.lower()
    if kit_key in QUEUES and QUEUES[kit_key]["testers"]:
        return await interaction.response.send_message(get_msg(interaction.guild.id, "cannot_close_active"), ephemeral=True)

    QUEUES.pop(kit_key, None)

    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id FROM queue_rooms WHERE kit = ?", (kit_key,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0]:
        target_channel = interaction.guild.get_channel(int(row[0]))
        if target_channel:
            closed_embed = discord.Embed(
                title=get_msg(interaction.guild.id, "closed_title", kit=kit.capitalize()),
                description=get_msg(interaction.guild.id, "closed_desc"),
                color=discord.Color.red()
            )
            closed_embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
            
            async for message in target_channel.history(limit=10):
                if message.author == bot.user and message.embeds:
                    await message.edit(embed=closed_embed, view=None)
                    break

    await interaction.response.send_message(get_msg(interaction.guild.id, "queue_closed", kit=kit), ephemeral=True)

@bot.tree.command(name="joinqueueastester", description="Připojí tě jako testera do fronty.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def joinqueueastester(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

    kit_key = kit.lower()
    if kit_key not in QUEUES:
        QUEUES[kit_key] = {"players": [], "testers": []}

    if interaction.user.id in QUEUES[kit_key]["testers"]:
        return await interaction.response.send_message(get_msg(interaction.guild.id, "already_tester"), ephemeral=True)

    QUEUES[kit_key]["testers"].append(interaction.user.id)
    await interaction.response.send_message(get_msg(interaction.guild.id, "tester_joined", kit=kit), ephemeral=True)
    
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id FROM queue_rooms WHERE kit = ?", (kit_key,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        ch = interaction.guild.get_channel(int(row[0]))
        if ch:
            await update_queue_message(ch, kit_key, interaction.guild.id)

@bot.tree.command(name="leavequeueastester", description="Odebere tě ze seznamu testerů.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def leavequeueastester(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

    kit_key = kit.lower()
    if kit_key in QUEUES and interaction.user.id in QUEUES[kit_key]["testers"]:
        QUEUES[kit_key]["testers"].remove(interaction.user.id)
        await interaction.response.send_message(get_msg(interaction.guild.id, "tester_left", kit=kit), ephemeral=True)
        
        conn = sqlite3.connect("tierbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT channel_id FROM queue_rooms WHERE kit = ?", (kit_key,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            ch = interaction.guild.get_channel(int(row[0]))
            if ch:
                await update_queue_message(ch, kit_key, interaction.guild.id)
    else:
        await interaction.response.send_message(get_msg(interaction.guild.id, "not_tester"), ephemeral=True)

@bot.tree.command(name="result", description="Odešle výsledek testu do result místnosti.")
@discord.app_commands.autocomplete(kit=kit_autocomplete, tier=tier_autocomplete)
async def result(interaction: discord.Interaction, discord_hrac: discord.Member, kit: str, tier: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT minecraft_ign FROM verified WHERE discord_id = ?", (str(discord_hrac.id),))
    row = cursor.fetchone()

    cursor.execute("SELECT tier FROM player_tiers WHERE discord_id = ? AND kit = ?", (str(discord_hrac.id), kit.lower()))
    prev_row = cursor.fetchone()
    prev_tier = prev_row[0] if prev_row else "N/A"

    t_clean = tier.upper().replace("R", "")
    cursor.execute("INSERT OR REPLACE INTO player_tiers (discord_id, kit, tier) VALUES (?, ?, ?)", (str(discord_hrac.id), kit.lower(), t_clean))
    cursor.execute("SELECT role_id FROM tier_roles WHERE kit = ? AND tier = ?", (kit.lower(), t_clean))
    role_row = cursor.fetchone()

    cursor.execute("SELECT result_room, cooldown_lt, cooldown_ht FROM server_settings WHERE guild_id = ?", (str(interaction.guild.id),))
    settings_row = cursor.fetchone()

    is_lt = t_clean.startswith("LT")
    cd_setting = (settings_row[1] if is_lt else settings_row[2]) if settings_row else "0"

    days, hours = parse_cooldown(cd_setting)

    if days > 0 or hours > 0:
        expiry = datetime.datetime.now() + datetime.timedelta(days=days, hours=hours)
        cd_type = "lt" if is_lt else "ht"
        cursor.execute("INSERT OR REPLACE INTO player_cooldowns (discord_id, kit, type, cooldown_until) VALUES (?, ?, ?, ?)", (str(discord_hrac.id), kit.lower(), cd_type, expiry.isoformat()))

    tester_id = str(interaction.user.id)
    current_month = datetime.datetime.now().strftime("%Y-%m")
    cursor.execute("INSERT INTO tester_monthly (discord_id, year_month, count) VALUES (?, ?, 1) ON CONFLICT(discord_id, year_month) DO UPDATE SET count = count + 1", (tester_id, current_month))
    cursor.execute("INSERT INTO tester_overall (discord_id, count) VALUES (?, 1) ON CONFLICT(discord_id) DO UPDATE SET count = count + 1", (tester_id,))

    conn.commit()
    conn.close()

    mc_ign = row[0] if row else "Neznámý"

    if role_row and role_row[0]:
        role = interaction.guild.get_role(int(role_row[0]))
        if role:
            try:
                await discord_hrac.add_roles(role)
            except Exception:
                pass

    dnes = datetime.datetime.now().strftime("%d.%m.%Y")

    embed = discord.Embed(
        title=get_msg(interaction.guild.id, "result_title", kit=kit),
        description=get_msg(interaction.guild.id, "result_desc", kit=kit),
        color=discord.Color.green()
    )
    embed.add_field(name="👤 Hráč (Discord)", value=discord_hrac.mention, inline=True)
    embed.add_field(name="🎮 Minecraft IGN", value=mc_ign, inline=True)
    embed.add_field(name="⚔️ Tester", value=interaction.user.mention, inline=True)
    embed.add_field(name="📉 Předchozí tier", value=prev_tier, inline=True)
    embed.add_field(name="📈 Nový tier", value=t_clean, inline=True)
    embed.set_footer(text=dnes)

    if mc_ign != "Neznámý":
        skin_url = f"https://visage.surgeplay.com/bust/512/{mc_ign}"
        embed.set_thumbnail(url=skin_url)

    if settings_row and settings_row[0]:
        room_id = int(settings_row[0])
        room = interaction.guild.get_channel(room_id)
        if room:
            await room.send(content=f"📢 **Nový výsledek pro {kit}!** | Hráč: {discord_hrac.mention} | Tester: {interaction.user.mention}", embed=embed)

    await interaction.response.send_message(get_msg(interaction.guild.id, "result_sent"), ephemeral=True)
    await asyncio.sleep(3)
    try:
        await interaction.channel.delete()
    except Exception as e:
        print(f"Nelze smazat místnost: {e}")

# Webový server pro Keep-Alive
async def handle_ping(request):
    return web.Response(text="Bot runs 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

TOKEN = os.getenv("DISCORD_TOKEN")

async def main():
    async with bot:
        await start_web_server()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
