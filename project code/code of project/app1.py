import streamlit as st
import requests
from PIL import Image
import base64

# Page config
st.set_page_config(page_title="EduTutor AI", layout="wide")

# Dummy course data
courses_list = [
    {"title": "Introduction to AI", "description": "Basics of Artificial Intelligence", "url": "https://youtu.be/2ePf9rue1Ao"},
    {"title": "Python Programming", "description": "Learn the fundamentals of Python", "url": "https://youtu.be/_uQrJ0TkZlc"},
    {"title": "Data Structures", "description": "Understand how data is organized", "url": "https://youtu.be/bum_19loj9A"},
]

# Background image base64 function
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Session state init
if "get_started" not in st.session_state:
    st.session_state.get_started = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.quiz_history = []
    st.session_state.registered_users = {}
    st.session_state.students = {}
    st.session_state.user_profile = {"name": "", "bio": "", "profile_pic": None}

# ------------------ GET STARTED PAGE ------------------
if not st.session_state.get_started:
    st.markdown("""
        <style>
        .stApp {
            background-color: #000;
            color: white;
        }
        .getstarted-container {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }
        .getstarted-title {
            font-size: 64px;
            color: white;
            text-shadow: 2px 2px #00000080;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""<div class='getstarted-container'><div class='getstarted-title'>EduTutor AI</div></div>""", unsafe_allow_html=True)
    centered = st.columns([4, 2, 4])
    with centered[1]:
        if st.button("🚀 Get Started"):
            st.session_state.get_started = True
    st.stop()

# ------------------ RESET BACKGROUND FOR OTHER PAGES ------------------
st.markdown("""
    <style>
    .stApp {
        background: white;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ LOGIN / REGISTER ------------------
if not st.session_state.logged_in:
    st.title("🔐 EduTutor AI Login/Register")
    role = st.selectbox("Select Role", ["student", "educator"])
    action = st.radio("Action", ["Login", "Register"])
    user_id = st.text_input("User ID")
    password = st.text_input("Password", type="password")

    if action == "Register" and st.button("Register"):
        if user_id and password:
            key = f"{role}:{user_id}"
            st.session_state.registered_users[key] = password
            st.success("Registered successfully!")
        else:
            st.warning("Fill both fields!")

    if action == "Login" and st.button("Login"):
        key = f"{role}:{user_id}"
        if st.session_state.registered_users.get(key) == password:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.user_id = user_id
            if role == "student" and user_id not in st.session_state.students:
                st.session_state.students[user_id] = []
        else:
            st.error("Invalid credentials.")
    st.stop()

# ------------------ STUDENT ------------------
if st.session_state.role == "student":
    st.sidebar.title("🎓 Student Panel")
    choice = st.sidebar.radio("Navigate", ["Dashboard", "Take Quiz", "Quiz History", "Courses"])

    if choice == "Dashboard":
        st.title(f"Welcome, {st.session_state.user_id}")
        st.subheader("🧑 Your Profile")

        uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "png"])
        if uploaded_file:
            st.session_state.user_profile["profile_pic"] = uploaded_file

        name = st.text_input("Full Name", value=st.session_state.user_profile.get("name", ""))
        bio = st.text_area("About You", value=st.session_state.user_profile.get("bio", ""))

        if st.button("Update Profile"):
            st.session_state.user_profile["name"] = name
            st.session_state.user_profile["bio"] = bio
            st.success("Profile updated!")

        if st.session_state.user_profile["profile_pic"]:
            st.image(st.session_state.user_profile["profile_pic"], width=150, caption="Profile Picture")

        st.write("**Name:**", st.session_state.user_profile.get("name", ""))
        st.write("**About:**", st.session_state.user_profile.get("bio", ""))

    elif choice == "Take Quiz":
        st.title("🧠 Take a Quiz")
        topic = st.text_input("Topic")
        num_questions = st.slider("Number of Questions", 1, 10, 3)

        if st.button("Generate Quiz"):
            if topic:
                try:
                    res = requests.post("http://127.0.0.1:8000/generate-quiz/", json={
                        "topic": topic,
                        "num_questions": num_questions
                    })
                    data = res.json()
                    st.session_state.quiz = data["questions"]
                    st.session_state.user_answers = [None] * num_questions
                    st.success("Quiz generated!")
                except:
                    st.error("Quiz server not running.")

        if "quiz" in st.session_state:
            st.subheader("Answer the Questions:")
            for i, q in enumerate(st.session_state.quiz):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                st.session_state.user_answers[i] = st.radio(
                    label=f"Q{i+1} Options",
                    options=["A", "B", "C", "D"],
                    key=f"q{i}"
                )

            if st.button("Submit Answers"):
                correct = sum([
                    1 for i in range(len(st.session_state.quiz))
                    if st.session_state.user_answers[i] == st.session_state.quiz[i]["answer"]
                ])
                st.success(f"Score: {correct}/{len(st.session_state.quiz)}")
                st.session_state.quiz_history.append({
                    "topic": topic,
                    "score": f"{correct}/{len(st.session_state.quiz)}"
                })
                st.session_state.students[st.session_state.user_id].append({
                    "topic": topic, "score": correct
                })

    elif choice == "Quiz History":
        st.title("📜 Quiz History")
        for q in st.session_state.quiz_history:
            st.write(f"📘 **{q['topic']}** - Score: {q['score']}")

    elif choice == "Courses":
        st.title("📚 Available Courses")
        for course in courses_list:
            st.subheader(course["title"])
            st.markdown(f"_{course['description']}_")
            st.markdown(f"[▶ Watch on YouTube]({course['url']})")

# ------------------ EDUCATOR ------------------
elif st.session_state.role == "educator":
    st.sidebar.title("👩‍🏫 Educator Panel")
    option = st.sidebar.radio("Navigate", ["Dashboard", "Student Activity"])

    if option == "Dashboard":
        st.title(f"Welcome Educator {st.session_state.user_id}")
        st.info("Here you can manage students and monitor activity.")

    elif option == "Student Activity":
        st.title("📊 Student Activity Monitor")
        if not st.session_state.students:
            st.warning("No student activity yet.")
        else:
            for student, records in st.session_state.students.items():
                st.subheader(f"👤 {student}")
                if not records:
                    st.markdown("_No quizzes taken yet._")
                for rec in records:
                    st.write(f"📝 Topic: **{rec['topic']}**, Score: **{rec['score']}**")