import pprint
import random
import threading
from pprint import pformat

from node_socket import UdpSocket
from util import get_logger

logger = get_logger('main')

class Order:
    RETREAT = 0
    ATTACK = 1

class General:

    def __init__(self, my_id: int, is_traitor: bool, my_port: int,
                 ports: list, node_socket: UdpSocket, city_port: int,
                 order=None, log_name=None):
        self.my_id = my_id
        self.ports = ports
        self.city_port = city_port
        self.node_socket = node_socket
        self.my_port = my_port
        self.is_traitor = is_traitor
        self.orders = []
        self.order = order

        if log_name is None:
            log_name = f'general{my_id}'
        self.logger = get_logger(log_name)

        self.general_port_dictionary = {}
        for i in range(0, 4):
            self.general_port_dictionary[i] = ports[i]
        self.logger.debug('self.general_port_dictionary: '
                          f'{pformat(self.general_port_dictionary)}')

        self.port_general_dictionary = {}
        for key, value in self.general_port_dictionary.items():
            self.port_general_dictionary[value] = key
        self.logger.debug(f'self.port_general_dictionary: '
                          f'{pprint.pformat(self.port_general_dictionary)}')

        if self.my_id > 0:
            self.logger.info(f'General {self.my_id} is running...')
        else:
            self.logger.info('Supreme general is running...')
        self.logger.debug(f'is_traitor: {self.is_traitor}')
        self.logger.debug(f'ports: {pformat(self.ports)}')
        self.logger.debug(f'my_port: {self.my_port}')
        self.logger.debug(f'is_supreme_general: {self.my_id==0}')
        if self.order:
            self.logger.debug(f'order: {self.order}')
        self.logger.debug(f'city_port: {self.city_port}')

    def close_connection(self):
        self.node_socket.close()

    def start(self):
        """
        TODO
        - Listen to all generals and distribute message to all your neighbor.

        :return: None
        """
        return

    def listen_procedure(self):
        """
        TODO
        - Receives a message

        :return: list of splitted message
        """
        return list()

    def get_random_order(self):
        return random.choice([Order.ATTACK, Order.RETREAT])

    def sending_procedure(self, sender, order):
        """
        TODO
        - Sends message (order) to all your neighbor.
        - Hmm what's the sender for?

        :param sender: sender id
        :param order: order
        :return: list of sent messages
        """
        return "" or None

    def _most_common(self, lst):
        return max(set(lst), key=lst.count)

    def conclude_action(self, orders):
        """
        TODO
        - Makes a conclusion based on received orders.
        - Sends the conclusion to the city as a form of consensus.

        :param orders: list
        :return: a conclusion
        """
        return "" or None


class SupremeGeneral(General):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, log_name='supreme_general', **kwargs)

    def start(self):
        """
        TODO
        - Do i need to listen to other generals?

        :return: None
        """
        return None

    def sending_procedure(self, sender, order):
        """
        TODO
        - Sends order for every generals.

        :param sender: sender id
        :param order: order
        :return: list of sent orders
        """
        return []

    def conclude_action(self, orders):
        """
        TODO
        - This means the logic to make a conclusion
        for supreme general is different.
        - Sends the conclusion to the city as a form of consensus.

        :param orders: list
        :return: str or None
        """
        return "" or None


def thread_exception_handler(args):
    logger.error('Uncaught exception', exc_info=(args.exc_type,
                                                 args.exc_value,
                                                 args.exc_traceback))

def main(is_traitor: bool, node_id: int, ports: list,
         my_port: int = 0, order: Order = Order.RETREAT,
         city_port: int = 0):
    threading.excepthook = thread_exception_handler
    try:
        if node_id == 0:
            obj = SupremeGeneral(my_id=node_id,
                                 city_port=city_port,
                                 is_traitor=is_traitor,
                                 node_socket=UdpSocket(my_port),
                                 my_port=my_port,
                                 ports=ports, order=order)
        else:
            obj = General(my_id=node_id,
                          city_port=city_port,
                          is_traitor=is_traitor,
                          node_socket=UdpSocket(my_port),
                          my_port=my_port,
                          ports=ports)
        obj.start()
    except Exception:
        logger.exception('Caught Error')
        raise

    finally:
        obj.close_connection()
