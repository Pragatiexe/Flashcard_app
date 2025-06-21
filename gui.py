import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox, filedialog
from collections import defaultdict
import csv
import sqlite3
import matplotlib.pyplot as plt

from score_logger import (
    init_score_db, get_score_history, clear_score_history, log_score,
    update_leaderboard, get_leaderboard, init_leaderboard_db
)
from flashcard_db import (
    init_db, add_flashcard_db, get_all_flashcards as db_get_all_flashcards,
    delete_flashcard, update_flashcard
)

# ------------- Utilities -------------
def get_all_flashcards(category=None, difficulty=None):
    all_cards = db_get_all_flashcards()
    if category:
        all_cards = [card for card in all_cards if card['category'] == category]
    if difficulty:
        all_cards = [card for card in all_cards if card['difficulty'] == difficulty]
    return all_cards

# ------------- Leaderboard -------------
def open_leaderboard():
    leaderboard = get_leaderboard()
    win = tk.Toplevel()
    win.title("🏆 Leaderboard")

    win.geometry("300x250")

    tk.Label(win, text="🏆 High Scores by Difficulty", font=("Arial", 12, "bold")).pack(pady=10)
    if not leaderboard:
        tk.Label(win, text="No scores recorded yet.").pack()
    else:
        for difficulty, score in leaderboard:
            tk.Label(win, text=f"{difficulty}: {score}").pack(pady=2)

# ------------- GUI Entry Point -------------
def main_gui():
    init_db()
    init_score_db()
    init_leaderboard_db()

    root = ttk.Window(themename="cosmo")
    root.title("📚 Flashcard App")
    root.geometry("400x500") 

    tk.Label(root, text="Flashcard Study App", font=("Arial", 16)).pack(pady=10)

    # ---------- Theme Switcher ----------
    theme_var = tk.StringVar(value="cosmo")
    themes = ["cosmo", "darkly", "morph", "journal", "superhero", "cyborg"]

    def switch_theme(event=None):
        root.style.theme_use(theme_var.get())

    ttk.Label(root, text="Choose Theme:", font=("Segoe UI", 10)).pack(pady=(5, 0))
    ttk.OptionMenu(root, theme_var, theme_var.get(), *themes, command=switch_theme).pack(pady=(0, 10))

    # ---------- Main Buttons ----------
    buttons = [
        ("Add Flashcard", open_add_flashcard),
        ("View Flashcards", open_view_flashcards),
        ("Take Quiz (GUI)", open_quiz_gui),
        ("View Score History", open_score_history_gui),
        ("🏆 Leaderboard", open_leaderboard),
        ("Export / Reports", open_export_window),
        ("View Difficulty Chart 📊", view_chart_by_difficulty),
        ("Exit", root.quit)
    ]

    for text, cmd in buttons:
        tk.Button(root, text=text, width=25, command=cmd).pack(pady=5)

    root.mainloop()

