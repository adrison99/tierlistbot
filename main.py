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
            cooldown_ht TEXT DEFAULT '0'
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS queue_rooms (kit TEXT PRIMARY KEY, channel_id TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS kit_categories (kit TEXT PRIMARY KEY, category_id TEXT)")
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
    conn.commit()
    conn.close()

init_db()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

VALID_TIERS = ["LT5", "HT5", "LT4", "HT4", "LT3", "HT3", "RLT2", "LT2", "RHT2", "HT2", "RLT1", "LT1", "RHT1", "HT1"]
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

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} je online!")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synchrováno {len(synced)} slash příkazů.")
    except Exception as e:
        print(f"❌ Chyba synchronizace: {e}")

# --- PŘÍKAZY PRO ZÁLOHU A OBNOVU DATABÁZE ---
@bot.tree.command(name="databaseinfo", description="Vygeneruje textový kód pro zálohu nastavení serveru.")
async def databaseinfo(interaction: discord.Interaction):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

    guild_id = str(interaction.guild.id)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()

    cursor.execute("SELECT result_room, helper_role, language, cooldown_lt, cooldown_ht FROM server_settings WHERE guild_id = ?", (guild_id,))
    settings = cursor.fetchone()

    cursor.execute("SELECT name FROM kits")
    kits = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT kit, tier, role_id FROM tier_roles")
    tier_roles = cursor.fetchall()

    cursor.execute("SELECT kit, channel_id FROM queue_rooms")
    queue_rooms = cursor.fetchall()

    cursor.execute("SELECT kit, category_id FROM kit_categories")
    kit_categories = cursor.fetchall()

    conn.close()

    lines = []
    if settings:
        result_room, helper_role, lang, cd_lt, cd_ht = settings
        if lang: lines.append(f"lang:{lang}")
        if cd_lt and cd_lt != "0": lines.append(f"cdlt:{cd_lt}")
        if cd_ht and cd_ht != "0": lines.append(f"cdht:{cd_ht}")
        if result_room: lines.append(f"resultroom:{result_room}")
        if helper_role: lines.append(f"helperrole:{helper_role}")

    for kit in kits:
        lines.append(f"kit:{kit}")

    for kit, tier, role_id in tier_roles:
        lines.append(f"tierrole:{kit}|{tier}|{role_id}")

    for kit, channel_id in queue_rooms:
        lines.append(f"queueroom:{kit}|{channel_id}")

    for kit, category_id in kit_categories:
        lines.append(f"kitcat:{kit}|{category_id}")

    backup_text = ";;".join(lines)
    if not backup_text:
        return await interaction.response.send_message("⚠️ V databázi nejsou uložena žádná nastavení k zálohování.", ephemeral=True)

    try:
        await interaction.user.send(f"📋 **Záloha databáze (zasetí do /database):**\n```text\n{backup_text}\n```")
        await interaction.response.send_message("✅ Záloha databáze ti byla odeslána do soukromých zpráv (DM).", ephemeral=True)
    except:
        await interaction.response.send_message(f"📋 **Záloha:**\n```text\n{backup_text}\n```", ephemeral=True)

@bot.tree.command(name="database", description="Hromadně obnoví nastavení serveru ze záložního kódu.")
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

    conn.commit()
    conn.close()

    await interaction.response.send_message(f"✅ Úspěšně obnoveno/nastaveno **{count}** položek z databázového kódu!", ephemeral=True)

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
    embed = discord.Embed(title=f"⏳ Cooldowny pro hráče {player.display_name}", color=discord.Color.orange())
    for kit, typ, until_str in rows:
        try:
            dt = datetime.datetime.fromisoformat(until_str)
            if datetime.datetime.now() < dt:
                embed.add_field(name=f"Kit: {kit.capitalize()} ({typ.upper()})", value=f"Do: {dt.strftime('%d.%m.%Y %H:%M')}", inline=False)
        except:
            pass
    if not embed.fields:
        return await interaction.response.send_message(f"✨ Uživatel {player.mention} nemá žádné aktivní cooldowny.", ephemeral=True)
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

    # Vymazání všech předchozích zpráv od bota v kanálu (smaže staré zavřené/otevřené fronty)
    try:
        async for message in target_channel.history(limit=50):
            if message.author == bot.user:
                await message.delete()
    except Exception as e:
        print(f"Nelzemazat staré zprávy: {e}")

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
    
    # Aktualizace zprávy, aby se hned ukázal tester
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

    cursor.execute("INSERT OR REPLACE INTO player_tiers (discord_id, kit, tier) VALUES (?, ?, ?)", (str(discord_hrac.id), kit.lower(), tier))
    cursor.execute("SELECT role_id FROM tier_roles WHERE kit = ? AND tier = ?", (kit.lower(), tier))
    role_row = cursor.fetchone()

    cursor.execute("SELECT result_room, cooldown_lt, cooldown_ht FROM server_settings WHERE guild_id = ?", (str(interaction.guild.id),))
    settings_row = cursor.fetchone()

    is_lt = tier.startswith("LT") or tier.startswith("RLT")
    cd_setting = (settings_row[1] if is_lt else settings_row[2]) if settings_row else "0"

    delta_days = 0
    delta_hours = 0
    if cd_setting.endswith("d"):
        try: delta_days = int(cd_setting[:-1])
        except: pass
    elif cd_setting.endswith("h"):
        try: delta_hours = int(cd_setting[:-1])
        except: pass

    if delta_days > 0 or delta_hours > 0:
        expiry = datetime.datetime.now() + datetime.timedelta(days=delta_days, hours=delta_hours)
        cd_type = "lt" if is_lt else "ht"
        cursor.execute("INSERT OR REPLACE INTO player_cooldowns (discord_id, kit, type, cooldown_until) VALUES (?, ?, ?, ?)", (str(discord_hrac.id), kit.lower(), cd_type, expiry.isoformat()))

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
    embed.add_field(name="📈 Nový tier", value=tier, inline=True)
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
