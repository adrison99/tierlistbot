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
            cooldown_ht TEXT DEFAULT '0',
            ht_ticket_room TEXT
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
    print(f"✅ Bot {bot.user} je online!")[cite: 3]
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synchrováno {len(synced)} slash příkazů.")[cite: 3]
    except Exception as e:
        print(f"❌ Chyba synchronizace: {e}")[cite: 3]

# --- DATABÁZE A KOMPLETNÍ ZÁLOHA/OBNOVA ---
@bot.tree.command(name="databaseinfo", description="Vygeneruje textový kód pro zálohu nastavení a dat hráčů.")
async def databaseinfo(interaction: discord.Interaction):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]

    guild_id = str(interaction.guild.id)[cite: 3]
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]

    cursor.execute("SELECT result_room, helper_role, language, cooldown_lt, cooldown_ht, ht_ticket_room FROM server_settings WHERE guild_id = ?", (guild_id,))[cite: 3]
    settings = cursor.fetchone()[cite: 3]

    cursor.execute("SELECT name FROM kits")[cite: 3]
    kits = [row[0] for row in cursor.fetchall()][cite: 3]

    cursor.execute("SELECT kit, tier, role_id FROM tier_roles")[cite: 3]
    tier_roles = cursor.fetchall()[cite: 3]

    cursor.execute("SELECT kit, channel_id FROM queue_rooms")[cite: 3]
    queue_rooms = cursor.fetchall()[cite: 3]

    cursor.execute("SELECT kit, category_id FROM kit_categories")[cite: 3]
    kit_categories = cursor.fetchall()[cite: 3]

    cursor.execute("SELECT kit, category_id FROM ht_ticket_categories")
    ht_ticket_categories = cursor.fetchall()

    cursor.execute("SELECT discord_id, minecraft_ign FROM verified")
    verified_users = cursor.fetchall()

    cursor.execute("SELECT discord_id, kit, tier FROM player_tiers")
    player_tiers = cursor.fetchall()

    cursor.execute("SELECT discord_id, kit, type, cooldown_until FROM player_cooldowns")
    player_cooldowns = cursor.fetchall()

    conn.close()[cite: 3]

    lines = [][cite: 3]
    if settings:
        result_room, helper_role, lang, cd_lt, cd_ht, ht_ticket_room = settings
        if lang: lines.append(f"lang:{lang}")[cite: 3]
        if cd_lt and cd_lt != "0": lines.append(f"cdlt:{cd_lt}")[cite: 3]
        if cd_ht and cd_ht != "0": lines.append(f"cdht:{cd_ht}")[cite: 3]
        if result_room: lines.append(f"resultroom:{result_room}")[cite: 3]
        if helper_role: lines.append(f"helperrole:{helper_role}")[cite: 3]
        if ht_ticket_room: lines.append(f"htticketroom:{ht_ticket_room}")

    for kit in kits:
        lines.append(f"kit:{kit}")[cite: 3]

    for kit, tier, role_id in tier_roles:
        lines.append(f"tierrole:{kit}|{tier}|{role_id}")[cite: 3]

    for kit, channel_id in queue_rooms:
        lines.append(f"queueroom:{kit}|{channel_id}")[cite: 3]

    for kit, category_id in kit_categories:
        lines.append(f"kitcat:{kit}|{category_id}")[cite: 3]

    for kit, category_id in ht_ticket_categories:
        lines.append(f"htticketcat:{kit}|{category_id}")

    for d_id, ign in verified_users:
        lines.append(f"ver:{d_id}|{ign}")

    for d_id, kit, tier in player_tiers:
        lines.append(f"ptier:{d_id}|{kit}|{tier}")

    for d_id, kit, typ, until in player_cooldowns:
        lines.append(f"pcd:{d_id}|{kit}|{typ}|{until}")

    backup_text = ";;".join(lines)[cite: 3]
    if not backup_text:
        return await interaction.response.send_message("⚠️ V databázi nejsou uložena žádná data k zálohování.", ephemeral=True)[cite: 3]

    try:
        await interaction.user.send(f"📋 **Záloha databáze (zasetí do /database):**\n```text\n{backup_text}\n```")[cite: 3]
        await interaction.response.send_message("✅ Kompletní záloha databáze (včetně hráčů) ti byla odeslána do soukromých zpráv (DM).", ephemeral=True)[cite: 3]
    except:
        await interaction.response.send_message(f"📋 **Záloha:**\n```text\n{backup_text}\n```", ephemeral=True)[cite: 3]

