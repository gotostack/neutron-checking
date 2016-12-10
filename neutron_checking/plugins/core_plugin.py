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

from oslo_log import log as logging

from neutron_checking.common import rpc as n_rpc
from neutron_checking.plugins import plugin_base

LOG = logging.getLogger(__name__)


class CorePlugin(plugin_base.ServicePluginBase,):

    def __init__(self):
        super(CorePlugin, self).__init__()
        self._setup_rpc()

    def _setup_rpc(self):
        self.topic = "ttt"
        self.conn = n_rpc.create_connection()
        self.conn.create_consumer(self.topic, self.endpoints,
                                  fanout=False)
        self.conn.consume_in_threads()
