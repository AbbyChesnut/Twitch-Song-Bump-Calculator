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

# --- NEW HELPER FUNCTION ---
# This function replicates the logic from your original print_users_by_total
def get_contribution_string(user_data):
    """Generates a detailed contribution string for a user."""
    contributions = []
    
    # Resub check
    if user_data['resub_tier'] == 3:
        contributions.append("Tier 3 resub")
    elif user_data['resub_tier'] == 2:
        contributions.append("Tier 2 resub")
    elif user_data['resub_tier'] == 1:
        contributions.append("Resub")

    # Gifted sub tier 1 check
    if user_data['tier1'] > 1:
        contributions.append(f"{user_data['tier1']} Tier 1 gifted subs")
    elif user_data['tier1'] == 1:
        contributions.append("Tier 1 gifted sub")
    
    # Gifted sub tier 2 check
    if user_data['tier2'] > 1:
        contributions.append(f"{user_data['tier2']} Tier 2 gifted subs")
    elif user_data['tier2'] == 1:
        contributions.append("Tier 2 gifted sub")

    # Gifted sub tier 3 check
    if user_data['tier3'] > 1:
        contributions.append(f"{user_data['tier3']} Tier 3 gifted subs")
    elif user_data['tier3'] == 1:
        contributions.append("Tier 3 gifted sub")
    
    # Bits check
    if user_data["num_bits"] > 1:
        contributions.append(f"{user_data['num_bits']} bits")
    elif user_data["num_bits"] == 1:
        contributions.append("1 bit")

    # Dono check
    if user_data["donos"] > 0:
        dono_amt = user_data["donos"]
        # Check if it's a whole number
        if dono_amt == int(dono_amt):
            contributions.append(f"${int(dono_amt)} dono")
        else:
            contributions.append(f"${dono_amt:.2f} dono")
    
    if not contributions:
        return "No contributions yet."

    return ", ".join(contributions).capitalize()

# --- Load users ---
users = load_users()

# --- Prices ---
tier1_price = 5.99
tier2_price = 9.99
tier3_price = 24.99

# --- Streamlit UI ---
st.title("🎵 Twitch Song Bump Calculator")

# --- Leaderboard (MODIFIED FOR SINGLE-LINE & RIGHT-ALIGNED CONTRIBUTION) ---
st.subheader("Leaderboard")
if users:
    # --- Recalculate totals and bump status before sorting ---
    for name, data in users.items():
        total = round(
            data["resub_total"] + data["gifted_subs_total"] + data["bits_total"] + data["donos"], 2
        )
        bump_status = (
            data["num_bits"] >= 500
            or data["resub_tier"] >= 2
            or data["gifted_subs_count"] >= 2
            or data["donos"] >= 5
            or data["tier2"] >= 1
            or data["tier3"] >= 1
            or total > 5.99
        )
        data["monetary_total"] = total
        data["bumpable"] = bump_status
        
    sorted_users = sorted(users.items(), key=lambda item: item[1]['monetary_total'], reverse=True)
    
    # --- Display each user in a single row using columns ---
    for name, data in sorted_users:
        contribution_string = get_contribution_string(data)
        
        # Shorten username for display if necessary to ensure single-line stats
        display_name = name
        if len(name) > 15: # Adjust 15 based on typical screen size/column width
            display_name = name[:12] + "..." # Truncate and add ellipsis

        # Use two columns: give more space to the stats column to prevent wrapping
        col_stats, col_contrib = st.columns([1.5, 2]) 

        with col_stats:
            # The HTML entity &nbsp; is used to ensure the space between the word and emoji doesn't allow a line break.
            bump_text = 'Bumpable&nbsp;🟢' if data['bumpable'] else 'Not&nbsp;Bumpable&nbsp;🔴'
            
            st.markdown(
                f"**{display_name}** | Total: **${data['monetary_total']:.2f}** | **{bump_text}**",
                unsafe_allow_html=True # Required because we are using the HTML entity &nbsp;
            )

        with col_contrib:
            # Use HTML to enforce both right-alignment AND italics (using the <i> tag)
            st.markdown(
                f'<div style="text-align: right;"><i>{contribution_string}</i></div>', 
                unsafe_allow_html=True
            )

        st.divider() # Visually separate each user
else:
    st.info("No users yet.")

# --- Add User ---
st.subheader("Add User")

