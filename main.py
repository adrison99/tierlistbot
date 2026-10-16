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

def clean_tier(tier: str) -> str:
    return tier.upper().replace("R", "")

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
            max_strikes INTEGER DEFAULT 2,
            strike_room TEXT,
            strike_system TEXT DEFAULT 'on'
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
    cursor.execute("CREATE TABLE IF NOT EXISTS ft_config (kit TEXT PRIMARY KEY, ft_num INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS passing_scores (id INTEGER PRIMARY KEY AUTOINCREMENT, kit TEXT, target_tier TEXT, opp_tier TEXT, count INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS strike_scores (id INTEGER PRIMARY KEY AUTOINCREMENT, kit TEXT, test_tier TEXT, opp_tier TEXT, score_str TEXT, is_unstrike INTEGER DEFAULT 0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS strikes (discord_id TEXT, kit TEXT, count INTEGER, PRIMARY KEY (discord_id, kit))")
    conn.commit()
    conn.close()

init_db()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

VALID_TIERS = ["LT5", "HT5", "LT4", "HT4", "LT3", "HT3", "LT2", "HT2", "LT1", "HT1"]
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

@bot.tree.command(name="databaseinfo", description="Záloha celé databáze.")
async def databaseinfo(interaction: discord.Interaction):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

    guild_id = str(interaction.guild.id)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()

    cursor.execute("SELECT result_room, helper_role, language, cooldown_lt, cooldown_ht, ht_ticket_room, max_strikes, strike_room, strike_system FROM server_settings WHERE guild_id = ?", (guild_id,))
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

    cursor.execute("SELECT kit, ft_num FROM ft_config")
    ft_configs = cursor.fetchall()

    cursor.execute("SELECT kit, target_tier, opp_tier, count FROM passing_scores")
    pass_scores = cursor.fetchall()

    cursor.execute("SELECT kit, test_tier, opp_tier, score_str, is_unstrike FROM strike_scores")
    strike_scores = cursor.fetchall()

    cursor.execute("SELECT discord_id, kit, count FROM strikes")
    user_strikes = cursor.fetchall()
    conn.close()

    lines = []
    if settings:
        r_room, h_role, lang, cd_lt, cd_ht, ht_room, max_s, s_room, s_sys = settings
        if lang: lines.append(f"lang:{lang}")
        if cd_lt and cd_lt != "0": lines.append(f"cdlt:{cd_lt}")
        if cd_ht and cd_ht != "0": lines.append(f"cdht:{cd_ht}")
        if r_room: lines.append(f"resultroom:{r_room}")
        if h_role: lines.append(f"helperrole:{h_role}")
        if ht_room: lines.append(f"htticketroom:{ht_room}")
        if max_s: lines.append(f"maxs:{max_s}")
        if s_room: lines.append(f"sroom:{s_room}")
        if s_sys: lines.append(f"ssys:{s_sys}")

    for kit in kits: lines.append(f"kit:{kit}")
    for kit, tier, role_id in tier_roles: lines.append(f"tierrole:{kit}|{tier}|{role_id}")
    for kit, channel_id in queue_rooms: lines.append(f"queueroom:{kit}|{channel_id}")
    for kit, category_id in kit_categories: lines.append(f"kitcat:{kit}|{category_id}")
    for kit, category_id in ht_ticket_categories: lines.append(f"htticketcat:{kit}|{category_id}")
    for d_id, ign in verified_users: lines.append(f"ver:{d_id}|{ign}")
    for d_id, kit, tier in player_tiers: lines.append(f"ptier:{d_id}|{kit}|{tier}")
    for d_id, kit, typ, until in player_cooldowns: lines.append(f"pcd:{d_id}|{kit}|{typ}|{until}")
    for d_id, ym, count in tester_monthly: lines.append(f"tmon:{d_id}|{ym}|{count}")
    for d_id, count in tester_overall: lines.append(f"tot:{d_id}|{count}")
    for kit, ft in ft_configs: lines.append(f"ft:{kit}|{ft}")
    for kit, tt, ot, c in pass_scores: lines.append(f"pscore:{kit}|{tt}|{ot}|{c}")
    for kit, tt, ot, s, iu in strike_scores: lines.append(f"sscore:{kit}|{tt}|{ot}|{s}|{iu}")
    for d_id, kit, c in user_strikes: lines.append(f"strike:{d_id}|{kit}|{c}")

    backup_text = ";;".join(lines)
    if not backup_text:
        return await interaction.response.send_message("⚠️ Žádná data k zálohování.", ephemeral=True)

    try:
        await interaction.user.send(f"📋 **Záloha databáze:**\n```text\n{backup_text}\n```")
        await interaction.response.send_message("✅ Záloha odeslána do DM.", ephemeral=True)
    except:
        await interaction.response.send_message(f"📋 **Záloha:**\n```text\n{backup_text}\n```", ephemeral=True)

