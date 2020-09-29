"""Repeating timer that calls a fucntion every set interval."""
#   Copyright 2020 WolkAbout Technology s.r.o.
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
from threading import Timer


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

    def __init__(self, interval, f, *args, **kwargs):  # type: ignore
        r"""
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

    def callback(self) -> None:
        """Call function and start timer."""
        self.f(*self.args, **self.kwargs)
        self.start()

    def cancel(self) -> None:
        """Cancel timer."""
        self.timer.cancel()

    def start(self) -> None:
        """Start timer."""
        self.timer = Timer(self.interval, self.callback)
        self.timer.start()
