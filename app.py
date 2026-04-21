import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

RESULT_FILE = "results.csv"

# -----------------------
# SAVE RESULT
# -----------------------
def save_result(email, test_id, score, total):
    data = {
        "email": email,
        "test_id": test_id,
        "score": score,
        "total": total,
        "timestamp": datetime.now()
    }

    df = pd.DataFrame([data])

    if os.path.exists(RESULT_FILE):
        df_existing = pd.read_csv(RESULT_FILE)
        df = pd.concat([df_existing, df], ignore_index=True)

    df.to_csv(RESULT_FILE, index=False)


# -----------------------
# LOAD TEST
# -----------------------
def load_test(test_id):
    file_path = f"tests/{test_id}.json"

    if not os.path.exists(file_path):
        st.error(f"❌ Test '{test_id}' not found")
        st.stop()

    with open(file_path, "r") as f:
        return json.load(f)


# -----------------------
# ADMIN DASHBOARD
# -----------------------
def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")

    st.subheader("Generate Test Link")

    test_name = st.text_input("Enter Test ID (example: ai101)")

    if st.button("Generate Link"):
        if test_name:
            link = f"?test={test_name}"
            st.success("Share this link with students:")
            st.code(link)

    st.divider()

    # Show results
    if os.path.exists(RESULT_FILE):
        st.subheader("📊 Results")
        df = pd.read_csv(RESULT_FILE)
        st.dataframe(df)
    else:
        st.info("No results yet.")


# -----------------------
# STUDENT LOGIN
# -----------------------
def student_login():
    st.title("🎓 Student Login")

    email = st.text_input("Enter your email")

    if st.button("Start Test"):
        if email:
            st.session_state.email = email
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.warning("Please enter email")


# -----------------------
# EXAM PAGE
# -----------------------
def exam_page(test_id):
    st.title(f"🧠 Test: {test_id}")
    st.write(f"Logged in as: **{st.session_state.email}**")

    questions = load_test(test_id)

    # Initialize state
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.answers = {}
        st.session_state.exam_finished = False

    idx = st.session_state.q_index

    # =====================
    # DURING EXAM
    # =====================
    if not st.session_state.exam_finished:

        if idx < len(questions):
            q = questions[idx]

            st.header(f"Question {idx + 1}")
            st.write(q["question"])

            ans = st.radio(
                "Select your answer:",
                q["options"],
                key=f"q_{idx}"
            )

            st.warning("⚠️ Do not refresh during exam")

            if st.button("Submit Answer"):
                st.session_state.answers[idx] = ans

                if ans == q["correct_answer"]:
                    st.session_state.score += 1

                st.session_state.q_index += 1
                st.rerun()

        else:
            st.session_state.exam_finished = True
            st.rerun()

    # =====================
    # AFTER EXAM
    # =====================
    else:
        st.success("🎉 Exam Finished!")

        st.subheader(
            f"Score: {st.session_state.score}/{len(questions)}"
        )

        # Save result once
        if "result_saved" not in st.session_state:
            save_result(
                st.session_state.email,
                test_id,
                st.session_state.score,
                len(questions)
            )
            st.session_state.result_saved = True

        # Show answers
        st.write("### Review Answers")
        for i, q in enumerate(questions):
            user_ans = st.session_state.answers.get(i, "Not Answered")

            st.write(f"**Q{i + 1}:** {q['question']}")
            st.write(f"Correct: {q['correct_answer']}")
            st.write(f"Your answer: {user_ans}")

            if user_ans == q["correct_answer"]:
                st.success("Correct")
            else:
                st.error("Wrong")

        # Buttons AFTER exam only
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔁 Retake"):
                keys_to_keep = ["email", "logged_in"]
                for key in list(st.session_state.keys()):
                    if key not in keys_to_keep:
                        del st.session_state[key]
                st.rerun()

        with col2:
            if st.button("🚪 Logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()


# -----------------------
# MAIN ROUTER
# -----------------------
def main():
    params = st.query_params

    # Admin route
    if "admin" in params:
        admin_dashboard()
        return

    # Test route
    if "test" in params:
        test_id = params["test"]

        if "logged_in" not in st.session_state:
            student_login()
        else:
            exam_page(test_id)

        return

    # Home
    st.title("🏠 Welcome to Exam App")
    st.write("Use links below:")

    st.code("?admin=true  → Admin Dashboard")
    st.code("?test=ai101 → Student Test")


if __name__ == "__main__":
    main()
