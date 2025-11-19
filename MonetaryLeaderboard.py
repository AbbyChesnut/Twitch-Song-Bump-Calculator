users={} #empty dictionary
tier1_price = 5.99 #price values to easily edit if needed
tier2_price = 9.99
tier3_price = 24.99

def main(): #main menu from GradeTrackerDB
    while True:
        print("""
        Twitch Song Bump Calculator
        [1] - Add User
        [2] - Edit User
        [3] - Delete User
        [4] - Clear All     
        [5] - Exit
        """)

        choice = input("Please choose an option: ").strip()

        if choice == '1':  #adding user option
            print("---Adding User---")
            user_name = input("What user would you like to add?: ").strip()
            add_user(user_name)
            print_users_by_total()

        elif choice == '2': #edit user option
            print("---Editing User---")
            user_name = input("What user would you like to edit?: ").strip()
            edit_user(user_name)
            print_users_by_total()

        elif choice == '3': #clearing a singular user
            print("---Deleting a User---")
            user_name = input("What user would you like to delete?: ").strip()
            delete_user(user_name)
            print_users_by_total()

        elif choice == '4': #clearing all users
            print("---Clearing All Users---")
            clear_all()
            print_users_by_total()

        elif choice == '5': #exit
            print("Goodbye!")
            break

        else:
            print("Invalid choice, please try again.")

def update_contributions(user_name, totals):
    #function to use in both add and update users
    user_name = totals["name"]
    user_total = totals["monetary_total"]
    resub_tier = totals["resub_tier"]
    total_resub = totals["resub_total"]
    num_tierone_gifted = totals["tier1"]
    num_tiertwo_gifted = totals["tier2"]
    num_tierthree_gifted = totals["tier3"]
    gifted_count = totals["gifted_subs_count"]
    total_gifted = totals["gifted_subs_total"]
    num_bits = totals["num_bits"]
    total_bits = totals["bits_total"]
    total_dono = totals["donos"]
    bump_status = totals["bumpable"]

    while True:
        cont_choice = input("Resub/gifted/bits/dono? (R,G,B,D, Q to Esc): ").strip().lower()
        if cont_choice == "q":
            user_total = round(total_resub + total_gifted + total_bits + total_dono, 2)
            bump_status = (num_bits >= 500) or (resub_tier >= 2) or (gifted_count >= 2) or (total_dono >= 5) or (num_tiertwo_gifted >= 1) or (num_tierthree_gifted >= 1) or (user_total > 5.99)

            #dictionary update
            users[user_name] = {
                "name": user_name,
                "monetary_total": user_total,
                "resub_tier": resub_tier,
                "resub_total": total_resub,
                "tier1": num_tierone_gifted,
                "tier2": num_tiertwo_gifted,
                "tier3": num_tierthree_gifted,
                "gifted_subs_count": gifted_count,
                "gifted_subs_total": total_gifted,
                "num_bits": num_bits,
                "bits_total": total_bits,
                "donos": total_dono,
                "bumpable": bump_status,
            }
            print(f"Updated {user_name}'s contributions.")
            return

        #resub change
        if cont_choice == "r":
            try:
                resub_tier = int(input("Resub: What tier? "))
            except ValueError:
                print("Invalid tier")
                continue
            if resub_tier == 1:
                amount = tier1_price
                print(f"Added Resub Tier {resub_tier} to {user_name} (${tier1_price})")
            elif resub_tier == 2:
                amount = tier2_price
                print(f"Added Resub Tier {resub_tier} to {user_name} (${tier2_price})")
            elif resub_tier == 3:
                amount = tier3_price
                print(f"Added Resub Tier {resub_tier} to {user_name} (${tier3_price})")
            else:
                print("Invalid tier")
                continue
            total_resub += amount

        #gifted update
        elif cont_choice == "g":
            try:
                gifted_amt = int(input("Gifted Subs: How many? "))
                print(gifted_amt, "Gifted Subs:", end=' ')
                gifted_tier = int(input("What Tier? "))
            except ValueError:
                print("Invalid amount or tier")
                continue
            if gifted_tier == 1:
                total_gifted += gifted_amt * tier1_price
                num_tierone_gifted += gifted_amt
                gifted_count += gifted_amt
                print(f"Added {gifted_amt} Tier {gifted_tier} Gifted to {user_name} (${gifted_amt * tier1_price:.2f})")
            elif gifted_tier == 2:
                total_gifted += gifted_amt * tier2_price
                num_tiertwo_gifted += gifted_amt
                gifted_count += gifted_amt
                print(f"Added {gifted_amt} Tier {gifted_tier} Gifted to {user_name} (${gifted_amt * tier2_price:.2f})")
            elif gifted_tier == 3:
                total_gifted += gifted_amt * tier3_price
                num_tierthree_gifted += gifted_amt
                gifted_count += gifted_amt
                print(f"Added {gifted_amt} Tier {gifted_tier} Gifted to {user_name} (${gifted_amt * tier3_price:.2f})")
            else:
                print("Invalid tier")
                continue

        #bit update
        elif cont_choice == "b":
            try:
                bit_amt = int(input("Bits: How many? "))
                print(f"Added {bit_amt} Bits to {user_name} (${(bit_amt * 0.01):.2f})")
            except ValueError:
                print("Invalid amount")
                continue
            total_bits += round(bit_amt * 0.01, 2)
            num_bits += bit_amt

        #dono update
        elif cont_choice == "d":
            try:
                dono_amt = float(input("Dono: How much? "))
                print(f"Added ${dono_amt:.2f} to {user_name}")
            except ValueError:
                print("Invalid amount")
                continue
            total_dono += round(dono_amt, 2)

        else:
            print("Unknown option")
            continue

