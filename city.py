import threading

from node import Order
from node_socket import UdpSocket
from util import get_logger

logger = get_logger("main")


class City:

    def __init__(self, my_port: int, number_general: int) -> None:
        self.number_general = number_general
        self.my_port = my_port
        self.node_socket = UdpSocket(my_port)
        self.logger = get_logger("city")

        self.logger.debug(f"city_port: {self.my_port}")
        self.logger.info(f"City is running...")
        self.logger.info(f"Number of loyal general: {number_general}")

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
        self.logger.info("Listen to incoming messages...")

        count_attack = 0
        count_retreat = 0

        for _ in range(self.number_general):
            input_value_byte, address = self.node_socket.listen()

            splitted_message = input_value_byte.split("~")
            sender = splitted_message[0].split("=")[0]
            order = splitted_message[1].split("=")[1]

            if order == "0":
                self.logger.info(f"{sender} RETREAT from us!")
                count_retreat += 1

            if order == "1":
                self.logger.info(f"{sender} ATTACK us!")
                count_attack += 1

        self.logger.info("Concluding what happen...")

        conclusion = ""
        if self.number_general <= 1:
            conclusion = "ERROR_LESS_THAN_TWO_GENERALS"

        elif count_attack == count_retreat:
            conclusion = "FAILED"

        elif count_attack > count_retreat:
            conclusion = "ATTACK"

        else:
            conclusion = "RETREAT"

        self.logger.info(f"GENERAL CONSENSUS: {conclusion}")

        return conclusion


def thread_exception_handler(args):
    logger.error(
        "Uncaught exception",
        exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
    )


def main(city_port: int, number_general: int):
    threading.excepthook = thread_exception_handler
    try:
        city = City(city_port, number_general)
        return city.start()

    except Exception:
        logger.exception("Caught Error")
        raise

    finally:
        city.close_connection()
