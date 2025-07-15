from pathlib import Path
from sys import path


class GameStats:
    """跟踪游戏的统计信息"""

    def __init__(self, ai_game):
        """初始化统计信息"""
        self.settings = ai_game.settings
        self.reset_stats()

        # 在任何情况下都不应重置最高分
        path=Path('score.txt')
       
        if path.exists():
            print(path.read_text())
        else:
             path.write_text('0')
        
        self.high_score=int(path.read_text())

    def reset_stats(self):
        """初始化在游戏运行期间可能变化的统计信息"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