# ------------- Flashcard Management -------------
def open_add_flashcard():
    win = tk.Toplevel()
    win.title("Add Flashcard")
    win.geometry("400x350")

    # --- Get existing categories ---
    all_flashcards = get_all_flashcards()
    existing_categories = sorted(set(card['category'] for card in all_flashcards))
    if not existing_categories:
        existing_categories = ["General"]

    # --- Question ---
    tk.Label(win, text="Question").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    question_entry = tk.Entry(win, width=30)
    question_entry.grid(row=0, column=1, padx=10, pady=5)

    # --- Answer ---
    tk.Label(win, text="Answer").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    answer_entry = tk.Entry(win, width=30)
    answer_entry.grid(row=1, column=1, padx=10, pady=5)

    # --- Category Dropdown (Dynamic) ---
    tk.Label(win, text="Category").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    category_var = tk.StringVar()
    category_cb = ttk.Combobox(win, textvariable=category_var, values=existing_categories + ["New Category..."], state="readonly")
    category_cb.set(existing_categories[0])
    category_cb.grid(row=2, column=1, padx=10, pady=5)

    # --- New Category Entry (hidden unless selected) ---
    new_cat_var = tk.StringVar()
    new_cat_entry = tk.Entry(win, textvariable=new_cat_var)
    new_cat_entry.grid(row=3, column=1, padx=10, pady=5)
    new_cat_entry.grid_remove()  # Hidden initially

    def toggle_new_category(*args):
        if category_var.get() == "New Category...":
            new_cat_entry.grid()
        else:
            new_cat_entry.grid_remove()

    category_var.trace_add("write", toggle_new_category)

    # --- Difficulty Dropdown ---
    tk.Label(win, text="Difficulty").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    difficulty_cb = ttk.Combobox(win, values=["Easy", "Medium", "Hard"], state="readonly")
    difficulty_cb.set("Easy")
    difficulty_cb.grid(row=4, column=1, padx=10, pady=5)

    # --- Submit Button ---
    def submit():
        question = question_entry.get().strip()
        answer = answer_entry.get().strip()
        category = new_cat_var.get().strip() if category_var.get() == "New Category..." else category_var.get()
        difficulty = difficulty_cb.get()

        if question and answer and category:
            add_flashcard_db(question, answer, category, difficulty)
            messagebox.showinfo("Success", "Flashcard added!")
            win.destroy()
        else:
            messagebox.showwarning("Input Error", "All fields are required.")

    ttk.Button(win, text="Add Flashcard", command=submit, bootstyle="success").grid(row=5, column=0, columnspan=2, pady=15)


def open_view_flashcards():
    def refresh():
        win.destroy()
        open_view_flashcards()

    win = tk.Toplevel()
    win.title("View Flashcards")
    win.geometry("450x400")

    tk.Label(win, text="📋 Your Flashcards", font=("Arial", 14)).pack(pady=5)

    # ---- Scrollable Canvas Setup ----
    container = tk.Frame(win)
    canvas = tk.Canvas(container, height=300)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    container.pack(fill="both", expand=True)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ✅ Optional: Mouse wheel support
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel)

    # ---- Load flashcards ----
    cards = get_all_flashcards()
    if not cards:
        tk.Label(scrollable_frame, text="No flashcards available.").pack()
        return

    cards_by_cat = defaultdict(list)
    for card in cards:
        cards_by_cat[card['category']].append(card)

    for category, cards_in_cat in cards_by_cat.items():
        tk.Label(scrollable_frame, text=f"📂 {category}", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=5)
        for card in cards_in_cat:
            frame = tk.Frame(scrollable_frame, borderwidth=1, relief="solid", padx=5, pady=5)
            frame.pack(fill="x", padx=5, pady=5)
            tk.Label(frame, text=f"Q: {card['question']}", anchor="w", wraplength=350).pack(anchor="w")
            tk.Label(frame, text=f"A: {card['answer']}", anchor="w", wraplength=350).pack(anchor="w")
            btn_frame = tk.Frame(frame)
            btn_frame.pack(anchor="e", pady=3)
            tk.Button(btn_frame, text="❌ Delete", fg="red", command=lambda c=card: (delete_flashcard(c['id']), refresh())).pack(side="right", padx=2)
            tk.Button(btn_frame, text="✏️ Edit", command=lambda c=card: open_edit_flashcard(c, refresh)).pack(side="right", padx=2)


def open_edit_flashcard(card, refresh_callback):
    win = tk.Toplevel()
    win.title("Edit Flashcard")
    win.geometry("300x300")

    fields = {}
    for label, key, val in [("Edit Question", "question", card['question']),
                            ("Edit Answer", "answer", card['answer']),
                            ("Edit Category", "category", card.get("category", "General")),
                            ("Edit Difficulty", "difficulty", card.get("difficulty", "Easy"))]:
        tk.Label(win, text=label).pack()
        e = tk.Entry(win, width=40)
        e.insert(0, val)
        e.pack()
        fields[key] = e

    def save_edits():
        update_flashcard(card['id'], fields["question"].get(), fields["answer"].get(),
                         fields["category"].get(), fields["difficulty"].get())
        messagebox.showinfo("Success", "Flashcard updated successfully!")
        win.destroy()
        refresh_callback()

    tk.Button(win, text="Save", command=save_edits).pack(pady=10)