if "current_new_user" not in st.session_state:
    st.session_state.current_new_user = None

new_user = st.text_input("Enter a new username", key="add_user_input")

if new_user and new_user not in users and st.session_state.current_new_user is None:
    users[new_user] = {
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
    st.session_state.current_new_user = new_user
    st.success(f"{new_user} added! Now enter their contributions below:")
    st.rerun() # Rerun to show the form immediately

elif new_user in users and st.session_state.current_new_user is None and st.session_state.editing_user is None:
    st.warning(f"{new_user} already exists.")

if st.session_state.current_new_user:
    user = st.session_state.current_new_user
    st.info(f"Adding initial contribution for **{user}**")
    
    # Radio button is outside the form for dynamic rendering
    st.radio(
        "Initial Contribution Type",
        ["Resub", "Gifted", "Bits", "Dono"],
        key="add_contrib_choice",
    )
    
    with st.form("add_contrib_form"):
        # Retrieve the choice from the state (guaranteed to be current)
        current_choice = st.session_state.get("add_contrib_choice", "Resub")

        # --- Define the container slot ---
        input_container = st.container() 

        # --- Draw Inputs based on the choice stored in state ---
        with input_container:
            if current_choice == "Resub":
                st.selectbox("Tier", [1, 2, 3], key="add_resub_tier")
            
            elif current_choice == "Gifted":
                st.number_input("Number of Gifted Subs", min_value=1, step=1, key="add_gifted_amt")
                st.selectbox("Gifted Tier", [1, 2, 3], key="add_gifted_tier")
            
            elif current_choice == "Bits":
                st.number_input("Number of Bits", min_value=1, step=1, key="add_bits_amt")
            
            elif current_choice == "Dono":
                st.number_input("Donation Amount ($)", min_value=0.01, step=0.01, format="%.2f", key="add_dono_amt")

        # --- Form Buttons (NEW) ---
        col_submit, col_cancel = st.columns(2)

        with col_submit:
            submitted = st.form_submit_button("Add Contribution", use_container_width=True, type="primary")

        with col_cancel:
            # We use a button with the same action as the form submission to trigger the logic
            canceled = st.form_submit_button("Cancel & Delete User", use_container_width=True)


        # --- Submission Logic ---
        if submitted:
            # ... (Existing 'Add Contribution' logic here) ...
            choice = current_choice
            
            if choice == "Resub":
                tier = st.session_state.add_resub_tier
                tier_prices = {1: tier1_price, 2: tier2_price, 3: tier3_price}
                
                if tier == 1: users[user]["resub_total"] += tier1_price
                elif tier == 2: users[user]["resub_total"] += tier2_price
                elif tier == 3: users[user]["resub_total"] += tier3_price
                users[user]["resub_tier"] = tier
                st.success(f"Resub Tier {tier} added to {user}")
            
            elif choice == "Gifted":
                gifted_amt = st.session_state.add_gifted_amt
                gifted_tier = st.session_state.add_gifted_tier
                tier_prices = {1: tier1_price, 2: tier2_price, 3: tier3_price}
                
                subs_price = tier_prices.get(gifted_tier, 0.0)
                
                users[user]["gifted_subs_total"] += gifted_amt * subs_price
                
                if gifted_tier == 1: users[user]["tier1"] += gifted_amt
                elif gifted_tier == 2: users[user]["tier2"] += gifted_amt
                elif gifted_tier == 3: users[user]["tier3"] += gifted_amt
                    
                users[user]["gifted_subs_count"] += gifted_amt
                st.success(f"{gifted_amt} Tier {gifted_tier} gifted subs added to {user}")
            
            elif choice == "Bits":
                bit_amt = st.session_state.add_bits_amt
                users[user]["bits_total"] += round(bit_amt * 0.01, 2)
                users[user]["num_bits"] += bit_amt
                st.success(f"{bit_amt} bits added to {user}")
            
            elif choice == "Dono":
                dono_amt = st.session_state.add_dono_amt
                users[user]["donos"] += round(dono_amt, 2)
                st.success(f"${dono_amt:.2f} donation added to {user}")

            # Recalculate monetary total before saving
            data = users[user]
            data["monetary_total"] = round(
                data["resub_total"] + data["gifted_subs_total"] + data["bits_total"] + data["donos"], 
                2
            )

            # --- Common Post-Submission Logic for successful ADD ---
            save_users(users)
            st.session_state.current_new_user = None
            st.session_state.pop("add_user_input", None)
            st.rerun()

        # --- NEW: Logic for CANCEL button ---
        if canceled:
            del users[user]
            save_users(users)
            st.warning(f"Adding user **{user}** canceled. User has been deleted.")
            st.session_state.current_new_user = None
            st.session_state.pop("add_user_input", None)
            st.rerun()

# --- Manage Existing Users (MODIFIED) ---
st.subheader("Manage Existing Users")

# --- Initialize edit state ---
if "editing_user" not in st.session_state:
    st.session_state.editing_user = None

# Variable to hold selected user from the selectbox
selected_user = None

if users:
    user_list = [""] + list(users.keys())
    selected_user = st.selectbox(
        "Choose a user", 
        user_list, 
        key="manage_user_select", 
        format_func=lambda x: "Select a user" if x == "" else x
    )
    
    # --- Show buttons if a user is selected and not currently being edited ---
    if selected_user and st.session_state.editing_user is None: 
        col1, col2 = st.columns([1, 1]) 

        with col1:
            if st.button("Manage Contributions", key="edit_user_btn", use_container_width=True):
                st.session_state.editing_user = selected_user
                st.rerun() 

        with col2:
            if st.button("Delete User", key="delete_user_btn", use_container_width=True, type="primary"):
                del users[selected_user]
                save_users(users)
                st.warning(f"{selected_user} has been deleted.")
                st.session_state.editing_user = None
                st.session_state.pop("manage_user_select", None)
                st.rerun()

# --- Contribution Management Form ---
if st.session_state.editing_user and st.session_state.editing_user in users:
    user_to_edit = st.session_state.editing_user 
    
    st.info(f"Managing contributions for **{user_to_edit}**")

    # 1. NEW: Operation Type (Add/Subtract)
    operation_type = st.radio(
        "Operation Type", 
        ["Add", "Subtract"], 
        key="edit_operation_type", 
        horizontal=True
    )
    
    # Get multiplier based on selection
    multiplier = 1 if operation_type == "Add" else -1
    
    # Radio button for the contribution type (outside the form for dynamic rendering)
    st.radio("Contribution Type", ["Resub", "Gifted", "Bits", "Dono"], key="edit_contrib_choice")

    with st.form("edit_contrib_form"):
        # Retrieve the choice from the state (guaranteed to be current)
        current_choice = st.session_state.get("edit_contrib_choice", "Resub")
        
        # --- Define the container slot for dynamic inputs ---
        input_container = st.container()

        # --- Draw Inputs inside the container ---
        with input_container:
            if current_choice == "Resub":
                st.selectbox("Tier", [1, 2, 3], key="edit_resub_tier")
            
            elif current_choice == "Gifted":
                st.number_input("Number of Gifted Subs", min_value=1, step=1, key="edit_gifted_amt")
                st.selectbox("Gifted Tier", [1, 2, 3], key="edit_gifted_tier")
            
            elif current_choice == "Bits":
                st.number_input("Number of Bits", min_value=1, step=1, key="edit_bits_amt")
            
            elif current_choice == "Dono":
                st.number_input("Donation Amount ($)", min_value=0.01, step=0.01, format="%.2f", key="edit_dono_amt")

        # --- Form Buttons ---
        col_submit, col_cancel = st.columns(2)
        with col_submit:
            submitted = st.form_submit_button(f"{operation_type} Contribution", use_container_width=True, type="primary")
        with col_cancel:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.editing_user = None
                st.rerun()

# --- Submission Logic ---
        if submitted:
            choice = st.session_state.edit_contrib_choice
            
            # --- Dictionary to map tier to price ---
            tier_prices = {1: tier1_price, 2: tier2_price, 3: tier3_price}
            
            # 💡 The multiplier is used here to ADD or SUBTRACT the value 
            if choice == "Resub":
                tier = st.session_state.edit_resub_tier
                
                if multiplier == 1:
                    # Logic for ADDING/CHANGING Resub Tier
                    
                    # 1. Get the price of the current (old) tier
                    old_tier = users[user_to_edit]["resub_tier"]
                    old_price = tier_prices.get(old_tier, 0.0) # 0.0 if user had no previous resub
                    
                    # 2. Get the price of the new tier
                    new_price = tier_prices.get(tier, 0.0)
                    
                    # 3. Calculate the net change in monetary value
                    net_change = new_price - old_price
                    
                    # 4. Apply the change to the total
                    users[user_to_edit]["resub_total"] += net_change
                    
                    # 5. Update the user's resub tier status
                    users[user_to_edit]["resub_tier"] = tier
                    
                    st.success(f"Resub Tier updated from Tier {old_tier} to **Tier {tier}** for {user_to_edit}")
                
                else: # Subtract logic (Removing Resub status entirely)
                    old_tier = users[user_to_edit]["resub_tier"]
                    
                    if old_tier > 0:
                        # Subtract the full cost of the current tier
                        price_to_subtract = tier_prices.get(old_tier)
                        users[user_to_edit]["resub_total"] -= price_to_subtract
                        
                        # Reset tier status
                        users[user_to_edit]["resub_tier"] = 0
                        st.success(f"Resub Tier {old_tier} status removed from {user_to_edit}")
                    else:
                        st.warning(f"{user_to_edit} currently has no active Resub status to remove.")


            elif choice == "Gifted":
                gifted_amt = st.session_state.edit_gifted_amt
                gifted_tier = st.session_state.edit_gifted_tier
                
                amount_change = gifted_amt * multiplier
                total_change = amount_change * tier_prices.get(gifted_tier) # Use the dictionary here too!

                users[user_to_edit]["gifted_subs_total"] += total_change
                users[user_to_edit]["gifted_subs_count"] += amount_change
                
                if gifted_tier == 1: users[user_to_edit]["tier1"] += amount_change
                elif gifted_tier == 2: users[user_to_edit]["tier2"] += amount_change
                elif gifted_tier == 3: users[user_to_edit]["tier3"] += amount_change
                
                st.success(f"{operation_type}ed {gifted_amt} Tier {gifted_tier} gifted subs to {user_to_edit}")

            elif choice == "Bits":
                bit_amt = st.session_state.edit_bits_amt
                
                users[user_to_edit]["bits_total"] += round(bit_amt * 0.01, 2) * multiplier
                users[user_to_edit]["num_bits"] += bit_amt * multiplier
                st.success(f"{operation_type}ed {bit_amt} bits to {user_to_edit}")

            elif choice == "Dono":
                dono_amt = st.session_state.edit_dono_amt
                
                users[user_to_edit]["donos"] += round(dono_amt, 2) * multiplier
                st.success(f"{operation_type}ed ${dono_amt:.2f} donation to {user_to_edit}")

            # --- Common Post-Submission Logic ---
            # Recalculate monetary total before saving
            data = users[user_to_edit]
            data["monetary_total"] = round(
                data["resub_total"] + data["gifted_subs_total"] + data["bits_total"] + data["donos"], 
                2
            )
            
            save_users(users)
            st.session_state.editing_user = None # Close the form
            st.session_state.pop("manage_user_select", None)
            st.session_state.pop("edit_contrib_choice", None)
            st.rerun()
else:
    st.info("No users available to edit or delete.")

# --- Clear All Users ---
st.subheader("Clear All Users")

with st.expander("Clear All Data", expanded=False):
    with st.form("clear_all_form"):
        confirm_clear = st.checkbox("I confirm I want to permanently delete all users", key="clear_confirm")
        submitted = st.form_submit_button("Clear All Users")

        if submitted:
            if confirm_clear:
                users.clear()
                save_users(users)
                st.warning("All users have been cleared.")
                st.session_state.editing_user = None # Clear edit state
                st.session_state.current_new_user = None # Clear add state
                st.rerun()
            else:
                st.info("Please confirm before clearing all users.")

st.subheader("Song Bump Rules")
with st.expander("View Contribution Tiers and Bump Rules"):
    st.markdown("""
    A user is considered **Bumpable (🟢)** if they meet **ANY** of the following contribution thresholds:

    * **Tier 2 Resub** or **Tier 3 Resub** is active.
    * **Total Contributions** exceed **$5.99** (more than a Tier 1 Sub).
    * **Bits** total **500** or more.
    * **Donations** total **$5.00** or more.
    * **Gifted Subs Count** is **2** or more (at any tier).
    * **Gifted Tier 2** subs total **1** or more.
    * **Gifted Tier 3** subs total **1** or more.
    """)