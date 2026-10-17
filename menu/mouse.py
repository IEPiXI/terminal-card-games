from prompt_toolkit.mouse_events import MouseButton, MouseEvent, MouseEventType


def handle_screen_click(screen, x: int, y: int) -> bool:
    """Map (x, y) click coordinates to menu items or footer hints."""
    lines = screen.render(color=False).split('\n')
    if not (0 <= y < len(lines)):
        return False
    line = lines[y]

    for idx, item in enumerate(screen.items):
        pattern = screen.format_item(item)
        start = line.find(pattern)
        if start != -1 and (start - 2 <= x < start + len(pattern)):
            screen.selected_idx = idx
            screen.on_select(item)
            return True

    for hint in screen.hints:
        pattern = f'[{hint.key}] {hint.label}'
        start = line.find(pattern)
        if start == -1 or not (start <= x < start + len(pattern)):
            continue

        key = hint.key.lower()
        if key == 'enter':
            screen.on_select(screen.get_selected_item())
            return True
        if key == 'esc':
            screen.cancel()
            return True
        if key == 'q':
            screen.quit()
            return True

        for idx, item in enumerate(screen.items):
            if item.key.lower() == key:
                screen.selected_idx = idx
                screen.on_select(item)
                return True

    return False


def handle_menu_mouse(screen, mouse_event: MouseEvent) -> bool:
    """Route terminal mouse events for a SelectableScreen."""
    if mouse_event.event_type == MouseEventType.MOUSE_UP and mouse_event.button == MouseButton.LEFT:
        return handle_screen_click(screen, mouse_event.position.x, mouse_event.position.y)
    return False
