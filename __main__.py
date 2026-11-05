"""Allow launching the clinic application with ``python3 .``."""

from main import main


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nClinic Management System closed.")
