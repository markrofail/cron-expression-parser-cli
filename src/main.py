import typer

from .parser import parse_expression
from .utils import print_json

app = typer.Typer()


@app.command()
def parse(expression: str):
    try:
        result = parse_expression(expression)
        typer.echo(print_json(result))
    except ValueError as error:
        typer.secho(error, fg=typer.colors.RED)


if __name__ == "__main__":
    app()
