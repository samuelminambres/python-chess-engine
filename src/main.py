import sys

import pygame

from ai import ChessAI
from game import SUCCESS, TIMEOUT, Game
from gui import Gui

FPS = 60
RESULT_DISPLAY_MS = 5000


class ChessApp:
    """Connects the game model, the AI opponent, and the Pygame interface.

    Attributes:
        gui (Gui): The graphical interface.
        game (Game): The current game.
        bot (ChessAI or None): The AI opponent, or None in 1vs1 mode.
        menu_active (bool): Whether the game mode menu is being shown.
        selected_square (tuple or None): Square of the piece picked by the player.
        pending_promotion (tuple or None): (start, end) of a promotion waiting for the
            player to choose a piece.
        running (bool): Whether the main loop keeps going.
    """

    def __init__(self):
        """Initializes the interface and shows the game mode menu."""
        self.gui = Gui()
        self.bot = None
        self.menu_active = True
        self.running = True
        self._new_game()

    def run(self):
        """Runs the main loop until the window is closed or the game ends."""
        clock = pygame.time.Clock()
        while self.running:
            self.gui.update_display(
                self.game, self.selected_square, self.pending_promotion is not None, self.menu_active
            )
            if not self.menu_active:
                self._update()
            for event in pygame.event.get():
                self._handle_event(event)
            clock.tick(FPS)
        pygame.quit()

    def _new_game(self):
        """Creates a fresh game in the standard position and clears the selection."""
        self.game = Game()
        self.game.setup_standard_board()
        self.selected_square = None
        self.pending_promotion = None

    def _update(self):
        """Checks the clock and lets the AI move when it is its turn."""
        if self.game.current_timer.is_timeout():
            self._finish(TIMEOUT)
        elif self.bot is not None and self.game.turn == self.bot.color:
            start, end = self.bot.get_best_move(self.game)
            self._play(start, end)

    def _play(self, start, end, promotion=None):
        """Plays a legal move and ends the game if it was the last one.

        Args:
            start (tuple): The starting (x, y) coordinates.
            end (tuple): The destination (x, y) coordinates.
            promotion (str, optional): Promotion piece key ('Q', 'R', 'B', 'N'). Defaults to None.
        """
        result = self.game.play_move(start, end, promotion)
        if result != SUCCESS:
            self._finish(result)

    def _finish(self, result):
        """Shows the game outcome for a few seconds and stops the main loop.

        Args:
            result (str): Game termination status ('CHECKMATE', 'TIMEOUT', etc.).
        """
        self.gui.show_result(self.game, result)
        pygame.time.wait(RESULT_DISPLAY_MS)
        self.running = False

    def _handle_event(self, event):
        """Dispatches a Pygame event.

        Args:
            event (pygame.event.Event): The event to handle.
        """
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEWHEEL:
            self.gui.handle_scroll(event.y)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        """Routes a mouse click to the dialog or area that is currently active.

        Args:
            pos (tuple[int, int]): Screen coordinates (x, y) of the click.
        """
        if self.menu_active:
            self._handle_menu_click(pos)
        elif self.pending_promotion is not None:
            self._handle_promotion_click(pos)
        elif not self.gui.is_in_board(pos):
            self._handle_sidebar_click(pos)
        else:
            self._handle_board_click(pos)

    def _handle_menu_click(self, pos):
        """Starts the game in the chosen mode.

        Args:
            pos (tuple[int, int]): Screen coordinates (x, y) of the click.
        """
        choice = self.gui.get_menu_selection(pos)
        if choice is None:
            return
        self.bot = ChessAI() if choice == "ai" else None
        self.menu_active = False
        self.game.start_clock()

    def _handle_promotion_click(self, pos):
        """Completes a pending promotion with the chosen piece.

        Args:
            pos (tuple[int, int]): Screen coordinates (x, y) of the click.
        """
        piece_key = self.gui.get_promotion_selection(pos)
        if piece_key is None:
            return
        start, end = self.pending_promotion
        self.pending_promotion = None
        self._play(start, end, piece_key)

    def _handle_sidebar_click(self, pos):
        """Handles the undo and restart buttons.

        Args:
            pos (tuple[int, int]): Screen coordinates (x, y) of the click.
        """
        button = self.gui.get_sidebar_button(pos)
        if button == "undo":
            # Against the AI, take back the player's move and the AI's reply.
            if not self.game.undo_turns(2 if self.bot else 1):
                print("Error: no moves to undo")
        elif button == "restart":
            self._new_game()
            self.game.start_clock()
        self.selected_square = None

    def _handle_board_click(self, pos):
        """Selects a piece, or tries to move the selected one to the clicked square.

        Args:
            pos (tuple[int, int]): Screen coordinates (x, y) of the click.
        """
        square = self.gui.translate_coords(*pos)
        piece = self.game.board.get_piece_at(square)
        own_piece_clicked = piece is not None and piece.color == self.game.turn

        if self.selected_square is None:
            if own_piece_clicked:
                self.selected_square = square
            return

        start, self.selected_square = self.selected_square, None
        if not self.game.is_legal_move(start, square):
            if own_piece_clicked:
                self.selected_square = square
        elif self.game.board.is_promotion(start, square):
            self.pending_promotion = (start, square)
        else:
            self._play(start, square)


if __name__ == "__main__":
    ChessApp().run()
    sys.exit()
