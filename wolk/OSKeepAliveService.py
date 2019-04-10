#   Copyright 2018 WolkAbout Technology s.r.o.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""OS Keep Alive Service module."""

from wolk import LoggerFactory
from wolk.interfaces.KeepAliveService import KeepAliveService
from threading import Timer


class OSKeepAliveService(KeepAliveService):
    """
    Send messages to platform in regular intervals to keep device connected.

    Used for cases where no data is being sent by device for over 30 minutes.

    :ivar connectivity_service: Connectivity service used to publish
    :vartype connectivity_service: wolk.interfaces.ConnectivityService.ConnectivityService
    :ivar interval: Number of seconds between each keep alive message
    :vartype interval: int
    :ivar logger: Logger instance issued by wolk.LoggerFactory
    :vartype logger: logging.Logger
    :ivar outbound_message_factory: message factory used to create pings
    :vartype outbound_message_factory: wolk.interfaces.OutboundMessageFactory.OutboundMessageFactory
    :ivar timer: timer for sending ping messages
    :vartype timer: wolk.OSKeepAliveService.RepeatingTimer
    """

    def __init__(self, connectivity_service, outbound_message_factory, interval=600):
        """
        Service for sending keep alive messages.

        :param connectivity_service: Connectivity service used to publish
        :type connectivity_service: wolk.interfaces.ConnectivityService.ConnectivityService
        :param outbound_message_factory: Message factory used to create pings
        :type outbound_message_factory: wolk.interfaces.OutboundMessageFactory.OutboundMessageFactory
        :param interval: Number of seconds between each keep alive message
        :type interval: int or None
        """
        self.logger = LoggerFactory.logger_factory.get_logger(
            str(self.__class__.__name__)
        )
        self.logger.debug(
            "Init:  Connectivity service: %s ; Outbound message factory: %s "
            "Interval: %s",
            connectivity_service,
            outbound_message_factory,
            interval,
        )
        self.connectivity_service = connectivity_service
        self.outbound_message_factory = outbound_message_factory
        self.interval = interval
        self.timer = None

    def handle_pong(self):
        """Handle keep alive response message received from the platform."""
        self.logger.debug("handle_pong called")
        pass

    def start(self):
        """
        Send a keep alive message as soon as the device is connected.

        Starts a repeating timer to send subsequent keep alive messages
        every self.interval seconds
        """
        self.logger.debug("start called")

        self.timer = RepeatingTimer(self.interval, self.send_keep_alive)
        t = Timer(5, self.timer.start)
        t.start()

    def stop(self):
        """Stop the repeating timer."""
        self.logger.debug("stop called")
        self.timer.cancel()

    def send_keep_alive(self):
        """
        Make ping and send.

        Create a keep alive message from the outbound message factory
        and publishes it using the connectivity service
        """
        self.logger.debug("send_keep_alive called")
        message = self.outbound_message_factory.make_from_keep_alive_message()
        self.connectivity_service.publish(message)


class RepeatingTimer:
    """
    Repeating timer calls function with arguments every interval.

    :ivar args: list of arguments
    :vartype args: list
    :ivar f: function to call
    :vartype f: function
    :ivar interval: number of seconds after which to call function
    :vartype interval: int
    :ivar kwargs: keyword arguments
    :vartype kwargs: kwargs
    :ivar timer: timer
    :vartype timer: threading.Timer
    """

    def __init__(self, interval, f, *args, **kwargs):
        """
        Create a repeating timer.

        :param interval: number of seconds after which to call function
        :type interval: int
        :param f: function to call
        :type f: function
        :param \*args: list of arguments
        :type \*args: list
        :param \*\*kwargs: keyword arguments
        :type \*\*kwargs: kwargs
        """
        self.interval = interval
        self.f = f
        self.args = args
        self.kwargs = kwargs

        self.timer = None

    def callback(self):
        """Call function and start timer."""
        self.f(*self.args, **self.kwargs)
        self.start()

    def cancel(self):
        """Cancel timer."""
        self.timer.cancel()

    def start(self):
        """Start timer."""
        self.timer = Timer(self.interval, self.callback)
        self.timer.start()
