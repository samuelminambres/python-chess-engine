import time


class Timer:
    """Manages game clock countdown and per-move increments for a player.

    Attributes:
        time_left (float): Remaining time in seconds.
        increment (float): Time increment in seconds added when stopped.
        last_start_time (float or None): Epoch timestamp of the last clock start.
        is_running (bool): Whether the timer is actively counting down.
    """

    def __init__(self, time_limit: float, increment: float):
        """Initializes the timer with a time limit and increment.

        Args:
            time_limit (float): Initial time limit in seconds.
            increment (float): Time increment in seconds added when stopped.
        """
        self.time_left = float(time_limit)
        self.increment = float(increment)
        self.last_start_time = None
        self.is_running = False

    def __str__(self):
        """Returns the remaining time as MM:SS (call update first for a live value).

        Returns:
            str: The remaining time formatted as 'MM:SS'.
        """
        minutes, seconds = divmod(int(self.time_left), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def start(self):
        """Starts the timer if it is not already running."""
        if not self.is_running:
            self.last_start_time = time.time()
            self.is_running = True

    def pause(self):
        """Stops the timer without adding the increment."""
        if self.is_running:
            self.update()
            self.is_running = False

    def stop(self):
        """Stops the timer and adds the increment to the remaining time."""
        if self.is_running:
            self.pause()
            self.time_left += self.increment

    def update(self):
        """Updates the remaining time based on the elapsed time since last start."""
        if self.is_running:
            current_time = time.time()
            self.time_left = max(0.0, self.time_left - (current_time - self.last_start_time))
            self.last_start_time = current_time

    def is_timeout(self):
        """Checks if the timer has expired.

        Returns:
            bool: True if remaining time is less than or equal to 0, False otherwise.
        """
        self.update()
        return self.time_left <= 0
