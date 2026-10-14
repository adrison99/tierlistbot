import os
import sqlite3
import datetime
import asyncio
import discord
from discord.ext import commands
from aiohttp import web

# 1. Slovník překladů pro všechny požadované jazyky
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
        "kit_cat_set": "✅ Pro kit **{kit}** byla nastavena kategorie **{cat}**.",
        "lang_set": "🌐 Jazyk serveru byl změněn na **Čeština**.",
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
        "result_title": "📝 Tier Test Result – {kit}",
        "result_desc": "Tier test successfully completed for queue **{kit}**!",
        "result_sent": "✅ Result recorded, this channel will be deleted shortly.",
        "test_started": "⚔️ Test started! Tester: {tester} | Player: {player}\nWhen finished, use `/result` directly in this channel.",
        "player_pulled": "✅ Player {player} pulled to channel {room}!",
        "not_verified": "❌ You cannot join queue until verified via `/verify <minecraft ign>`!",
        "already_in_queue": "⚠️ You are already in this queue!",
        "left_queue": "✅ Left the queue.",
        "not_in_queue": "⚠️ You are not in this queue."
    },
    "en-us": {
        "no_perms": "❌ You don't have permission to use this command!",
        "verified_success": "✅ Successfully verified Minecraft account: **{ign}**",
        "kit_created": "✅ Kit **{kit}** has been successfully added to the database.",
        "kit_exists": "⚠️ Kit **{kit}** already exists in the database.",
        "kit_removed": "🗑️ Kit **{kit}** was deleted.",
        "tier_role_set": "✅ Role **{role}** set for kit **{kit}** and tier **{tier}**.",
        "result_room_set": "✅ Result channel set to {room}.",
        "helper_role_set": "✅ Helper role set to {role}.",
        "queue_room_set": "✅ Queue for kit **{kit}** linked to channel {room}.",
        "kit_cat_set": "✅ Category **{cat}** set for kit **{kit}**.",
        "lang_set": "🌐 Server language set to **English (American)**.",
        "queue_opened": "✅ Queue for kit **{kit}** successfully opened in channel {room}!",
        "queue_closed": "🔒 Queue for kit **{kit}** has been closed.",
        "cannot_close_active": "⚠️ Cannot close queue while tests are in progress!",
        "tester_joined": "✅ Successfully joined as active tester for kit **{kit}**.",
        "tester_left": "✅ Removed from active testers for kit **{kit}**.",
        "already_tester": "⚠️ You are already listed as a tester in this queue!",
        "not_tester": "⚠️ You are not listed as an active tester in this queue.",
        "join_btn": "Join Queue",
        "leave_btn": "Leave Queue",
        "pull_btn": "Pull Player ⚔️",
        "queue_empty": "_Queue is empty. Be first!_",
        "no_testers": "_No active testers._",
        "active_testers": "Active Testers",
        "queue_title": "📝 {kit} Waitlist",
        "queue_desc": "⏱️ Queue updates automatically.\nUse buttons below to join or leave.",
        "result_title": "📝 Tier Test Result – {kit}",
        "result_desc": "Tier test successfully completed for queue **{kit}**!",
        "result_sent": "✅ Result logged, channel deleting soon.",
        "test_started": "⚔️ Test started! Tester: {tester} | Player: {player}\nWhen done, run `/result` in this channel.",
        "player_pulled": "✅ Player {player} pulled to {room}!",
        "not_verified": "❌ You can't join queue until you link your account with `/verify <minecraft ign>`!",
        "already_in_queue": "⚠️ You're already in this queue!",
        "left_queue": "✅ Left queue.",
        "not_in_queue": "⚠️ You're not in this queue."
    },
    "sk": {
        "no_perms": "❌ Na tento príkaz nemáš oprávnenie!",
        "verified_success": "✅ Úspešne verifikovaný Minecraft účet: **{ign}**",
        "kit_created": "✅ Kit **{kit}** bol úspešne pridaný do databázy.",
        "kit_exists": "⚠️ Kit **{kit}** už v databáze existuje.",
        "kit_removed": "🗑️ Kit **{kit}** bol odstránený.",
        "tier_role_set": "✅ Pre kit **{kit}** a tier **{tier}** bola nastavená rola **{role}**.",
        "result_room_set": "✅ Result miestnosť nastavená na {room}.",
        "helper_role_set": "✅ Helper rola nastavená na {role}.",
        "queue_room_set": "✅ Fronta pre kit **{kit}** zviazaná s kanálom {room}.",
        "kit_cat_set": "✅ Pre kit **{kit}** bola nastavená kategória **{cat}**.",
        "lang_set": "🌐 Jazyk servera bol zmenený na **Slovenčinu**.",
        "queue_opened": "✅ Fronta pre kit **{kit}** bola úspešne otvorená v kanáli {room}!",
        "queue_closed": "🔒 Fronta pre kit **{kit}** bola zatvorená.",
        "cannot_close_active": "⚠️ Nemôžeš zatvoriť frontu, pretože v nej stále prebiehajú testy!",
        "tester_joined": "✅ Úspešne si sa pridal ako aktívny tester pre kit **{kit}**.",
        "tester_left": "✅ Bol si odobraný z aktívnych testerov pre kit **{kit}**.",
        "already_tester": "⚠️ Už si zapísaný ako tester v tejto fronte!",
        "not_tester": "⚠️ Nie si vedený ako aktívny tester v tejto fronte.",
        "join_btn": "Vstúpiť do fronty",
        "leave_btn": "Opustiť frontu",
        "pull_btn": "Vytiahnuť hráča ⚔️",
        "queue_empty": "_Fronta je prázdna. Buď prvý!_",
        "no_testers": "_Žiadni aktívni testeri._",
        "active_testers": "Aktívni Testeri",
        "queue_title": "📝 {kit} Waitlist",
        "queue_desc": "⏱️ Fronta sa aktualizuje automaticky.\nPouži tlačidlá nižšie pre pridanie alebo odobranie.",
        "result_title": "📝 Výsledok tier testu – {kit}",
        "result_desc": "Tier test bol úspešne dokončený pre frontu **{kit}**!",
        "result_sent": "✅ Výsledok bol úspešne zaznamenaný a táto miestnosť bude o chvíľu zmazaná.",
        "test_started": "⚔️ Test začína! Tester: {tester} | Hráč: {player}\nPo dokončení zadajte `/result` priamo v tomto kanáli.",
        "player_pulled": "✅ Hráč {player} bol vytiahnutý do miestnosti {room}!",
        "not_verified": "❌ Nemôžeš vstúpiť do fronty, kým sa neprepojíš cez `/verify <minecraft ign>`!",
        "already_in_queue": "⚠️ Už si v tejto fronte!",
        "left_queue": "✅ Si vonku z fronty.",
        "not_in_queue": "⚠️ Nie si v tejto fronte."
    },
    "de": {
        "no_perms": "❌ Du hast keine Berechtigung für diesen Befehl!",
        "verified_success": "✅ Minecraft-Konto erfolgreich verifiziert: **{ign}**",
        "kit_created": "✅ Kit **{kit}** wurde zur Datenbank hinzugefügt.",
        "kit_exists": "⚠️ Kit **{kit}** existiert bereits.",
        "kit_removed": "🗑️ Kit **{kit}** wurde entfernt.",
        "tier_role_set": "✅ Rolle **{role}** für Kit **{kit}** und Tier **{tier}** festgelegt.",
        "result_room_set": "✅ Ergebniskanal auf {room} gesetzt.",
        "helper_role_set": "✅ Helper-Rolle auf {role} gesetzt.",
        "queue_room_set": "✅ Warteschlange für Kit **{kit}** an Kanal {room} gebunden.",
        "kit_cat_set": "✅ Kategorie **{cat}** für Kit **{kit}** festgelegt.",
        "lang_set": "🌐 Serversprache auf **Deutsch** geändert.",
        "queue_opened": "✅ Warteschlange für Kit **{kit}** in Kanal {room} geöffnet!",
        "queue_closed": "🔒 Warteschlange für Kit **{kit}** wurde geschlossen.",
        "cannot_close_active": "⚠️ Warteschlange kann während aktiver Tests nicht geschlossen werden!",
        "tester_joined": "✅ Erfogreich als aktiver Tester für Kit **{kit}** beigetreten.",
        "tester_left": "✅ Als aktiver Tester für Kit **{kit}** entfernt.",
        "already_tester": "⚠️ Du bist bereits als Tester in dieser Warteschlange eingetragen!",
        "not_tester": "⚠️ Du bist kein aktiver Tester in dieser Warteschlange.",
        "join_btn": "Warteschlange beitreten",
        "leave_btn": "Warteschlange verlassen",
        "pull_btn": "Spieler ziehen ⚔️",
        "queue_empty": "_Warteschlange ist leer. Sei der Erste!_",
        "no_testers": "_Keine aktiven Tester._",
        "active_testers": "Aktive Tester",
        "queue_title": "📝 {kit} Warteliste",
        "queue_desc": "⏱️ Warteschlange aktualisiert sich automatisch.",
        "result_title": "📝 Tier-Testergebnis – {kit}",
        "result_desc": "Tier-Test für Kit **{kit}** erfolgreich abgeschlossen!",
        "result_sent": "✅ Ergebnis gespeichert, Kanal wird in Kürze gelöscht.",
        "test_started": "⚔️ Test startet! Tester: {tester} | Spieler: {player}",
        "player_pulled": "✅ Spieler {player} in Kanal {room} gezogen!",
        "not_verified": "❌ Bitte verifiziere dich zuerst mit `/verify <minecraft ign>`!",
        "already_in_queue": "⚠️ Du bist bereits in dieser Warteschlange!",
        "left_queue": "✅ Warteschlange verlassen.",
        "not_in_queue": "⚠️ Du bist nicht in dieser Warteschlange."
    },
    "fr": {
        "no_perms": "❌ Vous n'avez pas la permission d'utiliser cette commande !",
        "verified_success": "✅ Compte Minecraft vérifié avec succès : **{ign}**",
        "kit_created": "✅ Le kit **{kit}** a été ajouté à la base de données.",
        "kit_exists": "⚠️ Le kit **{kit}** existe déjà.",
        "kit_removed": "🗑️ Le kit **{kit}** a été supprimé.",
        "tier_role_set": "✅ Rôle **{role}** défini pour le kit **{kit}** et le tier **{tier}**.",
        "result_room_set": "✅ Salon des résultats défini sur {room}.",
        "helper_role_set": "✅ Rôle Helper défini sur {role}.",
        "queue_room_set": "✅ File d'attente pour le kit **{kit}** liée au salon {room}.",
        "kit_cat_set": "✅ Catégorie **{cat}** définie pour le kit **{kit}**.",
        "lang_set": "🌐 Langue du serveur changée en **Français**.",
        "queue_opened": "✅ File d'attente pour le kit **{kit}** ouverte dans {room} !",
        "queue_closed": "🔒 File d'attente pour le kit **{kit}** fermée.",
        "cannot_close_active": "⚠️ Impossible de fermer la file d'attente pendant les tests actifs !",
        "tester_joined": "✅ Ajouté comme testeur actif pour le kit **{kit}**.",
        "tester_left": "✅ Retiré des testeurs actifs pour le kit **{kit}**.",
        "already_tester": "⚠️ Vous êtes déjà inscrit comme testeur !",
        "not_tester": "⚠️ Vous n'êtes pas testeur actif dans cette file.",
        "join_btn": "Rejoindre la file",
        "leave_btn": "Quitter la file",
        "pull_btn": "Tirer le joueur ⚔️",
        "queue_empty": "_File vide. Soyez le premier !_",
        "no_testers": "_Aucun testeur actif._",
        "active_testers": "Testeurs Actifs",
        "queue_title": "📝 File d'attente {kit}",
        "queue_desc": "⏱️ La file s'actualise automatiquement.",
        "result_title": "📝 Résultat du Test Tier – {kit}",
        "result_desc": "Test réussi pour le kit **{kit}** !",
        "result_sent": "✅ Résultat enregistré, salon en cours de suppression.",
        "test_started": "⚔️ Le test commence ! Testeur: {tester} | Joueur: {player}",
        "player_pulled": "✅ Joueur {player} tiré dans le salon {room} !",
        "not_verified": "❌ Veuillez vous vérifier avec `/verify <minecraft ign>` !",
        "already_in_queue": "⚠️ Vous êtes déjà dans cette file !",
        "left_queue": "✅ Vous avez quitté la file.",
        "not_in_queue": "⚠️ Vous n'êtes pas dans cette file."
    },
    "ru": {
        "no_perms": "❌ У вас нет прав для выполнения этой команды!",
        "verified_success": "✅ Аккаунт Minecraft успешно привязан: **{ign}**",
        "kit_created": "✅ Набор **{kit}** успешно добавлен в базу данных.",
        "kit_exists": "⚠️ Набор **{kit}** уже существует.",
        "kit_removed": "🗑️ Набор **{kit}** был удален.",
        "tier_role_set": "✅ Роль **{role}** установлена для набора **{kit}** и уровня **{tier}**.",
        "result_room_set": "✅ Канал результатов установлен на {room}.",
        "helper_role_set": "✅ Роль помощника установлена на {role}.",
        "queue_room_set": "✅ Очередь для набора **{kit}** привязана к каналу {room}.",
        "kit_cat_set": "✅ Категория **{cat}** установлена для набора **{kit}**.",
        "lang_set": "🌐 Язык сервера изменен на **Русский**.",
        "queue_opened": "✅ Очередь для набора **{kit}** открыта в канале {room}!",
        "queue_closed": "🔒 Очередь для набора **{kit}** закрыта.",
        "cannot_close_active": "⚠️ Нельзя закрыть очередь во время активных тестов!",
        "tester_joined": "✅ Вы успешно записались как активный тестер для набора **{kit}**.",
        "tester_left": "✅ Вы удалены из списка активных тестеров набора **{kit}**.",
        "already_tester": "⚠️ Вы уже записаны как тестер в этой очереди!",
        "not_tester": "⚠️ Вы не являетесь активным тестером в этой очереди.",
        "join_btn": "Войти в очередь",
        "leave_btn": "Выйти из очереди",
        "pull_btn": "Вызвать игрока ⚔️",
        "queue_empty": "_Очередь пуста. Будьте первым!_",
        "no_testers": "_Нет активных тестеров._",
        "active_testers": "Активные Тестеры",
        "queue_title": "📝 Очередь {kit}",
        "queue_desc": "⏱️ Очередь обновляется автоматически.",
        "result_title": "📝 Результат теста – {kit}",
        "result_desc": "Тест успешно завершен для набора **{kit}**!",
        "result_sent": "✅ Результат записан, канал скоро будет удален.",
        "test_started": "⚔️ Тест начался! Тестер: {tester} | Игрок: {player}",
        "player_pulled": "✅ Игрок {player} вызван в канал {room}!",
        "not_verified": "❌ Сначала авторизуйтесь через `/verify <minecraft ign>`!",
        "already_in_queue": "⚠️ Вы уже в очереди!",
        "left_queue": "✅ Вы вышли из очереди.",
        "not_in_queue": "⚠️ Вы не в очереди."
    },
    "it": {
        "no_perms": "❌ Non hai i permessi per usare questo comando!",
        "verified_success": "✅ Account Minecraft verificato con successo: **{ign}**",
        "kit_created": "✅ Il kit **{kit}** è stato aggiunto al database.",
        "kit_exists": "⚠️ Il kit **{kit}** esiste già.",
        "kit_removed": "🗑️ Il kit **{kit}** è stato rimosso.",
        "tier_role_set": "✅ Ruolo **{role}** impostato per il kit **{kit}** e tier **{tier}**.",
        "result_room_set": "✅ Canale risultati impostato su {room}.",
        "helper_role_set": "✅ Ruolo Helper impostato su {role}.",
        "queue_room_set": "✅ Coda per il kit **{kit}** collegata al canale {room}.",
        "kit_cat_set": "✅ Categoria **{cat}** impostata per il kit **{kit}**.",
        "lang_set": "🌐 Lingua del server impostata su **Italiano**.",
        "queue_opened": "✅ Coda per il kit **{kit}** aperta nel canale {room}!",
        "queue_closed": "🔒 Coda per il kit **{kit}** chiusa.",
        "cannot_close_active": "⚠️ Impossibile chiudere la coda con test attivi!",
        "tester_joined": "✅ Aggiunto come tester attivo per il kit **{kit}**.",
        "tester_left": "✅ Rimosso dai tester attivi per il kit **{kit}**.",
        "already_tester": "⚠️ Sei già registrato come tester in questa coda!",
        "not_tester": "⚠️ Non sei un tester attivo in questa coda.",
        "join_btn": "Entra in coda",
        "leave_btn": "Esci dalla coda",
        "pull_btn": "Pulla giocatore ⚔️",
        "queue_empty": "_La coda è vuota. Sii il primo!_",
        "no_testers": "_Nessun tester attivo._",
        "active_testers": "Tester Attivi",
        "queue_title": "📝 Coda {kit}",
        "queue_desc": "⏱️ La coda si aggiorna automaticamente.",
        "result_title": "📝 Risultato Test Tier – {kit}",
        "result_desc": "Test completato con successo per il kit **{kit}**!",
        "result_sent": "✅ Risultato registrato, il canale verrà eliminato a breve.",
        "test_started": "⚔️ Il test inizia! Tester: {tester} | Giocatore: {player}",
        "player_pulled": "✅ Giocatore {player} spostato nel canale {room}!",
        "not_verified": "❌ Verificati prima con `/verify <minecraft ign>`!",
        "already_in_queue": "⚠️ Sei già in questa coda!",
        "left_queue": "✅ Sei uscito dalla coda.",
        "not_in_queue": "⚠️ Non sei in questa coda."
    },
    "es": {
        "no_perms": "❌ ¡No tienes permiso para usar este comando!",
        "verified_success": "✅ Cuenta de Minecraft verificada con éxito: **{ign}**",
        "kit_created": "✅ Kit **{kit}** añadido con éxito a la base de datos.",
        "kit_exists": "⚠️ El kit **{kit}** ya existe en la base de datos.",
        "kit_removed": "🗑️ El kit **{kit}** fue eliminado.",
        "tier_role_set": "✅ Rol **{role}** configurado para kit **{kit}** y tier **{tier}**.",
        "result_room_set": "✅ Canal de resultados configurado en {room}.",
        "helper_role_set": "✅ Rol de Helper configurado en {role}.",
        "queue_room_set": "✅ Cola para el kit **{kit}** vinculada al canal {room}.",
        "kit_cat_set": "✅ Categoría **{cat}** configurada para el kit **{kit}**.",
        "lang_set": "🌐 Idioma del servidor cambiado a **Español**.",
        "queue_opened": "✅ Cola para el kit **{kit}** abierta con éxito en {room}!",
        "queue_closed": "🔒 La cola para el kit **{kit}** ha sido cerrada.",
        "cannot_close_active": "⚠️ ¡No se puede cerrar la cola mientras haya pruebas activas!",
        "tester_joined": "✅ Te has unido como probador activo para el kit **{kit}**.",
        "tester_left": "✅ Eliminado de los probadores activos para el kit **{kit}**.",
        "already_tester": "⚠️ ¡Ya estás registrado como probador en esta cola!",
        "not_tester": "⚠️ No estás registrado como probador activo en esta cola.",
        "join_btn": "Unirse a la cola",
        "leave_btn": "Salir de la cola",
        "pull_btn": "Jalar jugador ⚔️",
        "queue_empty": "_La cola está vacía. ¡Sé el primero!_",
        "no_testers": "_No hay probadores activos._",
        "active_testers": "Probadores Activos",
        "queue_title": "📝 Lista de espera {kit}",
        "queue_desc": "⏱️ La cola se actualiza automáticamente.",
        "result_title": "📝 Resultado de la Prueba Tier – {kit}",
        "result_desc": "¡Prueba completada con éxito para el kit **{kit}**!",
        "result_sent": "✅ Resultado registrado, el canal se eliminará pronto.",
        "test_started": "⚔️ ¡La prueba comienza! Probador: {tester} | Jugador: {player}",
        "player_pulled": "✅ ¡Jugador {player} movido al canal {room}!",
        "not_verified": "❌ ¡Debes verificarte primero usando `/verify <minecraft ign>`!",
        "already_in_queue": "⚠️ ¡Ya estás en esta cola!",
        "left_queue": "✅ Saliste de la cola.",
        "not_in_queue": "⚠️ No estás en esta cola."
    }
}

