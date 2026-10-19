from core.engine import GameEngine, GameSpec
from scoundrel.game import ScoundrelGame
from solitaire.game import SolitaireGame

GAMES: list[GameSpec] = [
    GameSpec('solitaire', 'Solitaire (Klondike)', SolitaireGame, shortcut='1'),
    GameSpec('scoundrel', 'Scoundrel', ScoundrelGame, shortcut='2'),
]


def main():
    """Launch the Terminal Card Games (TCG) engine."""
    GameEngine(games=GAMES).run()


if __name__ == '__main__':
    main()
