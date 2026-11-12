BOARD_SIZE = 8
FILES = "ABCDEFGH"
OPPONENT = {"W": "B", "B": "W"}


def validate_coords(value, allow_none=False):
    """Validates that a value is a pair of board coordinates.

    Args:
        value (tuple or None): The (x, y) coordinates to validate.
        allow_none (bool, optional): Whether None is an accepted value. Defaults to False.

    Raises:
        TypeError: If value is not a tuple of two ints (or None when allowed).
        ValueError: If any coordinate is outside the 0-7 range.
    """
    if value is None and allow_none:
        return
    if not isinstance(value, tuple) or len(value) != 2 or not all(isinstance(c, int) for c in value):
        raise TypeError("Coords must be a tuple of two ints")
    if not all(0 <= c < BOARD_SIZE for c in value):
        raise ValueError("Coords must be between 0 and 7")


def to_coords(square):
    """Converts algebraic chess notation to grid coordinates.

    Args:
        square (str): The chess square algebraic notation (e.g., 'E4', 'A1').

    Returns:
        tuple[int, int]: The (x, y) board coordinates, 0-indexed from top-left.

    Raises:
        ValueError: If the notation length is not 2, the file letter is invalid,
            or the rank is not a number between 1 and 8.
    """
    square = square.upper().strip()
    if len(square) != 2:
        raise ValueError("Length not valid")
    file, rank = square
    if file not in FILES:
        raise ValueError("Letter not valid")
    if rank not in "12345678":
        raise ValueError("Number must be between 1 and 8")
    return FILES.index(file), BOARD_SIZE - int(rank)


def to_notation(coords):
    """Converts grid coordinates to algebraic chess notation.

    Args:
        coords (tuple[int, int]): The (x, y) board coordinates, 0-indexed.

    Returns:
        str: The algebraic notation corresponding to the coordinates (e.g., 'E4').

    Raises:
        TypeError: If coords is not a tuple of two ints.
        ValueError: If coordinates are not between 0 and 7.
    """
    validate_coords(coords)
    x, y = coords
    return FILES[x] + str(BOARD_SIZE - y)
