from tabulate import tabulate


def print_json(json: dict) -> str:
    return tabulate(json.items(), tablefmt="plain")
