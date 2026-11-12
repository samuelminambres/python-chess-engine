MATE_SCORE = 10_000


class ChessAI:
    """Chess engine opponent implementing minimax with alpha-beta pruning.

    The evaluation is positive when White is ahead, so White maximizes and Black
    minimizes. Whose turn it is comes from the game itself, not from the engine.

    Attributes:
        depth (int): Search depth limit for minimax evaluation.
        color (str): The piece color played by the AI ('W' or 'B').
    """

    def __init__(self, depth=3, color="B"):
        """Initializes the ChessAI engine.

        Args:
            depth (int, optional): Search depth for the minimax algorithm (1-5). Defaults to 3.
            color (str, optional): The color played by the AI ('W' or 'B'). Defaults to "B".
        """
        self.depth = depth
        self.color = color

    @property
    def depth(self):
        """Gets the search depth for minimax.

        Returns:
            int: The search depth.
        """
        return self._depth

    @depth.setter
    def depth(self, value):
        """Sets the search depth for minimax.

        Args:
            value (int): Search depth between 1 and 5.

        Raises:
            TypeError: If value is not an int.
            ValueError: If value is not between 1 and 5.
        """
        if not isinstance(value, int):
            raise TypeError("Depth must be int")
        if value < 1 or value > 5:
            raise ValueError("Depth must be between 1 and 5")
        self._depth = value

    @property
    def color(self):
        """Gets the color played by the AI.

        Returns:
            str: Color string ('W' or 'B').
        """
        return self._color

    @color.setter
    def color(self, value):
        """Sets the color played by the AI.

        Args:
            value (str): Color string ('W' or 'B').

        Raises:
            TypeError: If value is not a str.
            ValueError: If value is not 'W' or 'B'.
        """
        if not isinstance(value, str):
            raise TypeError("Color must be str")
        if value != "W" and value != "B":
            raise ValueError('Color must be "W" or "B"')
        self._color = value

    def get_best_move(self, game):
        """Finds the best move for the side to move using minimax with alpha-beta pruning.

        Args:
            game (Game): The current chess game instance. It is left unchanged.

        Returns:
            tuple or None: A tuple of (start, end) coordinates representing the best move,
                or None if no legal moves exist.
        """
        _, best_move = self.minimax(game, self.depth)
        return best_move

    def minimax(self, game, depth, alpha=float("-inf"), beta=float("inf")):
        """Evaluates the position recursively using minimax with alpha-beta pruning.

        Checkmate scores are adjusted by the remaining depth so that faster mates
        are preferred; stalemate scores 0.

        Args:
            game (Game): The current chess game instance.
            depth (int): Remaining depth to search.
            alpha (float, optional): Best score that the maximizer can guarantee. Defaults to -inf.
            beta (float, optional): Best score that the minimizer can guarantee. Defaults to inf.

        Returns:
            tuple[float, tuple or None]: The evaluated score and the best (start, end)
                move for the side to move (None at leaf and terminal positions).
        """
        if depth == 0:
            return self.evaluate(game.board), None

        is_maximizing = game.turn == "W"
        legal_moves = game.get_all_legal_moves()
        if not legal_moves:
            if not game.is_in_check():
                return 0, None
            mate_score = MATE_SCORE + depth
            return (-mate_score if is_maximizing else mate_score), None

        # Captures first: they tend to cause earlier cutoffs.
        legal_moves.sort(key=lambda move: game.board.get_piece_at(move[1]) is None)

        best_score = float("-inf") if is_maximizing else float("inf")
        best_move = None
        for start, end in legal_moves:
            game.make_move(start, end)
            score, _ = self.minimax(game, depth - 1, alpha, beta)
            game.undo_move()

            if (score > best_score) if is_maximizing else (score < best_score):
                best_score, best_move = score, (start, end)
                if is_maximizing:
                    alpha = max(alpha, score)
                else:
                    beta = min(beta, score)
            if beta <= alpha:
                break
        return best_score, best_move

    def evaluate(self, board):
        """Computes a static heuristic evaluation of the board state.

        Args:
            board (Chessboard): The chessboard instance to evaluate.

        Returns:
            float: The heuristic score where positive favors White and negative favors Black.
        """
        evaluation = 0
        for color, sign in (("W", 1), ("B", -1)):
            for x, y in board.pieces_coords(color):
                piece = board.get_piece_at((x, y))
                row = y if color == "W" else 7 - y  # tables are written from White's side
                evaluation += sign * (piece.value + piece.piece_square_table[row][x])
        return evaluation
