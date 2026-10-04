import streamlit as st

from logic_utils import (
    get_attempt_limit,
    get_range_for_difficulty,
    new_game_state,
    process_guess,
)


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

GAME_STATE_KEYS = ("secret", "attempts", "score", "status", "history")


# FIX: One reset path for first load, New Game and difficulty change keeps the attempt counter consistent; I reported it, Claude unified it.
def start_new_game():
    st.session_state.update(new_game_state(st.session_state.difficulty))
    st.session_state.feedback = []


# FIX: Guess handled in a callback so the debug panel and score update immediately; I spotted the -20 vs -25 mismatch, Claude fixed it.
def submit_guess():
    """
    Runs as a callback, before the page is drawn, so everything rendered
    below already reflects this guess.
    """
    difficulty = st.session_state.difficulty
    state, feedback = process_guess(
        state={key: st.session_state[key] for key in GAME_STATE_KEYS},
        raw=st.session_state[f"guess_input_{difficulty}"],
        difficulty=difficulty,
        show_hint=st.session_state.get("show_hint", True),
    )
    st.session_state.update(state)
    st.session_state.feedback = feedback


if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Normal"

if "secret" not in st.session_state:
    start_new_game()

difficulty = st.session_state.difficulty
attempt_limit = get_attempt_limit(difficulty)
low, high = get_range_for_difficulty(difficulty)
game_over = st.session_state.status != "playing"
game_in_progress = not game_over and st.session_state.attempts > 0

st.sidebar.header("Settings")

# FIX: Difficulty can't change mid-game; my request, implemented by Claude in agent mode.
# Difficulty is locked once the first guess is made; changing it while
# no guesses have been made starts a fresh game in the new range.
st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    key="difficulty",
    disabled=game_in_progress,
    on_change=start_new_game,
)
if game_in_progress:
    st.sidebar.caption("Start a new game to change difficulty.")

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

st.subheader("Make a guess")

st.info(
    # FIX: Prompt said 1-100 for every difficulty; Claude found it, I asked for it to follow the range.
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

# FIX: Enter didn't submit and clicks resubmitted my previous guess; I reported both, Claude diagnosed and fixed them.
# A form sends the typed guess and the submit together, and lets Enter submit.
with st.form("guess_form", clear_on_submit=True):
    st.text_input(
        "Enter your guess:",
        key=f"guess_input_{difficulty}",
        # FIX: Guess box disabled after a game ends; my request after Claude flagged it.
        disabled=game_over,
    )
    st.form_submit_button(
        "Submit Guess 🚀",
        on_click=submit_guess,
        disabled=game_over,
    )

col1, col2 = st.columns(2)
with col1:
    new_game = st.button("New Game 🔁", on_click=start_new_game)
with col2:
    st.checkbox("Show hint", value=True, key="show_hint")

if new_game:
    st.success("New game started.")

# Show the result of the last guess once, then clear it.
feedback = st.session_state.feedback
st.session_state.feedback = []
for kind, message in feedback:
    if kind == "balloons":
        st.balloons()
    else:
        getattr(st, kind)(message)

if game_over and not feedback:
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