def get_msg(guild_id: int, key: str, **kwargs) -> str:
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM server_settings WHERE guild_id = ?", (str(guild_id),))
    row = cursor.fetchone()
    conn.close()
    
    lang = row[0] if row and row[0] in TRANSLATIONS else "cs"
    msg = TRANSLATIONS[lang].get(key, TRANSLATIONS["cs"].get(key, ""))
    return msg.format(**kwargs)

# 2. Inicializace databáze
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
            language TEXT DEFAULT 'cs'
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS queue_rooms (kit TEXT PRIMARY KEY, channel_id TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS kit_categories (kit TEXT PRIMARY KEY, category_id TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS player_tiers (discord_id TEXT, kit TEXT, tier TEXT, PRIMARY KEY (discord_id, kit))")
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

# --- PŘÍKAZ PRO ZMĚNU JAZYKA ---
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
    cursor.execute("""
        INSERT INTO server_settings (guild_id, language) VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET language = ?
    """, (str(interaction.guild.id), jazyk, jazyk))
    conn.commit()
    conn.close()

    await interaction.response.send_message(get_msg(interaction.guild.id, "lang_set"), ephemeral=True)

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
    cursor.execute("""
        INSERT INTO server_settings (guild_id, result_room) VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET result_room = ?
    """, (str(interaction.guild.id), str(discord_roomka.id), str(discord_roomka.id)))
    conn.commit()
    conn.close()
    await interaction.response.send_message(get_msg(interaction.guild.id, "result_room_set", room=discord_roomka.mention), ephemeral=True)

@bot.tree.command(name="helperoleset", description="Nastaví roli pro používání bota.")
async def helperoleset(interaction: discord.Interaction, role: discord.Role):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)
        
    conn = sqlite3.connect("tierbot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO server_settings (guild_id, helper_role) VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET helper_role = ?
    """, (str(interaction.guild.id), str(role.id), str(role.id)))
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
        conn.close()

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

        target_category = None
        if cat_row and cat_row[0]:
            target_category = interaction.guild.get_channel(int(cat_row[0]))

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            player: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        channel_name = f"{mc_ign.lower()}-test"
        test_channel = await interaction.guild.create_text_channel(
            name=channel_name,
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

    if players_list:
        players_str = "\n".join([f"{i+1}. <@{pid}>" for i, pid in enumerate(players_list)])
    else:
        players_str = get_msg(guild_id, "queue_empty")

    if testers_list:
        testers_str = "\n".join([f"{i+1}. <@{tid}>" for i, tid in enumerate(testers_list)])
    else:
        testers_str = get_msg(guild_id, "no_testers")

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

    channel_id = int(row[0])
    target_channel = interaction.guild.get_channel(channel_id)
    if not target_channel:
        return await interaction.response.send_message("❌ Kanál nebyl nalezen.", ephemeral=True)

    QUEUES[kit.lower()] = {"players": [], "testers": [interaction.user.id]}
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

    if kit_key in QUEUES:
        QUEUES.pop(kit_key)

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

@bot.tree.command(name="leavequeueastester", description="Odebere tě ze seznamu testerů.")
@discord.app_commands.autocomplete(kit=kit_autocomplete)
async def leavequeueastester(interaction: discord.Interaction, kit: str):
    if not await has_helper_perms(interaction):
        return await interaction.response.send_message(get_msg(interaction.guild.id, "no_perms"), ephemeral=True)

    kit_key = kit.lower()
    if kit_key in QUEUES and interaction.user.id in QUEUES[kit_key]["testers"]:
        QUEUES[kit_key]["testers"].remove(interaction.user.id)
        await interaction.response.send_message(get_msg(interaction.guild.id, "tester_left", kit=kit), ephemeral=True)
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
