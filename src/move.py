from dataclasses import dataclass

from pieces import Piece


@dataclass
class Move:
    """Records an executed chess move with everything needed to undo it.

    The "previous_*" fields must be captured BEFORE the move is applied.

    Attributes:
        start (tuple): Starting coordinates (x, y).
        end (tuple): Destination coordinates (x, y).
        piece (Piece): The piece that performed the move.
        captured (Piece or None): The captured piece, if any.
        captured_coords (tuple or None): Square the captured piece stood on. It only
            differs from end for en passant captures.
        rook_move (tuple or None): ((x, y), (x, y)) rook start and end squares when
            the move is a castling.
        promoted (Piece or None): The piece the pawn was promoted to, if any.
        previous_en_passant (tuple or None): En passant target square prior to the move.
        previous_has_moved (bool or None): Moved status of the piece prior to the move.
        previous_half_move_clock (int): Half-move clock value prior to the move.
        position_key (tuple or None): Position signature after the move, used to
            detect threefold repetition. Only set for moves actually played.
    """

    start: tuple
    end: tuple
    piece: Piece
    captured: Piece | None = None
    captured_coords: tuple | None = None
    rook_move: tuple | None = None
    promoted: Piece | None = None
    previous_en_passant: tuple | None = None
    previous_has_moved: bool | None = None
    previous_half_move_clock: int = 0
    position_key: tuple | None = None
