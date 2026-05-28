import stoat
import json
import os
import random
import requests

client = stoat.Client()

# =========================================================
# DATABASE FILES
# =========================================================

RANK_FILE = "ranks.json"
WARN_FILE = "warnings.json"
RBLX_FILE = "roblox_setup.json"

# Create database files if missing
for file in [RANK_FILE, WARN_FILE, RBLX_FILE]:

    if not os.path.exists(file):

        with open(file, "w") as f:
            json.dump({}, f, indent=4)

# =========================================================
# LOAD / SAVE FUNCTIONS
# =========================================================

def load_ranks():
    with open(RANK_FILE, "r") as f:
        return json.load(f)

def save_ranks(data):
    with open(RANK_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_warnings():
    with open(WARN_FILE, "r") as f:
        return json.load(f)

def save_warnings(data):
    with open(WARN_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_rblx():
    with open(RBLX_FILE, "r") as f:
        return json.load(f)

def save_rblx(data):
    with open(RBLX_FILE, "w") as f:
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

    try:

        # Server owner bypass
        if msg is not None:

            if hasattr(msg.channel, "server"):

                server = msg.channel.server

                if str(server.owner_id) == str(msg.author.id):
                    return 999

    except Exception as e:
        print(e)

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

    if msg.author.bot:
        return

    server_id = str(msg.channel.server_id)

# =================================================
# /verify
# Usage:
# /verify ROBLOX_USER_ID
# =================================================

if msg.content.startswith("/verify"):

    parts = msg.content.split(" ")

    if len(parts) < 2:

        await msg.channel.send(
            "❌ Usage:\n/verify ROBLOX_USER_ID"
        )

        return

    roblox_id = parts[1]

    # Make sure ID is numbers only
    if not roblox_id.isdigit():

        await msg.channel.send(
            "❌ Roblox User ID must be numbers only."
        )

        return

    try:

        response = requests.get(
            f"https://users.roblox.com/v1/users/{roblox_id}"
        )

        if response.status_code != 200:

            await msg.channel.send(
                "❌ Invalid Roblox User ID."
            )

            return

        data = response.json()

        roblox_username = data["name"]

        verify_code = str(random.randint(100000, 999999))

        verify_data = load_verify()

        verify_data[user_id] = {
            "roblox_username": roblox_username,
            "roblox_id": roblox_id,
            "verify_code": verify_code,
            "verified": False
        }

        save_verify(verify_data)

        await msg.channel.send(
            f"🔐 Verification Started\n\n"
            f"🎮 Roblox User: {roblox_username}\n"
            f"🆔 Roblox ID: {roblox_id}\n\n"
            f"Put THIS code in your Roblox profile description:\n\n"
            f"{verify_code}\n\n"
            f"Then run:\n"
            f"/confirmverify"
        )

    except Exception as e:

        print(e)

        await msg.channel.send(
            "❌ Failed to connect to Roblox."
        )

# =================================================
# /confirmverify
# =================================================

if msg.content.startswith("/confirmverify"):

    verify_data = load_verify()

    if user_id not in verify_data:

        await msg.channel.send(
            "❌ Start verification first with /verify"
        )

        return

    roblox_id = verify_data[user_id]["roblox_id"]
    verify_code = verify_data[user_id]["verify_code"]

    try:

        response = requests.get(
            f"https://users.roblox.com/v1/users/{roblox_id}"
        )

        if response.status_code != 200:

            await msg.channel.send(
                "❌ Failed to find Roblox account."
            )

            return

        data = response.json()

        description = data.get("description", "")

        if verify_code not in description:

            await msg.channel.send(
                "❌ Verification code was not found in your Roblox description.\n\n"
                "Make sure you pasted the code EXACTLY."
            )

            return

        verify_data[user_id]["verified"] = True

        save_verify(verify_data)

        await msg.channel.send(
            f"✅ Roblox Account Verified\n\n"
            f"🎮 Username: {verify_data[user_id]['roblox_username']}\n"
            f"🆔 Roblox ID: {roblox_id}"
        )

    except Exception as e:

        print(e)

        await msg.channel.send(
            "❌ Verification failed."
        )
    # =====================================================
    # /setupRBLX
    # =====================================================

    if msg.content.startswith("/setupRBLX"):

        await msg.channel.send(
            "🤖 Roblox Setup Commands\n\n"
            "/setupGroupId GROUP_ID\n"
            "/setupRankPerm RANK_NAME LEVEL\n"
            "/setupNames ROBLOX_ROLE STOAT_RANK"
        )

    # =====================================================
    # /setupGroupId
    # =====================================================

    if msg.content.startswith("/setupGroupId"):

        parts = msg.content.split(" ")

        if len(parts) < 2:

            await msg.channel.send(
                "❌ Usage:\n/setupGroupId GROUP_ID"
            )

            return

        group_id = parts[1]

        if not group_id.isdigit():

            await msg.channel.send(
                "❌ Group ID must be numbers only."
            )

            return

        url = f"https://groups.roblox.com/v1/groups/{group_id}"

        try:

            response = requests.get(url)

            if response.status_code != 200:

                await msg.channel.send(
                    "❌ Invalid Roblox Group ID."
                )

                return

            data = response.json()

            group_name = data["name"]

            roblox_data = load_rblx()

            if server_id not in roblox_data:
                roblox_data[server_id] = {}

            roblox_data[server_id]["group_id"] = group_id
            roblox_data[server_id]["group_name"] = group_name

            save_rblx(roblox_data)

            await msg.channel.send(
                f"✅ Roblox Group Connected\n\n"
                f"🏢 Group: {group_name}\n"
                f"🆔 Group ID: {group_id}"
            )

        except Exception as e:

            print(e)

            await msg.channel.send(
                "❌ Failed to connect to Roblox API."
            )

            return 
        
        group_id = parts[1]

        if not group_id.isdigit():

            await msg.channel.send(
                "❌ Group ID must be numbers only."
            )

            return

        url = f"https://groups.roblox.com/v1/groups/{group_id}"



    # =====================================================
    # /unconnectGroupId
    # =====================================================

    

    # =====================================================
    # /setupRankPerm
    # =====================================================

    if msg.content.startswith("/setupRankPerm"):

        parts = msg.content.split(" ")

        if len(parts) < 3:

            await msg.channel.send(
                "❌ Usage:\n/setupRankPerm RankName Level"
            )

            return

        rank_name = parts[1]

        try:
            level = int(parts[2])

        except:

            await msg.channel.send(
                "❌ Level must be a number."
            )

            return

        roblox_data = load_rblx()

        if server_id not in roblox_data:
            roblox_data[server_id] = {}

        if "rank_permissions" not in roblox_data[server_id]:
            roblox_data[server_id]["rank_permissions"] = {}

        roblox_data[server_id]["rank_permissions"][rank_name] = level

        save_rblx(roblox_data)

        await msg.channel.send(
            f"✅ Rank Permission Saved\n\n"
            f"🏅 Rank: {rank_name}\n"
            f"📊 Level: {level}"
        )

    # =====================================================
    # /setupNames
    # =====================================================

    if msg.content.startswith("/setupNames"):

        parts = msg.content.split(" ")

        if len(parts) < 3:

            await msg.channel.send(
                "❌ Usage:\n/setupNames ROBLOX_ROLE STOAT_RANK"
            )

            return

        roblox_role = parts[1]
        stoat_rank = parts[2]

        roblox_data = load_rblx()

        if server_id not in roblox_data:
            roblox_data[server_id] = {}

        if "role_links" not in roblox_data[server_id]:
            roblox_data[server_id]["role_links"] = {}

        roblox_data[server_id]["role_links"][roblox_role] = stoat_rank

        save_rblx(roblox_data)

        await msg.channel.send(
            f"✅ Roblox Role Linked\n\n"
            f"🎮 Roblox Role: {roblox_role}\n"
            f"🤖 Stoat Rank: {stoat_rank}"
        )

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
                "❌ You need rank level 3 or higher."
            )

            return

        parts = msg.content.split(" ")

        if len(parts) < 3:

            await msg.channel.send(
                "❌ Usage:\n/createrank RankName 1-5"
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

        if rank_level >= user_rank:

            await msg.channel.send(
                "❌ You can only create lower ranks than yourself."
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
                "❌ You need rank level 3 or higher."
            )

            return

        parts = msg.content.split(" ")

        if len(parts) < 3:

            await msg.channel.send(
                "❌ Usage:\n/rank USER RankName"
            )

            return

        target_user = parts[1]
        rank_name = parts[2]

        ranks = load_ranks()

        if server_id not in ranks:

            await msg.channel.send(
                "❌ No ranks exist."
            )

            return

        if rank_name not in ranks[server_id]["rank_definitions"]:

            await msg.channel.send(
                "❌ Rank does not exist."
            )

            return

        rank_level = ranks[server_id]["rank_definitions"][rank_name]

        if rank_level >= user_rank:

            await msg.channel.send(
                "❌ You can only assign lower ranks than yourself."
            )

            return

        target_rank = get_user_rank_level(
            server_id,
            target_user
        )

        if target_rank >= user_rank:

            await msg.channel.send(
                "❌ Cannot modify equal or higher ranks."
            )

            return

        ranks[server_id]["users"][target_user] = {
            "rank_name": rank_name,
            "rank_level": rank_level
        }

        save_ranks(ranks)

        await msg.channel.send(
            f"✅ {target_user} ranked as {rank_name}."
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
                "❌ You need rank level 1 or higher."
            )

            return

        parts = msg.content.split(" ", 2)

        if len(parts) < 3:

            await msg.channel.send(
                "❌ Usage:\n/warn USER REASON"
            )

            return

        target = parts[1]
        reason = parts[2]

        target_rank = get_user_rank_level(
            server_id,
            target
        )

        if target_rank >= user_rank:

            await msg.channel.send(
                "❌ Cannot warn equal or higher ranks."
            )

            return

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
            f"⚠️ {target} warned.\n"
            f"ID: {warn_id}\n"
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
