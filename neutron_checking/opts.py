#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import itertools

from oslo_config import cfg

import neutron_checking.conf.agent_config
import neutron_checking.conf.common

CONF = cfg.CONF


def list_agent_opts():
    return [
        ('agent',
         itertools.chain(
             neutron_checking.conf.agent_config.ROOT_HELPER_OPTS)
         ),
        ('DEFAULT',
         itertools.chain(
             neutron_checking.conf.agent_config.INTERFACE_DRIVER_OPTS)
         )
    ]


def list_opts():
    return [
        ('DEFAULT',
         itertools.chain(
             neutron_checking.conf.common.core_cli_opts,
             neutron_checking.conf.common.core_opts,
             neutron_checking.conf.common.socket_opts,
             neutron_checking.conf.common.service_opts)
         ),
    ]
