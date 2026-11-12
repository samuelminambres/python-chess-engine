from utils import BOARD_SIZE

# Positional bonus tables from White's perspective (row 0 is rank 8).
PAWN_TABLE = [
    [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
    [ 5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0],
    [ 1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0],
    [ 0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5],
    [ 0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0],
    [ 0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5,  0.5],
    [ 0.5,  1.0,  1.0, -2.0, -2.0,  1.0,  1.0,  0.5],
    [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
]
KNIGHT_TABLE = [
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
    [-4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0],
    [-3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0],
    [-3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0],
    [-3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0],
    [-3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0],
    [-4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0],
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
]
BISHOP_TABLE = [
    [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
    [-1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
    [-1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0],
    [-1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0],
    [-1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0],
    [-1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0],
    [-1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0],
    [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
]
ROOK_TABLE = [
    [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
    [ 0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5],
    [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [ 0.0,  0.0,  0.0,  0.5,  0.5,  0.0,  0.0,  0.0],
]
QUEEN_TABLE = [
    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
    [-1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
    [-1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
    [-0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
    [ 0.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
    [-1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
    [-1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0],
    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
]
KING_TABLE = [
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
    [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
    [ 2.0,  2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0],
    [ 2.0,  3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0],
]

ORTHOGONAL = ((1, 0), (-1, 0), (0, 1), (0, -1))
DIAGONAL = ((1, 1), (1, -1), (-1, 1), (-1, -1))


class Piece:
    """Base class representing a chess piece on the board.

    Subclasses only declare their data (directions, value, tables); the move
    generation shared by all non-pawn pieces lives here.

    Attributes:
        color (str): The piece color ('W' for White, 'B' for Black).
        has_moved (bool or None): Whether the piece has moved. Only tracked for kings
            and rooks (castling rights); None for every other piece.
        value (int): Material value of the piece.
        directions (tuple[tuple[int, int], ...]): Movement vectors (dx, dy).
        sliding (bool): True if the piece repeats its directions until blocked.
        piece_square_table (list[list[float]]): Positional bonus table for evaluation.
        symbols (tuple[str, str]): Unicode glyphs used for White and Black.
    """

    value = 0
    directions = ()
    sliding = False
    piece_square_table = None
    symbols = ("", "")

    def __init__(self, color):
        """Initializes a chess piece with its color.

        Args:
            color (str): The color of the piece, either 'W' (White) or 'B' (Black).
        """
        self.color = color
        self.has_moved = None

    @property
    def color(self):
        """Gets the color of the piece.

        Returns:
            str: The piece color ('W' or 'B').
        """
        return self._color

    @color.setter
    def color(self, value):
        """Sets the color of the piece.

        Args:
            value (str): The piece color ('W' or 'B').

        Raises:
            TypeError: If value is not a string.
            ValueError: If value is not 'W' or 'B'.
        """
        if not isinstance(value, str):
            raise TypeError("Color must be str")
        if value != "W" and value != "B":
            raise ValueError('Color must be "W" or "B"')
        self._color = value

    def __str__(self):
        """Returns the Unicode character representation of the piece.

        Returns:
            str: The glyph for White or for Black.
        """
        return self.symbols[0] if self.color == "W" else self.symbols[1]

    def get_possible_moves(self, board, coords):
        """Calculates the pseudo-legal moves along self.directions.

        Sliding pieces keep going until they hit a piece or the edge; the others
        take a single step. Moves that leave the own king in check are not filtered.

        Args:
            board (Chessboard): The chessboard instance.
            coords (tuple): Current (x, y) coordinates of the piece.

        Returns:
            list[tuple]: List of reachable destination coordinate tuples.
        """
        possible_moves = []
        for dir_x, dir_y in self.directions:
            x, y = coords
            while True:
                x += dir_x
                y += dir_y
                if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
                    break
                target = board.get_piece_at((x, y))
                if target is None or target.color != self.color:
                    possible_moves.append((x, y))
                if target is not None or not self.sliding:
                    break
        return possible_moves


class Pawn(Piece):
    """Represents a Pawn with single/double advance, captures, and en passant.

    Attributes:
        forward (int): Vertical step of the pawn (-1 for White, 1 for Black).
        start_row (int): Row where the pawn may still advance two squares.
        en_passant_row (int): Row of the target square when this pawn captures en passant.
    """

    value = 1
    piece_square_table = PAWN_TABLE
    symbols = ("♟", "♙")

    def __init__(self, color):
        """Initializes a Pawn and derives its direction from its color.

        Args:
            color (str): The color of the pawn ('W' or 'B').
        """
        super().__init__(color)
        is_white = self.color == "W"
        self.forward = -1 if is_white else 1
        self.start_row = 6 if is_white else 1
        self.en_passant_row = 2 if is_white else 5

    def get_possible_moves(self, board, coords):
        """Calculates pushes, captures, and en passant captures for the pawn.

        Args:
            board (Chessboard): The chessboard instance.
            coords (tuple): Current (x, y) coordinates of the pawn.

        Returns:
            list[tuple]: List of reachable destination coordinate tuples.
        """
        x, y = coords
        end_y = y + self.forward
        if not 0 <= end_y < BOARD_SIZE:
            return []

        possible_moves = []
        if board.get_piece_at((x, end_y)) is None:
            possible_moves.append((x, end_y))
            double_y = end_y + self.forward
            if y == self.start_row and board.get_piece_at((x, double_y)) is None:
                possible_moves.append((x, double_y))

        for end_x in (x - 1, x + 1):
            if not 0 <= end_x < BOARD_SIZE:
                continue
            target = board.get_piece_at((end_x, end_y))
            is_capture = target is not None and target.color != self.color
            is_en_passant = (end_x, end_y) == board.en_passant_target and end_y == self.en_passant_row
            if is_capture or is_en_passant:
                possible_moves.append((end_x, end_y))
        return possible_moves


class Knight(Piece):
    """Represents a Knight with L-shaped jumping movement."""

    value = 3
    directions = ((1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1))
    piece_square_table = KNIGHT_TABLE
    symbols = ("♞", "♘")


class Bishop(Piece):
    """Represents a Bishop with diagonal sliding movement."""

    value = 3
    directions = DIAGONAL
    sliding = True
    piece_square_table = BISHOP_TABLE
    symbols = ("♝", "♗")


class Rook(Piece):
    """Represents a Rook with orthogonal sliding movement and castling capability.

    Attributes:
        has_moved (bool): Whether the rook has moved from its original square.
    """

    value = 5
    directions = ORTHOGONAL
    sliding = True
    piece_square_table = ROOK_TABLE
    symbols = ("♜", "♖")

    def __init__(self, color, has_moved=False):
        """Initializes a Rook with its color and moved status.

        Args:
            color (str): The color of the rook ('W' or 'B').
            has_moved (bool, optional): Whether the rook has already moved. Defaults to False.
        """
        super().__init__(color)
        self.has_moved = has_moved


class Queen(Piece):
    """Represents a Queen with orthogonal and diagonal sliding movement."""

    value = 9
    directions = ORTHOGONAL + DIAGONAL
    sliding = True
    piece_square_table = QUEEN_TABLE
    symbols = ("♛", "♕")


class King(Piece):
    """Represents a King with 1-square movement in any direction and castling.

    Attributes:
        has_moved (bool): Whether the king has moved from its original square.
    """

    value = 900
    directions = ORTHOGONAL + DIAGONAL
    piece_square_table = KING_TABLE
    symbols = ("♚", "♔")

    def __init__(self, color, has_moved=False):
        """Initializes a King with its color and moved status.

        Args:
            color (str): The color of the king ('W' or 'B').
            has_moved (bool, optional): Whether the king has already moved. Defaults to False.
        """
        super().__init__(color)
        self.has_moved = has_moved

    def get_possible_moves(self, board, coords):
        """Calculates the king's 1-square moves plus castling.

        Whether the king is in check or crosses an attacked square is not verified
        here; that is the game's job, since it needs the whole position.

        Args:
            board (Chessboard): The chessboard instance.
            coords (tuple): Current (x, y) coordinates of the king.

        Returns:
            list[tuple]: List of reachable destination coordinate tuples.
        """
        possible_moves = super().get_possible_moves(board, coords)
        if self.has_moved:
            return possible_moves

        x, y = coords
        # (rook column, columns that must be empty, king destination column)
        castling_sides = ((7, (x + 1, x + 2), x + 2), (0, (x - 1, x - 2, x - 3), x - 2))
        for rook_x, between_xs, end_x in castling_sides:
            rook = board.get_piece_at((rook_x, y))
            if (isinstance(rook, Rook) and rook.color == self.color and not rook.has_moved
                    and all(board.get_piece_at((bx, y)) is None for bx in between_xs)):
                possible_moves.append((end_x, y))
        return possible_moves


PROMOTION_CLASSES = {"Q": Queen, "R": Rook, "B": Bishop, "N": Knight}
