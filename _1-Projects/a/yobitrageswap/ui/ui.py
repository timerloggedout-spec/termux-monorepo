from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Button, Static
from textual.containers import Vertical, Horizontal
from typing import List, Dict

class ArbitrageApp(App):
    CSS = """
    DataTable {
        width: 100%;
        height: 80%;
    }
    Button {
        width: 20%;
        margin: 1;
    }
    Static {
        width: 100%;
        height: 10%;
        content-align: center middle;
    }
    """

    def __init__(self, opportunities: List[Dict]):
        super().__init__()
        self.opportunities = opportunities

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Arbitrage Opportunities", id="title")
        yield DataTable()
        yield Horizontal(
            Button("Refresh", id="refresh", variant="primary"),
            Button("Execute", id="execute", variant="success"),
            Button("Exit", id="exit", variant="error")
        )
        yield Footer()

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("Exchange", "Path", "Profit (%)", "Amount In", "Amount Out", "Score")
        for opp in self.opportunities:
            table.add_row(
                opp['exchange'],
                opp['path'],
                opp['profit_percent'],
                f"{opp['amount_in']:.2f}",
                f"{opp['amount_out']:.2f}",
                f"{opp['score']:.2f}"
            )

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "exit":
            await self.exit()
        elif event.button.id == "refresh":
            table = self.query_one(DataTable)
            table.clear()
            for opp in self.opportunities:
                table.add_row(
                    opp['exchange'],
                    opp['path'],
                    opp['profit_percent'],
                    f"{opp['amount_in']:.2f}",
                    f"{opp['amount_out']:.2f}",
                    f"{opp['score']:.2f}"
                )
        elif event.button.id == "execute":
            self.notify("Execute button pressed (not implemented)", severity="warning")

    async def run_async(self):
        await self.run()
