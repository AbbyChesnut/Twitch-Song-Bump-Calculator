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

# --- GRAND TOTALS INITIALIZATION ---
grand_totals = {
    "total_monetary": 0.0,
    "total_resubs_value": 0.0,
    "total_gifted_subs_value": 0.0,
    "total_donos": 0.0,
    "total_bits_value": 0.0,
    "total_bits_amount": 0,
    "total_subs_count": 0,
    # --- NEW KEYS FOR RAW COUNTS ---
    "total_gifted_subs_count": 0, # Total gifted subs (Tier 1, 2, 3)
    "total_resubs_count": 0,      # Total Tier 1, 2, or 3 resubs (not value, just the count of active subs)
    "total_tier1": 0,
    "total_tier2": 0,
    "total_tier3": 0,
}

# --- Streamlit UI ---
st.title("🎵 Twitch Song Bump Calculator")

if users:
    # --- RESET GRAND TOTALS (IMPORTANT) ---
    # This must be done inside the 'if users' block before recalculating
    grand_totals = {key: 0.0 if isinstance(grand_totals[key], float) else 0 for key in grand_totals}

    # --- Recalculate totals and bump status before sorting (LEADERBOARD LOGIC) ---
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
        
        # Calculate the simplified sub count for Grand Total tracking
        sub_count = (1 if data['resub_tier'] > 0 else 0) + data['gifted_subs_count']

        data["monetary_total"] = total
        data["bumpable"] = bump_status

        # --- UPDATE GRAND TOTALS ---
        grand_totals["total_monetary"] += total
        grand_totals["total_resubs_value"] += data["resub_total"] # Keep value tracking
        grand_totals["total_gifted_subs_value"] += data["gifted_subs_total"] # Keep value tracking
        grand_totals["total_donos"] += data["donos"]
        grand_totals["total_bits_value"] += data["bits_total"]
        grand_totals["total_bits_amount"] += data["num_bits"]
        grand_totals["total_subs_count"] += sub_count
        
        # --- NEW: ACCUMULATE RAW COUNTS ---
        grand_totals["total_gifted_subs_count"] += data["gifted_subs_count"]
        # Only count the highest active tier for resubs (1 if T1/T2/T3 is active)
        if data["resub_tier"] > 0:
            grand_totals["total_resubs_count"] += 1 
        grand_totals["total_tier1"] += data["tier1"]
        grand_totals["total_tier2"] += data["tier2"]
        grand_totals["total_tier3"] += data["tier3"]
        
    sorted_users = sorted(users.items(), key=lambda item: item[1]['monetary_total'], reverse=True)
    
    # --- Leaderboard ---
    st.subheader("Leaderboard")
    
    # --- Display each user in a single row using flexbox ---
    for name, data in sorted_users:
        contribution_string = get_contribution_string(data)
        
        # Shorten username for display if necessary
        display_name = name
        if len(name) > 15:
            display_name = name[:12] + "..."

        # Use two columns: give more space to the stats column to prevent wrapping
        col_stats, col_contrib = st.columns([1.5, 2]) 

        with col_stats:
            # The HTML entity &nbsp; is used to ensure the space between the word and emoji doesn't allow a line break.
            bump_status_text = 'Bumpable&nbsp;🟢' if data['bumpable'] else 'Not&nbsp;Bumpable&nbsp;🔴'
            
            # Rearranged the output to include dividing pipes.
            st.markdown(
                f"**{display_name}** | Total: **${data['monetary_total']:.2f}** | {bump_status_text}",
                unsafe_allow_html=True
            )

        with col_contrib:
            # Use HTML to enforce both right-alignment AND italics (using the <i> tag)
            st.markdown(
                f'<div style="text-align: right;"><i>{contribution_string}</i></div>', 
                unsafe_allow_html=True
            )
            
        st.divider() # Visually separate each user

else:
    st.subheader("Leaderboard")
    st.info("No contributions yet. Beeg sadge :(")

st.markdown("---") # Separator between Leaderboard/Info and Forms

# --- Add User (MOVED OUTSIDE 'if users:' to always be available) ---
st.subheader("Add User")

if "current_new_user" not in st.session_state:
    st.session_state.current_new_user = None

# --- Initialize edit state ---
if "editing_user" not in st.session_state:
    st.session_state.editing_user = None

