import random
from score_logger import log_score
from flashcard import load_flashcards

def start_quiz():
    flashcards = load_flashcards()
    if not flashcards:
            print(f"\n🎯 You got {score}/{len(flashcards)} correct!")
    log_score(score, len(flashcards))


    random.shuffle(flashcards)
    score = 0

    for fc in flashcards:
        user_ans = input(f"Q: {fc['question']}\nYour answer: ").strip().lower()
        correct = fc['answer'].strip().lower()
        if user_ans == correct:
            print("✅ Correct!")
            score += 1
        else:
            print(f"❌ Wrong! Correct answer: {fc['answer']}")

    print(f"\n🎯 You got {score}/{len(flashcards)} correct!")
