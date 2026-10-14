import os
import sqlite3
import datetime
import asyncio
import discord
from discord.ext import commands

# 1. Nastavení databáze SQLite
def init_db():
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verified (
            discord_id TEXT PRIMARY KEY,
            minecraft_ign TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kits (
            name TEXT PRIMARY KEY
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tier_roles (
            kit TEXT,
            tier TEXT,
            role_id TEXT,
            PRIMARY KEY (kit, tier)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS server_settings (
            guild_id TEXT PRIMARY KEY,
            result_room TEXT,
            helper_role TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queue_rooms (
            kit TEXT PRIMARY KEY,
            channel_id TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_tiers (
            discord_id TEXT,
            kit TEXT,
            tier TEXT,
            PRIMARY KEY (discord_id, kit)
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

VALID_TIERS = [
    "LT5", "HT5", "LT4", "HT4", "LT3", "HT3", 
    "RLT2", "LT2", "RHT2", "HT2", "RLT1", "LT1", "RHT1", "HT1"
]

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
    return [
        discord.app_commands.Choice(name=kit, value=kit)
        for kit in kits if current.lower() in kit.lower()
    ]

async def tier_autocomplete(interaction: discord.Interaction, current: str):
    return [
        discord.app_commands.Choice(name=tier, value=tier)
        for tier in VALID_TIERS if current.lower() in tier.lower()
    ]

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} je online!")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synchrováno {len(synced)} slash příkazů.")
    except Exception as e:
        print(f"❌ Chyba synchronizace: {e}")

@bot.tree.command(name="verify", description="Propojí tvůj Discord účet s Minecraft IGN.")
async def verify(interaction: discord.Interaction, minecraft_ign: str):
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO verified (discord_id, minecraft_ign) VALUES (?, ?)", 
                   (str(interaction.user.id), minecraft_ign))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ Úspěšně verifikován Minecraft účet: **{minecraft_ign}**", ephemeral=True)

@bot.tree.command(name="createkit", description="Přidá nový kit do databáze.")
async def createkit(interaction: discord.Interaction, jmeno_kitu: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message("❌ Na tento příkaz nemáš oprávnění!", ephemeral=True)
    
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO kits (name) VALUES (?)", (jmeno_kitu.lower(),))
        conn.commit()
        await interaction.response.send_message(f"✅ Kit **{jmeno_kitu}** byl úspěšně přidán do databáze.", ephemeral=True)
    except sqlite3.IntegrityError:
        await interaction.response.send_message(f"⚠️ Kit **{jmeno_kitu}** již v databázi existuje.", ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(name="removekit", description="Odstraní kit z databáze.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def removekit(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message("❌ Na tento příkaz nemáš oprávnění!", ephemeral=True)
    
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kits WHERE name = ?", (kit.lower(),))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"🗑️ Kit **{kit}** byl odstraněn.", ephemeral=True)

@bot.tree.command(name="tieroleset", description="Nastaví roli pro daný kit a tier.")
@discord.app_commands.autocomplete(kit=kit_autocomplete, tier=tier_autocomplete)
async def tieroleset(interaction: discord.Interaction, kit: str, tier: str, role: discord.Role):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message("❌ Na tento příkaz nemáš oprávnění!", ephemeral=True)
    
    if tier not in VALID_TIERS:
        return await interaction.response.send_message("❌ Neplatný tier!", ephemeral=True)
        
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO tier_roles (kit, tier, role_id) VALUES (?, ?, ?)",
                   (kit.lower(), tier, str(role.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ Pro kit **{kit}** a tier **{tier}** byla nastavená role **{role.name}**.", ephemeral=True)

@bot.tree.command(name="resultroomset", description="Nastaví místnost pro posílání výsledků.")
async def resultroomset(interaction: discord.Interaction, discord_roomka: discord.TextChannel):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message("❌ Na tento příkaz nemáš oprávnění!", ephemeral=True)
        
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO server_settings (guild_id, result_room, helper_role) 
        VALUES (?, ?, (SELECT helper_role FROM server_settings WHERE guild_id = ?))
        ON CONFLICT(guild_id) DO UPDATE SET result_room = ?
    """, (str(interaction.guild.id), str(discord_roomka.id), str(interaction.guild.id), str(discord_roomka.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ Result místnost nastavena na {discord_roomka.mention}.", ephemeral=True)

@bot.tree.command(name="helperoleset", description="Nastaví roli, která má oprávnění používat tyto příkazy.")
async def helperoleset(interaction: discord.Interaction, role: discord.Role):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message("❌ Na tento příkaz nemáš oprávnění!", ephemeral=True)
        
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO server_settings (guild_id, result_room, helper_role) 
        VALUES (?, (SELECT result_room FROM server_settings WHERE guild_id = ?), ?)
        ON CONFLICT(guild_id) DO UPDATE SET helper_role = ?
    """, (str(interaction.guild.id), str(interaction.guild.id), str(role.id), str(role.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ Helper role nastavena na {role.mention}.", ephemeral=True)

@bot.tree.command(name="queueroomset", description="Nastaví textový kanál pro frontu daného kitu.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def queueroomset(interaction: discord.Interaction, discord_roomka: discord.TextChannel, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message("❌ Na tento příkaz nemáš oprávnění!", ephemeral=True)
        
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO queue_rooms (kit, channel_id) VALUES (?, ?)", (kit.lower(), str(discord_roomka.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ Fronta pro kit **{kit}** svázána s kanálem {discord_roomka.mention}.", ephemeral=True)

QUEUES = {}

class QueueView(discord.ui.View):
    def __init__(self, kit_name: str):
        super().__init__(timeout=None)
        self.kit_name = kit_name

    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.primary, custom_id="join_queue")
    async def join_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = sqlite3.connect("tierbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT minecraft_ign FROM verified WHERE discord_id = ?", (str(interaction.user.id),))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return await interaction.response.send_message("❌ Nemůžeš vstoupit do fronty, dokud se nepropojíš přes `/verify <minecraft ign>`!", ephemeral=True)

        if self.kit_name not in QUEUES:
            QUEUES[self.kit_name] = {"players": [], "testers": []}

        if interaction.user.id in QUEUES[self.kit_name]["players"]:
            return await interaction.response.send_message("⚠️ Už jsi v této frontě!", ephemeral=True)

        QUEUES[self.kit_name]["players"].append(interaction.user.id)
        await interaction.response.send_message("✅ Úspěšně jsi vstoupil do fronty!", ephemeral=True)
        await update_queue_message(interaction.channel, self.kit_name)

    @discord.ui.button(label="Leave Queue", style=discord.ButtonStyle.danger, custom_id="leave_queue")
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.kit_name in QUEUES and interaction.user.id in QUEUES[self.kit_name]["players"]:
            QUEUES[self.kit_name]["players"].remove(interaction.user.id)
            await interaction.response.send_message("✅ Jsi venku z fronty.", ephemeral=True)
            await update_queue_message(interaction.channel, self.kit_name)
        else:
            await interaction.response.send_message("⚠️ Nejsi v této frontě.", ephemeral=True)

    @discord.ui.button(label="Pull Player ⚔️", style=discord.ButtonStyle.success, custom_id="pull_player")
    async def pull_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await has_helper_perms(interaction):
            return await interaction.response.send_message("❌ Pouze testeré mohou vytahovat hráče z fronty!", ephemeral=True)

        if self.kit_name not in QUEUES or not QUEUES[self.kit_name]["players"]:
            return await interaction.response.send_message("⚠️ Fronta je prázdná!", ephemeral=True)

        if interaction.user.id not in QUEUES[self.kit_name]["testers"]:
            QUEUES[self.kit_name]["testers"].append(interaction.user.id)

        player_id = QUEUES[self.kit_name]["players"].pop(0)
        player = interaction.guild.get_member(player_id)
        
        await update_queue_message(interaction.channel, self.kit_name)
        
        if not player:
            return await interaction.response.send_message("⚠️ Hráč již není na serveru.", ephemeral=True)

        await interaction.response.send_message(f"⚔️ Vytáhl jsi hráče {player.mention}. Nastavuji přístup do soukromé místnosti...", ephemeral=True)
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            player: discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True, speak=True),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True, speak=True)
        }
        category = interaction.channel.category
        room = await interaction.guild.create_text_channel(name=f"test-{player.name}", category=category, overwrites=overwrites)
        await room.send(f"🎮 Test začíná! Tester: {interaction.user.mention} vs Hráč: {player.mention}. Až skončíte, použijte `/result` v původní místnosti.")

def get_queue_embed(kit_name: str):
    data = QUEUES.get(kit_name, {"players": [], "testers": []})
    players_list = data["players"]
    testers_list = data["testers"]

    if players_list:
        players_str = "\n".join([f"{i+1}. <@{pid}>" for i, pid in enumerate(players_list)])
    else:
        players_str = "_Fronta je prázdná. Buď první!_"

    if testers_list:
        testers_str = "\n".join([f"{i+1}. <@{tid}>" for i, tid in enumerate(testers_list)])
    else:
        testers_str = "_Žádní aktivní testeři._"

    embed = discord.Embed(
        title=f"📝 {kit_name.capitalize()} Waitlist",
        description=f"⏱️ Fronta se aktualizuje automaticky.\nPoužij tlačítka níže pro přidání nebo odebrání.\n\n**Fronta:**\n{players_str}\n\n**Aktivní Testeři:**\n{testers_str}",
        color=discord.Color.blue()
    )
    return embed

async def update_queue_message(channel, kit_name):
    embed = get_queue_embed(kit_name)
    async for message in channel.history(limit=10):
        if message.author == bot.user and message.embeds:
            await message.edit(embed=embed, view=QueueView(kit_name))
            return
    await channel.send(embed=embed, view=QueueView(kit_name))

@bot.tree.command(name="openqueue", description="Otevře queue pro daný kit v nastaveném kanálu.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def openqueue(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message("❌ Na tento příkaz nemáš oprávnění!", ephemeral=True)
    
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id FROM queue_rooms WHERE kit = ?", (kit.lower(),))
    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        return await interaction.response.send_message(f"❌ Pro kit **{kit}** není nastavena queue místnost! Použij nejdříve `/queueroomset`.", ephemeral=True)

    channel_id = int(row[0])
    target_channel = interaction.guild.get_channel(channel_id)
    if not target_channel:
        return await interaction.response.send_message("❌ Nastavený kanál pro frontu nebyl na serveru nalezen.", ephemeral=True)

    if kit.lower() not in QUEUES:
        QUEUES[kit.lower()] = {"players": [], "testers": [interaction.user.id]}
    else:
        if interaction.user.id not in QUEUES[kit.lower()]["testers"]:
            QUEUES[kit.lower()]["testers"].append(interaction.user.id)

    embed = get_queue_embed(kit.lower())
    
    await target_channel.send(content="@everyone", embed=embed, view=QueueView(kit.lower()))
    await interaction.response.send_message(f"✅ Fronta pro kit **{kit}** byla úspěšně otevřena v kanálu {target_channel.mention}!", ephemeral=True)

@bot.tree.command(name="result", description="Odešle výsledek testu do result místnosti.")
@discord.app_commands.autocomplete(kit=kit_autocomplete, tier=tier_autocomplete)
async def result(interaction: discord.Interaction, discord_hrac: discord.Member, kit: str, tier: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message("❌ Na tento příkaz nemáš oprávnění!", ephemeral=True)

    if tier not in VALID_TIERS:
        return await interaction.response.send_message("❌ Neplatný tier!", ephemeral=True)

    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT minecraft_ign FROM verified WHERE discord_id = ?", (str(discord_hrac.id),))
    row = cursor.fetchone()

    cursor.execute("SELECT tier FROM player_tiers WHERE discord_id = ? AND kit = ?", (str(discord_hrac.id), kit.lower()))
    prev_row = cursor.fetchone()
    prev_tier = prev_row[0] if prev_row else "N/A"

    cursor.execute("INSERT OR REPLACE INTO player_tiers (discord_id, kit, tier) VALUES (?, ?, ?)",
                   (str(discord_hrac.id), kit.lower(), tier))
    
    cursor.execute("SELECT role_id FROM tier_roles WHERE kit = ? AND tier = ?", (kit.lower(), tier))
    role_row = cursor.fetchone()

    cursor.execute("SELECT result_room FROM server_settings WHERE guild_id = ?", (str(interaction.guild.id),))
    settings_row = cursor.fetchone()
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
        title=f"📝 Výsledek tier testu – {kit}",
        description=f"Tier test byl úspěšně dokončen pro frontu **{kit}**!",
        color=discord.Color.green()
    )
    embed.add_field(name="👤 Hráč (Discord)", value=discord_hrac.mention, inline=True)
    embed.add_field(name="🎮 Minecraft IGN", value=mc_ign, inline=True)
    embed.add_field(name="⚔️ Tester", value=interaction.user.mention, inline=True)
    embed.add_field(name="📊 Skóre / Výsledek", value="3–0 (Tester vyhrál)", inline=False)
    embed.add_field(name="📉 Předchozí tier", value=prev_tier, inline=True)
    embed.add_field(name="📈 Nový tier", value=tier, inline=True)
    embed.set_footer(text=dnes)

    if settings_row and settings_row[0]:
        room_id = int(settings_row[0])
        room = interaction.guild.get_channel(room_id)
        if room:
            await room.send(content=f"📢 **Nový výsledek pro {kit}!** | Hráč: {discord_hrac.mention} | Tester: {interaction.user.mention}", embed=embed)
        else:
            await interaction.channel.send(content=f"📢 **Nový výsledek pro {kit}!** | Hráč: {discord_hrac.mention} | Tester: {interaction.user.mention}", embed=embed)
    else:
        await interaction.channel.send(content=f"📢 **Nový výsledek pro {kit}!** | Hráč: {discord_hrac.mention} | Tester: {interaction.user.mention}", embed=embed)
    
    if interaction.channel.name.startswith("test-"):
        await interaction.response.send_message("✅ Výsledek byl odeslán a testovací místnost bude smazána.", ephemeral=True)
        await asyncio.sleep(3)
        await interaction.channel.delete()
    else:
        await interaction.response.send_message("✅ Výsledek byl úspěšně zaznamenán a odeslán!", ephemeral=True)

TOKEN = os.getenv("DISCORD_TOKEN")
if __name__ == "__main__":
    bot.run(TOKEN)