@bot.tree.command(name="database", description="Obnova databáze.")
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
        elif key == "maxs":
            cursor.execute("INSERT INTO server_settings (guild_id, max_strikes) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET max_strikes = ?", (guild_id, int(val), int(val)))
            count += 1
        elif key == "sroom":
            cursor.execute("INSERT INTO server_settings (guild_id, strike_room) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET strike_room = ?", (guild_id, val, val))
            count += 1
        elif key == "ssys":
            cursor.execute("INSERT INTO server_settings (guild_id, strike_system) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET strike_system = ?", (guild_id, val, val))
            count += 1
        elif key == "kit":
            cursor.execute("INSERT OR IGNORE INTO kits (name) VALUES (?)", (val.lower(),))
            count += 1
        elif key == "tierrole":
            parts = val.split("|")
            if len(parts) == 3:
                cursor.execute("INSERT OR REPLACE INTO tier_roles (kit, tier, role_id) VALUES (?, ?, ?)", (parts[0].lower(), clean_tier(parts[1]), parts[2]))
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
                cursor.execute("INSERT OR REPLACE INTO player_tiers (discord_id, kit, tier) VALUES (?, ?, ?)", (parts[0], parts[1].lower(), clean_tier(parts[2])))
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
        elif key == "ft":
            parts = val.split("|")
            if len(parts) == 2:
                cursor.execute("INSERT OR REPLACE INTO ft_config (kit, ft_num) VALUES (?, ?)", (parts[0].lower(), int(parts[1])))
                count += 1
        elif key == "pscore":
            parts = val.split("|")
            if len(parts) == 4:
                cursor.execute("INSERT INTO passing_scores (kit, target_tier, opp_tier, count) VALUES (?, ?, ?, ?)", (parts[0].lower(), clean_tier(parts[1]), clean_tier(parts[2]), int(parts[3])))
                count += 1
        elif key == "sscore":
            parts = val.split("|")
            if len(parts) == 5:
                cursor.execute("INSERT INTO strike_scores (kit, test_tier, opp_tier, score_str, is_unstrike) VALUES (?, ?, ?, ?, ?)", (parts[0].lower(), clean_tier(parts[1]), clean_tier(parts[2]), parts[3], int(parts[4])))
                count += 1
        elif key == "strike":
            parts = val.split("|")
            if len(parts) == 3:
                cursor.execute("INSERT OR REPLACE INTO strikes (discord_id, kit, count) VALUES (?, ?, ?)", (parts[0], parts[1].lower(), int(parts[2])))
                count += 1

    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ Obnoveno **{count}** položek!", ephemeral=True)

@bot.tree.command(name="hticketset", description="Nastaví roomku pro HT tickety.")
async def hticketset(interaction: discord.Interaction, roomka: discord.TextChannel):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO server_settings (guild_id, ht_ticket_room) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET ht_ticket_room = ?", (str(interaction.guild.id), str(roomka.id), str(roomka.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ HT ticket místnost nastavena na {roomka.mention}.", ephemeral=True)

