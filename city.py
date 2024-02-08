import threading

from node import Order
from node_socket import UdpSocket
from util import get_logger

logger = get_logger('main')

class City:

    def __init__(self, my_port: int, number_general: int) -> None:
        self.number_general = number_general
        self.my_port = my_port
        self.node_socket = UdpSocket(my_port)
        self.logger = get_logger('city')

        self.logger.debug(f'city_port: {self.my_port}')
        self.logger.info(f'City is running...')
        self.logger.info(f'Number of loyal general: {number_general}')

    def close_connection(self):
        self.node_socket.close()

    def start(self):
        """
        TODO
        - Listens for actions/orders.
        - Concludes the actions as a consensus.
        - A heterogeneous actions is considered as a failed consensus.

        :return: the conclusion
        """
        return ''


def thread_exception_handler(args):
    logger.error('Uncaught exception', exc_info=(args.exc_type,
                                                 args.exc_value,
                                                 args.exc_traceback))

def main(city_port: int, number_general: int):
    threading.excepthook = thread_exception_handler
    try:
        city = City(city_port, number_general)
        return city.start()

    except Exception:
        logger.exception('Caught Error')
        raise

    finally:
        city.close_connection()