#clear all users
def clear_all():
    users.clear()

#clearing a singular user
def delete_user(user_name):
    global users
    if user_name in users:
        del users[user_name]
        print(f"{user_name} has been deleted.")
    else:
        print(f"{user_name} not found.")


def edit_user(user_name):
    if user_name not in users:
            print(f"{user_name} is not on the list")
            add_input = input(f"Do you want to add {user_name}? (Y or N): ").strip().lower()
            if add_input == "y":
                add_user(user_name)
            return

    #loading existing totals
    user_data = users[user_name]
    totals = {
        "name": user_data["name"],
        "monetary_total": user_data["monetary_total"],
        "resub_tier": user_data["resub_tier"],
        "resub_total": user_data["resub_total"],
        "tier1": user_data["tier1"],
        "tier2": user_data["tier2"],
        "tier3": user_data["tier3"],
        "gifted_subs_count": user_data["gifted_subs_count"],
        "gifted_subs_total": user_data["gifted_subs_total"],
        "num_bits": user_data["num_bits"],
        "bits_total": user_data["bits_total"],
        "donos": user_data["donos"],
        "bumpable": user_data["bumpable"],
    }

    update_contributions(user_name, totals)

def add_user(user_name):
    if user_name in users:
        print(f"{user_name} is already on list.")
        edit_choice = input("Would you like to edit? (Y or N): ").strip().lower()
        if edit_choice == "y":
            edit_user(user_name)
        return

    #fresh totals
    totals = {
                "name": user_name,
                "monetary_total": 0.0,
                "resub_tier": 0,
                "resub_total": 0,
                "tier1": 0,
                "tier2": 0,
                "tier3": 0,
                "gifted_subs_count" : 0,
                "gifted_subs_total": 0.0,
                "num_bits": 0,
                "bits_total": 0.0,
                "donos": 0.0,
                "bumpable": False,
            }
    
    update_contributions(user_name, totals)

#function to show the users sorted by monetary value, highest to lowest
def print_users_by_total():
    global users
    if not users:
        print("There are no usernames to show")
        return
    sorted_users = sorted(
        users.items(),
        key=lambda item: item[1]['monetary_total'],
        reverse = True
    )
    print("\n---Monetary Leaderboard---")
    for user_name, user_data in sorted_users:
        total = user_data['monetary_total']

        bump = "Bumpable" if user_data['bumpable'] else "Not Bumpable" #Learned that you can combine if else on one line
        contributions =[] 

        #resub check
        if user_data['resub_tier'] == 3:
            contributions.append("tier 3 resub")
        elif user_data['resub_tier'] == 2:
            contributions.append("tier 2 resub")
        elif user_data['resub_tier'] == 1:
            contributions.append("resub")


        #gifted sub tier 1 check
        if user_data['tier1'] > 1:
            contributions.append(f"{user_data['tier1']} gifted subs")
        elif user_data['tier1'] == 1:
            contributions.append("gifted sub")
        
        #gifted sub tier 2 check
        if user_data['tier2'] > 1:
            contributions.append(f"{user_data['tier2']} tier 2 gifted subs")
        elif user_data['tier2'] == 1:
            contributions.append("tier 2 gifted sub")

        #gifted sub tier 3 check
        if user_data['tier3'] > 1:
            contributions.append(f"{user_data['tier3']} tier 3 gifted subs")
        elif user_data['tier3'] == 1:
            contributions.append("tier 3 gifted sub")
        
        #bits check
        if user_data["num_bits"] > 1:
            contributions.append(f"{user_data['num_bits']} bits")
        elif user_data["num_bits"] == 1:
            contributions.append("1 bit")

        #dono check
        if user_data["donos"] > 0:
            contributions.append(f"${user_data['donos']:.2f} dono")

        #joining the strings
        contribution_string = ", ".join(contributions)            
        line = (f"{user_name.ljust(15)} | Total: ${total:>6.2f} | {bump.rjust(12)} | {(contribution_string).capitalize()}")

        print(line)
main()