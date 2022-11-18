if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    from .gtk4_ui import main

    main()
