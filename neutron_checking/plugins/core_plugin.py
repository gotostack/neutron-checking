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

from oslo_log import helpers as log_helpers
from oslo_log import log as logging

from neutron_checking.api.rpc.callbacks import checking_agent_callback_api
from neutron_checking.api.rpc.callbacks import core_check_pull_api
from neutron_checking.common import constants
from neutron_checking.common import rpc as n_rpc
from neutron_checking.common import topics
from neutron_checking.plugins import plugin_base

LOG = logging.getLogger(__name__)


class CorePlugin(plugin_base.ServicePluginBase):

    def __init__(self):
        super(CorePlugin, self).__init__()
        self.check_rpc_api = core_check_pull_api.CoreCheckingPullAPI()

    def _setup_rpc(self):
        """Initialize components to support agent communication."""
        self.endpoints = [
            checking_agent_callback_api.CheckingAgentCallbackAPI()]

    def get_plugin_type(self):
        """Return one of predefined service types."""
        return constants.CORE

    def get_plugin_description(self):
        """Return string description of the plugin."""
        return "Core plugin"

    @log_helpers.log_method_call
    def start_rpc_listeners(self):
        """Start the RPC loop to let the plugin communicate with agents."""
        self._setup_rpc()
        LOG.info("=================start_rpc_listeners")
        self.topic = topics.PLUGIN
        LOG.info("===========start_rpc_listeners self.topic: %s" % self.topic)
        self.conn = n_rpc.create_connection()
        LOG.info("===========start_rpc_listeners self.conn: %s" % self.conn)
        self.conn.create_consumer(self.topic, self.endpoints, fanout=False)
        return self.conn.consume_in_threads()
