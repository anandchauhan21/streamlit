import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

RESULT_FILE = "results.xlsx"

# -----------------------
# UTIL FUNCTIONS
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
        df_existing = pd.read_excel(RESULT_FILE)
        df = pd.concat([df_existing, df], ignore_index=True)

    df.to_excel(RESULT_FILE, index=False)


def load_test(test_id):
    with open(f"tests/{test_id}.json", "r") as f:
        return json.load(f)


# -----------------------
# ADMIN DASHBOARD
# -----------------------

def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")

    test_name = st.text_input("Test ID (example: math1)")

    if st.button("Generate Test Link"):
        if test_name:
            link = f"?test={test_name}"
            st.success("Share this link with students:")
            st.code(link)

    # Show results
    if os.path.exists(RESULT_FILE):
        st.subheader("📊 Results")
        df = pd.read_excel(RESULT_FILE)
        st.dataframe(df)


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


# -----------------------
# EXAM
# -----------------------

def exam_page(test_id):
    st.title(f"🧠 Test: {test_id}")
    st.write(f"Logged in as: **{st.session_state.email}**")

    questions = load_test(test_id)

    if "q_index" not in st.session_state:
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.answers = {}

    idx = st.session_state.q_index

    if idx < len(questions):
        q = questions[idx]

        st.write(f"### Q{idx + 1}: {q['question']}")

        ans = st.radio("Select:", q["options"], key=f"q{idx}")

        if st.button("Submit"):
            st.session_state.answers[idx] = ans

            if ans == q["correct_answer"]:
                st.session_state.score += 1

            st.session_state.q_index += 1
            st.rerun()

    else:
        st.success("✅ Test Finished!")

        save_result(
            st.session_state.email,
            test_id,
            st.session_state.score,
            len(questions)
        )

        st.write(f"Score: {st.session_state.score}/{len(questions)}")

        if st.button("Exit"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# -----------------------
# MAIN ROUTER
# -----------------------

def main():
    params = st.query_params

    # If admin mode
    if "admin" in params:
        admin_dashboard()
        return

    # If test link
    if "test" in params:
        test_id = params["test"]

        if "logged_in" not in st.session_state:
            student_login()
        else:
            exam_page(test_id)

        return

    # Default screen
    st.title("🏠 Welcome")
    st.write("Use:")
    st.code("?admin=true  → Admin Dashboard")
    st.code("?test=math1 → Student Test")


if __name__ == "__main__":
    main()
