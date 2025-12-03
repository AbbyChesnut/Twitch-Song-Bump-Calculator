import streamlit as st
import json

# --- Persistence ---
DATA_FILE = "users.json"

def load_users():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

users = load_users()

# --- Prices ---
tier1_price = 5.99
tier2_price = 9.99
tier3_price = 24.99

# --- Streamlit UI ---
st.title("🎵 Twitch Song Bump Calculator")

# Add User
st.subheader("Add or Edit User")
user_name = st.text_input("Username")

if st.button("Add User"):
    if user_name in users:
        st.warning(f"{user_name} already exists.")
    else:
        users[user_name] = {
            "monetary_total": 0.0,
            "resub_tier": 0,
            "resub_total": 0.0,
            "tier1": 0,
            "tier2": 0,
            "tier3": 0,
            "gifted_subs_count": 0,
            "gifted_subs_total": 0.0,
            "num_bits": 0,
            "bits_total": 0.0,
            "donos": 0.0,
            "bumpable": False,
        }
        save_users(users)
        st.success(f"{user_name} added!")

# Contribution Updates
st.subheader("Update Contributions")
if user_name and user_name in users:
    choice = st.radio("Contribution Type", ["Resub", "Gifted", "Bits", "Dono"])
    if choice == "Resub":
        tier = st.selectbox("Tier", [1, 2, 3])
        if st.button("Add Resub"):
            if tier == 1:
                users[user_name]["resub_total"] += tier1_price
            elif tier == 2:
                users[user_name]["resub_total"] += tier2_price
            elif tier == 3:
                users[user_name]["resub_total"] += tier3_price
            users[user_name]["resub_tier"] = tier
            save_users(users)
            st.success(f"Resub Tier {tier} added to {user_name}")

    elif choice == "Gifted":
        gifted_amt = st.number_input("Number of Gifted Subs", min_value=1, step=1)
        gifted_tier = st.selectbox("Gifted Tier", [1, 2, 3])
        if st.button("Add Gifted"):
            if gifted_tier == 1:
                users[user_name]["gifted_subs_total"] += gifted_amt * tier1_price
                users[user_name]["tier1"] += gifted_amt
            elif gifted_tier == 2:
                users[user_name]["gifted_subs_total"] += gifted_amt * tier2_price
                users[user_name]["tier2"] += gifted_amt
            elif gifted_tier == 3:
                users[user_name]["gifted_subs_total"] += gifted_amt * tier3_price
                users[user_name]["tier3"] += gifted_amt
            users[user_name]["gifted_subs_count"] += gifted_amt
            save_users(users)
            st.success(f"{gifted_amt} Tier {gifted_tier} gifted subs added to {user_name}")

    elif choice == "Bits":
        bit_amt = st.number_input("Number of Bits", min_value=1, step=1)
        if st.button("Add Bits"):
            users[user_name]["bits_total"] += round(bit_amt * 0.01, 2)
            users[user_name]["num_bits"] += bit_amt
            save_users(users)
            st.success(f"{bit_amt} bits added to {user_name}")

    elif choice == "Dono":
        dono_amt = st.number_input("Donation Amount ($)", min_value=0.01, step=0.01)
        if st.button("Add Dono"):
            users[user_name]["donos"] += round(dono_amt, 2)
            save_users(users)
            st.success(f"${dono_amt:.2f} donation added to {user_name}")

# Leaderboard
st.subheader("Leaderboard")
if users:
    sorted_users = sorted(users.items(), key=lambda item: item[1]['monetary_total'], reverse=True)
    for name, data in sorted_users:
        total = round(data["resub_total"] + data["gifted_subs_total"] + data["bits_total"] + data["donos"], 2)
        bump_status = (data["num_bits"] >= 500 or data["resub_tier"] >= 2 or 
                       data["gifted_subs_count"] >= 2 or data["donos"] >= 5 or 
                       data["tier2"] >= 1 or data["tier3"] >= 1 or total > 5.99)
        data["monetary_total"] = total
        data["bumpable"] = bump_status
        st.write(f"**{name}** | Total: ${total:.2f} | {'Bumpable' if bump_status else 'Not Bumpable'}")
else:
    st.info("No users yet.")