# ------------- Quiz Functionality -------------

def open_quiz_gui():
    flashcards = get_all_flashcards()
    if not flashcards:
        messagebox.showwarning("No Flashcards", "Please add some flashcards first.")
        return

    setup_win = tk.Toplevel()
    setup_win.title("Quiz Setup")
    setup_win.geometry("300x250")

    ttk.Label(setup_win, text="Select Category:").pack(pady=(10, 0))
    category_var = tk.StringVar()

    # ✅ Dynamically fetch unique categories
    unique_categories = sorted(set(card['category'] for card in flashcards))
    category_cb = ttk.Combobox(
        setup_win,
        textvariable=category_var,
        values=["All"] + unique_categories,
        state="readonly"
    )
    category_cb.set("All")
    category_cb.pack(pady=5)

    ttk.Label(setup_win, text="Select Difficulty:").pack(pady=(10, 0))
    difficulty_var = tk.StringVar()
    difficulty_cb = ttk.Combobox(
        setup_win,
        textvariable=difficulty_var,
        values=["All", "Easy", "Medium", "Hard"],
        state="readonly"
    )
    difficulty_cb.set("All")
    difficulty_cb.pack(pady=5)

    def start_quiz():
        selected_category = category_cb.get()
        selected_difficulty = difficulty_cb.get()

        filtered = get_all_flashcards(
            category=None if selected_category == "All" else selected_category,
            difficulty=None if selected_difficulty == "All" else selected_difficulty
        )

        if not filtered:
            messagebox.showinfo("No Flashcards", "No flashcards found for selected filters.")
            return

        # ✅ Launch quiz window with selected cards
        setup_win.destroy()
        start_quiz_window(filtered, selected_difficulty)

    ttk.Button(setup_win, text="Start Quiz", command=start_quiz).pack(pady=10)


def start_quiz_window(cards, difficulty):
    quiz_win = tk.Toplevel()
    quiz_win.title("Quiz")
    quiz_win.geometry("400x350")

    current_index = 0
    score = {"correct": 0}
    time_left = tk.IntVar(value=60)

    question_label = tk.Label(quiz_win, text="", font=("Helvetica", 14), wraplength=350)
    question_label.pack(pady=10)

    answer_entry = tk.Entry(quiz_win, font=("Helvetica", 12))
    answer_entry.pack(pady=5)

    feedback_label = tk.Label(quiz_win, text="", font=("Helvetica", 12))
    feedback_label.pack()

    timer_label = tk.Label(quiz_win, text="Time left: 60 sec", font=("Helvetica", 10))
    timer_label.pack()

    progress_label = tk.Label(quiz_win, text="", font=("Helvetica", 10))
    progress_label.pack()

    timer_id = None

    def countdown():
        nonlocal timer_id
        t = time_left.get()
        if t > 0:
            time_left.set(t - 1)
            timer_label.config(text=f"Time left: {t - 1} sec")
            timer_id = quiz_win.after(1000, countdown)
        else:
            submit_answer(auto=True)

    def submit_answer(auto=False):
        nonlocal current_index, timer_id
        user_ans = answer_entry.get().strip().lower()
        correct_ans = cards[current_index]['answer'].strip().lower()

        if auto:
            feedback = f"⏰ Time's up! Correct: {correct_ans}"
        elif user_ans == correct_ans:
            feedback = "✅ Correct!"
            score["correct"] += 1
        else:
            feedback = f"❌ Incorrect! Correct: {correct_ans}"

        feedback_label.config(text=feedback)
        quiz_win.after_cancel(timer_id)
        current_index += 1
        quiz_win.after(1500, next_question)

    def next_question():
        nonlocal timer_id
        if current_index < len(cards):
            card = cards[current_index]
            question_label.config(text=f"Q{current_index + 1}: {card['question']}")
            answer_entry.delete(0, tk.END)
            feedback_label.config(text="")
            time_left.set(60)
            timer_label.config(text="Time left: 60 sec")
            progress_label.config(text=f"Question {current_index + 1} of {len(cards)}")
            countdown()
        else:
            log_score(score['correct'], len(cards), difficulty)
            update_leaderboard(score['correct'], difficulty)
            messagebox.showinfo("Quiz Over", f"You scored {score['correct']} out of {len(cards)}.")
            quiz_win.destroy()

    submit_btn = tk.Button(quiz_win, text="Submit", command=lambda: submit_answer(auto=False), font=("Helvetica", 12))
    submit_btn.pack(pady=10)

    next_question()


