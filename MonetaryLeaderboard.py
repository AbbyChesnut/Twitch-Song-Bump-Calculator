users={}

def add_user():
    global users
    total_resub = total_gifted = total_bits = total_dono = 0.00
    resub_tier = num_tierone_gifted = num_tiertwo_gifted = num_tierthree_gifted = 0
    bump_status = False

    user_name = input("enter the username: ").strip()
    if not user_name:
        print("Username required")
        return

    while True:
        cont_choice = input("Resub/gifted/bits/dono? (R,G,B,D, Q to Esc): ").strip().lower()
        if cont_choice == "q":
            user_total = round(total_resub + total_gifted + total_bits + total_dono,2)

            users[user_name] = {
                "monetary_total": user_total,
                "name": user_name,
                "bumpable": bump_status,
                "resub_tier": resub_tier,
                "gifted_subs": {
                    "tier1": num_tierone_gifted,
                    "tier2": num_tiertwo_gifted,
                    "tier3": num_tierthree_gifted,
                },
                "bits": total_bits,
                "donos": total_dono,
            }
            return

        if cont_choice == "r":
            try:
                resub_tier = int(input("Resub: What tier? "))
            except ValueError:
                print("Invalid tier")
                continue
            if resub_tier == 1:
                amount = 5.99
                print("Added Resub Tier",resub_tier, "to", user_name, "($5.99)")
            elif resub_tier == 2:
                amount = 9.99
                bump_status = True
                print("Added Resub Tier",resub_tier, "to", user_name, "($9.99)")
            elif resub_tier == 3:
                amount = 24.99
                bump_status = True
                print("Added Resub Tier",resub_tier, "to", user_name, "($24.99)")
            else:
                print("Invalid tier")
                continue
            total_resub += amount

        elif cont_choice == "g":
            try:
                gifted_amt = int(input("Gifted Subs: How many? "))
                print(gifted_amt,"Gifted Subs:",end = ' ')
                gifted_tier = int(input("What Tier? "))
            except ValueError:
                print("Invalid amount or tier")
                continue
            if gifted_tier == 1:
                total_gifted += gifted_amt * 5.99
                num_tierone_gifted += gifted_amt
                bump_status = gifted_amt >= 2
                print("Added", str(gifted_amt), "Tier", gifted_tier, "Gifted to", user_name, "($"+str(gifted_amt * 5.99)+")")
            elif gifted_tier == 2:
                total_gifted += gifted_amt * 9.99
                num_tiertwo_gifted += gifted_amt
                bump_status = True
                print("Added", str(gifted_amt), "Tier", gifted_tier, "Gifted to", user_name, "($"+str(gifted_amt * 9.99)+")")
            elif gifted_tier == 3:
                total_gifted += gifted_amt * 24.99
                num_tierthree_gifted += gifted_amt
                bump_status = True
                print("Added", str(gifted_amt), "Tier", gifted_tier, "Gifted to", user_name, "($"+str(gifted_amt * 24.99)+")")
            else:
                print("Invalid tier")
                continue

        elif cont_choice == "b":
            try:
                bit_amt = int(input("Bits: How many? "))
                print("Added", str(bit_amt), "Bits to", user_name, "($"+str(bit_amt * 0.01)+")")
            except ValueError:
                print("Invalid amount")
                continue
            total_bits += round(bit_amt * 0.01,2)
            bump_status = total_bits >= 5.00

        elif cont_choice == "d":
            try:
                dono_amt = float(input("Dono: How much? "))
                print("Added $", str(dono_amt), "to", user_name)
            except ValueError:
                print("Invalid amount")
                continue
            total_dono += dono_amt
            bump_status = total_dono >= 5.00

        else:
            print("Unknown option")
            continue

def get_user_info(user_name):
    global users
    if user_name in users:
        return users[user_name]
    else:
        return print("User '{user_name}' not found.")

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
    print("Monetary Leaderboard:")
    for user_name, user_data in sorted_users:
        total = user_data['monetary_total']

        bump = "Bumpable" if user_data['bumpable'] else "Not Bumpable" #Learned that you can combine if else on one line
        contributions =[] 

        if user_data['resub_tier'] == 3:
            contributions.append("tier 3 resub")
        elif user_data['resub_tier'] == 2:
            contributions.append("tier 3 resub")
        elif user_data['resub_tier'] == 1:
            contributions.append("resub")


        #gifted sub tier 1 check
        if user_data['gifted_subs']['tier1'] > 1:
            contributions.append(str(user_data['gifted_subs']['tier1']) + " gifted subs")
        elif user_data['gifted_subs']['tier1'] == 1:
            contributions.append("gifted sub")
        
        #gifted sub tier 2 check
        if user_data['gifted_subs']['tier2'] > 1:
            contributions.append(str(user_data['gifted_subs']['tier2']) + " tier 2 gifted subs")
        elif user_data['gifted_subs']['tier2'] == 1:
            contributions.append("tier 2 gifted sub")

        #gifted sub tier 3 check
        if user_data['gifted_subs']['tier3'] > 1:
            contributions.append(str(user_data['gifted_subs']['tier3']) + " tier 3 gifted subs")
        elif user_data['gifted_subs']['tier3'] == 1:
            contributions.append("tier 3 gifted sub")
        
        #bits check
        if user_data["bits"] > 1:
            contributions.append(str(user_data["bits"]) + " bits")
        elif user_data["bits"] == 1:
            contributions.append("1 bit")


        #dono check
        if user_data["donos"] > 0:
            contributions.append("$" + str(user_data['donos']) + "dono")
                                 
        #joining the strings
        contribution_string = ", ".join(contributions)            
        line = (user_name.ljust(15)+ " | " + "Total: $" + str(round(total)) + " | " + bump + " | " + (contribution_string).capitalize())

        print(line)

#user_to_find = input("Enter a username to lookup: ").strip()
#info = get_user_info(user_to_find)
#print(info)

add_user()
print_users_by_total()