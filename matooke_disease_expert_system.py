import tkinter as tk
from tkinter import messagebox

# ==========================================
# 1. KNOWLEDGE BASE (Separated Data)
# ==========================================
KNOWLEDGE_BASE = {
    "Banana Xanthomonas Wilt (BXW)": {
        "description": "A destructive bacterial disease affecting matooke.",
        "treatment": "Remove and bury infected mats, sterilize tools, and do not use infected planting materials.",
        "rules": [
            {"symptom": "yellowing_leaves", "cf": 0.8},
            {"symptom": "premature_ripening_fruit", "cf": 0.9},
            {"symptom": "yellow_ooze_in_pseudostem", "cf": 1.0},
            {"symptom": "wilting_and_drying", "cf": 0.7}
        ]
    },
    "Black Sigatoka": {
        "description": "A fungal leaf spot disease common in humid areas.",
        "treatment": "Prune severely infected leaves, improve drainage, and apply recommended fungicides if severe.",
        "rules": [
            {"symptom": "yellowing_leaves", "cf": 0.5},
            {"symptom": "dark_brown_leaf_streaks", "cf": 0.9},
            {"symptom": "widespread_leaf_necrosis", "cf": 0.8}
        ]
    },
    "Banana Bunchy Top Virus (BBTV)": {
        "description": "A viral disease causing stunted and bunchy growth.",
        "treatment": "Uproot and destroy infected plants immediately to prevent spread by aphids.",
        "rules": [
            {"symptom": "stunted_growth", "cf": 0.9},
            {"symptom": "narrow_upward_curling_leaves", "cf": 0.8},
            {"symptom": "dark_green_streaks_on_petioles", "cf": 1.0}
        ]
    }
}

# ==========================================
# 2. INFERENCE ENGINE (Backward Chaining)
# ==========================================
class BackwardChainingEngine:
    """
    Backward Chaining Strategy:
    Starts with a goal hypothesis (a specific disease) and works backward 
    to check if required symptoms match user observations.
    """
    def __init__(self, kb):
        self.kb = kb
        self.diseases = list(kb.keys())
        self.current_disease_idx = 0
        self.current_rule_idx = 0
        self.accumulated_cf = 0.0
        self.matched_rules_trace = []

    def get_current_goal(self):
        if self.current_disease_idx < len(self.diseases):
            return self.diseases[self.current_disease_idx]
        return None

    def record_answer(self, symptom, score, rule_cf):
        disease = self.get_current_goal()
        if score > 0:
            # MYCIN-style combination for Uncertainty Factors
            self.accumulated_cf = self.accumulated_cf + (rule_cf * score * (1 - self.accumulated_cf))
            self.matched_rules_trace.append(f"Observed '{symptom}' supporting {disease} (CF: {rule_cf * score})")

    def evaluate_current_hypothesis(self):
        disease = self.get_current_goal()
        final_score = self.accumulated_cf
        
        result = {
            "disease": disease, 
            "confidence": round(final_score * 100, 2), 
            "trace": list(self.matched_rules_trace)
        }
        
        # Reset for next disease
        self.accumulated_cf = 0.0
        self.matched_rules_trace = []
        return result

    def reset(self):
        self.current_disease_idx = 0
        self.current_rule_idx = 0
        self.accumulated_cf = 0.0
        self.matched_rules_trace = []


