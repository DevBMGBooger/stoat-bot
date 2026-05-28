import stoat
import json
import os
import random
import requests

client = stoat.Client()

# =====================================================
# DATABASE FILES
# =====================================================

RANK_FILE = "ranks.json"
WARN_FILE = "warnings.json"
RBLX_FILE = "roblox_setup.json"

# =====================================================
# CREATE FILES IF MISSING
# =====================================================

for file in [RANK_FILE, WARN_FILE, RBLX_FILE]:

    if not os.path.exists(file):

        with open(file, "w") as f:
            json.dump({}, f, indent=4)

# =====================================================
# LOAD / SAVE FUNCTIONS
# =====================================================

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

# =====================================================
# GENERATE WARNING ID
# =====================================================

def generate_warn_id():

    return str(random.randint(100000, 999999))

# =====================================================
# GET USER RANK LEVEL
# =====================================================

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

# =====================================================
# READY EVENT
# =====================================================

@client.on(stoat.ReadyEvent)
async def ready(event):

    print(f"Logged in as {event.me.tag}")

# =====================================================
# MESSAGE EVENT
# =====================================================

@client.on(stoat.MessageCreateEvent)
async def message(event):

    msg = event.message

    if msg.author.bot:
        return

    server_id = str(msg.channel.server_id)

    # =================================================
    # /setupRBLX
    # =================================================

    if msg.content.startswith("/setupRBLX"):

        setup_table = (
            "╔════════════════════════════╗\n"
            "║     ROBLOX SETUP GUIDE     ║\n"
            "╠════════════════════════════╣\n"
            "║ /setupGroupId GROUP_ID     ║\n"
            "║ /setupRankPerm NAME LEVEL  ║\n"
            "║ /setupNames ROLE RANK      ║\n"
            "║ /unconnectGroupId          ║\n"
            "╚════════════════════════════╝"
        )

        await msg.channel.send(setup_table)

    # =================================================
    # /setupGroupId
    # =================================================

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
                f"🆔 ID: {group_id}"
            )

        except Exception as e:

            print(e)

            await msg.channel.send(
                "❌ Failed to connect to Roblox API."
            )

    # =================================================
    # /unconnectGroupId
    # =================================================

    if msg.content.startswith("/unconnectGroupId"):

        roblox_data = load_rblx()

        if server_id not in roblox_data:

            await msg.channel.send(
                "❌ No Roblox group connected."
            )

            return

        if "group_id" not in roblox_data[server_id]:

            await msg.channel.send(
                "❌ No Roblox group connected."
            )

            return

        old_group_id = roblox_data[server_id]["group_id"]

        old_group_name = roblox_data[server_id].get(
            "group_name",
            "Unknown Group"
        )

        roblox_data[server_id].pop("group_id", None)
        roblox_data[server_id].pop("group_name", None)
        roblox_data[server_id].pop("role_links", None)
        roblox_data[server_id].pop("rank_permissions", None)

        save_rblx(roblox_data)

        await msg.channel.send(
            f"✅ Roblox group disconnected.\n\n"
            f"🏢 Group: {old_group_name}\n"
            f"🆔 Removed ID: {old_group_id}"
        )

    # =================================================
    # /setupRankPerm
    # =================================================

    if msg.content.startswith("/setupRankPerm"):

        parts = msg.content.split(" ")

        if len(parts) < 3:

            await msg.channel.send(
                "❌ Usage:\n/setupRankPerm NAME LEVEL"
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

    # =================================================
    # /setupNames
    # =================================================

    if msg.content.startswith("/setupNames"):

        parts = msg.content.split(" ")

        if len(parts) < 3:

            await msg.channel.send(
                "❌ Usage:\n/setupNames ROLE STOAT_RANK"
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
# START BOT
# =====================================================

client.run("BOT TOKEN")
