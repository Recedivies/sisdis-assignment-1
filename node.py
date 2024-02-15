import pprint
import random
import threading
from pprint import pformat

from node_socket import UdpSocket
from util import get_logger

logger = get_logger("main")


class Order:
    RETREAT = 0
    ATTACK = 1


class General:

    def __init__(
        self,
        my_id: int,
        is_traitor: bool,
        my_port: int,
        ports: list,
        node_socket: UdpSocket,
        city_port: int,
        order=None,
        log_name=None,
    ):
        self.my_id = my_id
        self.ports = ports
        self.city_port = city_port
        self.node_socket = node_socket
        self.my_port = my_port
        self.is_traitor = is_traitor
        self.orders = []
        self.order = order

        if log_name is None:
            log_name = f"general{my_id}"
        self.logger = get_logger(log_name)

        self.general_port_dictionary = {}
        for i in range(0, 4):
            self.general_port_dictionary[i] = ports[i]
        self.logger.debug(
            "self.general_port_dictionary: " f"{pformat(self.general_port_dictionary)}"
        )

        self.port_general_dictionary = {}
        for key, value in self.general_port_dictionary.items():
            self.port_general_dictionary[value] = key
        self.logger.debug(
            f"self.port_general_dictionary: "
            f"{pprint.pformat(self.port_general_dictionary)}"
        )

        if self.my_id > 0:
            self.logger.info(f"General {self.my_id} is running...")
        else:
            self.logger.info("Supreme general is running...")
        self.logger.debug(f"is_traitor: {self.is_traitor}")
        self.logger.debug(f"ports: {pformat(self.ports)}")
        self.logger.debug(f"my_port: {self.my_port}")
        self.logger.debug(f"is_supreme_general: {self.my_id==0}")
        if self.order:
            self.logger.debug(f"order: {self.order}")
        self.logger.debug(f"city_port: {self.city_port}")

    def close_connection(self):
        self.node_socket.close()

    def start(self):
        """
        TODO
        - Listen to all generals and distribute message to all your neighbor.

        :return: None
        """
        self.logger.info(f"General {self.my_id} is starting...")

        self.logger.info("Start listening for incoming messages...")

        # Listen from Supreme General
        splitted_message = self.listen_procedure()
        order = splitted_message[1].split("=")[1]

        if self.is_traitor:
            self.order = self.get_random_order()
        else:
            self.order = order

        self.logger.info(
            "Send supreme general order to other generals with threading..."
        )

        # Listen from other nodes
        process_listen_threads = []
        for _ in range(2):
            process_listen = threading.Thread(target=self.listen_procedure)
            process_listen.start()
            process_listen_threads.append(process_listen)

        # Sending to all neighbours (e.g. 1 to 2-3, 2 to 1-3)
        process_send = threading.Thread(
            target=self.sending_procedure,
            args=(
                f"supreme_general",
                self.order,
            ),
        )
        process_send.start()

        process_send.join()
        for thread in process_listen_threads:
            thread.join()

        for sender_id in range(1, 4):
            if sender_id == self.my_id:
                continue

            process_send_general = threading.Thread(
                target=self.sending_procedure,
                args=(
                    f"general_{sender_id}",
                    self.order,
                ),
            )
            process_send_general.start()

        self.conclude_action(self.orders)

        return None

    def listen_procedure(self):
        """
        TODO
        - Receives a message

        :return: list of splitted message
        """
        input_value_byte, address = self.node_socket.listen()

        splitted_message = input_value_byte.split("~")
        sender = splitted_message[0].split("=")[0]
        order = splitted_message[1].split("=")[1]

        self.logger.info(f"Got incoming message from {sender}: {splitted_message}")
        self.orders.append(int(order))

        self.logger.info(f"Append message to a list: {self.orders}")

        return splitted_message

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
        result = []

        if self.is_traitor:
            send_order = self.get_random_order()
        else:
            send_order = order
        message = f"general_{self.my_id}~order={send_order}"

        if sender == "supreme_general":
            for receiver_id in range(1, 4):
                if receiver_id == self.my_id:
                    continue

                self.logger.info(f"message: {message}")

                self.logger.info("Initiate threading to send the message...")
                self.logger.info("Start threading...")

                receiver_port = self.general_port_dictionary.get(receiver_id)

                self.node_socket.send(
                    message,
                    receiver_port,
                )

                self.logger.info(f"Done sending message to general {receiver_id}...")

                result.append(message)

        return result or None

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
        result = ""

        self.logger.info("Concluding action...")

        if self.is_traitor:
            self.logger.info("I am a traitor...")
        else:
            conclude = 0 if len(orders) == 0 else self._most_common(orders)
            if conclude == 0:
                self.logger.info("action: RETREAT")

            if conclude == 1:
                self.logger.info("action: ATTACK")

            message = f"general_{self.my_id}~action={self.order}"

            self.node_socket.send(
                message,
                self.city_port,
            )

            self.logger.info("Done doing my action...")

            result = f"general_{self.my_id}~action={conclude}"

        return result or None