@bot.tree.command(name="database", description="Hromadně obnoví nastavení a data hráčů ze záložního kódu.")
async def database(interaction: discord.Interaction, kod: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]

    guild_id = str(interaction.guild.id)[cite: 3]
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]

    items = kod.split(";;")[cite: 3]
    count = 0[cite: 3]

    for item in items:
        if ":" not in item:
            continue[cite: 3]
        key, val = item.split(":", 1)[cite: 3]

        if key == "lang":
            cursor.execute("INSERT INTO server_settings (guild_id, language) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET language = ?", (guild_id, val, val))[cite: 3]
            count += 1[cite: 3]
        elif key == "cdlt":
            cursor.execute("INSERT INTO server_settings (guild_id, cooldown_lt) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET cooldown_lt = ?", (guild_id, val, val))[cite: 3]
            count += 1[cite: 3]
        elif key == "cdht":
            cursor.execute("INSERT INTO server_settings (guild_id, cooldown_ht) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET cooldown_ht = ?", (guild_id, val, val))[cite: 3]
            count += 1[cite: 3]
        elif key == "resultroom":
            cursor.execute("INSERT INTO server_settings (guild_id, result_room) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET result_room = ?", (guild_id, val, val))[cite: 3]
            count += 1[cite: 3]
        elif key == "helperrole":
            cursor.execute("INSERT INTO server_settings (guild_id, helper_role) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET helper_role = ?", (guild_id, val, val))[cite: 3]
            count += 1[cite: 3]
        elif key == "htticketroom":
            cursor.execute("INSERT INTO server_settings (guild_id, ht_ticket_room) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET ht_ticket_room = ?", (guild_id, val, val))
            count += 1
        elif key == "kit":
            cursor.execute("INSERT OR IGNORE INTO kits (name) VALUES (?)", (val.lower(),))[cite: 3]
            count += 1[cite: 3]
        elif key == "tierrole":
            parts = val.split("|")[cite: 3]
            if len(parts) == 3:
                cursor.execute("INSERT OR REPLACE INTO tier_roles (kit, tier, role_id) VALUES (?, ?, ?)", (parts[0].lower(), parts[1], parts[2]))[cite: 3]
                count += 1[cite: 3]
        elif key == "queueroom":
            parts = val.split("|")[cite: 3]
            if len(parts) == 2:
                cursor.execute("INSERT OR REPLACE INTO queue_rooms (kit, channel_id) VALUES (?, ?)", (parts[0].lower(), parts[1]))[cite: 3]
                count += 1[cite: 3]
        elif key == "kitcat":
            parts = val.split("|")[cite: 3]
            if len(parts) == 2:
                cursor.execute("INSERT OR REPLACE INTO kit_categories (kit, category_id) VALUES (?, ?)", (parts[0].lower(), parts[1]))[cite: 3]
                count += 1[cite: 3]
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

    conn.commit()[cite: 3]
    conn.close()[cite: 3]

    await interaction.response.send_message(f"✅ Úspěšně obnoveno/nastaveno **{count}** položek z databázového kódu (včetně hráčů)!", ephemeral=True)[cite: 3]

# --- HT TICKET SYSTÉM ---
@bot.tree.command(name="hticketset", description="Nastaví místnost pro výběr HT ticketů.")
async def hticketset(interaction: discord.Interaction, roomka: discord.TextChannel):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    
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
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    
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

        # Logika posunu o tier výš a odstranění "R" (např. RLT2 -> LT2)
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
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]

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
            return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
        
        conn = sqlite3.connect("tierbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT cooldown_ht FROM server_settings WHERE guild_id = ?", (str(interaction.guild.id),))
        s_row = cursor.fetchone()
        conn.close()

        parts = interaction.channel.name.split("-")
        if len(parts) >= 3:
            ign = parts[0]
            kit = parts[-1]
            conn = sqlite3.connect("tierbot.db")
            cursor = conn.cursor()
            cursor.execute("SELECT discord_id FROM verified WHERE minecraft_ign = ?", (ign,))
            u_row = cursor.fetchone()
            if u_row:
                discord_id = u_row[0]
                cd_setting = s_row[0] if s_row and s_row[0] else "0"
                delta_days, delta_hours = 0, 0
                if cd_setting.endswith("d"):
                    try: delta_days = int(cd_setting[:-1])
                    except: pass
                elif cd_setting.endswith("h"):
                    try: delta_hours = int(cd_setting[:-1])
                    except: pass
                
                if delta_days > 0 or delta_hours > 0:
                    expiry = datetime.datetime.now() + datetime.timedelta(days=delta_days, hours=delta_hours)
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
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT cooldown_ht FROM server_settings WHERE guild_id = ?", (str(interaction.guild.id),))
    s_row = cursor.fetchone()
    conn.close()

    parts = interaction.channel.name.split("-")
    if len(parts) >= 3:
        ign = parts[0]
        kit = parts[-1]
        conn = sqlite3.connect("tierbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT discord_id FROM verified WHERE minecraft_ign = ?", (ign,))
        u_row = cursor.fetchone()
        if u_row:
            discord_id = u_row[0]
            cd_setting = s_row[0] if s_row and s_row[0] else "0"
            delta_days, delta_hours = 0, 0
            if cd_setting.endswith("d"):
                try: delta_days = int(cd_setting[:-1])
                except: pass
            elif cd_setting.endswith("h"):
                try: delta_hours = int(cd_setting[:-1])
                except: pass
            
            if delta_days > 0 or delta_hours > 0:
                expiry = datetime.datetime.now() + datetime.timedelta(days=delta_days, hours=delta_hours)
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
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    
    try:
        await interaction.channel.set_permissions(user, view_channel=True, send_messages=True, read_message_history=True)
        await interaction.response.send_message(f"✅ Uživatel {user.mention} byl přidán do ticketu.", ephemeral=False)
    except Exception as e:
        await interaction.response.send_message(f"❌ Nepodařilo se přidat uživatele: {e}", ephemeral=True)

