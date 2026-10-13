from menu.base import ScreenItem, SelectableScreen

WIN_BANNER: str = """\
     ┌─────────┐                                           ┌─────────┐
     │ A ♠     │        ██╗   ██╗ ██████╗ ██╗   ██╗        │ Q ♦     │
     │         │        ╚██╗ ██╔╝██╔═══██╗██║   ██║        │         │
     │   ┌─────┴───┐     ╚████╔╝ ██║   ██║██║   ██║    ┌───┴─────┐   │
     │   │ K ♥     │      ╚██╔╝  ██║   ██║██║   ██║    │ J ♣     │   │
     │   │         │       ██║   ╚██████╔╝╚██████╔╝    │         │ ♦ │
     └───┤    ♥    │       ╚═╝    ╚═════╝  ╚═════╝     │    ♣    ├───┘
         │         │                                   │         │
         │     K ♥ │     ██╗    ██╗██╗███╗   ██╗██╗    │     J ♣ │
         └─────────┘     ██║    ██║██║████╗  ██║██║    └─────────┘
                         ██║ █╗ ██║██║██╔██╗ ██║██║
                         ██║███╗██║██║██║╚██╗██║╚═╝
                         ╚███╔███╔╝██║██║ ╚████║██╗
                          ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═╝"""


class WinScreen(SelectableScreen):
    """Victory screen displayed when a game is completed."""

    banner: str = WIN_BANNER
    title: str = '♠   ♥   Congratulations!   ♦   ♣\nYou completed the game!'
    items: tuple[ScreenItem, ...] = (
        ScreenItem('r', 'Play Again', value='restart'),
        ScreenItem('m', 'Main Menu', value='menu'),
    )
    hints: tuple[ScreenItem, ...] = (
        ScreenItem('Enter', 'Select'),
        ScreenItem('q', 'Quit'),
    )
