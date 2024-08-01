import dataclasses
from chess import Piece
from typing import TypedDict


@dataclasses.dataclass
class Player:
    """
    A Player node class that will act like a node that can be used for certain data structures such as linked lists.
    In this case it will be used inside a Circular Linked List structure which will be used to iterate over player
    turns.
    """
    symbol: str
    next_player: 'Player' = None

    def __repr__(self):
        return self.symbol


class PlayerSquareValue(TypedDict):
    player: Player
    piece: Piece
