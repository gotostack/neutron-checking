# Copyright 2011 VMware, Inc
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from neutron_lib import constants as lib_const
from neutron_lib.plugins import directory
from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging
from oslo_service import periodic_task
from oslo_utils import excutils
from osprofiler import profiler
import six

from neutron_checking._i18n import _, _LE, _LI
from neutron_checking.common import constants
from neutron_checking.utils import utils


LOG = logging.getLogger(__name__)

CORE_PLUGINS_NAMESPACE = 'neutron_checking.core_plugins'


class ManagerMeta(profiler.TracedMeta, type(periodic_task.PeriodicTasks)):
    pass


@six.add_metaclass(ManagerMeta)
class Manager(periodic_task.PeriodicTasks):
    __trace_args__ = {"name": "rpc"}

    # Set RPC API version to 1.0 by default.
    target = oslo_messaging.Target(version='1.0')

    def __init__(self, host=None):
        if not host:
            host = cfg.CONF.host
        self.host = host
        conf = getattr(self, "conf", cfg.CONF)
        super(Manager, self).__init__(conf)

    def periodic_tasks(self, context, raise_on_error=False):
        self.run_periodic_tasks(context, raise_on_error=raise_on_error)

    def init_host(self):
        """Handle initialization if this is a standalone service.

        Child classes should override this method.

        """
        pass

    def after_start(self):
        """Handler post initialization stuff.

        Child classes can override this method.
        """
        pass


def validate_post_plugin_load():
    """Checks if the configuration variables are valid.

    If the configuration is invalid then the method will return an error
    message. If all is OK then it will return None.
    """
    if ('dhcp_agents_per_network' in cfg.CONF and
        cfg.CONF.dhcp_agents_per_network <= 0):
        msg = _("dhcp_agents_per_network must be >= 1. '%s' "
                "is invalid.") % cfg.CONF.dhcp_agents_per_network
        return msg


def validate_pre_plugin_load():
    """Checks if the configuration variables are valid.

    If the configuration is invalid then the method will return an error
    message. If all is OK then it will return None.
    """
    if cfg.CONF.core_plugin is None:
        msg = _('Neutron core_plugin not configured!')
        return msg


@six.add_metaclass(profiler.TracedMeta)
class NeutronManager(object):
    """Neutron's Manager class.

    Neutron's Manager class is responsible for parsing a config file and
    instantiating the correct plugin that concretely implements
    neutron_plugin_base class.
    """
    # TODO(armax): use of the singleton pattern for this class is vestigial,
    # and it is mainly relied on by the unit tests. It is safer to get rid
    # of it once the entire codebase (neutron + subprojects) has switched
    # entirely to using the plugins directory.
    _instance = None
    __trace_args__ = {"name": "rpc"}

    def __init__(self, options=None, config_file=None):
        # If no options have been provided, create an empty dict
        if not options:
            options = {}

        msg = validate_pre_plugin_load()
        if msg:
            LOG.critical(msg)
            raise Exception(msg)

        # NOTE(jkoelker) Testing for the subclass with the __subclasshook__
        #                breaks tach monitoring. It has been removed
        #                intentionally to allow v2 plugins to be monitored
        #                for performance metrics.
        plugin_provider = cfg.CONF.core_plugin
        LOG.info(_LI("Loading core plugin: %s"), plugin_provider)
        # NOTE(armax): keep hold of the actual plugin object
        plugin = self._get_plugin_instance(CORE_PLUGINS_NAMESPACE,
                                           plugin_provider)
        directory.add_plugin(lib_const.CORE, plugin)
        msg = validate_post_plugin_load()
        if msg:
            LOG.critical(msg)
            raise Exception(msg)

        # load services from the core plugin first
        self._load_services_from_core_plugin(plugin)

    @staticmethod
    def load_class_for_provider(namespace, plugin_provider):
        """Loads plugin using alias or class name
        :param namespace: namespace where alias is defined
        :param plugin_provider: plugin alias or class name
        :returns plugin that is loaded
        :raises ImportError if fails to load plugin
        """

        try:
            return utils.load_class_by_alias_or_classname(namespace,
                    plugin_provider)
        except ImportError:
            with excutils.save_and_reraise_exception():
                LOG.error(_LE("Plugin '%s' not found."), plugin_provider)

    def _get_plugin_instance(self, namespace, plugin_provider):
        plugin_class = self.load_class_for_provider(namespace, plugin_provider)
        return plugin_class()

    def _load_services_from_core_plugin(self, plugin):
        """Puts core plugin in service_plugins for supported services."""
        LOG.debug("Loading services supported by the core plugin")

        # supported service types are derived from supported extensions
        for ext_alias in getattr(plugin, "supported_extension_aliases", []):
            if ext_alias in constants.EXT_TO_SERVICE_MAPPING:
                service_type = constants.EXT_TO_SERVICE_MAPPING[ext_alias]
                directory.add_plugin(service_type, plugin)
                LOG.info(_LI("Service %s is supported by the core plugin"),
                         service_type)

    def _get_default_service_plugins(self):
        """Get default service plugins to be loaded."""
        return constants.DEFAULT_SERVICE_PLUGINS.keys()

    @classmethod
    @utils.synchronized("manager")
    def _create_instance(cls):
        if not cls.has_instance():
            cls._instance = cls()

    @classmethod
    def has_instance(cls):
        return cls._instance is not None

    @classmethod
    def clear_instance(cls):
        cls._instance = None

    @classmethod
    def get_instance(cls):
        # double checked locking
        if not cls.has_instance():
            cls._create_instance()
        return cls._instance


def init():
    """Call to load the plugins (core+services) machinery."""
    # TODO(armax): use is_loaded() when available
    if not directory.get_plugins():
        NeutronManager.get_instance()
