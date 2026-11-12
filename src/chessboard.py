from move import Move
from pieces import PROMOTION_CLASSES, King, Pawn, Rook
from utils import BOARD_SIZE, validate_coords


class Chessboard:
    """Manages the 8x8 chessboard state, piece positions, and move execution.

    Attributes:
        grid (list[list[Piece or None]]): 2D list representing squares on the 8x8 board.
        en_passant_target (tuple or None): Target coordinates eligible for en passant.
    """

    def __init__(self):
        """Initializes an empty 8x8 chessboard and resets state variables."""
        self._grid = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self._pieces_coords = {"W": [], "B": []}
        self._king_coords = {"W": None, "B": None}
        self.en_passant_target = None

    @property
    def grid(self):
        """Gets the 8x8 chessboard grid.

        Returns:
            list[list[Piece or None]]: The 2D grid containing pieces or None.
        """
        return self._grid

    @property
    def en_passant_target(self):
        """Gets current en passant target square coordinates.

        Returns:
            tuple or None: (x, y) coordinates of target square, or None.
        """
        return self._en_passant_target

    @en_passant_target.setter
    def en_passant_target(self, value):
        """Sets current en passant target square coordinates.

        Args:
            value (tuple or None): (x, y) coordinates of target square, or None.

        Raises:
            TypeError: If value is not a tuple of two ints or None.
            ValueError: If coordinates are not between 0 and 7.
        """
        validate_coords(value, allow_none=True)
        self._en_passant_target = value

    def __str__(self):
        """Returns a colored ANSI string representation of the chessboard.

        Returns:
            str: String representing the chessboard with ANSI background colors.
        """
        reset = "\033[0m"
        result = "   A  B  C  D  E  F  G  H  "
        for y in range(BOARD_SIZE):
            result += f"\n{BOARD_SIZE - y} "
            for x in range(BOARD_SIZE):
                piece = self.grid[y][x]
                is_light_square = (x + y) % 2 == 0
                bg_color = "\033[47m" if is_light_square else "\033[100m"
                glyph = " " if piece is None else piece.symbols[int((piece.color == "W") == is_light_square)]
                result += f"{bg_color} {glyph} {reset}"
        return result

    def pieces_coords(self, color):
        """Gets the coordinates of all active pieces of a color.

        Args:
            color (str): 'W' or 'B'.

        Returns:
            list[tuple]: List of (x, y) coordinate tuples.
        """
        return self._pieces_coords[color]

    def king_coords(self, color):
        """Gets the coordinates of the king of a color.

        Args:
            color (str): 'W' or 'B'.

        Returns:
            tuple or None: (x, y) coordinates of the king, or None if it is not on the board.
        """
        return self._king_coords[color]

    def get_piece_at(self, coords):
        """Retrieves the piece located at the given coordinates.

        Args:
            coords (tuple): The (x, y) coordinates on the board.

        Returns:
            Piece or None: The piece at the coordinates, or None if empty.
        """
        x, y = coords
        return self._grid[y][x]

    def add_piece(self, piece, coords):
        """Adds a piece to the board at the specified coordinates.

        Args:
            piece (Piece): The piece to add to the chessboard.
            coords (tuple): The (x, y) coordinates where the piece will be placed.

        Returns:
            bool: True if the piece was successfully placed, False if square is occupied.
        """
        if self.get_piece_at(coords) is not None:
            return False
        x, y = coords
        self._grid[y][x] = piece
        self._pieces_coords[piece.color].append(coords)
        if isinstance(piece, King):
            self._king_coords[piece.color] = coords
        return True

    def remove_piece(self, coords):
        """Removes the piece at the specified coordinates from the board.

        Args:
            coords (tuple): The (x, y) coordinates of the piece to remove.

        Returns:
            bool: True if a piece was removed, False if square was empty.
        """
        piece = self.get_piece_at(coords)
        if piece is None:
            return False
        x, y = coords
        self._grid[y][x] = None
        self._pieces_coords[piece.color].remove(coords)
        if isinstance(piece, King):
            self._king_coords[piece.color] = None
        return True

    def is_promotion(self, start, end):
        """Checks whether moving the piece at start to end is a pawn promotion.

        Args:
            start (tuple): The starting (x, y) coordinates.
            end (tuple): The destination (x, y) coordinates.

        Returns:
            bool: True if a pawn would reach the last row, False otherwise.
        """
        return isinstance(self.get_piece_at(start), Pawn) and end[1] in (0, BOARD_SIZE - 1)

    def make_move(self, start, end, promotion=None):
        """Executes a move (captures, castling, en passant, promotion) WITHOUT validating it.

        Callers must make sure the move is pseudo-legal; use Game.play_move for
        validated moves.

        Args:
            start (tuple): The starting (x, y) coordinates of the piece.
            end (tuple): The destination (x, y) coordinates.
            promotion (str, optional): Promotion piece key ('Q', 'R', 'B', 'N'). Only
                used when the move is a promotion. Defaults to 'Q'.

        Returns:
            Move: The record needed to revert the move with undo_move.
        """
        piece = self.get_piece_at(start)
        is_promotion = self.is_promotion(start, end)
        move = Move(
            start, end, piece,
            previous_en_passant=self.en_passant_target,
            previous_has_moved=piece.has_moved,
        )
        start_x, start_y = start
        end_x, end_y = end

        # Capture. For en passant the victim is beside the pawn, not on the destination.
        captured_coords = end
        if isinstance(piece, Pawn) and end == self.en_passant_target:
            captured_coords = (end_x, start_y)
        captured = self.get_piece_at(captured_coords)
        if captured is not None:
            move.captured = captured
            move.captured_coords = captured_coords
            self.remove_piece(captured_coords)

        # Castling: the rook jumps over the king.
        if isinstance(piece, King) and abs(end_x - start_x) == 2:
            rook_start_x, rook_end_x = (7, end_x - 1) if end_x > start_x else (0, end_x + 1)
            rook_start, rook_end = (rook_start_x, start_y), (rook_end_x, start_y)
            rook = self.get_piece_at(rook_start)
            self._relocate(rook, rook_start, rook_end)
            rook.has_moved = True
            move.rook_move = (rook_start, rook_end)

        if isinstance(piece, (King, Rook)):
            piece.has_moved = True

        self.en_passant_target = None
        if isinstance(piece, Pawn) and abs(end_y - start_y) == 2:
            self.en_passant_target = (start_x, (start_y + end_y) // 2)

        self._relocate(piece, start, end)

        if is_promotion:
            promoted = PROMOTION_CLASSES[promotion or "Q"](piece.color)
            if promoted.has_moved is not None:
                promoted.has_moved = True
            self.remove_piece(end)
            self.add_piece(promoted, end)
            move.promoted = promoted
        return move

    def undo_move(self, move):
        """Reverts a move previously returned by make_move.

        Args:
            move (Move): The record of the move to revert. Moves must be undone in
                the reverse order they were made.
        """
        self.remove_piece(move.end)  # the moved piece, or the promoted one
        self.add_piece(move.piece, move.start)
        move.piece.has_moved = move.previous_has_moved

        if move.rook_move is not None:
            rook_start, rook_end = move.rook_move
            rook = self.get_piece_at(rook_end)
            self._relocate(rook, rook_end, rook_start)
            rook.has_moved = False

        if move.captured is not None:
            self.add_piece(move.captured, move.captured_coords)
        self.en_passant_target = move.previous_en_passant

    def _relocate(self, piece, start, end):
        """Moves a piece to an empty square, keeping the coordinate caches in sync.

        Args:
            piece (Piece): The piece standing on start.
            start (tuple): The current (x, y) coordinates of the piece.
            end (tuple): The empty destination (x, y) coordinates.
        """
        self.remove_piece(start)
        self.add_piece(piece, end)
