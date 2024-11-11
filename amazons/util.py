import logging


def configure_loggers():
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.ERROR)

    engineio_logger = logging.getLogger('engineio.server')
    engineio_logger.setLevel(logging.ERROR)

    # Configure Logger
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    return logger