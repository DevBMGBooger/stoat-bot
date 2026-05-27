import stoat
import json
import os
import random

client = stoat.Client()

# =========================================================
# RANK DATABASE FILE
# =========================================================

RANK_FILE = "ranks.json"

if not os.path.exists(RANK_FILE):
    with open(RANK_FILE, "w") as f:
        json.dump({}, f, indent=4)

# =========================================================
# WARNING DATABASE FILE
# =========================================================

WARN_FILE = "warnings.json"

if not os.path.exists(WARN_FILE):
    with open(WARN_FILE, "w") as f:
        json.dump({}, f, indent=4)

# =========================================================
# LOAD / SAVE RANKS
# =========================================================

def load_ranks():
    with open(RANK_FILE, "r") as f:
        return json.load(f)

def save_ranks(data):
    with open(RANK_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================================================
# LOAD / SAVE WARNINGS
# =========================================================

def load_warnings():
    with open(WARN_FILE, "r") as f:
        return json.load(f)

def save_warnings(data):
    with open(WARN_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================================================
# GENERATE WARNING ID
# =========================================================

def generate_warn_id():
    return str(random.randint(100000, 999999))

# =========================================================
# GET USER RANK LEVEL
# =========================================================

def get_user_rank_level(server_id, username, msg=None):

    # SERVER OWNER ALWAYS HAS FULL ACCESS
    try:

        if msg is not None:

            if hasattr(msg.channel, "server"):

                server = msg.channel.server

                # If user is server owner
                if str(server.owner_id) == str(msg.author.id):
                    return 999

    except Exception as e:
        print(f"Owner check failed: {e}")

    ranks = load_ranks()

    if server_id not in ranks:
        return 0

    if "users" not in ranks[server_id]:
        return 0

    if username not in ranks[server_id]["users"]:
        return 0

    return ranks[server_id]["users"][username]["rank_level"]

# =========================================================
# READY EVENT
# =========================================================

@client.on(stoat.ReadyEvent)
async def ready(event):
    print(f"Logged in as {event.me.tag}")

# =========================================================
# MESSAGE EVENT
# =========================================================

@client.on(stoat.MessageCreateEvent)
async def message(event):

    msg = event.message

    # Ignore bots
    if msg.author.bot:
        return

    server_id = str(msg.channel.server_id)

    # =====================================================
    # /createrank
    # =====================================================

    if msg.content.startswith("/createrank"):

        user_rank = get_user_rank_level(
            server_id,
            msg.author.name,
            msg
        )

        if user_rank < 3:
            await msg.channel.send(
                "❌ You need rank level 3 or higher to use rank commands."
            )
            return

        parts = msg.content.split(" ")

        if len(parts) < 3:
            await msg.channel.send(
                "❌ Usage:\n"
                "/createrank RankName 1-5"
            )
            return

        rank_name = parts[1]

        try:
            rank_level = int(parts[2])
        except:
            await msg.channel.send(
                "❌ Rank level must be a number."
            )
            return

        if rank_level < 1 or rank_level > 5:
            await msg.channel.send(
                "❌ Rank level must be between 1 and 5."
            )
            return

        ranks = load_ranks()

        if server_id not in ranks:
            ranks[server_id] = {
                "rank_definitions": {},
                "users": {}
            }

        ranks[server_id]["rank_definitions"][rank_name] = rank_level

        save_ranks(ranks)

        await msg.channel.send(
            f"✅ Created rank '{rank_name}' with level {rank_level}."
        )

    # =====================================================
    # /rank
    # =====================================================

    if msg.content.startswith("/rank"):

        user_rank = get_user_rank_level(
            server_id,
            msg.author.name,
            msg
        )

        if user_rank < 3:
            await msg.channel.send(
                "❌ You need rank level 3 or higher to use rank commands."
            )
            return

        parts = msg.content.split(" ")

        if len(parts) < 3:
            await msg.channel.send(
                "❌ Usage:\n"
                "/rank USER RankName"
            )
            return

        target_user = parts[1]
        rank_name = parts[2]

        ranks = load_ranks()

        if server_id not in ranks:
            await msg.channel.send(
                "❌ No ranks exist in this server."
            )
            return

        if rank_name not in ranks[server_id]["rank_definitions"]:
            await msg.channel.send(
                "❌ That rank does not exist."
            )
            return

        rank_level = ranks[server_id]["rank_definitions"][rank_name]

        ranks[server_id]["users"][target_user] = {
            "rank_name": rank_name,
            "rank_level": rank_level
        }

        save_ranks(ranks)

        await msg.channel.send(
            f"✅ {target_user} has been ranked '{rank_name}'."
        )

    # =====================================================
    # /unrank
    # =====================================================

    if msg.content.startswith("/unrank"):

        user_rank = get_user_rank_level(
            server_id,
            msg.author.name,
            msg
        )

        if user_rank < 3:
            await msg.channel.send(
                "❌ You need rank level 3 or higher to use rank commands."
            )
            return

        parts = msg.content.split(" ")

        if len(parts) < 2:
            await msg.channel.send(
                "❌ Usage:\n"
                "/unrank USER"
            )
            return

        target_user = parts[1]

        # Prevent demoting server owner
        try:

            if hasattr(msg.channel, "server"):

                server = msg.channel.server

                owner_member = await server.fetch_member(
                    server.owner_id
                )

                if owner_member.name == target_user:

                    await msg.channel.send(
                        "❌ You cannot demote the server owner."
                    )

                    return

        except Exception as e:
            print(f"Owner protection failed: {e}")

        ranks = load_ranks()

        if server_id not in ranks:
            await msg.channel.send(
                "❌ No ranks exist in this server."
            )
            return

        ranks[server_id]["users"][target_user] = {
            "rank_name": "Unranked",
            "rank_level": 0
        }

        save_ranks(ranks)

        await msg.channel.send(
            f"✅ {target_user} has been unranked."
        )

    # =====================================================
    # /checkrank
    # =====================================================

    if msg.content.startswith("/checkrank"):

        parts = msg.content.split(" ")

        if len(parts) < 2:
            await msg.channel.send(
                "❌ Usage:\n"
                "/checkrank USER"
            )
            return

        target_user = parts[1]

        # Show owner automatically
        try:

            if hasattr(msg.channel, "server"):

                server = msg.channel.server

                owner_member = await server.fetch_member(
                    server.owner_id
                )

                if owner_member.name == target_user:

                    await msg.channel.send(
                        f"👑 {target_user} is the Server Owner.\n"
                        f"🏅 Rank Level: 999"
                    )

                    return

        except Exception as e:
            print(f"Owner check failed: {e}")

        ranks = load_ranks()

        if (
            server_id not in ranks or
            target_user not in ranks[server_id]["users"]
        ):
            await msg.channel.send(
                f"❌ {target_user} has no rank."
            )
            return

        user_rank_data = ranks[server_id]["users"][target_user]

        await msg.channel.send(
            f"👤 User: {target_user}\n"
            f"🏅 Rank: {user_rank_data['rank_name']}\n"
            f"📊 Level: {user_rank_data['rank_level']}"
        )

    # =====================================================
    # /warn
    # =====================================================

    if msg.content.startswith("/warn"):

        user_rank = get_user_rank_level(
            server_id,
            msg.author.name,
            msg
        )

        if user_rank < 1:
            await msg.channel.send(
                "❌ You need rank level 1 or higher to use warn commands."
            )
            return

        parts = msg.content.split(" ", 2)

        if len(parts) < 3:
            await msg.channel.send(
                "❌ Usage:\n"
                "/warn USER REASON"
            )
            return

        target = parts[1]
        reason = parts[2]

        warnings = load_warnings()

        if server_id not in warnings:
            warnings[server_id] = {}

        if target not in warnings[server_id]:
            warnings[server_id][target] = []

        warn_id = generate_warn_id()

        warnings[server_id][target].append({
            "id": warn_id,
            "moderator": msg.author.name,
            "reason": reason
        })

        save_warnings(warnings)

        await msg.channel.send(
            f"⚠️ {target} has been warned.\n"
            f"Warning ID: {warn_id}\n"
            f"Reason: {reason}"
        )

    # =====================================================
    # /warnings
    # =====================================================

    if msg.content.startswith("/warnings"):

        user_rank = get_user_rank_level(
            server_id,
            msg.author.name,
            msg
        )

        if user_rank < 1:
            await msg.channel.send(
                "❌ You need rank level 1 or higher to use warn commands."
            )
            return

        parts = msg.content.split(" ", 1)

        if len(parts) < 2:
            await msg.channel.send(
                "❌ Usage:\n"
                "/warnings WARNING_ID"
            )
            return

        warn_id = parts[1]

        warnings = load_warnings()

        if server_id not in warnings:
            await msg.channel.send(
                "❌ No warnings exist in this server."
            )
            return

        found = False

        for user in warnings[server_id]:

            for warn in warnings[server_id][user]:

                if warn["id"] == warn_id:

                    found = True

                    await msg.channel.send(
                        f"⚠️ Warning Found\n\n"
                        f"User: {user}\n"
                        f"Warning ID: {warn['id']}\n"
                        f"Reason: {warn['reason']}\n"
                        f"Moderator: {warn['moderator']}"
                    )

                    break

            if found:
                break

        if not found:
            await msg.channel.send(
                "❌ Warning ID not found in this server."
            )

    # =====================================================
    # /unwarn
    # =====================================================

    if msg.content.startswith("/unwarn"):

        user_rank = get_user_rank_level(
            server_id,
            msg.author.name,
            msg
        )

        if user_rank < 1:
            await msg.channel.send(
                "❌ You need rank level 1 or higher to use warn commands."
            )
            return

        parts = msg.content.split(" ", 1)

        if len(parts) < 2:
            await msg.channel.send(
                "❌ Usage:\n"
                "/unwarn WARNING_ID"
            )
            return

        warn_id = parts[1]

        warnings = load_warnings()

        if server_id not in warnings:
            await msg.channel.send(
                "❌ No warnings exist in this server."
            )
            return

        found = False

        for user in warnings[server_id]:

            for warn in warnings[server_id][user]:

                if warn["id"] == warn_id:

                    warnings[server_id][user].remove(warn)

                    found = True

                    save_warnings(warnings)

                    await msg.channel.send(
                        f"✅ Warning {warn_id} removed from {user}."
                    )

                    break

            if found:
                break

        if not found:
            await msg.channel.send(
                "❌ Warning ID not found in this server."
            )

# =========================================================
# KEEP BOT ONLINE
# =========================================================

while True:

    try:

        client.run("91qudXeynh0CRRQMsrXJOVL9ro_LvB5Ab9D6wFB07dVFyOwjxztPYa0OsLXcTwYx")

    except Exception as e:

        print(f"Bot crashed: {e}")
        print("Restarting bot...")