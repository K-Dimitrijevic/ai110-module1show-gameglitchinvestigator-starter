# FIX: Moved all game logic here from app.py so it is testable; I asked, Claude refactored it in agent mode.
import random

ATTEMPT_LIMITS = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    # FIX: Hard was 1-50 (easier than Normal); Claude flagged it, I chose 1-200.
    if difficulty == "Hard":
        return 1, 200
    return 1, 100


def get_attempt_limit(difficulty: str):
    """Return how many guesses a game allows for a given difficulty."""
    return ATTEMPT_LIMITS.get(difficulty, ATTEMPT_LIMITS["Normal"])


def parse_guess(raw: str, low: int = None, high: int = None):
    """
    Parse user input into an int guess, optionally within [low, high].

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    # FIX: Blank/space-only input now says 'Enter a guess.'; Claude found it, I chose the message.
    if raw is None or raw.strip() == "":
        return False, None, "Enter a guess."

    raw = raw.strip()

    # FIX: Decimals were silently truncated; Claude found it, I chose to reject them with a whole-number prompt.
    if "." in raw:
        return False, None, "Please enter a whole number."

    try:
        value = int(raw)
    except ValueError:
        return False, None, "That is not a number."

    # FIX: Out-of-range guesses were accepted; Claude found it, I asked that they be rejected.
    if low is not None and high is not None and not low <= value <= high:
        return False, None, f"Your guess must be between {low} and {high}."

    return True, value, None


def check_guess(guess: int, secret: int):
    """
    Compare guess to secret and return the outcome.

    outcome is one of: "Win", "Too High", "Too Low"
    """
    # FIX: Secret flipped between int and str on even attempts; I reported it changing, Claude traced the cause.
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def get_hint_message(outcome: str):
    """Return the hint shown to the player for a given outcome."""
    if outcome == "Win":
        return "🎉 Correct!"
    if outcome == "Too High":
        # FIX: Hints were backwards; I reported it, Claude swapped them and added a test.
        return "📉 Go LOWER!"
    return "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        # 100 for a first-try win, 10 fewer for each extra attempt.
        # FIX: Win score was off by one (first-try win gave 70); Claude found it, I asked for it fixed.
        points = 100 - 10 * (attempt_number - 1)
        if points < 10:
            points = 10
        return current_score + points

    # FIX: Some wrong 'Too High' guesses added points; Claude found it, I asked for it fixed.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score


def new_game_state(difficulty: str):
    """Return the starting state for a game with a fresh secret."""
    low, high = get_range_for_difficulty(difficulty)
    return {
        "secret": random.randint(low, high),
        "attempts": 0,
        # FIX: Score carried over between games; I reported it, Claude made new games reset it.
        "score": 0,
        "status": "playing",
        "history": [],
    }


def process_guess(state: dict, raw: str, difficulty: str, show_hint: bool = True):
    """
    Apply one raw guess to a game state.

    Returns: (new_state: dict, feedback: list of (kind, message))
    kind is one of "error", "warning", "success", "balloons".
    Invalid input (empty, non-numbers, decimals, out of range) leaves the
    state unchanged and does not use up an attempt.
    """
    low, high = get_range_for_difficulty(difficulty)
    state = {**state, "history": list(state["history"])}
    feedback = []

    # FIX: Invalid input used up attempts (could go negative); Claude found it, I set the rule that it costs nothing.
    ok, guess, err = parse_guess(raw, low, high)
    if not ok:
        feedback.append(("error", err))
        return state, feedback

    state["attempts"] += 1
    state["history"].append(guess)

    outcome = check_guess(guess, state["secret"])

    if show_hint:
        feedback.append(("warning", get_hint_message(outcome)))

    state["score"] = update_score(state["score"], outcome, state["attempts"])

    if outcome == "Win":
        state["status"] = "won"
        feedback.append(("balloons", None))
        feedback.append((
            "success",
            f"You won! The secret was {state['secret']}. "
            f"Final score: {state['score']}",
        ))
    elif state["attempts"] >= get_attempt_limit(difficulty):
        state["status"] = "lost"
        feedback.append((
            "error",
            f"Out of attempts! "
            f"The secret was {state['secret']}. "
            f"Score: {state['score']}",
        ))

    return state, feedback
