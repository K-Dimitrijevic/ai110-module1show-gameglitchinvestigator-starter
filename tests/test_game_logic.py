from logic_utils import (
    check_guess,
    get_attempt_limit,
    get_hint_message,
    get_range_for_difficulty,
    new_game_state,
    parse_guess,
    process_guess,
    update_score,
)

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


def test_hard_range_is_largest():
    assert get_range_for_difficulty("Hard") == (1, 200)


def test_wrong_guesses_always_lose_points():
    for attempt in range(1, 6):
        assert update_score(50, "Too High", attempt) == 45
        assert update_score(50, "Too Low", attempt) == 45


def test_hints_point_toward_secret():
    assert "LOWER" in get_hint_message("Too High")
    assert "HIGHER" in get_hint_message("Too Low")


def test_parse_valid_whole_number():
    assert parse_guess(" 42 ", 1, 100) == (True, 42, None)


def test_parse_empty_and_blank_ask_for_guess():
    for raw in [None, "", "   "]:
        assert parse_guess(raw, 1, 100) == (False, None, "Enter a guess.")


def test_parse_rejects_non_numbers():
    assert parse_guess("abc", 1, 100) == (False, None, "That is not a number.")


def test_parse_rejects_decimals():
    for raw in ["12.5", "12.0"]:
        assert parse_guess(raw, 1, 100) == (False, None, "Please enter a whole number.")


def test_parse_rejects_out_of_range():
    for raw in ["0", "-5", "101"]:
        ok, value, err = parse_guess(raw, 1, 100)
        assert not ok and value is None
        assert err == "Your guess must be between 1 and 100."


def test_win_score_by_attempt():
    assert update_score(0, "Win", 1) == 100
    assert update_score(0, "Win", 2) == 90
    assert update_score(0, "Win", 20) == 10


def test_attempt_limits():
    assert get_attempt_limit("Easy") == 6
    assert get_attempt_limit("Normal") == 8
    assert get_attempt_limit("Hard") == 5


def test_new_game_state_is_fresh_and_in_range():
    for difficulty in ["Easy", "Normal", "Hard"]:
        state = new_game_state(difficulty)
        low, high = get_range_for_difficulty(difficulty)
        assert low <= state["secret"] <= high
        assert state["attempts"] == 0
        assert state["score"] == 0
        assert state["status"] == "playing"
        assert state["history"] == []


def _game(secret=50):
    return {**new_game_state("Normal"), "secret": secret}


def test_invalid_guess_does_not_use_attempt():
    state = _game()
    for raw in ["", "abc", "12.5", "500"]:
        new_state, feedback = process_guess(state, raw, "Normal")
        assert new_state == state
        assert feedback[0][0] == "error"


def test_wrong_guess_uses_attempt_and_hints():
    state, feedback = process_guess(_game(50), "60", "Normal")
    assert state["attempts"] == 1
    assert state["history"] == [60]
    assert state["score"] == -5
    assert ("warning", "📉 Go LOWER!") in feedback


def test_process_guess_does_not_mutate_input():
    original = _game(50)
    process_guess(original, "60", "Normal")
    assert original["attempts"] == 0
    assert original["history"] == []


def test_correct_guess_wins():
    state, feedback = process_guess(_game(50), "50", "Normal")
    assert state["status"] == "won"
    assert state["score"] == 100


def test_running_out_of_attempts_loses():
    state = _game(50)
    for _ in range(get_attempt_limit("Normal")):
        state, feedback = process_guess(state, "1", "Normal")
    assert state["status"] == "lost"
    assert feedback[-1][1].startswith("Out of attempts!")