def open_score_history_gui():
    win = tk.Toplevel()
    win.title("Score History")
    win.geometry("400x350")

    tk.Label(win, text="📊 Your Quiz Score History", font=("Arial", 12)).pack(pady=5)
    history = get_score_history()

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, width=60)
    for line in history:
        listbox.insert(tk.END, line.strip())
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    def export_score_history_txt():
        if not history:
            messagebox.showwarning("Empty", "No score history found.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("Score History:\n" + "\n".join(history))
            messagebox.showinfo("Success", f"Exported to:\n{file_path}")

        
    def clear_history():
        if messagebox.askyesno("Confirm", "Clear all score history?"):
            clear_score_history()
            listbox.delete(0, tk.END)
            messagebox.showinfo("Success", "History cleared.")

    tk.Button(win, text="📈 Export Score History", command=export_score_history_txt).pack(pady=5)
    tk.Button(win, text="🗑️ Clear History", command=clear_history).pack(pady=5)


def view_chart_by_difficulty():
    conn = sqlite3.connect("score_history.db")
    c = conn.cursor()
    c.execute("SELECT difficulty, score, total FROM score_log")
    rows = c.fetchall()
    conn.close()

    performance = {}
    for difficulty, score, total in rows:
        if difficulty not in performance:
            performance[difficulty] = {"score": 0, "total": 0}
        performance[difficulty]["score"] += score
        performance[difficulty]["total"] += total

    labels = list(performance.keys())
    accuracy = [round((v["score"] / v["total"]) * 100, 2) if v["total"] > 0 else 0 for v in performance.values()]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, accuracy, color='green')
    plt.ylabel("Accuracy (%)")
    plt.title("Performance by Difficulty")
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.show()


def open_export_window():
    win = tk.Toplevel()
    win.title("Export Options")
    win.geometry("400x300")

    tk.Label(win, text="📁 Export / Reports", font=("Arial", 12)).pack(pady=5)

    def export_flashcards_txt():
        cards = get_all_flashcards()
        if not cards:
            messagebox.showwarning("No Flashcards", "No flashcards to export.")
            return
        with open("flashcards_export.txt", "w", encoding="utf-8") as f:
            for card in cards:
                f.write(f"Q: {card['question']}\nA: {card['answer']}\n\n")
        messagebox.showinfo("Export Successful", "Exported to flashcards_export.txt")

    def export_flashcards_csv():
        cards = get_all_flashcards()
        if not cards:
            messagebox.showwarning("No Flashcards", "No flashcards to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Question", "Answer", "Category", "Difficulty"])
                for card in cards:
                    writer.writerow([card["question"], card["answer"], card["category"], card["difficulty"]])
            messagebox.showinfo("Export Successful", f"Exported to:\n{file_path}")

    tk.Button(win, text="📁 Export Flashcards (.txt)", command=export_flashcards_txt).pack(pady=5)
    tk.Button(win, text="📁 Export Flashcards (.csv)", command=export_flashcards_csv).pack(pady=5)


if __name__ == "__main__":
    main_gui()