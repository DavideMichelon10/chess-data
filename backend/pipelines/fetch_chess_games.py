import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from commons.chesscom_data_collector import ChesscomDataCollector

if __name__ == "__main__":
    collector = ChesscomDataCollector()
    players = ["davideblunder"]
    collector.fetch_and_store_games(players)