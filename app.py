import streamlit as st

def main():
    st.set_page_config(page_title="Exam Conductor", layout="centered")
    st.title("🧠 Exam Conductor App")

    # --- Exam Questions ---
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

    # --- Initialize session state ---
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
        st.session_state.answers = {}
        st.session_state.score = 0
        st.session_state.exam_finished = False

    # --- Exam Flow ---
    if not st.session_state.exam_finished:
        current_index = st.session_state.current_question_index

        if current_index < len(questions):
            question_data = questions[current_index]

            st.header(f"Question {current_index + 1}")
            st.write(question_data["question"])

            selected_option = st.radio(
                "Select your answer:",
                question_data["options"],
                key=f"q_{current_index}"
            )

            if st.button("Submit Answer", key=f"submit_{current_index}"):
                st.session_state.answers[current_index] = selected_option

                if selected_option == question_data['correct_answer']:
                    st.session_state.score += 1

                st.session_state.current_question_index += 1
                st.rerun()   # ✅ FIXED

        else:
            st.session_state.exam_finished = True
            st.rerun()   # ✅ FIXED

    # --- Result Page ---
    else:
        st.header("Exam Finished!")
        st.subheader(
            f"Your final score: {st.session_state.score} out of {len(questions)}"
        )

        st.write("### Your Answers:")

        for i, q_data in enumerate(questions):
            st.write(f"**Question {i + 1}:** {q_data['question']}")
            st.write(f"Correct Answer: {q_data['correct_answer']}")

            user_answer = st.session_state.answers.get(i, "Not Answered")
            st.write(f"Your Answer: {user_answer}")

            if user_answer == q_data['correct_answer']:
                st.success("Correct!")
            else:
                st.error("Incorrect.")

        # --- Retake Button ---
        if st.button("Retake Exam"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()   # ✅ FIXED


if __name__ == "__main__":
    main()
