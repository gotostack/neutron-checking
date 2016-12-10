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

from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging
from oslo_service import periodic_task

from neutron_checking.common import agent_rpc
from neutron_checking import context
from neutron_checking import manager
from neutron_checking.resources import resources

from neutron_checking._i18n import _LI

CHECK = 'check'


LOG = logging.getLogger(__name__)


class CheckingAgent(manager.Manager):
    target = oslo_messaging.Target(version='1.0')

    def __init__(self, host, conf=None):
        super(CheckingAgent, self).__init__()
        self.conf = conf or cfg.CONF
        # self.ovs = ovs_lib.BaseOVS()
        self.agent_conf = self.conf.AGENT
        # self.ovs_conf = self.conf.OVS
        #self.l2_pop = self.agent_conf.l2_population

        self.setup_rpc()

    def setup_rpc(self):
        # RPC network init
        self.context = context.get_admin_context_without_session()
        # Define the listening consumers for the agent
        consumers = [[resources.PORT, CHECK],
                     [resources.TUNNEL, CHECK],
                     [resources.ROUTER, CHECK],
                     [resources.NETWORK, CHECK],
                     [resources.FLOATING_IP, CHECK]]
        #if self.l2_pop:
        #    consumers.append([topics.L2POPULATION, CHECK])
        self.connection = agent_rpc.create_consumers([self],
                                                     resources.AGENT,
                                                     consumers,
                                                     start_listening=False)

    def after_start(self):
        self.run()
        LOG.info(_LI("Hello world"))

    def run(self):
        self.periodic_resync(self.context)

    @periodic_task.periodic_task(spacing=1)
    def periodic_resync(self, context):
        LOG.info(_LI("periodic_resync Hello world"))
