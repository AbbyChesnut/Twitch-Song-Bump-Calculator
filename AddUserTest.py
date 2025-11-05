users = {}

def add_user():
    global users
    total_resub = total_gifted = total_bits = total_dono = 0.0
    num_tierone_gifted = num_tiertwo_gifted = num_tierthree_gifted = 0
    bump_status = False

    user_name = input("enter the username: ").strip()
    if not user_name:
        print("Username required")
        return

    while True:
        cont_choice = input("Resub/gifted/bits/dono? (R,G,B,D, Q to Esc): ").strip().lower()
        if cont_choice == "q":
            user_total = total_resub + total_gifted + total_bits + total_dono
            users[user_name] = {
                "monetary_total": user_total,
                "resub": total_resub,
                "gifted_subs": total_gifted,
                "bits": total_bits,
                "donos": total_dono,
                "gift_counts": {
                    "tier1": num_tierone_gifted,
                    "tier2": num_tiertwo_gifted,
                    "tier3": num_tierthree_gifted,
                "bumpable": bump_status,
                },
            }
            return users[user_name]

        if cont_choice == "r":
            try:
                resub_tier = int(input("What tier? "))
            except ValueError:
                print("Invalid tier")
                continue
            if resub_tier == 1:
                amount = 5.99
            elif resub_tier == 2:
                amount = 9.99
                bump_status = True
            elif resub_tier == 3:
                amount = 24.99
                bump_status = True
            else:
                print("Invalid tier")
                continue
            total_resub += amount

        elif cont_choice == "g":
            try:
                gifted_amt = int(input("How many? "))
                gifted_tier = int(input("What Tier? "))
            except ValueError:
                print("Invalid amount or tier")
                continue
            if gifted_tier == 1:
                total_gifted += gifted_amt * 5.99
                num_tierone_gifted += gifted_amt
                bump_status = gifted_amt >= 2
            elif gifted_tier == 2:
                total_gifted += gifted_amt * 9.99
                num_tiertwo_gifted += gifted_amt
                bump_status = True
            elif gifted_tier == 3:
                total_gifted += gifted_amt * 24.99
                num_tierthree_gifted += gifted_amt
                bump_status = True
            else:
                print("Invalid tier")
                continue

        elif cont_choice == "b":
            try:
                bit_amt = int(input("How many? "))
            except ValueError:
                print("Invalid amount")
                continue
            total_bits += bit_amt * 0.01
            bump_status = total_bits >= 5.00

        elif cont_choice == "d":
            try:
                dono_amt = float(input("How much? "))
            except ValueError:
                print("Invalid amount")
                continue
            total_dono += dono_amt
            bump_status = total_dono >= 5.00

        else:
            print("Unknown option")
            continue
	
add_user()

print(users)
