# state.py v1.1
import threading
import time

class BuzzState:
    def __init__(self):
        self.lock = threading.Lock()
        self.first_buzz = None  # {"team": str, "timestamp": float}
        self.last_clear = time.time()

    def buzz(self, team_name: str):
        """
        Attempt to buzz in.
        Returns (success: bool, first_buzz: dict|None).
        """
        now = time.time()
        with self.lock:
            if self.first_buzz is None:
                self.first_buzz = {"team": team_name, "timestamp": now}
                return True, self.first_buzz
            else:
                return False, self.first_buzz

    def clear(self):
        """Clear the buzzer lockout."""
        with self.lock:
            self.first_buzz = None
            self.last_clear = time.time()

    def get(self):
        """Return the first buzz info."""
        with self.lock:
            return self.first_buzz


# ---------------------------------------------------------
# TEAM NAMES (default placeholders)
# These will be replaced when students enter their names.
# ---------------------------------------------------------
TEAM_NAMES = {
    0: "Team 1",
    1: "Team 2",
    2: "Team 3",
    3: "Team 4"
}

# Shared buzzer state instance
BUZZ_STATE = BuzzState()