class SupremeGeneral(General):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, log_name="supreme_general", **kwargs)

    def start(self):
        """
        TODO
        - Do i need to listen to other generals?

        :return: None
        """

        self.logger.info("Supreme general is starting...")

        self.logger.info("Wait until all generals are running...")

        import time

        time.sleep(1)

        self.orders = self.sending_procedure("supreme_general", self.order)

        self.logger.info(f"Finish sending message to other generals...")

        self.conclude_action(self.orders)

        return None

    def sending_procedure(self, sender, order):
        """
        TODO
        - Sends order for every generals.

        :param sender: sender id
        :param order: order
        :return: list of sent orders
        """
        result = []

        if sender == "supreme_general":
            for receiver_id in range(1, 4):
                if self.is_traitor:
                    send_order = self.get_random_order()
                else:
                    send_order = order

                receiver_port = self.general_port_dictionary.get(receiver_id)
                self.logger.info(
                    f"Send message to general {receiver_id} with port {receiver_port}"
                )

                message = f"{sender}~order={send_order}"

                self.node_socket.send(
                    message,
                    receiver_port,
                )

                result.append(send_order)

        return result or None

    def conclude_action(self, orders):
        """
        TODO
        - This means the logic to make a conclusion
        for supreme general is different.
        - Sends the conclusion to the city as a form of consensus.

        :param orders: list
        :return: str or None
        """
        result = ""

        self.logger.info("Concluding action...")

        if self.is_traitor:
            self.logger.info("I am a traitor...")
        else:
            conclude = 0 if len(orders) == 0 else self._most_common(orders)
            if conclude == 0:
                self.logger.info("RETREAT from the city...")

            if conclude == 1:
                self.logger.info("ATTACK to the city...")

            self.logger.info("Send information to city...")

            message = f"supreme_general~action={self.order}"

            self.node_socket.send(
                message,
                self.city_port,
            )

            self.logger.info("Done sending information...")

            result = message

        return result or None


def thread_exception_handler(args):
    logger.error(
        "Uncaught exception",
        exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
    )


def main(
    is_traitor: bool,
    node_id: int,
    ports: list,
    my_port: int = 0,
    order: Order = Order.RETREAT,
    city_port: int = 0,
):
    threading.excepthook = thread_exception_handler
    try:
        if node_id == 0:
            obj = SupremeGeneral(
                my_id=node_id,
                city_port=city_port,
                is_traitor=is_traitor,
                node_socket=UdpSocket(my_port),
                my_port=my_port,
                ports=ports,
                order=order,
            )
        else:
            obj = General(
                my_id=node_id,
                city_port=city_port,
                is_traitor=is_traitor,
                node_socket=UdpSocket(my_port),
                my_port=my_port,
                ports=ports,
            )
        obj.start()
    except Exception:
        logger.exception("Caught Error")
        raise

    finally:
        obj.close_connection()