# ==========================================
# 3. USER INTERFACE (Tkinter GUI)
# ==========================================
class ExpertSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Uganda Crop Disease Expert System")
        self.root.geometry("700x560")
        self.root.config(bg="#f4f6f8")

        self.engine = BackwardChainingEngine(KNOWLEDGE_BASE)
        self.diagnosis_results = []

        # Calculate total questions across all disease rules
        self.total_questions = sum(len(d["rules"]) for d in KNOWLEDGE_BASE.values())
        self.question_counter = 0

        # Header Banner Container
        self.header_frame = tk.Frame(root, bg="#2d6a4f", height=80)
        self.header_frame.pack(fill="x", padx=0, pady=0)
        self.header_frame.pack_propagate(False)

        self.title_label = tk.Label(
            self.header_frame, 
            text="Matooke Disease Diagnostic Assistant", 
            font=("Segoe UI", 16, "bold"), 
            bg="#2d6a4f", 
            fg="white"
        )
        self.title_label.pack(pady=(12, 2))

        self.subtitle_label = tk.Label(
            self.header_frame, 
            text="Answer symptom questions to explore possible banana diseases", 
            font=("Segoe UI", 10), 
            bg="#2d6a4f", 
            fg="#d8f3dc"
        )
        self.subtitle_label.pack()

        # Main Card Container
        self.card_frame = tk.Frame(root, bg="white", bd=1, relief="solid")
        self.card_frame.pack(fill="both", expand=True, padx=25, pady=20)

        # Progress Section Inside Card
        self.progress_counter_label = tk.Label(
            self.card_frame, 
            text="QUESTION 1 OF 10", 
            font=("Segoe UI", 10, "bold"), 
            bg="white", 
            fg="#2d6a4f"
        )
        self.progress_counter_label.pack(pady=(15, 5))

        # Custom Canvas Progress Bar
        self.progress_canvas = tk.Canvas(self.card_frame, width=580, height=14, bg="#e9ecef", highlightthickness=0)
        self.progress_canvas.pack(pady=(0, 10))
        self.progress_bar = self.progress_canvas.create_rectangle(0, 0, 0, 14, fill="#2d6a4f", width=0)

        self.hypothesis_label = tk.Label(
            self.card_frame, 
            text="Used when evaluating: -", 
            font=("Segoe UI", 9, "italic"), 
            bg="white", 
            fg="#6c757d"
        )
        self.hypothesis_label.pack(pady=(0, 20))

        # Question Text
        self.question_label = tk.Label(
            self.card_frame, 
            text="", 
            font=("Segoe UI", 13, "bold"), 
            bg="white", 
            fg="#212529", 
            wraplength=560, 
            justify="center"
        )
        self.question_label.pack(expand=True, padx=20, pady=10)

        # Action Buttons Frame (Yes / No / Don't Know)
        self.btn_frame = tk.Frame(self.card_frame, bg="white")
        self.btn_frame.pack(pady=(10, 20))

        self.btn_yes = tk.Button(
            self.btn_frame, text="✓ Yes", font=("Segoe UI", 11, "bold"), 
            bg="#2d6a4f", fg="white", activebackground="#1b4332", activeforeground="white",
            relief="flat", width=12, pady=8, cursor="hand2", command=lambda: self.process_answer(1.0)
        )
        self.btn_yes.grid(row=0, column=0, padx=10)

        self.btn_no = tk.Button(
            self.btn_frame, text="✕ No", font=("Segoe UI", 11, "bold"), 
            bg="#b7094c", fg="white", activebackground="#89023e", activeforeground="white",
            relief="flat", width=12, pady=8, cursor="hand2", command=lambda: self.process_answer(-1.0)
        )
        self.btn_no.grid(row=0, column=1, padx=10)

        self.btn_maybe = tk.Button(
            self.btn_frame, text="? Don't Know", font=("Segoe UI", 11, "bold"), 
            bg="#d4a373", fg="white", activebackground="#bc6c25", activeforeground="white",
            relief="flat", width=14, pady=8, cursor="hand2", command=lambda: self.process_answer(0.0)
        )
        self.btn_maybe.grid(row=0, column=2, padx=10)

        # Bottom Utility Bar (Why & Restart)
        self.footer_frame = tk.Frame(self.card_frame, bg="white")
        self.footer_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.btn_why = tk.Button(
            self.footer_frame, text="Why are you asking this?", font=("Segoe UI", 9), 
            bg="#e9ecef", fg="#495057", relief="flat", padx=10, pady=5, cursor="hand2", command=self.explain_why
        )
        self.btn_why.pack(side="left")

        self.btn_restart = tk.Button(
            self.footer_frame, text="Restart", font=("Segoe UI", 9), 
            bg="#e9ecef", fg="#495057", relief="flat", padx=15, pady=5, cursor="hand2", command=self.restart_system
        )
        self.btn_restart.pack(side="right")

        self.current_symptom = None
        self.current_hypothesis = None
        self.current_rule_cf = 0.0

        self.load_next_question()

    def update_progress_bar(self):
        self.question_counter += 1
        self.progress_counter_label.config(text=f"QUESTION {self.question_counter} OF {self.total_questions}")
        
        # Calculate width proportion on 580px canvas
        width_px = (self.question_counter / self.total_questions) * 580
        self.progress_canvas.coords(self.progress_bar, 0, 0, width_px, 14)

    def load_next_question(self):
        disease = self.engine.get_current_goal()
        if disease is None:
            self.show_results()
            return
        
        rules = KNOWLEDGE_BASE[disease]["rules"]
        if self.engine.current_rule_idx < len(rules):
            rule = rules[self.engine.current_rule_idx]
            self.current_symptom = rule["symptom"]
            self.current_rule_cf = rule["cf"]
            self.current_hypothesis = disease
            
            formatted_symptom = self.current_symptom.replace("_", " ")
            self.hypothesis_label.config(text=f"Used when evaluating: {self.current_hypothesis}")
            self.question_label.config(text=f"Is the plant showing signs of:\n\n'{formatted_symptom}'?")
        else:
            # Finished all rules for this disease, evaluate hypothesis
            res = self.engine.evaluate_current_hypothesis()
            self.diagnosis_results.append(res)
            
            # Move to next disease
            self.engine.current_disease_idx += 1
            self.engine.current_rule_idx = 0
            self.load_next_question()

    def process_answer(self, score):
        self.engine.record_answer(self.current_symptom, score, self.current_rule_cf)
        self.engine.current_rule_idx += 1
        self.update_progress_bar()
        self.load_next_question()

    def explain_why(self):
        explanation = (
            f"Backward Chaining Trace:\n\n"
            f"• Current Hypothesis: '{self.current_hypothesis}'\n"
            f"• Required Symptom: '{self.current_symptom.replace('_', ' ')}'\n\n"
            f"The system is evaluating this symptom to determine the presence and confidence level of the disease."
        )
        messagebox.showinfo("Explanation Facility (Why)", explanation)

    def restart_system(self):
        self.engine.reset()
        self.diagnosis_results = []
        self.question_counter = 0
        self.progress_canvas.coords(self.progress_bar, 0, 0, 0, 14)
        self.progress_counter_label.config(text=f"QUESTION 1 OF {self.total_questions}")
        self.load_next_question()

    def show_results(self):
        # Clear main card content
        for widget in self.card_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.card_frame, 
            text="Diagnosis Results & Recommendations", 
            font=("Segoe UI", 14, "bold"), 
            bg="white", 
            fg="#2d6a4f"
        ).pack(pady=15)

        # Scrollable Results Area
        text_frame = tk.Frame(self.card_frame, bg="white")
        text_frame.pack(fill="both", expand=True, padx=15, pady=5)

        text_widget = tk.Text(text_frame, font=("Segoe UI", 10), wrap="word", bg="white", fg="#212529", bd=0)
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Sort diagnoses by confidence level descending
        self.diagnosis_results.sort(key=lambda x: x["confidence"], reverse=True)

        report = "====================================================\n"
        report += "          AGRICULTURAL EXPERT ASSESSMENT REPORT     \n"
        report += "====================================================\n\n"

        for res in self.diagnosis_results:
            disease_name = res["disease"]
            conf = res["confidence"]
            details = KNOWLEDGE_BASE[disease_name]
            
            report += f"• Disease: {disease_name}\n"
            report += f"  Confidence Level: {conf}%\n"
            report += f"  Description: {details['description']}\n"
            report += f"  Recommended Action: {details['treatment']}\n"
            report += f"{'-' * 52}\n\n"

        text_widget.insert("1.0", report)
        text_widget.config(state="disabled")

        # Restart Button at Bottom of Results
        btn_restart_res = tk.Button(
            self.card_frame, text="Start New Diagnosis", font=("Segoe UI", 10, "bold"), 
            bg="#2d6a4f", fg="white", activebackground="#1b4332", activeforeground="white",
            relief="flat", padx=20, pady=8, cursor="hand2", command=self.restart_from_results
        )
        btn_restart_res.pack(pady=15)

    def restart_from_results(self):
        for widget in self.card_frame.winfo_children():
            widget.destroy()
        
        # Re-initialize UI elements in card
        self.__init_card_widgets()
        self.restart_system()

    def __init_card_widgets(self):
        self.progress_counter_label = tk.Label(self.card_frame, text="QUESTION 1 OF 10", font=("Segoe UI", 10, "bold"), bg="white", fg="#2d6a4f")
        self.progress_counter_label.pack(pady=(15, 5))

        self.progress_canvas = tk.Canvas(self.card_frame, width=580, height=14, bg="#e9ecef", highlightthickness=0)
        self.progress_canvas.pack(pady=(0, 10))
        self.progress_bar = self.progress_canvas.create_rectangle(0, 0, 0, 14, fill="#2d6a4f", width=0)

        self.hypothesis_label = tk.Label(self.card_frame, text="Used when evaluating: -", font=("Segoe UI", 9, "italic"), bg="white", fg="#6c757d")
        self.hypothesis_label.pack(pady=(0, 20))

        self.question_label = tk.Label(self.card_frame, text="", font=("Segoe UI", 13, "bold"), bg="white", fg="#212529", wraplength=560, justify="center")
        self.question_label.pack(expand=True, padx=20, pady=10)

        self.btn_frame = tk.Frame(self.card_frame, bg="white")
        self.btn_frame.pack(pady=(10, 20))

        self.btn_yes = tk.Button(self.btn_frame, text="✓ Yes", font=("Segoe UI", 11, "bold"), bg="#2d6a4f", fg="white", relief="flat", width=12, pady=8, cursor="hand2", command=lambda: self.process_answer(1.0))
        self.btn_yes.grid(row=0, column=0, padx=10)

        self.btn_no = tk.Button(self.btn_frame, text="✕ No", font=("Segoe UI", 11, "bold"), bg="#b7094c", fg="white", relief="flat", width=12, pady=8, cursor="hand2", command=lambda: self.process_answer(-1.0))
        self.btn_no.grid(row=0, column=1, padx=10)

        self.btn_maybe = tk.Button(self.btn_frame, text="? Don't Know", font=("Segoe UI", 11, "bold"), bg="#d4a373", fg="white", relief="flat", width=14, pady=8, cursor="hand2", command=lambda: self.process_answer(0.0))
        self.btn_maybe.grid(row=0, column=2, padx=10)

        self.footer_frame = tk.Frame(self.card_frame, bg="white")
        self.footer_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.btn_why = tk.Button(self.footer_frame, text="Why are you asking this?", font=("Segoe UI", 9), bg="#e9ecef", fg="#495057", relief="flat", padx=10, pady=5, cursor="hand2", command=self.explain_why)
        self.btn_why.pack(side="left")

        self.btn_restart = tk.Button(self.footer_frame, text="Restart", font=("Segoe UI", 9), bg="#e9ecef", fg="#495057", relief="flat", padx=15, pady=5, cursor="hand2", command=self.restart_system)
        self.btn_restart.pack(side="right")


# ==========================================
# Main Program Execution
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpertSystemGUI(root)
    root.mainloop()