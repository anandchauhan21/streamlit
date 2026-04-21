import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime

# -----------------------
# CONFIG
# -----------------------
RESULT_FILE = "results.csv"
LINKS_FILE = "links.csv"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

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
        old = pd.read_csv(RESULT_FILE)
        df = pd.concat([old, df], ignore_index=True)

    df.to_csv(RESULT_FILE, index=False)


# -----------------------
# SAVE LINK
# -----------------------
def save_link(test_id, time_limit):
    data = {
        "test_id": test_id,
        "time_limit": time_limit,
        "link": f"?test={test_id}&time={time_limit}",
        "created_at": datetime.now()
    }

    df = pd.DataFrame([data])

    if os.path.exists(LINKS_FILE):
        old = pd.read_csv(LINKS_FILE)
        df = pd.concat([old, df], ignore_index=True)

    df.to_csv(LINKS_FILE, index=False)


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
# ADMIN LOGIN
# -----------------------
def admin_login():
    st.title("🔐 Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")


# -----------------------
# ADMIN DASHBOARD
# -----------------------
def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")

    # Logout
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # -----------------------
    # GENERATE LINK
    # -----------------------
    st.subheader("Generate Test Link")

    test_name = st.text_input("Enter Test ID (example: ai102)")
    time_limit = st.number_input("Set Timer (minutes)", 1, 180, 10)

    if st.button("Generate & Save Link"):
        if test_name:
            link = f"?test={test_name}&time={time_limit}"
            save_link(test_name, time_limit)

            st.success("Link generated and saved!")
            st.code(link)

    st.divider()

    # -----------------------
    # SHOW LINKS
    # -----------------------
    st.subheader("🔗 Generated Links")

    if os.path.exists(LINKS_FILE):
        df = pd.read_csv(LINKS_FILE)

        for i, row in df.iterrows():
            st.write(f"**Test:** {row['test_id']} | ⏱️ {row['time_limit']} min")

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"[👉 Open Test]({row['link']})")
                st.code(row["link"])

            with col2:
                if st.button("❌", key=f"del_{i}"):
                    df = df.drop(i)
                    df.to_csv(LINKS_FILE, index=False)
                    st.rerun()
    else:
        st.info("No links generated yet.")

    st.divider()

    # -----------------------
    # RESULTS + CLEAR BUTTON
    # -----------------------
    st.subheader("📊 Results")

    if os.path.exists(RESULT_FILE):
        df = pd.read_csv(RESULT_FILE)
        st.dataframe(df)

        st.divider()
        st.subheader("⚠️ Danger Zone")

        if "confirm_delete" not in st.session_state:
            st.session_state.confirm_delete = False

        if not st.session_state.confirm_delete:
            if st.button("🗑️ Clear All Results"):
                st.session_state.confirm_delete = True
                st.rerun()
        else:
            st.warning("Are you sure? This will delete ALL results permanently.")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Yes, Delete"):
                    os.remove(RESULT_FILE)
                    st.success("All results deleted!")
                    st.session_state.confirm_delete = False
                    st.rerun()

            with col2:
                if st.button("❌ Cancel"):
                    st.session_state.confirm_delete = False
                    st.rerun()
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
def exam_page(test_id, time_limit):
    st.title(f"🧠 Test: {test_id}")
    st.write(f"Logged in as: **{st.session_state.email}**")

    questions = load_test(test_id)

    # Initialize
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.answers = {}
        st.session_state.exam_finished = False

    # Timer
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

    elapsed = time.time() - st.session_state.start_time
    remaining = int(time_limit * 60 - elapsed)

    if remaining <= 0:
        st.session_state.exam_finished = True

    mins = max(remaining, 0) // 60
    secs = max(remaining, 0) % 60
    st.markdown(f"### ⏳ Time Left: {mins:02d}:{secs:02d}")

    idx = st.session_state.q_index

    # DURING EXAM
    if not st.session_state.exam_finished:

        if idx < len(questions):
            q = questions[idx]

            st.header(f"Question {idx + 1}")
            st.write(q["question"])

            ans = st.radio("Select your answer:", q["options"], key=f"q_{idx}")

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

    # AFTER EXAM
    else:
        st.success("⏱️ Time Up! / Exam Finished")

        st.subheader(f"Score: {st.session_state.score}/{len(questions)}")

        if "result_saved" not in st.session_state:
            save_result(
                st.session_state.email,
                test_id,
                st.session_state.score,
                len(questions)
            )
            st.session_state.result_saved = True

        st.write("### Review Answers")

        for i, q in enumerate(questions):
            user_ans = st.session_state.answers.get(i, "Not Answered")

            st.write(f"**Q{i + 1}:** {q['question']}")
            st.write(f"Correct: {q['correct_answer']}")
            st.write(f"Your answer: {user_ans}")

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
# MAIN
# -----------------------
def main():
    params = st.query_params

    # ADMIN
    if "admin" in params:
        if "admin_logged_in" not in st.session_state:
            st.session_state.admin_logged_in = False

        if st.session_state.admin_logged_in:
            admin_dashboard()
        else:
            admin_login()
        return

    # TEST
    if "test" in params:
        test_id = params["test"]
        time_limit = int(params.get("time", 10))

        if "logged_in" not in st.session_state:
            student_login()
        else:
            exam_page(test_id, time_limit)
        return

    # HOME
    st.title("🏠 Welcome to Exam App")
    st.code("?admin=true  → Admin Login")
    st.code("?test=ai102&time=10 → Start Test")


if __name__ == "__main__":
    main()
