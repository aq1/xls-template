from rich import print


def log(msg: str):
    print(msg)


def error(msg: str):
    log(f"[red]{msg}[/red]")
