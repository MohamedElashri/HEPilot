"""Legacy entry point delegating to the new ArXiv collector CLI."""

from .run import main


if __name__ == "__main__":  # pragma: no cover
    main()
