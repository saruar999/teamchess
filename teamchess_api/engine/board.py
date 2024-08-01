import random
import chess
from typing import List, Dict, Optional
from .constants import *
from .definitions import Player, PlayerSquareValue


class TeamChessBoard(chess.Board):
    player_of_spades: Player
    player_of_hearts: Player
    player_of_diamonds: Player
    player_of_clubs: Player

    player_squares: Dict[chess.Square, PlayerSquareValue]

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

    def _allocate_white_squares(self):
        """
        Responsible for defining the pawn range and other pieces range for white.
        """
        pawns = range(8)
        pieces = range(8, 16)

        self._allocate_squares(pawns, pieces, *self.white_team_players)

    def _allocate_black_squares(self):
        """
        Responsible for defining the pawn range and other pieces range for black.
        """
        pawns = range(56, 64)
        pieces = range(48, 56)

        self._allocate_squares(pawns, pieces, *self.black_team_players)

    def _allocate_squares(self, pawns, pieces, player1, player2):
        """
        Takes pawns integer range of squares and randomly splits it into two groups, does the same for pieces range.
        Each player will receive half of the pawns and half of the pieces, in a normal chess game that adds up to
        8 pieces per player, that they will be randomly assigned.

        Once assignment is done, iterates over squares and populates the player_squares dictionary, with the following
        structure:
            ```
                {
                    square(int): {
                        'player': Player instance
                        'piece': chess.Piece instance
                    }
                }
            ```
        """
        player1_pawns = random.sample(pawns, k=int(len(pawns) / 2))
        player1_pieces = random.sample(pieces, k=int(len(pieces) / 2))

        player2_pawns = list(set(pawns).difference(player1_pawns))
        player2_pieces = list(set(pieces).difference(player1_pieces))

        for player1_square, player2_square in zip(player1_pawns + player1_pieces, player2_pawns+ player2_pieces):
            self.player_squares.update(
                {
                    player1_square: PlayerSquareValue(
                        player=player1,
                        piece=self.piece_at(player1_square)
                    ),
                    player2_square: PlayerSquareValue(
                        player=player2,
                        piece=self.piece_at(player2_square)
                    )
                }
            )

    def board_fen(self, *, promoted: Optional[bool] = False) -> str:
        """
        Gets the board custom FEN with player symbol suffixes for each piece
        (e.g.,
        ``r♥n♣b♥q♥k♣b♣n♣r♥/p♥p♣p♣p♥p♥p♥p♣p♣/8/8/8/8/P♠P♦P♦P♦P♠P♦P♠P♠/R♦N♠B♠Q♦K♦B♠N♦R♠``
        ).
        """
        builder = []
        empty = 0

        for square in chess.SQUARES_180:
            piece = self.piece_at(square)

            if not piece:
                empty += 1
            else:
                if empty:
                    builder.append(str(empty))
                    empty = 0
                builder.append(piece.symbol())
                if promoted and chess.BB_SQUARES[square] & self.promoted:
                    builder.append("~")

                # Check which player this piece belongs to, and add their symbol to the builder string
                builder.append(self.player_squares[square]['player'].symbol)

            if chess.BB_SQUARES[square] & chess.BB_FILE_H:
                if empty:
                    builder.append(str(empty))
                    empty = 0

                if square != chess.H1:
                    builder.append("/")

        return "".join(builder)

    def __init__(
        self,
        *,
        fen: str = None,
        chess960: bool = False,
        current_turn_player_symbol: str = None
    ):
        super().__init__(chess.STARTING_FEN, chess960=chess960)
        self.player_squares = {}
        self._set_players()
        self._set_player_turns()
        self._set_current_turn_player(current_turn_player_symbol)

        if fen is None:
            # Start a new game
            self._allocate_white_squares()
            self._allocate_black_squares()

        print(self.board_fen())
