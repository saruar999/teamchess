import chess


class ChessGame:

    def __init__(self):
        board = chess.Board()
        board.set_fen('3rk2r/5p2/4p3/pN2Pnp1/R6p/7P/2P2PPB/4K1R1 b k - 0 28')
        board.push_san('d8d2')
        print(board.is_check())
        print(board.fen())
        # for move in board.legal_moves:
        #     print(move)


ChessGame()
