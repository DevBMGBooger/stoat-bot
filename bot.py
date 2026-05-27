import stoat
import json
import os
import random

client = stoat.Client()


# ---------------------------
# RANK DATABASE FILE
# ---------------------------

RANK_FILE = "rank.json"

if not os.path.exists(RANK_FILE):
    with open(RANK_FILE, "w") as f:
        json.dump({}, f, indent=4)

# ----------------------------
# LOAD RANKS
# ----------------------------

def load_ranks():
    with open ("RANK_FILE", "r") as f:
        json.dump({}, f, indent=4)

# ----------------------------
# SAVE RANKS
# ----------------------------

def save_ranks(data):
    with open(RANK_FILE, "w") as f:
        json.dump(data, f, indent=4)



        

# ----------------------------
# WARNING DATABASE FILE
# ----------------------------

WARN_FILE = "warnings.json"

# Create warning database if missing
if not os.path.exists(WARN_FILE):
    with open(WARN_FILE, "w") as f:
        json.dump({}, f, indent=4)

# ----------------------------
# LOAD WARNINGS
# ----------------------------

def load_warnings():
    with open(WARN_FILE, "r") as f:
        return json.load(f)

# ----------------------------
# SAVE WARNINGS
# ----------------------------

def save_warnings(data):
    with open(WARN_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ----------------------------
# GENERATE UNIQUE WARNING ID
# ----------------------------

def generate_warn_id():
    return str(random.randint(100000, 999999))




# ----------------------------
# READY EVENT
# ----------------------------

@client.on(stoat.ReadyEvent)
async def ready(event):
    print(f"Logged in as {event.me.tag}")

# ----------------------------
# MESSAGE EVENT
# ----------------------------

@client.on(stoat.MessageCreateEvent)
async def message(event):

    msg = event.message

    # Ignore bots
    if msg.author.bot:
        return


    # =========================================================
    # /createrank COMMAND
    # Usage:
    # /createrank Name 1-5
    # =========================================================

    if msg.content.startswith("/warn"):
        parts = msg.content.split(" ", 2)

        if len(parts) < 3:
            await msg.channel.send(
                "❌ Usage: \n"
                "/createrank Name, 1-5."
            )
            return
        target = parts[1]
        rank = parts[2]

        ranks = load_ranks()

        if server_id not in ranks:
            ranks[server_id] = {}

        if target not in ranks[server_id]:
            ranks[server_id][target] = []

        if rank not in ranks[server_id]:
            ranks[server_id][target] = []

        save_ranks(ranks)

        ranks[server_id][target].append({
            "Name": target,
            "RankNumber": rank,
        }) 

        await msg.channel.send(
            f"⚠️ Rank named {target} has been created",
            f"⚠️ Rank was given {rank} permission",
        )

    # =========================================================
    # /warn COMMAND
    # Usage:
    # /warn USERNAME_OR_USERID REASON
    # =========================================================

    if msg.content.startswith("/warn"):

        parts = msg.content.split(" ", 2)

        if len(parts) < 3:
            await msg.channel.send(
                "❌ Usage:\n"
                "/warn USERNAME_OR_USERID REASON"
            )
            return

        target = parts[1]
        reason = parts[2]

        # Current server ID
        server_id = str(msg.channel.server_id)

        warnings = load_warnings()

        # Create server section if missing
        if server_id not in warnings:
            warnings[server_id] = {}

        # Create user section if missing
        if target not in warnings[server_id]:
            warnings[server_id][target] = []

        # Generate unique warning ID
        warn_id = generate_warn_id()

        # Add warning
        warnings[server_id][target].append({
            "id": warn_id,
            "moderator": msg.author.name,
            "reason": reason
        })

        # Save database
        save_warnings(warnings)

        # Confirmation message
        await msg.channel.send(
            f"⚠️ {target} has been warned.\n"
            f"Warning ID: {warn_id}\n"
            f"Reason: {reason}"
        )

    # =========================================================
    # /warnings COMMAND
    # Usage:
    # /warnings WARNING_ID
    # =========================================================

    if msg.content.startswith("/warnings"):

        parts = msg.content.split(" ", 1)

        if len(parts) < 2:
            await msg.channel.send(
                "❌ Usage:\n"
                "/warnings WARNING_ID"
            )
            return

        warn_id = parts[1]

        server_id = str(msg.channel.server_id)

        warnings = load_warnings()

        # Check if server exists
        if server_id not in warnings:
            await msg.channel.send(
                "❌ No warnings exist in this server."
            )
            return

        found = False

        # Search current server only
        for user in warnings[server_id]:

            user_warns = warnings[server_id][user]

            for warn in user_warns:

                if warn["id"] == warn_id:

                    found = True

                    response = (
                        f"⚠️ Warning Found\n\n"
                        f"User: {user}\n"
                        f"Warning ID: {warn['id']}\n"
                        f"Reason: {warn['reason']}\n"
                        f"Moderator: {warn['moderator']}"
                    )

                    await msg.channel.send(response)

                    break

            if found:
                break

        # Warning not found
        if not found:
            await msg.channel.send(
                "❌ Warning ID not found in this server."
            )

    # =========================================================
    # /unwarn COMMAND
    # Usage:
    # /unwarn WARNING_ID
    # =========================================================

    if msg.content.startswith("/unwarn"):

        parts = msg.content.split(" ", 1)

        if len(parts) < 2:
            await msg.channel.send(
                "❌ Usage:\n"
                "/unwarn WARNING_ID"
            )
            return

        warn_id = parts[1]

        server_id = str(msg.channel.server_id)

        warnings = load_warnings()

        # Check if server exists
        if server_id not in warnings:
            await msg.channel.send(
                "❌ No warnings exist in this server."
            )
            return

        found = False

        # Search current server only
        for user in warnings[server_id]:

            user_warns = warnings[server_id][user]

            for warn in user_warns:

                if warn["id"] == warn_id:

                    user_warns.remove(warn)

                    found = True

                    # Save database
                    save_warnings(warnings)

                    await msg.channel.send(
                        f"✅ Warning {warn_id} has been removed from {user}."
                    )

                    break

            if found:
                break

        # Warning not found
        if not found:
            await msg.channel.send(
                "❌ Warning ID not found in this server."
            )

# ----------------------------
# START BOT
# ----------------------------

client.run("91qudXeynh0CRRQMsrXJOVL9ro_LvB5Ab9D6wFB07dVFyOwjxztPYa0OsLXcTwYx")