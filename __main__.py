import sys
from pathlib import Path

sys.path.append(Path(__file__).parent.absolute())


def main():
    import bot

    bot.main()


if __name__ == "__main__":
    main()
