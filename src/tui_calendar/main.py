from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static

class TuiCalApp(App):
    """Минимальная заглушка приложения."""
    
    CSS = """
    Screen {
        align: center middle;
    }
    #hello {
        width: 40;
        height: 5;
        border: heavy white;
        content-align: center middle;
        background: $accent;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("📅 TUI Calendar MVP\nReady for development", id="hello")
        yield Footer()

def run():
    app = TuiCalApp()
    app.run()

if __name__ == "__main__":
    run()
