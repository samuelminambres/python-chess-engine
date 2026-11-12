import os
from math import ceil

import pygame

from pieces import PROMOTION_CLASSES

BOARD_DIMENSION = 8
COLOR_LIGHT = (240, 217, 181)
COLOR_DARK = (181, 136, 99)
COLOR_SIDEBAR = (139, 90, 43)
COLOR_SCROLL_TRACK = (112, 72, 34)
COLOR_OVERLAY = (0, 0, 0, 80)
COLOR_HIGHLIGHT = (100, 200, 255, 90)
PIECE_NAMES = (
    "WPawn", "WRook", "WKnight", "WBishop", "WQueen", "WKing",
    "BPawn", "BRook", "BKnight", "BBishop", "BQueen", "BKing"
)
MENU_OPTIONS = (("ai", "vs AI", 42), ("1vs1", "1vs1", 48))
RESULT_TITLES = {
    "CHECKMATE": "CHECKMATE!",
    "TIMEOUT": "TIMEOUT!",
    "STALEMATE": "STALEMATE!",
    "DRAW": "DRAW!",
}
MIN_THUMB_HEIGHT = 24


class Gui:
    """Manages graphical rendering, Pygame windows, menus, and user interactions.

    Attributes:
        height (int): Window height in pixels.
        width (int): Window width in pixels.
        board_size (int): Pixel size of the square chessboard area.
        square_size (int): Pixel dimension of each chessboard square.
        panel_x (int): Horizontal starting offset for the sidebar panel.
        panel_width (int): Width of the sidebar panel in pixels.
        display (pygame.Surface): Main Pygame display surface.
        images (dict): Loaded and scaled piece texture images.
        scroll_y (int): Vertical scroll offset for move history.
        line_h (int): Height of each line of move history text.
    """

    def __init__(self, height: int = 800, width: int = 1200):
        """Initializes the graphical user interface and Pygame window.

        Args:
            height (int, optional): Window height in pixels. Defaults to 800.
            width (int, optional): Window width in pixels. Defaults to 1200.
        """
        pygame.init()
        self.height = height
        self.width = width

        self.board_size = self.height
        self.square_size = self.board_size // BOARD_DIMENSION
        self.panel_x = self.square_size * BOARD_DIMENSION
        self.panel_width = self.width - self.panel_x

        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Python chess engine")

        self.font_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", "fonts", "PressStart2P.ttf"
        )
        self._font_cache = {}

        self.images = {}
        self.load_images()

        self.scroll_y = 0
        self.line_h = 24

        self._init_layout()

    def _init_layout(self):
        """Computes every bounding rectangle once, shared by drawing and click detection."""
        # Sidebar buttons and move history
        btn_margin, btn_w, btn_h = 25, 150, 50
        btn_y = self.height - 75
        self.undo_btn_rect = pygame.Rect(self.panel_x + btn_margin, btn_y, btn_w, btn_h)
        self.restart_btn_rect = pygame.Rect(
            self.panel_x + self.panel_width - btn_margin - btn_w, btn_y, btn_w, btn_h
        )

        self.bar_w = 10
        self.bar_x = self.restart_btn_rect.right - self.bar_w
        history_x = self.undo_btn_rect.left
        history_width = (self.bar_x - 10) - history_x
        self.history_rect = pygame.Rect(history_x, 257, history_width, 435)
        self.scroll_track_rect = pygame.Rect(
            self.bar_x, self.history_rect.y, self.bar_w, self.history_rect.height
        )

        col_x = (history_x + 20 + 70, history_x + 180 + 70)  # (white, black)
        self.col_x = col_x
        self.col_local_x = tuple(x - self.history_rect.x for x in col_x)

        # Game mode menu
        self.menu_rect = self._centered_rect(600, 400)
        card_size = 240
        gap = (self.menu_rect.width - card_size * len(MENU_OPTIONS)) // (len(MENU_OPTIONS) + 1)
        card_y = self.menu_rect.y + 110
        self.menu_cards = {
            key: pygame.Rect(self.menu_rect.x + gap + i * (card_size + gap), card_y, card_size, card_size)
            for i, (key, _, _) in enumerate(MENU_OPTIONS)
        }

        # Promotion dialog
        self.promotion_rect = self._centered_rect(650, 200)
        card_size = 120
        gap = (self.promotion_rect.width - card_size * len(PROMOTION_CLASSES)) // (len(PROMOTION_CLASSES) + 1)
        card_y = self.promotion_rect.y + (self.promotion_rect.height - card_size) // 2
        self.promotion_cards = {
            code: pygame.Rect(self.promotion_rect.x + gap + i * (card_size + gap), card_y, card_size, card_size)
            for i, code in enumerate(PROMOTION_CLASSES)
        }

    def _centered_rect(self, width: int, height: int) -> pygame.Rect:
        """Creates a rectangle centered on the window.

        Args:
            width (int): Rectangle width in pixels.
            height (int): Rectangle height in pixels.

        Returns:
            pygame.Rect: The centered rectangle.
        """
        rect = pygame.Rect(0, 0, width, height)
        rect.center = (self.width // 2, self.height // 2)
        return rect

    def _get_font(self, size: int) -> pygame.font.Font:
        """Retrieves a cached Font instance for the given point size.

        Args:
            size (int): Font size in points.

        Returns:
            pygame.font.Font: Loaded or cached font instance.
        """
        if size not in self._font_cache:
            if os.path.exists(self.font_path):
                self._font_cache[size] = pygame.font.Font(self.font_path, size)
            else:
                self._font_cache[size] = pygame.font.SysFont("sans-serif", size)
        return self._font_cache[size]

    def _render_text(self, text: str, size: int, color, center=None, topleft=None, surface=None):
        """Renders text onto a target surface or the main display.

        Args:
            text (str): The text string to render.
            size (int): Font size in points.
            color (tuple): RGB color tuple for the font.
            center (tuple, optional): Center position (x, y). Defaults to None.
            topleft (tuple, optional): Top-left position (x, y). Defaults to None.
            surface (pygame.Surface, optional): Surface to render onto. Defaults to None.

        Returns:
            pygame.Rect: Bounding rectangle of the drawn text.
        """
        text_surf = self._get_font(size).render(text, True, color)
        if center:
            text_rect = text_surf.get_rect(center=center)
        else:
            text_rect = text_surf.get_rect(topleft=topleft or (0, 0))
        (surface or self.display).blit(text_surf, text_rect)
        return text_rect

    def _draw_dialog(self, rect: pygame.Rect):
        """Dims the whole window and draws a dialog background on top.

        Args:
            rect (pygame.Rect): Rectangle of the dialog.
        """
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(COLOR_OVERLAY)
        self.display.blit(overlay, (0, 0))
        pygame.draw.rect(self.display, COLOR_DARK, rect)

    def load_images(self):
        """Loads and scales piece image assets from the assets directory."""
        images_route = os.path.join(os.path.dirname(__file__), "..", "assets", "images")
        for piece in PIECE_NAMES:
            png_route = os.path.join(images_route, f"{piece}.png")
            if os.path.exists(png_route):
                image = pygame.image.load(png_route)
                self.images[piece] = pygame.transform.scale(
                    image, (self.square_size, self.square_size)
                )

    # ------------------------------------------------------------------ drawing

    def update_display(self, game, selected_square, show_promotion, show_menu):
        """Redraws the interface elements and flips the display buffer.

        Args:
            game (Game): The current game instance.
            selected_square (tuple or None): The currently selected square (x, y) or None.
            show_promotion (bool): True if the promotion dialog is active.
            show_menu (bool): True if the main menu is active.
        """
        if show_menu:
            self.draw_menu()
        else:
            self.draw_board()
            self.draw_information(game)
            self._draw_highlight(selected_square)
            self.draw_pieces(game.board)
            if show_promotion:
                self.draw_promotion_menu(game)
        pygame.display.flip()

    def draw_board(self):
        """Draws the alternating light and dark squares of the chessboard."""
        for y in range(BOARD_DIMENSION):
            for x in range(BOARD_DIMENSION):
                color = COLOR_LIGHT if (x + y) % 2 == 0 else COLOR_DARK
                square = (x * self.square_size, y * self.square_size, self.square_size, self.square_size)
                pygame.draw.rect(self.display, color, square)

    def _draw_highlight(self, square):
        """Highlights the selected square.

        Args:
            square (tuple or None): The (x, y) square to highlight, or None.
        """
        if square is None:
            return
        highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        highlight.fill(COLOR_HIGHLIGHT)
        self.display.blit(highlight, (square[0] * self.square_size, square[1] * self.square_size))

    def draw_pieces(self, board):
        """Draws all active chess pieces on their corresponding squares.

        Args:
            board (Chessboard): The chessboard containing the pieces to draw.
        """
        for y in range(BOARD_DIMENSION):
            for x in range(BOARD_DIMENSION):
                piece = board.get_piece_at((x, y))
                if piece is None:
                    continue
                texture = f"{piece.color}{type(piece).__name__}"
                if texture in self.images:
                    self.display.blit(self.images[texture], (x * self.square_size, y * self.square_size))

    def draw_information(self, game):
        """Renders the sidebar panel including the timer, move history, and buttons.

        Args:
            game (Game): The current game instance.
        """
        pygame.draw.rect(self.display, COLOR_SIDEBAR, (self.panel_x, 0, self.panel_width, self.height))
        self.draw_timer(game)

        panel_center_x = self.panel_x + self.panel_width // 2
        self._render_text("Game history:", 28, COLOR_LIGHT, center=(panel_center_x, 165))
        self._render_text("Whites", 22, COLOR_LIGHT, center=(self.col_x[0], 215))
        self._render_text("Blacks", 22, COLOR_LIGHT, center=(self.col_x[1], 215))
        self._draw_history(game)

        for rect, label in ((self.undo_btn_rect, "UNDO"), (self.restart_btn_rect, "RESTART")):
            pygame.draw.rect(self.display, COLOR_DARK, rect)
            self._render_text(label, 20, COLOR_LIGHT, center=rect.center)

    def draw_timer(self, game):
        """Renders the active turn player and countdown timer on the sidebar.

        Args:
            game (Game): The current game instance.
        """
        timer = game.current_timer
        timer.update()
        turn = "Whites'" if game.turn == "W" else "Blacks'"
        center_x = self.panel_x + self.panel_width // 2
        self._render_text(f"{turn} turn", 30, COLOR_LIGHT, center=(center_x, 60))
        self._render_text(str(timer), 28, COLOR_LIGHT, center=(center_x, 110))

    def _draw_history(self, game):
        """Renders the scrollable move history, two moves (White, Black) per row.

        Args:
            game (Game): The current game instance.
        """
        self._clamp_scroll(game)
        surface = pygame.Surface(self.history_rect.size, pygame.SRCALPHA)
        for i, line in enumerate(str(game).splitlines()):
            center_y = (i // 2) * self.line_h + self.scroll_y + self.line_h // 2
            self._render_text(
                line, 15, COLOR_LIGHT,
                center=(self.col_local_x[i % 2], center_y),
                surface=surface
            )
        self.display.blit(surface, self.history_rect.topleft)
        self._draw_scrollbar(game)

    def _content_height(self, game) -> int:
        """Calculates the total height of the move history content in pixels.

        Args:
            game (Game): The current game instance.

        Returns:
            int: The total height in pixels.
        """
        return ceil(len(game.history) / 2) * self.line_h

    def _clamp_scroll(self, game):
        """Restricts the vertical scroll position within the history boundaries.

        Args:
            game (Game): The current game instance.
        """
        max_scroll = min(0, self.history_rect.height - self._content_height(game))
        self.scroll_y = max(max_scroll, min(0, self.scroll_y))

    def _draw_scrollbar(self, game):
        """Renders the scrollbar track and thumb when the history overflows.

        Args:
            game (Game): The current game instance.
        """
        visible_h = self.history_rect.height
        total_h = self._content_height(game)
        if total_h <= visible_h:
            return

        pygame.draw.rect(self.display, COLOR_SCROLL_TRACK, self.scroll_track_rect)
        thumb_h = max(MIN_THUMB_HEIGHT, int(visible_h * visible_h / total_h))
        scroll_pct = -self.scroll_y / (total_h - visible_h)
        thumb_y = self.scroll_track_rect.y + int(scroll_pct * (visible_h - thumb_h))
        pygame.draw.rect(self.display, COLOR_LIGHT, pygame.Rect(self.bar_x, thumb_y, self.bar_w, thumb_h))

    def draw_menu(self):
        """Renders the game start menu for selecting the game mode."""
        self.display.fill(COLOR_DARK)
        self._draw_dialog(self.menu_rect)
        self._render_text(
            "Select game mode:", 28, COLOR_LIGHT,
            center=(self.menu_rect.centerx, self.menu_rect.y + 50)
        )
        for key, label, size in MENU_OPTIONS:
            card = self.menu_cards[key]
            pygame.draw.rect(self.display, COLOR_LIGHT, card)
            self._render_text(label, size, COLOR_DARK, center=card.center)

    def draw_promotion_menu(self, game):
        """Renders the pawn promotion dialog overlay with selectable pieces.

        Args:
            game (Game): The current game instance.
        """
        self._draw_dialog(self.promotion_rect)
        for code, piece_class in PROMOTION_CLASSES.items():
            card = self.promotion_cards[code]
            pygame.draw.rect(self.display, COLOR_LIGHT, card)
            texture = f"{game.turn}{piece_class.__name__}"
            if texture in self.images:
                self.display.blit(self.images[texture], self.images[texture].get_rect(center=card.center))

    def show_result(self, game, result):
        """Displays an overlay with the final match outcome dialog.

        Args:
            game (Game): The current game instance.
            result (str): Game termination status ('CHECKMATE', 'TIMEOUT', 'STALEMATE', 'DRAW').
        """
        dialog_rect = self._centered_rect(int(self.width * 0.65), int(self.height * 0.5))
        self._draw_dialog(dialog_rect)

        # For these results game.turn is the side that lost on board or on time.
        if result in ("CHECKMATE", "TIMEOUT"):
            subtitle = f"{'Blacks' if game.turn == 'W' else 'Whites'} win"
        else:
            subtitle = "Tie"

        center_x, center_y = dialog_rect.center
        self._render_text(RESULT_TITLES[result], 70, COLOR_LIGHT, center=(center_x, center_y - 50))
        self._render_text(subtitle, 50, COLOR_LIGHT, center=(center_x, center_y + 50))
        pygame.display.flip()

    # -------------------------------------------------------------- interaction

    def handle_scroll(self, y_offset: int, sens: int = 5):
        """Scrolls the move history view vertically.

        Args:
            y_offset (int): Mouse wheel scroll delta.
            sens (int, optional): Scroll sensitivity multiplier. Defaults to 5.
        """
        self.scroll_y += y_offset * sens

    @staticmethod
    def _find_clicked(rects: dict, pos: tuple[int, int]) -> str | None:
        """Finds which rectangle of a dictionary contains a position.

        Args:
            rects (dict): Mapping of identifier to pygame.Rect.
            pos (tuple[int, int]): Screen coordinates (x, y) of the click.

        Returns:
            str or None: The identifier of the clicked rectangle, or None.
        """
        for key, rect in rects.items():
            if rect.collidepoint(pos):
                return key
        return None

    def get_menu_selection(self, pos: tuple[int, int]) -> str | None:
        """Determines which game mode card was clicked in the start menu.

        Args:
            pos (tuple[int, int]): Screen coordinates (x, y) of the click.

        Returns:
            str or None: 'ai' for AI mode, '1vs1' for 2-player mode, or None.
        """
        return self._find_clicked(self.menu_cards, pos)

    def get_promotion_selection(self, pos: tuple[int, int]) -> str | None:
        """Determines which piece was selected from the promotion menu.

        Args:
            pos (tuple[int, int]): Screen coordinates (x, y) of the click.

        Returns:
            str or None: Piece abbreviation ('Q', 'R', 'B', 'N') or None if not clicked.
        """
        return self._find_clicked(self.promotion_cards, pos)

    def get_sidebar_button(self, pos: tuple[int, int]) -> str | None:
        """Checks if a sidebar action button was clicked.

        Args:
            pos (tuple[int, int]): Screen coordinates (x, y) of the click.

        Returns:
            str or None: 'undo' or 'restart' if a button was clicked, None otherwise.
        """
        return self._find_clicked({"undo": self.undo_btn_rect, "restart": self.restart_btn_rect}, pos)

    def is_in_board(self, pos: tuple[int, int]) -> bool:
        """Checks whether the given position lies inside the chessboard area.

        Args:
            pos (tuple[int, int]): Screen coordinates (x, y) of the position.

        Returns:
            bool: True if position is within chessboard bounds, False otherwise.
        """
        x, y = pos
        return 0 <= x < self.panel_x and 0 <= y < self.height

    def translate_coords(self, x_mouse, y_mouse):
        """Translates pixel mouse coordinates to board square grid coordinates.

        Args:
            x_mouse (int): Mouse x coordinate in pixels.
            y_mouse (int): Mouse y coordinate in pixels.

        Returns:
            tuple[int, int]: The (col, row) coordinates on the chessboard grid.
        """
        return x_mouse // self.square_size, y_mouse // self.square_size