@bot.tree.command(name="remove", description="Odebere uživateli přístup z aktuálního ticketu.")
async def remove(interaction: discord.Interaction, user: discord.Member):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    
    try:
        await interaction.channel.set_permissions(user, overwrite=None)
        await interaction.response.send_message(f"✅ Uživatelu {user.mention} byl odebrán přístup z ticketu.", ephemeral=False)
    except Exception as e:
        await interaction.response.send_message(f"❌ Nepodařilo se odebrat uživatele: {e}", ephemeral=True)

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
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    cursor.execute("INSERT INTO server_settings (guild_id, language) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET language = ?", (str(interaction.guild.id), jazyk, jazyk))[cite: 3]
    conn.commit()[cite: 3]
    conn.close()[cite: 3]
    await interaction.response.send_message(get_msg(interaction.guild.id, "lang_set"), ephemeral=True)[cite: 3]

@bot.tree.command(name="cooldownset", description="Nastaví globální cooldown pro LT nebo HT tiery.")
@discord.app_commands.choices(typ=[discord.app_commands.Choice(name="LT", value="lt"), discord.app_commands.Choice(name="HT", value="ht")])
async def cooldownset(interaction: discord.Interaction, typ: str, cas: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    column = "cooldown_lt" if typ == "lt" else "cooldown_ht"[cite: 3]
    cursor.execute(f"INSERT INTO server_settings (guild_id, {column}) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET {column} = ?", (str(interaction.guild.id), cas, cas))[cite: 3]
    conn.commit()[cite: 3]
    conn.close()[cite: 3]
    await interaction.response.send_message(get_msg(interaction.guild.id, "cooldown_set", tipo=typ.upper(), time=cas), ephemeral=True)[cite: 3]

@bot.tree.command(name="removecooldown", description="Odstraní cooldown hráči podle výběru.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
@discord.app_commands.choices(typ=[discord.app_commands.Choice(name="LT", value="lt"), discord.app_commands.Choice(name="HT", value="ht")])
async def removecooldown(interaction: discord.Interaction, kit: str, discord_hrac: discord.Member, typ: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    cursor.execute("DELETE FROM player_cooldowns WHERE discord_id = ? AND kit = ? AND type = ?", (str(discord_hrac.id), kit.lower(), typ.lower()))[cite: 3]
    conn.commit()[cite: 3]
    conn.close()[cite: 3]
    await interaction.response.send_message(get_msg(interaction.guild.id, "cooldown_removed", tipo=typ.upper(), kit=kit, player=discord_hrac.mention), ephemeral=True)[cite: 3]

@bot.tree.command(name="cooldown", description="Zobrazí všechny aktivní cooldowny daného hráče.")
async def cooldown(interaction: discord.Interaction, player: discord.Member):
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    cursor.execute("SELECT kit, type, cooldown_until FROM player_cooldowns WHERE discord_id = ?", (str(player.id),))[cite: 3]
    rows = cursor.fetchall()[cite: 3]
    conn.close()[cite: 3]
    if not rows:
        return await interaction.response.send_message(f"✨ Uživatel {player.mention} nemá žádné aktivní cooldowny.", ephemeral=True)[cite: 3]
    embed = discord.Embed(title=f"⏳ Cooldowny pro hráče {player.display_name}", color=discord.Color.orange())[cite: 3]
    for kit, typ, until_str in rows:
        try:
            dt = datetime.datetime.fromisoformat(until_str)[cite: 3]
            if datetime.datetime.now() < dt:[cite: 3]
                embed.add_field(name=f"Kit: {kit.capitalize()} ({typ.upper()})", value=f"Do: {dt.strftime('%d.%m.%Y %H:%M')}", inline=False)[cite: 3]
        except:
            pass
    if not embed.fields:
        return await interaction.response.send_message(f"✨ Uživatel {player.mention} nemá žádné aktivní cooldowny.", ephemeral=True)[cite: 3]
    await interaction.response.send_message(embed=embed, ephemeral=True)[cite: 3]

@bot.tree.command(name="verify", description="Propojí tvůj Discord účet s Minecraft IGN.")
async def verify(interaction: discord.Interaction, minecraft_ign: str):
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    cursor.execute("INSERT OR REPLACE INTO verified (discord_id, minecraft_ign) VALUES (?, ?)", (str(interaction.user.id), minecraft_ign))[cite: 3]
    conn.commit()[cite: 3]
    conn.close()[cite: 3]
    await interaction.response.send_message(get_msg(interaction.guild.id, "verified_success", ign=minecraft_ign), ephemeral=True)[cite: 3]

@bot.tree.command(name="createkit", description="Přidá nový kit do databáze.")
async def createkit(interaction: discord.Interaction, jmeno_kitu: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    try:
        cursor.execute("INSERT INTO kits (name) VALUES (?)", (jmeno_kitu.lower(),))[cite: 3]
        conn.commit()[cite: 3]
        await interaction.response.send_message(get_msg(interaction.guild.id, "kit_created", kit=jmeno_kitu), ephemeral=True)[cite: 3]
    except sqlite3.IntegrityError:
        await interaction.response.send_message(get_msg(interaction.guild.id, "kit_exists", kit=jmeno_kitu), ephemeral=True)[cite: 3]
    finally:
        conn.close()[cite: 3]

@bot.tree.command(name="removekit", description="Odstraní kit z databáze.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def removekit(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    cursor.execute("DELETE FROM kits WHERE name = ?", (kit.lower(),))[cite: 3]
    conn.commit()[cite: 3]
    conn.close()[cite: 3]
    await interaction.response.send_message(get_msg(interaction.guild.id, "kit_removed", kit=kit), ephemeral=True)[cite: 3]

@bot.tree.command(name="tieroleset", description="Nastaví roli pro daný kit a tier.")
@discord.app_commands.autocomplete(kit=kit_autocomplete, tier=tier_autocomplete)
async def tieroleset(interaction: discord.Interaction, kit: str, tier: str, role: discord.Role):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    cursor.execute("INSERT OR REPLACE INTO tier_roles (kit, tier, role_id) VALUES (?, ?, ?)", (kit.lower(), tier, str(role.id)))[cite: 3]
    conn.commit()[cite: 3]
    conn.close()[cite: 3]
    await interaction.response.send_message(get_msg(interaction.guild.id, "tier_role_set", kit=kit, tier=tier, role=role.name), ephemeral=True)[cite: 3]

@bot.tree.command(name="resultroomset", description="Nastaví místnost pro posílání výsledků.")
async def resultroomset(interaction: discord.Interaction, discord_roomka: discord.TextChannel):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    cursor.execute("INSERT INTO server_settings (guild_id, result_room) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET result_room = ?", (str(interaction.guild.id), str(discord_roomka.id), str(discord_roomka.id)))[cite: 3]
    conn.commit()[cite: 3]
    conn.close()[cite: 3]
    await interaction.response.send_message(get_msg(interaction.guild.id, "result_room_set", room=discord_roomka.mention), ephemeral=True)[cite: 3]

@bot.tree.command(name="helperoleset", description="Nastaví roli pro používání bota.")
async def helperoleset(interaction: discord.Interaction, role: discord.Role):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    cursor.execute("INSERT INTO server_settings (guild_id, helper_role) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET helper_role = ?", (str(interaction.guild.id), str(role.id), str(role.id)))[cite: 3]
    conn.commit()[cite: 3]
    conn.close()[cite: 3]
    await interaction.response.send_message(get_msg(interaction.guild.id, "helper_role_set", role=role.mention), ephemeral=True)[cite: 3]

@bot.tree.command(name="queueroomset", description="Nastaví textový kanál pro frontu daného kitu.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def queueroomset(interaction: discord.Interaction, discord_roomka: discord.TextChannel, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    cursor.execute("INSERT OR REPLACE INTO queue_rooms (kit, channel_id) VALUES (?, ?)", (kit.lower(), str(discord_roomka.id)))[cite: 3]
    conn.commit()[cite: 3]
    conn.close()[cite: 3]
    await interaction.response.send_message(get_msg(interaction.guild.id, "queue_room_set", kit=kit, room=discord_roomka.mention), ephemeral=True)[cite: 3]

@bot.tree.command(name="kitcategoryset", description="Nastaví kategorii pro vygenerování testovací místnosti.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def kitcategoryset(interaction: discord.Interaction, kit: str, kategorie: discord.CategoryChannel):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    cursor.execute("INSERT OR REPLACE INTO kit_categories (kit, category_id) VALUES (?, ?)", (kit.lower(), str(kategorie.id)))[cite: 3]
    conn.commit()[cite: 3]
    conn.close()[cite: 3]
    await interaction.response.send_message(get_msg(interaction.guild.id, "kit_cat_set", kit=kit, cat=kategorie.name), ephemeral=True)[cite: 3]

QUEUES = {}[cite: 3]

class QueueView(discord.ui.View):
    def __init__(self, kit_name: str, guild_id: int):
        super().__init__(timeout=None)[cite: 3]
        self.kit_name = kit_name[cite: 3]
        self.guild_id = guild_id[cite: 3]
        self.children[0].label = get_msg(guild_id, "join_btn")[cite: 3]
        self.children[1].label = get_msg(guild_id, "leave_btn")[cite: 3]
        self.children[2].label = get_msg(guild_id, "pull_btn")[cite: 3]

    @discord.ui.button(style=discord.ButtonStyle.primary, custom_id="join_queue")
    async def join_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = sqlite3.connect("tierbot.db")[cite: 3]
        cursor = conn.cursor()[cite: 3]
        cursor.execute("SELECT minecraft_ign FROM verified WHERE discord_id = ?", (str(interaction.user.id),))[cite: 3]
        row = cursor.fetchone()[cite: 3]
        cursor.execute("SELECT cooldown_until FROM player_cooldowns WHERE discord_id = ? AND kit = ?", (str(interaction.user.id), self.kit_name.lower()))[cite: 3]
        cd_row = cursor.fetchone()[cite: 3]
        conn.close()[cite: 3]

        if cd_row and cd_row[0]:
            try:
                cd_time = datetime.datetime.fromisoformat(cd_row[0])[cite: 3]
                if datetime.datetime.now() < cd_time:[cite: 3]
                    return await interaction.response.send_message(f"⏳ Cooldown aktivní do **{cd_time.strftime('%d.%m.%Y %H:%M')}**!", ephemeral=True)[cite: 3]
            except:
                pass

        if not row:
            return await interaction.response.send_message(get_msg(interaction.guild.id, "not_verified"), ephemeral=True)[cite: 3]

        if self.kit_name not in QUEUES:
            QUEUES[self.kit_name] = {"players": [], "testers": []}[cite: 3]

        if interaction.user.id in QUEUES[self.kit_name]["players"]:
            return await interaction.response.send_message(get_msg(interaction.guild.id, "already_in_queue"), ephemeral=True)[cite: 3]

        QUEUES[self.kit_name]["players"].append(interaction.user.id)[cite: 3]
        await interaction.response.send_message("✅", ephemeral=True)[cite: 3]
        await update_queue_message(interaction.channel, self.kit_name, interaction.guild.id)[cite: 3]

    @discord.ui.button(style=discord.ButtonStyle.danger, custom_id="leave_queue")
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.kit_name in QUEUES and interaction.user.id in QUEUES[self.kit_name]["players"]:
            QUEUES[self.kit_name]["players"].remove(interaction.user.id)[cite: 3]
            await interaction.response.send_message(get_msg(interaction.guild.id, "left_queue"), ephemeral=True)[cite: 3]
            await update_queue_message(interaction.channel, self.kit_name, interaction.guild.id)[cite: 3]
        else:
            await interaction.response.send_message(get_msg(interaction.guild.id, "not_in_queue"), ephemeral=True)[cite: 3]

    @discord.ui.button(style=discord.ButtonStyle.success, custom_id="pull_player")
    async def pull_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await has_helper_perms(interaction):
            return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]

        if self.kit_name not in QUEUES or not QUEUES[self.kit_name]["players"]:
            return await interaction.response.send_message(get_msg(interaction.guild.id, "queue_empty"), ephemeral=True)[cite: 3]

        conn = sqlite3.connect("tierbot.db")[cite: 3]
        cursor = conn.cursor()[cite: 3]
        cursor.execute("SELECT category_id FROM kit_categories WHERE kit = ?", (self.kit_name.lower(),))[cite: 3]
        cat_row = cursor.fetchone()[cite: 3]
        
        player_id = QUEUES[self.kit_name]["players"][0][cite: 3]
        cursor.execute("SELECT minecraft_ign FROM verified WHERE discord_id = ?", (str(player_id),))[cite: 3]
        ign_row = cursor.fetchone()[cite: 3]
        conn.close()[cite: 3]

        player = interaction.guild.get_member(player_id)[cite: 3]
        if not player:
            QUEUES[self.kit_name]["players"].pop(0)[cite: 3]
            return await interaction.response.send_message("⚠️ Hráč již není na serveru.", ephemeral=True)[cite: 3]

        mc_ign = ign_row[0] if ign_row else player.name[cite: 3]
        target_category = interaction.guild.get_channel(int(cat_row[0])) if cat_row and cat_row[0] else None[cite: 3]

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),[cite: 3]
            player: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),[cite: 3]
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)[cite: 3]
        }

        test_channel = await interaction.guild.create_text_channel(
            name=f"{mc_ign.lower()}-test",[cite: 3]
            category=target_category if isinstance(target_category, discord.CategoryChannel) else interaction.channel.category,[cite: 3]
            overwrites=overwrites[cite: 3]
        )

        QUEUES[self.kit_name]["players"].pop(0)[cite: 3]
        if interaction.user.id not in QUEUES[self.kit_name]["testers"]:
            QUEUES[self.kit_name]["testers"].append(interaction.user.id)[cite: 3]

        await update_queue_message(interaction.channel, self.kit_name, interaction.guild.id)[cite: 3]
        await test_channel.send(get_msg(interaction.guild.id, "test_started", tester=interaction.user.mention, player=player.mention))[cite: 3]
        await interaction.response.send_message(get_msg(interaction.guild.id, "player_pulled", player=player.mention, room=test_channel.mention), ephemeral=True)[cite: 3]

def get_queue_embed(kit_name: str, guild_id: int):
    data = QUEUES.get(kit_name, {"players": [], "testers": []})[cite: 3]
    players_list = data["players"][cite: 3]
    testers_list = data["testers"][cite: 3]

    players_str = "\n".join([f"{i+1}. <@{pid}>" for i, pid in enumerate(players_list)]) if players_list else get_msg(guild_id, "queue_empty")[cite: 3]
    testers_str = "\n".join([f"{i+1}. <@{tid}>" for i, tid in enumerate(testers_list)]) if testers_list else get_msg(guild_id, "no_testers")[cite: 3]

    embed = discord.Embed(
        title=get_msg(guild_id, "queue_title", kit=kit_name.capitalize()),[cite: 3]
        description=f"{get_msg(guild_id, 'queue_desc')}\n\n**Fronta:**\n{players_str}\n\n**{get_msg(guild_id, 'active_testers')}:**\n{testers_str}",[cite: 3]
        color=discord.Color.blue()[cite: 3]
    )
    return embed[cite: 3]

async def update_queue_message(channel, kit_name, guild_id):
    embed = get_queue_embed(kit_name, guild_id)[cite: 3]
    async for message in channel.history(limit=10):[cite: 3]
        if message.author == bot.user and message.embeds:[cite: 3]
            await message.edit(embed=embed, view=QueueView(kit_name, guild_id))[cite: 3]
            return
    await channel.send(embed=embed, view=QueueView(kit_name, guild_id))[cite: 3]

@bot.tree.command(name="openqueue", description="Otevře queue pro daný kit.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def openqueue(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]
    
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    cursor.execute("SELECT channel_id FROM queue_rooms WHERE kit = ?", (kit.lower(),))[cite: 3]
    row = cursor.fetchone()[cite: 3]
    conn.close()[cite: 3]

    if not row or not row[0]:
        return await interaction.response.send_message(f"❌ Pro kit **{kit}** není nastavena queue místnost!", ephemeral=True)[cite: 3]

    target_channel = interaction.guild.get_channel(int(row[0]))[cite: 3]
    if not target_channel:
        return await interaction.response.send_message("❌ Kanál nebyl nalezen.", ephemeral=True)[cite: 3]

    try:
        async for message in target_channel.history(limit=50):
            if message.author == bot.user:
                await message.delete()
    except Exception as e:
        print(f"Nelze smazat staré zprávy: {e}")

    QUEUES[kit.lower()] = {"players": [], "testers": []}[cite: 3]
    embed = get_queue_embed(kit.lower(), interaction.guild.id)[cite: 3]
    
    await target_channel.send(content="@everyone", embed=embed, view=QueueView(kit.lower(), interaction.guild.id))[cite: 3]
    await interaction.response.send_message(get_msg(interaction.guild.id, "queue_opened", kit=kit, room=target_channel.mention), ephemeral=True)[cite: 3]

@bot.tree.command(name="closequeue", description="Zavře frontu pro daný kit.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def closequeue(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]

    kit_key = kit.lower()[cite: 3]
    if kit_key in QUEUES and QUEUES[kit_key]["testers"]:
        return await interaction.response.send_message(get_msg(interaction.guild.id, "cannot_close_active"), ephemeral=True)[cite: 3]

    QUEUES.pop(kit_key, None)[cite: 3]

    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    cursor.execute("SELECT channel_id FROM queue_rooms WHERE kit = ?", (kit_key,))[cite: 3]
    row = cursor.fetchone()[cite: 3]
    conn.close()[cite: 3]

    if row and row[0]:
        target_channel = interaction.guild.get_channel(int(row[0]))[cite: 3]
        if target_channel:
            closed_embed = discord.Embed(
                title=get_msg(interaction.guild.id, "closed_title", kit=kit.capitalize()),[cite: 3]
                description=get_msg(interaction.guild.id, "closed_desc"),[cite: 3]
                color=discord.Color.red()[cite: 3]
            )
            closed_embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))[cite: 3]
            
            async for message in target_channel.history(limit=10):[cite: 3]
                if message.author == bot.user and message.embeds:[cite: 3]
                    await message.edit(embed=closed_embed, view=None)[cite: 3]
                    break

    await interaction.response.send_message(get_msg(interaction.guild.id, "queue_closed", kit=kit), ephemeral=True)[cite: 3]

@bot.tree.command(name="joinqueueastester", description="Připojí tě jako testera do fronty.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def joinqueueastester(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]

    kit_key = kit.lower()[cite: 3]
    if kit_key not in QUEUES:
        QUEUES[kit_key] = {"players": [], "testers": []}[cite: 3]

    if interaction.user.id in QUEUES[kit_key]["testers"]:
        return await interaction.response.send_message(get_msg(interaction.guild.id, "already_tester"), ephemeral=True)[cite: 3]

    QUEUES[kit_key]["testers"].append(interaction.user.id)[cite: 3]
    await interaction.response.send_message(get_msg(interaction.guild.id, "tester_joined", kit=kit), ephemeral=True)[cite: 3]
    
    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    cursor.execute("SELECT channel_id FROM queue_rooms WHERE kit = ?", (kit_key,))[cite: 3]
    row = cursor.fetchone()[cite: 3]
    conn.close()[cite: 3]
    if row and row[0]:
        ch = interaction.guild.get_channel(int(row[0]))[cite: 3]
        if ch:
            await update_queue_message(ch, kit_key, interaction.guild.id)[cite: 3]

@bot.tree.command(name="leavequeueastester", description="Odebere tě ze seznamu testerů.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def leavequeueastester(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]

    kit_key = kit.lower()[cite: 3]
    if kit_key in QUEUES and interaction.user.id in QUEUES[kit_key]["testers"]:
        QUEUES[kit_key]["testers"].remove(interaction.user.id)[cite: 3]
        await interaction.response.send_message(get_msg(interaction.guild.id, "tester_left", kit=kit), ephemeral=True)[cite: 3]
        
        conn = sqlite3.connect("tierbot.db")[cite: 3]
        cursor = conn.cursor()[cite: 3]
        cursor.execute("SELECT channel_id FROM queue_rooms WHERE kit = ?", (kit_key,))[cite: 3]
        row = cursor.fetchone()[cite: 3]
        conn.close()[cite: 3]
        if row and row[0]:
            ch = interaction.guild.get_channel(int(row[0]))[cite: 3]
            if ch:
                await update_queue_message(ch, kit_key, interaction.guild.id)[cite: 3]
    else:
        await interaction.response.send_message(get_msg(interaction.guild.id, "not_tester"), ephemeral=True)[cite: 3]

@bot.tree.command(name="result", description="Odešle výsledek testu do result místnosti.")
@discord.app_commands.autocomplete(kit=kit_autocomplete, tier=tier_autocomplete)
async def result(interaction: discord.Interaction, discord_hrac: discord.Member, kit: str, tier: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)[cite: 3]

    conn = sqlite3.connect("tierbot.db")[cite: 3]
    cursor = conn.cursor()[cite: 3]
    cursor.execute("SELECT minecraft_ign FROM verified WHERE discord_id = ?", (str(discord_hrac.id),))[cite: 3]
    row = cursor.fetchone()[cite: 3]

    cursor.execute("SELECT tier FROM player_tiers WHERE discord_id = ? AND kit = ?", (str(discord_hrac.id), kit.lower()))[cite: 3]
    prev_row = cursor.fetchone()[cite: 3]
    prev_tier = prev_row[0] if prev_row else "N/A"[cite: 3]

    cursor.execute("INSERT OR REPLACE INTO player_tiers (discord_id, kit, tier) VALUES (?, ?, ?)", (str(discord_hrac.id), kit.lower(), tier))[cite: 3]
    cursor.execute("SELECT role_id FROM tier_roles WHERE kit = ? AND tier = ?", (kit.lower(), tier))[cite: 3]
    role_row = cursor.fetchone()[cite: 3]

    cursor.execute("SELECT result_room, cooldown_lt, cooldown_ht FROM server_settings WHERE guild_id = ?", (str(interaction.guild.id),))[cite: 3]
    settings_row = cursor.fetchone()[cite: 3]

    is_lt = tier.startswith("LT") or tier.startswith("RLT")[cite: 3]
    cd_setting = (settings_row[1] if is_lt else settings_row[2]) if settings_row else "0"[cite: 3]

    delta_days = 0[cite: 3]
    delta_hours = 0[cite: 3]
    if cd_setting.endswith("d"):
        try: delta_days = int(cd_setting[:-1])[cite: 3]
        except: pass
    elif cd_setting.endswith("h"):
        try: delta_hours = int(cd_setting[:-1])[cite: 3]
        except: pass

    if delta_days > 0 or delta_hours > 0:
        expiry = datetime.datetime.now() + datetime.timedelta(days=delta_days, hours=delta_hours)[cite: 3]
        cd_type = "lt" if is_lt else "ht"[cite: 3]
        cursor.execute("INSERT OR REPLACE INTO player_cooldowns (discord_id, kit, type, cooldown_until) VALUES (?, ?, ?, ?)", (str(discord_hrac.id), kit.lower(), cd_type, expiry.isoformat()))[cite: 3]

    conn.commit()[cite: 3]
    conn.close()[cite: 3]

    mc_ign = row[0] if row else "Neznámý"[cite: 3]

    if role_row and role_row[0]:
        role = interaction.guild.get_role(int(role_row[0]))[cite: 3]
        if role:
            try:
                await discord_hrac.add_roles(role)[cite: 3]
            except Exception:
                pass

    dnes = datetime.datetime.now().strftime("%d.%m.%Y")[cite: 3]

    embed = discord.Embed(
        title=get_msg(interaction.guild.id, "result_title", kit=kit),[cite: 3]
        description=get_msg(interaction.guild.id, "result_desc", kit=kit),[cite: 3]
        color=discord.Color.green()[cite: 3]
    )
    embed.add_field(name="👤 Hráč (Discord)", value=discord_hrac.mention, inline=True)[cite: 3]
    embed.add_field(name="🎮 Minecraft IGN", value=mc_ign, inline=True)[cite: 3]
    embed.add_field(name="⚔️ Tester", value=interaction.user.mention, inline=True)[cite: 3]
    embed.add_field(name="📉 Předchozí tier", value=prev_tier, inline=True)[cite: 3]
    embed.add_field(name="📈 Nový tier", value=tier, inline=True)[cite: 3]
    embed.set_footer(text=dnes)[cite: 3]

    if mc_ign != "Neznámý":
        skin_url = f"https://visage.surgeplay.com/bust/512/{mc_ign}"[cite: 3]
        embed.set_thumbnail(url=skin_url)[cite: 3]

    if settings_row and settings_row[0]:
        room_id = int(settings_row[0])[cite: 3]
        room = interaction.guild.get_channel(room_id)[cite: 3]
        if room:
            await room.send(content=f"📢 **Nový výsledek pro {kit}!** | Hráč: {discord_hrac.mention} | Tester: {interaction.user.mention}", embed=embed)[cite: 3]

    await interaction.response.send_message(get_msg(interaction.guild.id, "result_sent"), ephemeral=True)[cite: 3]
    await asyncio.sleep(3)[cite: 3]
    try:
        await interaction.channel.delete()[cite: 3]
    except Exception as e:
        print(f"Nelze smazat místnost: {e}")[cite: 3]

# Webový server pro Keep-Alive
async def handle_ping(request):
    return web.Response(text="Bot runs 24/7!")[cite: 3]

async def start_web_server():
    app = web.Application()[cite: 3]
    app.router.add_get("/", handle_ping)[cite: 3]
    runner = web.AppRunner(app)[cite: 3]
    await runner.setup()[cite: 3]
    port = int(os.environ.get("PORT", 8080))[cite: 3]
    site = web.TCPSite(runner, "0.0.0.0", port)[cite: 3]
    await site.start()[cite: 3]

TOKEN = os.getenv("DISCORD_TOKEN")[cite: 3]

async def main():
    async with bot:
        await start_web_server()[cite: 3]
        await bot.start(TOKEN)[cite: 3]

if __name__ == "__main__":
    asyncio.run(main())[cite: 3]
