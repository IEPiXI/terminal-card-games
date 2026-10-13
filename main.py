from core.engine import GameEngine, GameSpec
from solitaire.game import SolitaireGame

GAMES: list[GameSpec] = [
    GameSpec('solitaire', 'Solitaire (Klondike)', SolitaireGame, shortcut='1'),
]


def main():
    """Launch the Terminal Card Games (TCG) engine."""
    GameEngine(games=GAMES).run()


if __name__ == '__main__':
    main()