@bot.tree.command(name="categorysetforhtticket", description="Nastaví kategorii pro HT ticket kit.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def categorysetforhtticket(interaction: discord.Interaction, kit: str, kategorie: discord.CategoryChannel):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO ht_ticket_categories (kit, category_id) VALUES (?, ?)", (kit.lower(), str(kategorie.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ Kategorie pro kit **{kit}** nastavena.", ephemeral=True)

class HTTicketKitSelect(discord.ui.Select):
    def __init__(self, kits):
        options = [discord.SelectOption(label=kit.capitalize(), value=kit) for kit in kits[:25]]
        super().__init__(placeholder="Vyber kit pro HT ticket...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        kit = self.values[0]
        user_id = str(interaction.user.id)

        conn = sqlite3.connect("tierbot.db")
        cursor = conn.cursor()
        
        # Kontrola HT cooldownu před vytvořením ticketu
        cursor.execute("SELECT cooldown_until FROM player_cooldowns WHERE discord_id = ? AND kit = ? AND type = 'ht'", (user_id, kit.lower()))
        cd_row = cursor.fetchone()
        if cd_row and cd_row[0]:
            try:
                dt = datetime.datetime.fromisoformat(cd_row[0])
                if datetime.datetime.now() < dt:
                    conn.close()
                    return await interaction.response.send_message(f"⏳ Máš aktivní HT cooldown do **{dt.strftime('%d.%m.%Y %H:%M')}**!", ephemeral=True)
            except: pass

        cursor.execute("SELECT minecraft_ign FROM verified WHERE discord_id = ?", (user_id,))
        v_row = cursor.fetchone()
        if not v_row:
            conn.close()
            return await interaction.response.send_message("❌ Nejsi propojený přes `/verify`!", ephemeral=True)
        
        mc_ign = v_row[0]
        cursor.execute("SELECT tier FROM player_tiers WHERE discord_id = ? AND kit = ?", (user_id, kit.lower()))
        t_row = cursor.fetchone()
        cursor.execute("SELECT category_id FROM ht_ticket_categories WHERE kit = ?", (kit.lower(),))
        cat_row = cursor.fetchone()
        conn.close()

        current_tier = t_row[0] if t_row else "LT5"
        next_tier = "HT3"
        ct = clean_tier(current_tier)
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
            if h_role: overwrites[h_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        ticket_channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=target_category if isinstance(target_category, discord.CategoryChannel) else None,
            overwrites=overwrites
        )

        await ticket_channel.send(f"⚔️ HT Ticket otevřen pro {interaction.user.mention} na kit **{kit.capitalize()}** (Cílový tier: **{next_tier}**).\nPro uzavření použij tlačítko níže nebo `/close`.", view=CloseTicketView())
        await interaction.response.send_message(f"✅ Tvůj ticket byl vytvořen: {ticket_channel.mention}", ephemeral=True)

class HTTicketView(discord.ui.View):
    def __init__(self, kits):
        super().__init__(timeout=None)
        self.add_item(HTTicketKitSelect(kits))

@bot.tree.command(name="hticketsend", description="Odešle zprávu pro HT tickety.")
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

    if not row or not row[0]: return await interaction.response.send_message("❌ Není nastavená místnost!", ephemeral=True)
    target_channel = interaction.guild.get_channel(int(row[0]))
    if not target_channel: return await interaction.response.send_message("❌ Kanál nenalezen.", ephemeral=True)

    embed = discord.Embed(title="⚔️ HT Tier Test Tickets", description="Zde můžeš požádat o test na **HT3+** kity.\n\n⚠️ **Pravidla:**\n- Netroluj tikety.\n- Vyber níže správný kit.", color=discord.Color.gold())
    await target_channel.send(embed=embed, view=HTTicketView(kits))
    await interaction.response.send_message("✅ Zpráva odeslána.", ephemeral=True)

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
            ign, kit = parts[0], parts[-1]
            cursor.execute("SELECT discord_id FROM verified WHERE minecraft_ign = ?", (ign,))
            u_row = cursor.fetchone()
            if u_row:
                d_id = u_row[0]
                days, hours = parse_cooldown(s_row[0] if s_row else "0")
                if days > 0 or hours > 0:
                    exp = datetime.datetime.now() + datetime.timedelta(days=days, hours=hours)
                    cursor.execute("INSERT OR REPLACE INTO player_cooldowns (discord_id, kit, type, cooldown_until) VALUES (?, ?, 'ht', ?)", (d_id, kit.lower(), exp.isoformat()))
                    conn.commit()
        conn.close()

        await interaction.response.send_message("🔒 Ticket bude smazán...", ephemeral=True)
        await asyncio.sleep(3)
        try: await interaction.channel.delete()
        except: pass

@bot.tree.command(name="close", description="Zavře aktuální ticket.")
async def close(interaction: discord.Interaction):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT cooldown_ht FROM server_settings WHERE guild_id = ?", (str(interaction.guild.id),))
    s_row = cursor.fetchone()
    parts = interaction.channel.name.split("-")
    if len(parts) >= 3:
        ign, kit = parts[0], parts[-1]
        cursor.execute("SELECT discord_id FROM verified WHERE minecraft_ign = ?", (ign,))
        u_row = cursor.fetchone()
        if u_row:
            d_id = u_row[0]
            days, hours = parse_cooldown(s_row[0] if s_row else "0")
            if days > 0 or hours > 0:
                exp = datetime.datetime.now() + datetime.timedelta(days=days, hours=hours)
                cursor.execute("INSERT OR REPLACE INTO player_cooldowns (discord_id, kit, type, cooldown_until) VALUES (?, ?, 'ht', ?)", (d_id, kit.lower(), exp.isoformat()))
                conn.commit()
    conn.close()

    await interaction.response.send_message("🔒 Ticket bude smazán...", ephemeral=True)
    await asyncio.sleep(3)
    try: await interaction.channel.delete()
    except: pass

@bot.tree.command(name="add", description="Přidá uživatele do ticketu.")
async def add(interaction: discord.Interaction, user: discord.Member):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    try:
        await interaction.channel.set_permissions(user, view_channel=True, send_messages=True, read_message_history=True)
        await interaction.response.send_message(f"✅ Uživatel {user.mention} přidán.", ephemeral=False)
    except Exception as e:
        await interaction.response.send_message(f"❌ Chyba: {e}", ephemeral=True)

@bot.tree.command(name="remove", description="Odebere uživatele z ticketu.")
async def remove(interaction: discord.Interaction, user: discord.Member):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    try:
        await interaction.channel.set_permissions(user, overwrite=None)
        await interaction.response.send_message(f"✅ Uživatel {user.mention} odebrán.", ephemeral=False)
    except Exception as e:
        await interaction.response.send_message(f"❌ Chyba: {e}", ephemeral=True)

@bot.tree.command(name="maximumstrikes", description="Nastaví maximální striky.")
async def maximumstrikes(interaction: discord.Interaction, number: int):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO server_settings (guild_id, max_strikes) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET max_strikes = ?", (str(interaction.guild.id), number, number))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ Max strikes nastaveno na {number}.", ephemeral=True)

@bot.tree.command(name="strikeroom", description="Nastaví strike roomku.")
async def strikeroom(interaction: discord.Interaction, room: discord.TextChannel):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO server_settings (guild_id, strike_room) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET strike_room = ?", (str(interaction.guild.id), str(room.id), str(room.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ Strike roomka nastavena na {room.mention}.", ephemeral=True)

@bot.tree.command(name="strikesystem", description="Zapne/vypne strike systém.")
@discord.app_commands.choices(stav=[discord.app_commands.Choice(name="ON", value="on"), discord.app_commands.Choice(name="OFF", value="off")])
async def strikesystem(interaction: discord.Interaction, stav: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO server_settings (guild_id, strike_system) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET strike_system = ?", (str(interaction.guild.id), stav, stav))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ Strike systém nastaven na {stav.upper()}.", ephemeral=True)

@bot.tree.command(name="ft", description="Nastaví FT config.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def ft(interaction: discord.Interaction, kit: str, number: int):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO ft_config (kit, ft_num) VALUES (?, ?)", (kit.lower(), number))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ FT pro kit **{kit}** nastaveno na {number}.", ephemeral=True)

@bot.tree.command(name="passingscore", description="Zobrazí nebo nastaví passing score.")
@discord.app_commands.autocomplete(kit=kit_autocomplete, tier=tier_autocomplete)
async def passingscore(interaction: discord.Interaction, kit: str, tier: str = None):
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    
    if not tier:
        cursor.execute("SELECT id, target_tier, opp_tier, count FROM passing_scores WHERE kit = ? ORDER BY target_tier", (kit.lower(),))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return await interaction.response.send_message("✨ Žádná passing pravidla pro tento kit.", ephemeral=True)
        
        grouped = {}
        for r_id, tt, ot, count in rows:
            grouped.setdefault(tt, []).append(f"`{r_id}`. {count}x {ot}")
            
        desc_parts = []
        for tt, items in grouped.items():
            desc_parts.append(f"__**{tt}**__")
            for item in items:
                desc_parts.append(f"> {item}")
                
        embed = discord.Embed(title=f"📋 Passing Score pro kit: {kit.capitalize()}", description="\n".join(desc_parts), color=discord.Color.blue())
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if not await has_helper_perms(interaction):
        conn.close()
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn.close()

    class PassModal(discord.ui.Modal, title=f"Passing Score: {kit.capitalize()} ({clean_tier(tier)})"):
        opp1_tier = discord.ui.TextInput(label="1. Soupeřův tier (např. HT3)", required=True)
        opp1_count = discord.ui.TextInput(label="Počet 1. soupeřů (např. 2)", required=True)
        opp2_tier = discord.ui.TextInput(label="2. Soupeřův tier (nepovinné)", required=False)
        opp2_count = discord.ui.TextInput(label="Počet 2. soupeřů (nepovinné)", required=False)

        async def on_submit(self, modal_interaction: discord.Interaction):
            c = sqlite3.connect("tierbot.db")
            cur = c.cursor()
            t_clean = clean_tier(tier)
            o1_clean = clean_tier(self.opp1_tier.value)
            try: c1 = int(self.opp1_count.value)
            except: c1 = 1
            
            cur.execute("INSERT INTO passing_scores (kit, target_tier, opp_tier, count) VALUES (?, ?, ?, ?)", (kit.lower(), t_clean, o1_clean, c1))
            if self.opp2_tier.value and self.opp2_count.value:
                o2_clean = clean_tier(self.opp2_tier.value)
                try: c2 = int(self.opp2_count.value)
                except: c2 = 1
                cur.execute("INSERT INTO passing_scores (kit, target_tier, opp_tier, count) VALUES (?, ?, ?, ?)", (kit.lower(), t_clean, o2_clean, c2))
            c.commit()
            c.close()
            await modal_interaction.response.send_message("✅ Passing score úspěšně nastaveno!", ephemeral=True)

    await interaction.response.send_modal(PassModal())

@bot.tree.command(name="strikescore", description="Nastaví strike score.")
@discord.app_commands.autocomplete(kit=kit_autocomplete, test_tier=tier_autocomplete, opp_tier=tier_autocomplete)
async def strikescore(interaction: discord.Interaction, kit: str, test_tier: str, opp_tier: str, score: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO strike_scores (kit, test_tier, opp_tier, score_str, is_unstrike) VALUES (?, ?, ?, ?, 0)", (kit.lower(), clean_tier(test_tier), clean_tier(opp_tier), score))
    conn.commit()
    conn.close()
    await interaction.response.send_message("✅ Strike pravidlo přidáno.", ephemeral=True)

@bot.tree.command(name="unstrikescore", description="Nastaví unstrike score.")
@discord.app_commands.autocomplete(kit=kit_autocomplete, test_tier=tier_autocomplete, opp_tier=tier_autocomplete)
async def unstrikescore(interaction: discord.Interaction, kit: str, test_tier: str, opp_tier: str, score: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO strike_scores (kit, test_tier, opp_tier, score_str, is_unstrike) VALUES (?, ?, ?, ?, 1)", (kit.lower(), clean_tier(test_tier), clean_tier(opp_tier), score))
    conn.commit()
    conn.close()
    await interaction.response.send_message("✅ Unstrike pravidlo přidáno.", ephemeral=True)

@bot.tree.command(name="strikerules", description="Zobrazí strike pravidla.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def strikerules(interaction: discord.Interaction, kit: str):
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, test_tier, opp_tier, score_str, is_unstrike FROM strike_scores WHERE kit = ?", (kit.lower(),))
    rows = cursor.fetchall()
    conn.close()
    if not rows: return await interaction.response.send_message("✨ Žádná pravidla.", ephemeral=True)
    lines = [f"`{r_id}`. {tt} vs {ot} -> {sc} [{'UNSTRIKE' if iu==1 else 'STRIKE'}]" for r_id, tt, ot, sc, iu in rows]
    await interaction.response.send_message(embed=discord.Embed(title=f"📜 Strike pravidla: {kit.capitalize()}", description="\n".join(lines), color=discord.Color.red()), ephemeral=True)

@bot.tree.command(name="strikeruledelete", description="Smaže strike pravidlo.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def strikeruledelete(interaction: discord.Interaction, kit: str, rule_id: int):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM strike_scores WHERE id = ? AND kit = ?", (rule_id, kit.lower()))
    conn.commit()
    conn.close()
    await interaction.response.send_message("🗑️ Smazáno.", ephemeral=True)

@bot.tree.command(name="passingrule", description="Smaže passing pravidlo.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def passingrule(interaction: discord.Interaction, kit: str, rule_id: int):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM passing_scores WHERE id = ? AND kit = ?", (rule_id, kit.lower()))
    conn.commit()
    conn.close()
    await interaction.response.send_message("🗑️ Smazáno.", ephemeral=True)

@bot.tree.command(name="htresult", description="Vyhodnotí HT test, vyhodnotí skóre a udělí případný strike.")
@discord.app_commands.autocomplete(tier=tier_autocomplete, kit=kit_autocomplete)
async def htresult(interaction: discord.Interaction, discord_hrac: discord.Member, tier: str, status: str, kit: str, opponents: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    
    t_clean = clean_tier(tier)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT strike_system, max_strikes, strike_room FROM server_settings WHERE guild_id = ?", (str(interaction.guild.id),))
    s_row = cursor.fetchone()
    strike_system_on = s_row and s_row[0] == "on"
    max_s = s_row[1] if s_row and s_row[1] else 2
    strike_room_id = s_row[2] if s_row else None

    # Zpracování tester statistik (+1 test)
    tester_id = str(interaction.user.id)
    ym = datetime.datetime.now().strftime("%Y-%m")
    cursor.execute("INSERT INTO tester_monthly (discord_id, year_month, count) VALUES (?, ?, 1) ON CONFLICT(discord_id, year_month) DO UPDATE SET count = count + 1", (tester_id, ym))
    cursor.execute("INSERT INTO tester_overall (discord_id, count) VALUES (?, 1) ON CONFLICT(discord_id) DO UPDATE SET count = count + 1", (tester_id,))

    # Pokud testovaný získává tier, aktualizujeme mu tier v databázi a přidáme roli
    if status.lower() in ["získává", "ziskava"]:
        cursor.execute("INSERT OR REPLACE INTO player_tiers (discord_id, kit, tier) VALUES (?, ?, ?)", (str(discord_hrac.id), kit.lower(), t_clean))
        cursor.execute("SELECT role_id FROM tier_roles WHERE kit = ? AND tier = ?", (kit.lower(), t_clean))
        role_row = cursor.fetchone()
        if role_row and role_row[0]:
            role = interaction.guild.get_role(int(role_row[0]))
            if role:
                try: await discord_hrac.add_roles(role)
                except: pass

    # Automatické vyhodnocení striků z argumentu opponents (např. "10-8 HT3, 4-10 HT3 @tester")
    strike_count_change = 0
    match_details_text = opponents

    if strike_system_on and strike_room_id:
        # Načteme pravidla strike_scores pro tento kit a tier
        cursor.execute("SELECT opp_tier, score_str, is_unstrike FROM strike_scores WHERE kit = ? AND test_tier = ?", (kit.lower(), t_clean))
        rules = cursor.fetchall()
        
        # Jednoduchá heuristika: Projdeme pravidla a zkusíme v zadaném textu opponents najít shodu se skóre
        for opp_t, sc_str, is_unst in rules:
            if sc_str in opponents.lower():
                if is_unst == 1:
                    strike_count_change = -1
                else:
                    strike_count_change = 1
                break

    current_strikes = 0
    if strike_system_on and strike_room_id and strike_count_change != 0:
        cursor.execute("SELECT count FROM strikes WHERE discord_id = ? AND kit = ?", (str(discord_hrac.id), kit.lower()))
        st_row = cursor.fetchone()
        current_strikes = max(0, (st_row[0] if st_row else 0) + strike_count_change)
        cursor.execute("INSERT OR REPLACE INTO strikes (discord_id, kit, count) VALUES (?, ?, ?)", (str(discord_hrac.id), kit.lower(), current_strikes))

    conn.commit()
    conn.close()

    # Odeslání do strike místnosti
    if strike_system_on and strike_room_id and strike_count_change != 0:
        s_channel = interaction.guild.get_channel(int(strike_room_id))
        if s_channel:
            action_text = f"dostává strike {current_strikes}/{max_s}" if strike_count_change > 0 else f"odebrán strike ({current_strikes}/{max_s})"
            await s_channel.send(f"{discord_hrac.mention} {t_clean} {kit} {action_text} - {match_details_text}")

    await interaction.response.send_message("✅ HT Výsledek úspěšně zpracován!", ephemeral=True)
    await asyncio.sleep(3)
    try: await interaction.channel.delete()
    except: pass

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
        ym = now.strftime("%Y-%m")
        title, query = "🏆 TOP testeři tento měsíc", "SELECT discord_id, count FROM tester_monthly WHERE year_month = ? ORDER BY count DESC LIMIT 10"
        cursor.execute(query, (ym,))
    elif obdobi == "minulymesic":
        ym = (now.replace(day=1) - datetime.timedelta(days=1)).strftime("%Y-%m")
        title, query = "🏆 TOP testeři minulý měsíc", "SELECT discord_id, count FROM tester_monthly WHERE year_month = ? ORDER BY count DESC LIMIT 10"
        cursor.execute(query, (ym,))
    else:
        title, query = "🏆 TOP testeři celkově", "SELECT discord_id, count FROM tester_overall ORDER BY count DESC LIMIT 10"
        cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    if not rows: return await interaction.response.send_message("✨ Žádné záznamy.", ephemeral=True)
    lines = [f"{i}. <@{d_id}>: {count} testů" for i, (d_id, count) in enumerate(rows, 1)]
    await interaction.response.send_message(embed=discord.Embed(title=title, description="\n".join(lines), color=discord.Color.gold()), ephemeral=True)

@bot.tree.command(name="language", description="Změní jazyk bota.")
@discord.app_commands.choices(jazyk=[discord.app_commands.Choice(name="🇨🇿 Čeština", value="cs")])
async def language(interaction: discord.Interaction, jazyk: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO server_settings (guild_id, language) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET language = ?", (str(interaction.guild.id), jazyk, jazyk))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "lang_set"), ephemeral=True)

@bot.tree.command(name="cooldownset", description="Nastaví cooldown pro LT nebo HT.")
@discord.app_commands.choices(typ=[discord.app_commands.Choice(name="LT", value="lt"), discord.app_commands.Choice(name="HT", value="ht")])
async def cooldownset(interaction: discord.Interaction, typ: str, cas: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    col = "cooldown_lt" if typ == "lt" else "cooldown_ht"
    cursor.execute(f"INSERT INTO server_settings (guild_id, {col}) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET {col} = ?", (str(interaction.guild.id), cas, cas))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "cooldown_set", tipo=typ.upper(), time=cas), ephemeral=True)

@bot.tree.command(name="removecooldown", description="Odstraní cooldown hráči.")
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

@bot.tree.command(name="cooldown", description="Zobrazí aktivní cooldowny hráče.")
async def cooldown(interaction: discord.Interaction, player: discord.Member):
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT kit, type, cooldown_until FROM player_cooldowns WHERE discord_id = ?", (str(player.id),))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return await interaction.response.send_message(f"✨ Uživatel {player.mention} nemá žádné aktivní cooldowny.", ephemeral=True)
        
    lt_lines, ht_lines = [], []
    now = datetime.datetime.now()
    for kit, typ, until in rows:
        try:
            dt = datetime.datetime.fromisoformat(until)
            if now < dt:
                line = f"**{kit.capitalize()}:** {dt.strftime('%d.%m.%Y %H:%M')}"
                if typ.lower() == "lt": lt_lines.append(line)
                else: ht_lines.append(line)
        except: pass
            
    parts = []
    if lt_lines:
        parts.append("__**LT Cooldowny**__")
        parts.extend(lt_lines)
    if ht_lines:
        if parts: parts.append("")
        parts.append("__**HT Cooldowny**__")
        parts.extend(ht_lines)
        
    if not parts:
        return await interaction.response.send_message(f"✨ Uživatel {player.mention} nemá žádné aktivní cooldowny.", ephemeral=True)
        
    await interaction.response.send_message(embed=discord.Embed(title=f"⏳ Cooldowny pro {player.display_name}", description="\n".join(parts), color=discord.Color.orange()), ephemeral=True)

@bot.tree.command(name="verify", description="Propojení účtu.")
async def verify(interaction: discord.Interaction, minecraft_ign: str):
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO verified (discord_id, minecraft_ign) VALUES (?, ?)", (str(interaction.user.id), minecraft_ign))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "verified_success", ign=minecraft_ign), ephemeral=True)

@bot.tree.command(name="createkit", description="Přidá kit.")
async def createkit(interaction: discord.Interaction, jmeno_kitu: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO kits (name) VALUES (?)", (jmeno_kitu.lower(),))
        conn.commit()
        await interaction.response.send_message(get_msg(interaction.guild.id, "kit_created", kit=jmeno_kitu), ephemeral=True)
    except:
        await interaction.response.send_message(get_msg(interaction.guild.id, "kit_exists", kit=jmeno_kitu), ephemeral=True)
    finally: conn.close()

@bot.tree.command(name="removekit", description="Odstraní kit.")
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

@bot.tree.command(name="tieroleset", description="Nastaví roli pro tier.")
@discord.app_commands.autocomplete(kit=kit_autocomplete, tier=tier_autocomplete)
async def tieroleset(interaction: discord.Interaction, kit: str, tier: str, role: discord.Role):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO tier_roles (kit, tier, role_id) VALUES (?, ?, ?)", (kit.lower(), clean_tier(tier), str(role.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "tier_role_set", kit=kit, tier=clean_tier(tier), role=role.name), ephemeral=True)

@bot.tree.command(name="resultroomset", description="Nastaví result místnost.")
async def resultroomset(interaction: discord.Interaction, discord_roomka: discord.TextChannel):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO server_settings (guild_id, result_room) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET result_room = ?", (str(interaction.guild.id), str(discord_roomka.id), str(discord_roomka.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "result_room_set", room=discord_roomka.mention), ephemeral=True)

@bot.tree.command(name="helperoleset", description="Nastaví helper roli.")
async def helperoleset(interaction: discord.Interaction, role: discord.Role):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO server_settings (guild_id, helper_role) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET helper_role = ?", (str(interaction.guild.id), str(role.id), str(role.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "helper_role_set", role=role.mention), ephemeral=True)

@bot.tree.command(name="queueroomset", description="Nastaví queue místnost.")
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

@bot.tree.command(name="kitcategoryset", description="Nastaví kategorii pro kit.")
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
        
        cursor.execute("SELECT cooldown_until FROM player_cooldowns WHERE discord_id = ? AND kit = ? AND type = 'lt'", (str(interaction.user.id), self.kit_name.lower()))
        cd_row = cursor.fetchone()
        if cd_row and cd_row[0]:
            try:
                dt = datetime.datetime.fromisoformat(cd_row[0])
                if datetime.datetime.now() < dt:
                    conn.close()
                    return await interaction.response.send_message(f"⏳ Máš aktivní LT cooldown do **{dt.strftime('%d.%m.%Y %H:%M')}**!", ephemeral=True)
            except: pass

        cursor.execute("SELECT minecraft_ign FROM verified WHERE discord_id = ?", (str(interaction.user.id),))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return await interaction.response.send_message(get_msg(interaction.guild.id, "not_verified"), ephemeral=True)

        if self.kit_name not in QUEUES: QUEUES[self.kit_name] = {"players": [], "testers": []}
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
    players_str = "\n".join([f"{i+1}. <@{pid}>" for i, pid in enumerate(data["players"])]) if data["players"] else get_msg(guild_id, "queue_empty")
    testers_str = "\n".join([f"{i+1}. <@{tid}>" for i, tid in enumerate(data["testers"])]) if data["testers"] else get_msg(guild_id, "no_testers")

    return discord.Embed(
        title=get_msg(guild_id, "queue_title", kit=kit_name.capitalize()),
        description=f"{get_msg(guild_id, 'queue_desc')}\n\n**Fronta:**\n{players_str}\n\n**{get_msg(guild_id, 'active_testers')}:**\n{testers_str}",
        color=discord.Color.blue()
    )

async def update_queue_message(channel, kit_name, guild_id):
    embed = get_queue_embed(kit_name, guild_id)
    async for message in channel.history(limit=10):
        if message.author == bot.user and message.embeds:
            await message.edit(embed=embed, view=QueueView(kit_name, guild_id))
            return
    await channel.send(embed=embed, view=QueueView(kit_name, guild_id))

@bot.tree.command(name="openqueue", description="Otevře queue.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def openqueue(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id FROM queue_rooms WHERE kit = ?", (kit.lower(),))
    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]: return await interaction.response.send_message("❌ Kanál nenalezen.", ephemeral=True)
    target_channel = interaction.guild.get_channel(int(row[0]))
    if not target_channel: return await interaction.response.send_message("❌ Kanál neexistuje.", ephemeral=True)

    try:
        async for message in target_channel.history(limit=50):
            if message.author == bot.user: await message.delete()
    except: pass

    QUEUES[kit.lower()] = {"players": [], "testers": []}
    await target_channel.send(content="@everyone", embed=get_queue_embed(kit.lower(), interaction.guild.id), view=QueueView(kit.lower(), interaction.guild.id))
    await interaction.response.send_message(get_msg(interaction.guild.id, "queue_opened", kit=kit, room=target_channel.mention), ephemeral=True)

@bot.tree.command(name="closequeue", description="Zavře queue.")
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
        ch = interaction.guild.get_channel(int(row[0]))
        if ch:
            closed_embed = discord.Embed(title=get_msg(interaction.guild.id, "closed_title", kit=kit.capitalize()), description=get_msg(interaction.guild.id, "closed_desc"), color=discord.Color.red())
            closed_embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
            async for message in ch.history(limit=10):
                if message.author == bot.user and message.embeds:
                    await message.edit(embed=closed_embed, view=None)
                    break
    await interaction.response.send_message(get_msg(interaction.guild.id, "queue_closed", kit=kit), ephemeral=True)

@bot.tree.command(name="joinqueueastester", description="Připojí testera.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def joinqueueastester(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    kit_key = kit.lower()
    if kit_key not in QUEUES: QUEUES[kit_key] = {"players": [], "testers": []}
    if interaction.user.id in QUEUES[kit_key]["testers"]: return await interaction.response.send_message(get_msg(interaction.guild.id, "already_tester"), ephemeral=True)
    QUEUES[kit_key]["testers"].append(interaction.user.id)
    await interaction.response.send_message(get_msg(interaction.guild.id, "tester_joined", kit=kit), ephemeral=True)
    
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id FROM queue_rooms WHERE kit = ?", (kit_key,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        ch = interaction.guild.get_channel(int(row[0]))
        if ch: await update_queue_message(ch, kit_key, interaction.guild.id)

@bot.tree.command(name="leavequeueastester", description="Odebere testera.")
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
            if ch: await update_queue_message(ch, kit_key, interaction.guild.id)
    else: await interaction.response.send_message(get_msg(interaction.guild.id, "not_tester"), ephemeral=True)

@bot.tree.command(name="result", description="Odešle výsledek testu.")
@discord.app_commands.autocomplete(kit=kit_autocomplete, tier=tier_autocomplete)
async def result(interaction: discord.Interaction, discord_hrac: discord.Member, kit: str, tier: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
    
    t_clean = clean_tier(tier)
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT minecraft_ign FROM verified WHERE discord_id = ?", (str(discord_hrac.id),))
    row = cursor.fetchone()
    cursor.execute("SELECT tier FROM player_tiers WHERE discord_id = ? AND kit = ?", (str(discord_hrac.id), kit.lower()))
    prev_row = cursor.fetchone()
    prev_tier = prev_row[0] if prev_row else "N/A"

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
    ym = datetime.datetime.now().strftime("%Y-%m")
    cursor.execute("INSERT INTO tester_monthly (discord_id, year_month, count) VALUES (?, ?, 1) ON CONFLICT(discord_id, year_month) DO UPDATE SET count = count + 1", (tester_id, ym))
    cursor.execute("INSERT INTO tester_overall (discord_id, count) VALUES (?, 1) ON CONFLICT(discord_id) DO UPDATE SET count = count + 1", (tester_id,))

    conn.commit()
    conn.close()

    mc_ign = row[0] if row else "Neznámý"
    if role_row and role_row[0]:
        role = interaction.guild.get_role(int(role_row[0]))
        if role:
            try: await discord_hrac.add_roles(role)
            except: pass

    embed = discord.Embed(title=get_msg(interaction.guild.id, "result_title", kit=kit), description=get_msg(interaction.guild.id, "result_desc", kit=kit), color=discord.Color.green())
    embed.add_field(name="👤 Hráč", value=discord_hrac.mention, inline=True)
    embed.add_field(name="🎮 IGN", value=mc_ign, inline=True)
    embed.add_field(name="⚔️ Tester", value=interaction.user.mention, inline=True)
    embed.add_field(name="📉 Předchozí", value=prev_tier, inline=True)
    embed.add_field(name="📈 Nový", value=t_clean, inline=True)
    embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y"))

    if mc_ign != "Neznámý": embed.set_thumbnail(url=f"https://visage.surgeplay.com/bust/512/{mc_ign}")
    if settings_row and settings_row[0]:
        room = interaction.guild.get_channel(int(settings_row[0]))
        if room: await room.send(content=f"📢 **Nový výsledek pro {kit}!** | Hráč: {discord_hrac.mention} | Tester: {interaction.user.mention}", embed=embed)

    await interaction.response.send_message(get_msg(interaction.guild.id, "result_sent"), ephemeral=True)
    await asyncio.sleep(3)
    try: await interaction.channel.delete()
    except: pass

async def handle_ping(request): return web.Response(text="Bot runs 24/7!")
async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()

TOKEN = os.getenv("DISCORD_TOKEN")
async def main():
    async with bot:
        await start_web_server()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
