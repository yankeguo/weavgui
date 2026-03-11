import argparse
from importlib.metadata import PackageNotFoundError, version


def app_version() -> str:
    try:
        return version("weavgui")
    except PackageNotFoundError:
        return "0.0.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="weavgui",
        description="Orchestrate and automate graphical desktop workflows.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {app_version()}",
    )
    return parser


def main() -> int:
    parser = build_parser()
    parser.parse_args()
    print("weavgui is installed and ready.")
    return 0
