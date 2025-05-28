import random
import time

def add_flashcard(flashcards):
        print("\nCurrent Flashcards:")
        if flashcards:
            for i, card in enumerate(flashcards):
                print(f"{i+1}. Front: {card[0]} | Back: {card[1]}")
        else:
            print("No flashcards yet!")

        while True:
            try:
                num_cards = int(input("\nHow many flashcards would you like to add? "))
                if num_cards <= 0:
                    print("Please enter a positive number.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")

        for i in range(num_cards):
            print(f"\nFlashcard {i + 1}:")
            front = input("Enter the front of the flashcard: ")
            back = input("Enter the back of the flashcard: ")
            flashcards.append([front, back])
        return flashcards

def shuffle_flashcards(flashcards):
    if not flashcards:
        time.sleep(1)
        print("No flashcards to shuffle.")
    else:
        random.shuffle(flashcards)
        time.sleep(2)
        print("Flashcards shuffled!")

def flashcards_reversed(flashcards):
    for flashcard in flashcards:
        flashcard[0], flashcard[1] = flashcard[1], flashcard[0]
    time.sleep(2)
    print("Flashcards reversed!")

def showknowledge(known_cards, unknown_cards):        
    print("\n--- Known Flashcards ---")
    if not flashcards:
        print("No flashcards have been created yet.")
    elif known_cards:
        for card in known_cards:
            print(f"Front: {card[0]} | Back: {card[1]}")
            print("-" * 25)
    else:
        print("No cards were answered correctly.")
    print("\n--- Unknown Flashcards (Need Review) ---")
    if not flashcards:
        print("No flashcards have been created yet.")
    elif unknown_cards:
        for card in unknown_cards:
            print(f"Front: {card[0]} | Back: {card[1]}")
            print("-" * 25)
    else:
        print("All flashcards are known!") 

def study_review(flashcards):
    known_cards = []
    unknown_cards = []
    for card in flashcards:
        print(f"\nFront: {card[0]}")
        user_input = input("Enter the answer for the back of the flashcard: ").strip()
        if user_input.lower() == card[1].lower():
            print("Correct!")
            known_cards.append(card)
        else:
            print("Incorrect!")
            unknown_cards.append(card)   
    showknowledge(known_cards, unknown_cards)
    while unknown_cards:
        review_choice = input("\nDo you want to review unknown flashcards again? (y/n): ").lower()
        if review_choice != 'y':
            break
        temp_unknown = unknown_cards.copy()
        unknown_cards = []
        for card in temp_unknown:
            print(f"\nFront: {card[0]}")
            user_input = input("Enter the answer for the back of the flashcard: ").strip()
            if user_input.lower() == card[1].lower():
                print("Correct!")
                known_cards.append(card)
            else:
                print("Incorrect!")
                unknown_cards.append(card)
        showknowledge(known_cards, unknown_cards)
    return known_cards, unknown_cards


print("Welcome to the Flashcard Study Helper!")
flashcards = []
while True:
    print("\nFlashcard Generator Menu:")
    print("1. Add Flashcards")
    print("2. Shuffle Flashcards")
    print("3. Reverse Flashcards")
    print("4. Study and Review")
    print("5. Exit")
    choice = input("Choose an option (num only): ")
    if choice == '1':
        flashcards = add_flashcard(flashcards)
    elif choice == '2': 
        shuffle_flashcards(flashcards)
    elif choice == '3':
        flashcards_reversed(flashcards)
    elif choice == '4':
        known, unknown = study_review(flashcards)
    elif choice == '5':
        print("\nExiting Flashcards; Goodbye!")
        break
    else:
        print("\nInvalid option. Please choose again.")
        continue