import streamlit as st

# --- Dummy user database ---
USERS = {
    "admin": "1234",
    "user": "pass"
}

# --- Authentication function ---
def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid username or password")

# --- Exam App ---
def exam_app():
    st.title("🧠 Exam Conductor App")
    st.write(f"Welcome, **{st.session_state.username}** 👋")

    # --- Logout ---
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # --- Questions ---
    questions = [
        {
            "question": "What is the capital of France?",
            "options": ["Berlin", "Madrid", "Paris", "Rome"],
            "correct_answer": "Paris"
        },
        {
            "question": "Which planet is known as the Red Planet?",
            "options": ["Earth", "Mars", "Jupiter", "Venus"],
            "correct_answer": "Mars"
        },
        {
            "question": "What is 2 + 2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": "4"
        }
    ]

    # --- Initialize state ---
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
        st.session_state.answers = {}
        st.session_state.score = 0
        st.session_state.exam_finished = False

    # --- Exam Flow ---
    if not st.session_state.exam_finished:
        idx = st.session_state.current_question_index

        if idx < len(questions):
            q = questions[idx]

            st.header(f"Question {idx + 1}")
            st.write(q["question"])

            selected = st.radio(
                "Select your answer:",
                q["options"],
                key=f"q_{idx}"
            )

            if st.button("Submit Answer"):
                st.session_state.answers[idx] = selected

                if selected == q["correct_answer"]:
                    st.session_state.score += 1

                st.session_state.current_question_index += 1
                st.rerun()
        else:
            st.session_state.exam_finished = True
            st.rerun()

    else:
        st.header("Exam Finished!")
        st.subheader(
            f"Score: {st.session_state.score} / {len(questions)}"
        )

        for i, q in enumerate(questions):
            user_ans = st.session_state.answers.get(i, "Not Answered")

            st.write(f"**Q{i + 1}:** {q['question']}")
            st.write(f"Correct: {q['correct_answer']}")
            st.write(f"Your answer: {user_ans}")

            if user_ans == q["correct_answer"]:
                st.success("Correct")
            else:
                st.error("Wrong")

        if st.button("Retake Exam"):
            keys_to_keep = ["logged_in", "username"]
            for key in list(st.session_state.keys()):
                if key not in keys_to_keep:
                    del st.session_state[key]
            st.rerun()


# --- Main ---
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        exam_app()
    else:
        login()


if __name__ == "__main__":
    main()