# --- NEW EXCLUSION BLOCK ---
# This block is for creating a new user, which should always be possible.
if st.session_state.editing_user is None and st.session_state.current_new_user is None:

    # 1. Initialize the input value (must be done before the input is called)
    if "add_user_input_value" not in st.session_state:
        st.session_state["add_user_input_value"] = ""

    new_user = st.text_input(
        "Enter a new username", 
        key="add_user_input", 
        value=st.session_state["add_user_input_value"]
    )

    # --- Logic for creating the new user ---
    if new_user and new_user not in users:
        users[new_user] = {
            # ... (Your user initialization dictionary content) ...
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
        st.rerun() 

    # --- Warning Logic (simplified since we've excluded editing_user) ---
    # We also check the 'just_submitted_add' flag to skip the warning immediately after submission
    is_just_submitted = st.session_state.pop("just_submitted_add", False)
    
    if new_user in users and not is_just_submitted:
        st.warning(f"{new_user} already exists.")

# --- Contribution Form Logic (if current_new_user is set) ---
# This form only appears after a user name is entered above.
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
            st.session_state["add_user_input_value"] = ""
            
            # NEW LINE: Temporarily set flag to suppress "already exists" warning
            st.session_state["just_submitted_add"] = True 
            
            st.rerun()

    # --- NEW: Logic for CANCEL button ---
        if canceled:
            del users[user]
            save_users(users)
            st.warning(f"Adding user **{user}** canceled. User has been deleted.")
            st.session_state.current_new_user = None
            st.session_state["add_user_input_value"] = "" # Reset the input value
            st.rerun()

st.markdown("---") # Separator between Add User and Manage Users

# --- Manage Existing Users (MODIFIED: Only show subheader if users exist) ---
if users:
    st.subheader("Manage Existing Users")

    # Variable to hold selected user from the selectbox
    selected_user = None

    # This nested check is redundant now, but keeps the selectbox logic correct
    # We proceed because the parent 'if users:' is true.
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

# --- Display Grand Totals (Moved to be the last section inside 'if users:') ---
if users:
    st.markdown("---")
    st.subheader("📊 Grand Totals")
    
    # 1. Calculate Grand Total Status
    total_subs_count = int(grand_totals['total_subs_count'])
    stream_sub_goal = 20 # Define the goal here for clarity
    is_goal_reached = total_subs_count >= stream_sub_goal
    
    if is_goal_reached:
        status_color = '#FFD700' # Gold for Success
        subs_needed_line = f'Stream Sub Goal Reached! 🎉'
    else:
        subs_needed = stream_sub_goal - total_subs_count
        status_color = '#FFFFFF' # Default color
        subs_needed_line = f'Need <b>{subs_needed}</b> more!'

    # 2. Compile the Grand Contribution String (RAW AMOUNTS with singular/plural)
    grand_contribution_parts = []
    
    # Gifted Subs
    if grand_totals['total_gifted_subs_count'] > 0:
        count = grand_totals['total_gifted_subs_count']
        word = "gifted sub" if count == 1 else "gifted subs"
        grand_contribution_parts.append(f"{count} {word}")
        
    # Resubs
    if grand_totals['total_resubs_count'] > 0:
        count = grand_totals['total_resubs_count']
        word = "resub" if count == 1 else "resubs"
        grand_contribution_parts.append(f"{count} {word}")
        
    # Bits
    if grand_totals['total_bits_amount'] > 0:
        count = grand_totals['total_bits_amount']
        word = "bit" if count == 1 else "bits"
        grand_contribution_parts.append(f"{count:,} {word}") 
        
    # Donations (Changed wording to "in donos")
    if grand_totals['total_donos'] > 0:
        grand_contribution_parts.append(f"${grand_totals['total_donos']:.2f} in donos") 

    grand_contribution_string = ", ".join(grand_contribution_parts).capitalize()
    if not grand_contribution_string:
        grand_contribution_string = "No contributions recorded."

    # 3. Display in a single line (using flexbox for left/right alignment)
    total_monetary = f"${grand_totals['total_monetary']:.2f}"
    
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <span>
            Total value: <b>{total_monetary}</b> | Subs: <span style="color: {status_color};"><b>{total_subs_count}</b> /{stream_sub_goal} - {subs_needed_line}</span>
        </span>
        <span style="flex-shrink: 0; margin-left: 10px;">
            <i style="color: gray;">{grand_contribution_string}</i>
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Display detailed revenue breakdown in an expander
    with st.expander("Detailed Revenue Breakdown"):
        st.markdown(f"""
        * Total Resubs (Value): ${grand_totals['total_resubs_value']:.2f}
        * Total Gifted Subs (Value): ${grand_totals['total_gifted_subs_value']:.2f}
        * Total Donations: ${grand_totals['total_donos']:.2f}
        * Total Bits (Amount): {grand_totals['total_bits_amount']:,}
        ---
        * Tier 1 Subs Gifted: {grand_totals['total_tier1']}
        * Tier 2 Subs Gifted: {grand_totals['total_tier2']}
        * Tier 3 Subs Gifted: {grand_totals['total_tier3']}
        """)

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