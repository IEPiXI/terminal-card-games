from menu.base import ScreenItem, SelectableScreen

TCG_BANNER: str = """\
     ┌─────────┐                                           ┌─────────┐
     │ A ♠     │       ████████╗  ██████╗   ██████╗        │ Q ♦     │
     │         │       ╚══██╔══╝ ██╔════╝  ██╔════╝        │         │
     │   ┌─────┴───┐      ██║    ██║       ██║  ███╗   ┌───┴─────┐   │
     │   │ K ♥     │      ██║    ██║       ██║   ██║   │ J ♣     │   │
     │   │         │      ██║    ╚██████╗  ╚██████╔╝   │         │ ♦ │
     └───┤    ♥    │      ╚═╝     ╚═════╝   ╚═════╝    │    ♣    ├───┘
         │         │        TERMINAL CARD GAMES        │         │
         │     K ♥ │                                   │     J ♣ │
         └─────────┘           ♠   ♥   ♦   ♣           └─────────┘"""


class TCGMenu(SelectableScreen):
    """Main menu screen displaying the TCG logo and game selection."""

    banner: str = TCG_BANNER
    title: str = 'G A M E S'
    hints: tuple[ScreenItem, ...] = (
        ScreenItem('Enter', 'Play'),
        ScreenItem('q', 'Quit'),
    )

    def get_selected_game(self) -> str:
        """Return identifier of currently selected game."""
        return self.get_selected_item().value
