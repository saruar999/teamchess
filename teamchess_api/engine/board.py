import dataclasses
import itertools
import random

import chess
from typing import List, Optional, Iterator
import chess.variant
from chess import Bitboard, BB_ALL, Move

# from player.models import Player

SPADE = '♠'
HEART = '♥'
CLUB = '♣'
DIAMOND = '♦'

WHITE_PAWNS = [chess.A2, chess.B2, chess.C2, chess.D2, chess.E2, chess.F2, chess.G2, chess.H2]
WHITE_PIECES = [chess.A1, chess.B1, chess.C1, chess.D1, chess.E1, chess.F1, chess.G1, chess.H1]

BLACK_PAWNS = [chess.A7, chess.B7, chess.C7, chess.D7, chess.E7, chess.F7, chess.G7, chess.H7]
BLACK_PIECES = [chess.A8, chess.B8, chess.C8, chess.D8, chess.E8, chess.F8, chess.G8, chess.H8]


@dataclasses.dataclass
class Player:
    """
    A Player node class that will act like a node that can be used for certain data structures such as linked lists.
    In this case it will be used inside a Circular Linked List structure which will be used to iterate over player
    turns.
    """
    symbol: str
    next_player: 'Player' = None


class TeamChessBoard(chess.Board):
    player_of_spades: Player
    player_of_hearts: Player
    player_of_diamonds: Player
    player_of_clubs: Player

    spades_squares: List[chess.Square]
    hearts_squares: List[chess.Square]
    diamonds_squares: List[chess.Square]
    clubs_squares: List[chess.Square]

    current_turn_player: Player

    white_team_players: List[Player]
    black_team_players: List[Player]

    def _set_players(self):
        """
        Initializes the player node objects with their respective symbols, as well as each color's player list.
        """
        self.player_of_spades = Player(SPADE)
        self.player_of_hearts = Player(HEART)
        self.player_of_diamonds = Player(DIAMOND)
        self.player_of_clubs = Player(CLUB)

        self.white_team_players = [self.player_of_spades, self.player_of_diamonds]
        self.black_team_players = [self.player_of_hearts, self.player_of_clubs]

    def _set_player_turns(self):
        """
        Initializes the turn circular linked list.
        The player turns will be as follows:
            spades -> hearts -> diamonds -> clubs -> spades -> ...
        """
        self.player_of_spades.next_player = self.player_of_hearts
        self.player_of_hearts.next_player = self.player_of_diamonds
        self.player_of_diamonds.next_player = self.player_of_clubs
        self.player_of_clubs.next_player = self.player_of_spades

    def _set_current_turn_player(self, symbol: str = None):
        """
        Sets the current turn player node, if no symbol is provided, it will set it to the player of spades node.
        """
        self.current_turn_player = self.player_of_spades
        if symbol is not None:
            self.current_turn_player = self._find_player_node_by_symbol(self.current_turn_player, symbol)

    @classmethod
    def _find_player_node_by_symbol(cls, player: Player, symbol: str) -> Player:
        """
        A recursive method that will iterate a linked list of player nodes and return the player node that matches the
        passed symbol.
        """
        if player.symbol == symbol:
            return player
        else:
            return cls._find_player_node_by_symbol(player.next_player, symbol)

    def _allocate_white(self):
        pawns = range(8)
        pieces = range(8, 16)

        self.spades_squares, self.diamonds_squares = self._shuffle_squares(pawns, pieces)

    def _allocate_black(self):
        pawns = range(56, 64)
        pieces = range(48, 56)

        self.hearts_squares, self.clubs_squares = self._shuffle_squares(pawns, pieces)

    @staticmethod
    def _shuffle_squares(pawns, pieces):
        player1_pawns = random.sample(pawns, k=4)
        player1_pieces = random.sample(pieces, k=4)

        player2_pawns = list(set(pawns).difference(player1_pawns))
        player2_pieces = list(set(pieces).difference(player1_pieces))

        return player1_pawns + player1_pieces, player2_pawns + player2_pieces

    def __init__(
        self: chess.BoardT,
        fen: Optional[str] = chess.STARTING_FEN,
        *,
        chess960: bool = False,
        current_turn_player_symbol: str = None
    ):
        super().__init__(fen, chess960=chess960)
        self._set_players()
        self._set_player_turns()
        self._set_current_turn_player(current_turn_player_symbol)
        if fen == chess.STARTING_FEN:
            self._allocate_white()
            self._allocate_black()
