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

from oslo_log import log as logging
import oslo_messaging

from neutron_checking.common import constants as n_const
from neutron_checking.common import topics

LOG = logging.getLogger(__name__)


class CheckingAgentCallbackAPI(object):
    target = oslo_messaging.Target(
        topic=topics.AGENT,
        namespace=n_const.RPC_NAMESPACE_CHECKING_AGETN,
        version='1.0')

    def get_router_info(self, context, **kwargs):
        """Returns a router info."""
        host = kwargs.get('host')
        router_id = kwargs.get('router_id')
        LOG.info("=========================call from host: %s" % host)
        LOG.info("=========================called router_id: %s" % router_id)
        return {"router_id": "I am a router id."}
