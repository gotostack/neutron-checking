# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

from oslo_config import cfg
from oslo_service import service

from neutron_checking._i18n import _
from neutron_checking.common import config as common_config
from neutron_checking.conf import agent_config as config
from neutron_checking import service as neutron_service


TEST_OPTS = [
    cfg.StrOpt('this_is_test',
               help=_("this_is_test"))
]


def register_options():
    cfg.CONF.register_opts(TEST_OPTS, 'AGENT')
    config.register_root_helper(cfg.CONF)


def main():
    register_options()
    common_config.init(sys.argv[1:])
    config.setup_logging()
    server = neutron_service.Service.create(
        binary='neutron-health-check-agent',
        topic="health-check",
        report_interval=1,
        manager='neutron_checking.agent.checking_agent.CheckingAgent')
    service.launch(cfg.CONF, server).wait()
