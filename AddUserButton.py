def add_user():
    global users #global variable so it can be read outside of the function
    #variable resets
    total_resub = total_gifted = total_bits = total_dono = 0.00
    resub_tier = num_tierone_gifted = num_tiertwo_gifted = num_tierthree_gifted = num_bits = 0
    bump_status = False #default bump status as False

    #username input
    user_name = input("enter the username: ").strip()
    if not user_name:
        print("Username required")
        return
    
    #checks if username is in the user dictionary
    if user_name in users:
        print(f"{user_name} is already on list.")
        edit_choice = input("Would you like to edit? (Y or N): ").strip().lower()
        if edit_choice == "n":
            return
        elif edit_choice == "y":
            edit_user(user_name) #goes into the edit user function
            return

    while user_name.lower() != "q": #makes it so that 'q' exits out
        cont_choice = input("Resub/gifted/bits/dono? (R,G,B,D, Q to Esc): ").strip().lower()
        if cont_choice == "q": 
            user_total = round(total_resub + total_gifted + total_bits + total_dono,2)
            bump_status = bump_status or (num_bits >= 500) or (resub_tier >= 2) or (total_gifted >= 2) or (total_dono >= 5)

            #user info
            users[user_name] = {
                "monetary_total": user_total,
                "name": user_name,
                "bumpable": bump_status,
                "resub_tier": resub_tier,
                "resub_total": total_resub,
                "gifted_subs": {
                    "gifted_subs_total": total_gifted,
                    "tier1": num_tierone_gifted,
                    "tier2": num_tiertwo_gifted,
                    "tier3": num_tierthree_gifted,
                },
                "num_bits" : num_bits,
                "bits_total": total_bits,
                "donos": total_dono,
            }
            print_users_by_total()
            return
        #resub choice
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

        #gifted choice
        elif cont_choice == "g":
            try:
                gifted_amt = int(input("Gifted Subs: How many? "))
                print(gifted_amt,"Gifted Subs:",end = ' ')
                gifted_tier = int(input("What Tier? "))
            except ValueError:
                print("Invalid amount or tier")
                continue
            if gifted_tier == 1:
                total_gifted += gifted_amt * tier1_price
                num_tierone_gifted += gifted_amt
                print(f"Added {gifted_amt} Tier {gifted_tier} Gifted to {user_name} (${gifted_amt * tier1_price:.2f})")
            elif gifted_tier == 2:
                total_gifted += gifted_amt * tier2_price
                num_tiertwo_gifted += gifted_amt
                print(f"Added {gifted_amt} Tier {gifted_tier} Gifted to {user_name} (${gifted_amt * tier2_price:.2f})")
            elif gifted_tier == 3:
                total_gifted += gifted_amt * tier3_price
                num_tierthree_gifted += gifted_amt
                print(f"Added {gifted_amt} Tier {gifted_tier} Gifted to {user_name} (${gifted_amt * tier3_price:.2f})")
            else:
                print("Invalid tier")
                continue
        
        #bits choice
        elif cont_choice == "b":
            try:
                bit_amt = int(input("Bits: How many? "))
                print(f"Added {bit_amt} Bits to {user_name} (${(bit_amt * 0.01):.2f})")
            except ValueError:
                print("Invalid amount")
                continue
            total_bits += round(bit_amt * 0.01,2)
            num_bits += bit_amt
        
        #dono choice
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
add_user()