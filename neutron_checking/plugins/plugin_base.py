# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import abc
import six

from neutron_checking import worker


@six.add_metaclass(abc.ABCMeta)
class PluginInterface(object):

    @classmethod
    def __subclasshook__(cls, klass):
        """Checking plugin class.

        The __subclasshook__ method is a class method
        that will be called every time a class is tested
        using issubclass(klass, PluginInterface).
        In that case, it will check that every method
        marked with the abstractmethod decorator is
        provided by the plugin class.
        """

        if not cls.__abstractmethods__:
            return NotImplemented

        for method in cls.__abstractmethods__:
            if any(method in base.__dict__ for base in klass.__mro__):
                continue
            return NotImplemented
        return True


@six.add_metaclass(abc.ABCMeta)
class ServicePluginBase(PluginInterface,
                        worker.WorkerSupportServiceMixin):
    """Define base interface for any Advanced Service plugin."""
    supported_extension_aliases = []

    @abc.abstractmethod
    def get_plugin_type(self):
        """Return one of predefined service types.

        See neutron/plugins/common/constants.py
        """
        pass

    @abc.abstractmethod
    def get_plugin_description(self):
        """Return string description of the plugin."""
        pass

    def rpc_workers_supported(self):
        """Return whether the plugin supports multiple RPC workers.

        A plugin that supports multiple RPC workers should override the
        start_rpc_listeners method to ensure that this method returns True and
        that start_rpc_listeners is called at the appropriate time.
        Alternately, a plugin can override this method to customize detection
        of support for multiple rpc workers

        .. note:: this method is optional, as it was not part of the originally
                  defined plugin API.
        """
        return (self.__class__.start_rpc_listeners !=
                ServicePluginBase.start_rpc_listeners)
