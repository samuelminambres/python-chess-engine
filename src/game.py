from chessboard import Chessboard
from pieces import Bishop, King, Knight, Pawn, Queen, Rook
from timers import Timer
from utils import OPPONENT, to_notation

SUCCESS = "SUCCESS"
INVALID = "INVALID"
CHECKMATE = "CHECKMATE"
STALEMATE = "STALEMATE"
DRAW = "DRAW"
TIMEOUT = "TIMEOUT"

BACK_RANK = (Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook)
FIFTY_MOVE_LIMIT = 100  # half-moves (50 moves by each player)
REPETITION_LIMIT = 3


class Game:
    """Controls the chess rules, turn cycle, timers, and move history.

    Attributes:
        board (Chessboard): The active chessboard instance.
        turn (str): Current player turn ('W' or 'B').
        white_timer (Timer): Clock timer for the White player.
        black_timer (Timer): Clock timer for the Black player.
        half_move_clock (int): Half-moves since the last pawn move or capture.
        history (list[Move]): Chronological list of completed moves.
        initial_position_key (tuple or None): Signature of the starting position.
    """

    def __init__(self, time_limit=600.0, increment=0.0):
        """Initializes a new chess game.

        Args:
            time_limit (float, optional): Initial time per player in seconds. Defaults to 600.0.
            increment (float, optional): Time increment per move in seconds. Defaults to 0.0.
        """
        self.board = Chessboard()
        self.turn = "W"
        self.white_timer = Timer(time_limit, increment)
        self.black_timer = Timer(time_limit, increment)
        self.half_move_clock = 0
        self.history = []
        self.initial_position_key = None

    @property
    def turn(self):
        """Gets the current player's turn.

        Returns:
            str: 'W' for White or 'B' for Black.
        """
        return self._turn

    @turn.setter
    def turn(self, value):
        """Sets the current player's turn.

        Args:
            value (str): 'W' or 'B'.

        Raises:
            TypeError: If value is not a string.
            ValueError: If value is not 'W' or 'B'.
        """
        if not isinstance(value, str):
            raise TypeError("Turn must be str")
        if value != "W" and value != "B":
            raise ValueError('Turn must be "W" or "B"')
        self._turn = value

    @property
    def half_move_clock(self):
        """Gets the half-move clock counter for the 50-move rule.

        Returns:
            int: Number of half-moves since last pawn move or capture.
        """
        return self._half_move_clock

    @half_move_clock.setter
    def half_move_clock(self, value):
        """Sets the half-move clock counter for the 50-move rule.

        Args:
            value (int): Half-move counter value.

        Raises:
            TypeError: If value is not an int.
            ValueError: If value is negative.
        """
        if not isinstance(value, int):
            raise TypeError("Counter value must be int")
        if value < 0:
            raise ValueError("Value must be 0 or greater")
        self._half_move_clock = value

    @property
    def current_timer(self):
        """Gets the timer of the player whose turn it is.

        Returns:
            Timer: The timer of the side to move.
        """
        return self.white_timer if self.turn == "W" else self.black_timer

    def __str__(self):
        """Returns the formatted move history in algebraic notation.

        Returns:
            str: String of moves in format 'A1 -> A2\\n'.
        """
        return "".join(f"{to_notation(m.start)} -> {to_notation(m.end)}\n" for m in self.history)

    def setup_standard_board(self):
        """Sets up initial piece positions and records the starting position signature."""
        for x, piece_class in enumerate(BACK_RANK):
            self.board.add_piece(piece_class("B"), (x, 0))
            self.board.add_piece(Pawn("B"), (x, 1))
            self.board.add_piece(Pawn("W"), (x, 6))
            self.board.add_piece(piece_class("W"), (x, 7))
        self.initial_position_key = self.get_position_key()

    def start_clock(self):
        """Starts the clock of the player whose turn it is."""
        self.current_timer.start()

    def swap_turn(self):
        """Swaps the turn between White ('W') and Black ('B')."""
        self.turn = OPPONENT[self.turn]

    def make_move(self, start, end, promotion=None):
        """Applies a move and passes the turn WITHOUT validating it or touching the clocks.

        Meant for search algorithms that apply and revert moves with undo_move.

        Args:
            start (tuple): The starting (x, y) coordinates.
            end (tuple): The destination (x, y) coordinates.
            promotion (str, optional): Promotion piece key ('Q', 'R', 'B', 'N'). Defaults to 'Q'.

        Returns:
            Move: The record of the applied move (also appended to history).
        """
        move = self.board.make_move(start, end, promotion)
        move.previous_half_move_clock = self.half_move_clock
        if isinstance(move.piece, Pawn) or move.captured is not None:
            self.half_move_clock = 0
        else:
            self.half_move_clock += 1
        self.history.append(move)
        self.swap_turn()
        return move

    def undo_move(self):
        """Reverts the last move, restoring the board, half-move clock, and turn."""
        move = self.history.pop()
        self.board.undo_move(move)
        self.half_move_clock = move.previous_half_move_clock
        self.swap_turn()

    def undo_turns(self, count=1):
        """Reverts the last moves and gives the running clock back to the side to move.

        Args:
            count (int, optional): Number of half-moves to revert. Defaults to 1.

        Returns:
            bool: True if the moves were reverted, False if the history is too short.
        """
        if len(self.history) < count:
            return False
        for _ in range(count):
            self.undo_move()
        self.white_timer.pause()
        self.black_timer.pause()
        self.start_clock()
        return True

    def is_in_check(self, color=None):
        """Checks whether a king is attacked.

        Args:
            color (str, optional): Color of the king to check. Defaults to the side to move.

        Returns:
            bool: True if the king is attacked, False otherwise.
        """
        color = color or self.turn
        king_coords = self.board.king_coords(color)
        for coords in self.board.pieces_coords(OPPONENT[color]):
            piece = self.board.get_piece_at(coords)
            if king_coords in piece.get_possible_moves(self.board, coords):
                return True
        return False

    def is_insufficient_material(self):
        """Determines if the game is a draw due to insufficient material to checkmate.

        Returns:
            bool: True for king vs king, or king vs king plus one minor piece.
        """
        white = self.board.pieces_coords("W")
        black = self.board.pieces_coords("B")
        for lone_king, other in ((white, black), (black, white)):
            if len(lone_king) == 1 and len(other) <= 2:
                return all(isinstance(self.board.get_piece_at(c), (King, Bishop, Knight)) for c in other)
        return False

    def get_position_key(self):
        """Generates an immutable signature of the current board and game state.

        Encapsulates piece layout, castling rights (via piece movement flags), the
        player to move, and the en passant target, to evaluate threefold repetition.

        Returns:
            tuple: The 64-square layout, the player to move, and the en passant target.
        """
        squares = tuple(
            None if piece is None else (piece.color, type(piece).__name__, piece.has_moved)
            for row in self.board.grid
            for piece in row
        )
        return (squares, self.turn, self.board.en_passant_target)

    def is_threefold_repetition(self, current_key):
        """Determines whether the given position has occurred three or more times.

        Args:
            current_key (tuple): The position signature generated by get_position_key.

        Returns:
            bool: True if the position has occurred at least 3 times, False otherwise.
        """
        count = int(self.initial_position_key == current_key)
        count += sum(move.position_key == current_key for move in self.history)
        return count >= REPETITION_LIMIT

    def get_all_legal_moves(self):
        """Generates all legal (start, end) coordinate moves for the current player.

        Returns:
            list[tuple[tuple[int, int], tuple[int, int]]]: List of tuples with start and end coordinates.
        """
        legal_moves = []
        # Iterate over a copy: simulating moves reorders the coordinate lists.
        for start in list(self.board.pieces_coords(self.turn)):
            piece = self.board.get_piece_at(start)
            for end in piece.get_possible_moves(self.board, start):
                if self._is_legal(piece, start, end):
                    legal_moves.append((start, end))
        return legal_moves

    def is_legal_move(self, start, end):
        """Checks whether a move is legal for the current player.

        Args:
            start (tuple): The starting (x, y) coordinates.
            end (tuple): The destination (x, y) coordinates.

        Returns:
            bool: True if the move is legal, False otherwise.
        """
        return (start, end) in self.get_all_legal_moves()

    def play_move(self, start, end, promotion=None):
        """Plays a move if it is legal and reports the resulting game status.

        Args:
            start (tuple): The starting (x, y) coordinates.
            end (tuple): The destination (x, y) coordinates.
            promotion (str, optional): Promotion piece key ('Q', 'R', 'B', 'N'). Defaults to 'Q'.

        Returns:
            str: SUCCESS if the game goes on, INVALID if the move was rejected (nothing
                changes), TIMEOUT if the mover's clock had expired (nothing changes), or
                CHECKMATE, STALEMATE, DRAW if the move ended the game. After a game-ending
                move, turn is the side that is checkmated or stalemated.
        """
        mover_timer = self.current_timer
        if mover_timer.is_timeout():
            return TIMEOUT
        if not self.is_legal_move(start, end):
            return INVALID

        move = self.make_move(start, end, promotion)
        move.position_key = self.get_position_key()
        mover_timer.stop()
        self.start_clock()

        if not self.get_all_legal_moves():
            return CHECKMATE if self.is_in_check() else STALEMATE
        if (self.half_move_clock >= FIFTY_MOVE_LIMIT
                or self.is_threefold_repetition(move.position_key)
                or self.is_insufficient_material()):
            return DRAW
        return SUCCESS

    def _is_legal(self, piece, start, end):
        """Checks that a pseudo-legal move does not leave the mover's king in check.

        Castling additionally requires that the king is not in check and does not
        cross an attacked square.

        Args:
            piece (Piece): The piece making the move.
            start (tuple): The starting (x, y) coordinates.
            end (tuple): The destination (x, y) coordinates.

        Returns:
            bool: True if the move is legal, False otherwise.
        """
        color = piece.color
        if isinstance(piece, King) and abs(end[0] - start[0]) == 2:
            crossed_square = ((start[0] + end[0]) // 2, start[1])
            if self.is_in_check(color) or not self._is_king_safe_after(color, start, crossed_square):
                return False
        return self._is_king_safe_after(color, start, end)

    def _is_king_safe_after(self, color, start, end):
        """Simulates a move and checks whether the mover's king is safe afterwards.

        Args:
            color (str): Color of the moving player.
            start (tuple): The starting (x, y) coordinates.
            end (tuple): The destination (x, y) coordinates.

        Returns:
            bool: True if the king is not attacked after the move, False otherwise.
        """
        move = self.board.make_move(start, end)
        is_safe = not self.is_in_check(color)
        self.board.undo_move(move)
        return is_safe
