import unittest

from ai import ChessAI
from game import CHECKMATE, SUCCESS, Game
from pieces import PROMOTION_CLASSES, Bishop, King, Knight, Pawn, Queen, Rook
from utils import to_coords

PIECE_CLASSES = {"p": Pawn, "n": Knight, "b": Bishop, "r": Rook, "q": Queen, "k": King}
ROOK_RIGHTS = {(7, 7): "K", (0, 7): "Q", (7, 0): "k", (0, 0): "q"}


def game_from_fen(fen):
    """Builds a Game from a FEN string (piece placement, turn, castling, en passant).

    Args:
        fen (str): The FEN string.

    Returns:
        Game: A game set up in the given position.
    """
    placement, turn, castling, en_passant = fen.split()[:4]
    game = Game()
    game.turn = "W" if turn == "w" else "B"
    for y, row in enumerate(placement.split("/")):
        x = 0
        for char in row:
            if char.isdigit():
                x += int(char)
                continue
            piece = PIECE_CLASSES[char.lower()]("W" if char.isupper() else "B")
            if isinstance(piece, King):
                piece.has_moved = not any(r in castling for r in ("KQ" if piece.color == "W" else "kq"))
            elif isinstance(piece, Rook):
                piece.has_moved = ROOK_RIGHTS.get((x, y), "-") not in castling
            game.board.add_piece(piece, (x, y))
            x += 1
    if en_passant != "-":
        game.board.en_passant_target = to_coords(en_passant)
    return game


def perft(game, depth):
    """Counts the leaf nodes of the legal move tree, expanding every promotion choice.

    Args:
        game (Game): The game to explore. It is left unchanged.
        depth (int): Number of half-moves to explore.

    Returns:
        int: The number of leaf positions.
    """
    nodes = 0
    for start, end in game.get_all_legal_moves():
        choices = tuple(PROMOTION_CLASSES) if game.board.is_promotion(start, end) else (None,)
        if depth == 1:
            nodes += len(choices)
            continue
        for choice in choices:
            game.make_move(start, end, choice)
            nodes += perft(game, depth - 1)
            game.undo_move()
    return nodes


class TestRules(unittest.TestCase):
    """Validates move generation against well-known perft node counts."""

    def test_start_position(self):
        game = Game()
        game.setup_standard_board()
        self.assertEqual([perft(game, d) for d in (1, 2, 3)], [20, 400, 8902])

    def test_kiwipete_castling_and_en_passant(self):
        game = game_from_fen("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -")
        self.assertEqual([perft(game, d) for d in (1, 2, 3)], [48, 2039, 97862])

    def test_en_passant_pins(self):
        game = game_from_fen("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - -")
        self.assertEqual([perft(game, d) for d in (1, 2, 3)], [14, 191, 2812])

    def test_promotions_and_castling_rights(self):
        game = game_from_fen("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq -")
        self.assertEqual([perft(game, d) for d in (1, 2, 3)], [6, 264, 9467])


class TestMakeUndo(unittest.TestCase):
    """Validates that undoing moves restores the whole game state."""

    def test_state_is_restored_after_exploring_the_tree(self):
        game = game_from_fen("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -")
        key = game.get_position_key()
        perft(game, 2)
        self.assertEqual(game.get_position_key(), key)
        self.assertEqual(game.history, [])
        self.assertEqual(game.half_move_clock, 0)

    def test_castling_rights_survive_legal_move_generation(self):
        game = Game()
        game.setup_standard_board()
        for start, end in (("e2", "e4"), ("e7", "e5"), ("g1", "f3"), ("b8", "c6"), ("f1", "c4"), ("f8", "c5")):
            self.assertEqual(game.play_move(to_coords(start), to_coords(end)), SUCCESS)
        self.assertIn((to_coords("e1"), to_coords("g1")), game.get_all_legal_moves())

    def test_undo_promotion(self):
        game = game_from_fen("8/P6k/8/8/8/8/8/K7 w - -")
        game.make_move(to_coords("a7"), to_coords("a8"), "N")
        self.assertIsInstance(game.board.get_piece_at(to_coords("a8")), Knight)
        game.undo_move()
        self.assertIsInstance(game.board.get_piece_at(to_coords("a7")), Pawn)
        self.assertIsNone(game.board.get_piece_at(to_coords("a8")))


class TestGameFlow(unittest.TestCase):
    """Validates game status detection and the AI."""

    def test_scholars_mate_is_detected_on_the_mating_move(self):
        game = Game()
        game.setup_standard_board()
        moves = (("e2", "e4"), ("e7", "e5"), ("d1", "h5"), ("b8", "c6"), ("f1", "c4"), ("g8", "f6"))
        for start, end in moves:
            self.assertEqual(game.play_move(to_coords(start), to_coords(end)), SUCCESS)
        self.assertEqual(game.play_move(to_coords("h5"), to_coords("f7")), CHECKMATE)

    def test_ai_finds_mate_in_one(self):
        game = game_from_fen("6k1/5ppp/8/8/8/8/5PPP/R5K1 w - -")
        ai = ChessAI(depth=2, color="W")
        self.assertEqual(ai.get_best_move(game), (to_coords("a1"), to_coords("a8")))

    def test_ai_leaves_the_game_unchanged(self):
        game = Game()
        game.setup_standard_board()
        key = game.get_position_key()
        ChessAI(depth=2, color="W").get_best_move(game)
        self.assertEqual(game.get_position_key(), key)
        self.assertEqual(game.history, [])


if __name__ == "__main__":
    unittest.main()
