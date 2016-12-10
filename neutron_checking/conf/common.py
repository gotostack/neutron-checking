# Copyright 2011 VMware, Inc.
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

from neutron_lib.utils import net
from oslo_config import cfg
from oslo_service import wsgi

from neutron_checking._i18n import _


core_opts = [
    cfg.StrOpt('bind_host', default='0.0.0.0',
               help=_("The host IP to bind to")),
    cfg.PortOpt('bind_port', default=19696,
                help=_("The port to bind to")),
    cfg.StrOpt('auth_strategy', default='keystone',
               help=_("The type of authentication to use")),
    cfg.StrOpt('core_plugin',
               help=_("The core plugin Neutron will use")),
    cfg.ListOpt('service_plugins', default=[],
                help=_("The service plugins Neutron will use")),
    cfg.StrOpt('base_mac', default="fa:16:3e:00:00:00",
               help=_("The base MAC address Neutron will use for VIFs. "
                      "The first 3 octets will remain unchanged. If the 4th "
                      "octet is not 00, it will also be used. The others "
                      "will be randomly generated.")),
    cfg.BoolOpt('allow_bulk', default=True,
                help=_("Allow the usage of the bulk API")),
    cfg.StrOpt('host', default=net.get_hostname(),
               sample_default='example.domain',
               help=_("Hostname to be used by the Neutron server, agents and "
                      "services running on this machine. All the agents and "
                      "services running on this machine must use the same "
                      "host value.")),
    cfg.IntOpt('send_events_interval', default=2,
               help=_('Number of seconds between sending events to nova if '
                      'there are any events to send.')),
    cfg.StrOpt('web_framework', default='legacy',
               choices=('legacy', 'pecan'),
               help=_("This will choose the web framework in which to run "
                      "the Neutron API server. 'pecan' is a new experimental "
                      "rewrite of the API server."))
]


def register_core_common_config_opts(cfg=cfg.CONF):
    cfg.register_opts(core_opts)
    wsgi.register_opts(cfg)


socket_opts = [
    cfg.IntOpt('backlog',
               default=4096,
               help=_("Number of backlog requests to configure "
                      "the socket with")),
    cfg.IntOpt('retry_until_window',
               default=30,
               help=_("Number of seconds to keep retrying to listen")),
    cfg.BoolOpt('use_ssl',
                default=False,
                help=_('Enable SSL on the API server')),
]


def register_socket_opts(cfg=cfg.CONF):
    cfg.register_opts(socket_opts)
    wsgi.register_opts(cfg)


service_opts = [
    cfg.IntOpt('periodic_interval',
               default=40,
               help=_('Seconds between running periodic tasks.')),
    cfg.IntOpt('api_workers',
               help=_('Number of separate API worker processes for service. '
                      'If not specified, the default is equal to the number '
                      'of CPUs available for best performance.')),
    cfg.IntOpt('rpc_workers',
               default=1,
               help=_('Number of RPC worker processes for service.')),
    cfg.IntOpt('rpc_state_report_workers',
               default=1,
               help=_('Number of RPC worker processes dedicated to state '
                      'reports queue.')),
    cfg.IntOpt('periodic_fuzzy_delay',
               default=5,
               help=_('Range of seconds to randomly delay when starting the '
                      'periodic task scheduler to reduce stampeding. '
                      '(Disable by setting to 0)')),
]


def register_service_opts(opts, conf=cfg.CONF):
    conf.register_opts(opts)
