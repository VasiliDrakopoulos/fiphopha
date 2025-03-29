from fiphopha.between_bootstrap import main as between_bootstrap_main
from fiphopha.within_bootstrap import main as within_bootstrap_main
from fiphopha.downsampler import main as downsampler_main
from fiphopha.timebins import main as timebins_main

def run():
    print("\nFiPhoPHA - Fiber Photometry Post-Hoc Analysis\n")
    print("Choose a script to run:")
    print("1: Between-Groups Bootstrap & Permutation Tests")
    print("2: Within-Groups Bootstrap & Permutation Tests")
    print("3: Downsampler")
    print("4: Time Bins")

    while True:
        choice = input("\nEnter the number of the script you want to run: ")

        try:
            if choice == "1":
                between_bootstrap_main()
                break
            elif choice == "2":
                within_bootstrap_main()
                break
            elif choice == "3":
                downsampler_main()
                break
            elif choice == "4":
                timebins_main()
                break
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"An error occurred: {e}")
            break
