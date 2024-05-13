import chess


class ChessGame:

    def __init__(self):
        board = chess.Board()
        board.push_san('d4')
        board.push_san('e5')
        # move = chess.Move.from_uci('d4d5')
        for piece in board.pieces(chess.PAWN, chess.WHITE):
            print(chess.square_name(piece))
        # board.push_san('d4e5')
        # board.push_san('f8b4')
        # print(bool(board.is_check()))
        # for move in board.legal_moves:
        #     print(move)
        #     print(board.castling_rights)


print(ChessGame())
