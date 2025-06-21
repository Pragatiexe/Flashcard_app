from flashcard import add_flashcard, view_flashcards
from quiz import start_quiz
from score_logger import view_score_history

def main():
    while True:
        print("\n📚 Flashcard App Menu")
        print("1. Add Flashcard")
        print("2. View Flashcards")
        print("3. Take Quiz")
        print("4. View Score History")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            q = input("Enter question: ")
            a = input("Enter answer: ")
            add_flashcard(q, a)
            print("Flashcard added.")
        elif choice == '2':
            view_flashcards()
        elif choice == '3':
            start_quiz()
        elif choice == '4':
            view_score_history()
        elif choice == '5':
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
