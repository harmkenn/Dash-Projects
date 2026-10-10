# pages/buzzer.py v1.1
import streamlit as st
import time

from state import BUZZ_STATE, TEAM_NAMES

st.set_page_config(page_title="Team Buzzer", layout="centered")

st.title("🔔 Team Buzzer")

st.write("Enter your **team name** and wait for the teacher to start a question.")

# ---------------------------------------------------------
# TEAM NAME ENTRY
# ---------------------------------------------------------
team_name = st.text_input("Team name", value="", max_chars=30)

if "assigned_team_index" not in st.session_state:
    st.session_state.assigned_team_index = None

# Assign team slot when they enter a name
if st.button("Save Team Name"):
    if not team_name.strip():
        st.warning("Please enter a valid team name.")
    else:
        # If this phone has not been assigned a team slot yet
        if st.session_state.assigned_team_index is None:
            # 1. Check if this team name already exists (reconnect)
            found_existing = False
            for i, name in TEAM_NAMES.items():
                if name == team_name.strip():
                    st.session_state.assigned_team_index = i
                    found_existing = True
                    break
            
            # 2. If not found, find first available slot
            if not found_existing:
                for i in range(4):
                    if TEAM_NAMES[i].startswith("Team "):  # default placeholder
                        TEAM_NAMES[i] = team_name.strip()
                        st.session_state.assigned_team_index = i
                        break
        else:
            # Update existing slot
            TEAM_NAMES[st.session_state.assigned_team_index] = team_name.strip()

        st.success(f"Team name set to: {team_name.strip()}")

# If they haven't saved a name yet, stop here
if st.session_state.assigned_team_index is None:
    st.stop()

team_index = st.session_state.assigned_team_index
team_label = TEAM_NAMES[team_index]

st.markdown(f"### Your team: **{team_label}**")

# ---------------------------------------------------------
# BUZZER BUTTON
# ---------------------------------------------------------
if "last_buzz_result" not in st.session_state:
    st.session_state.last_buzz_result = None

if st.button("🔴 BUZZ IN!", use_container_width=True):
    success, first = BUZZ_STATE.buzz(team_label)
    st.session_state.last_buzz_result = success
    st.session_state.last_buzz_time = time.time()

# ---------------------------------------------------------
# BUZZER FEEDBACK
# ---------------------------------------------------------
if st.session_state.last_buzz_result is True:
    st.success("🎉 You buzzed in FIRST! Wait for the teacher.")
elif st.session_state.last_buzz_result is False:
    first = BUZZ_STATE.get()
    if first:
        st.error(f"Too late! **{first['team']}** buzzed in first.")
    else:
        st.info("No active question or buzzers have been cleared yet.")

st.markdown("---")
st.caption("Keep this page open. Tap the button as soon as you know the answer.")
