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
from neutron_checking.common import rpc as n_rpc
from neutron_checking import context

LOG = logging.getLogger(__name__)


class CheckingAgentPluginApi(object):
    def __init__(self, topic, host):
        self.host = host
        target = oslo_messaging.Target(
                topic=topic,
                namespace=n_const.RPC_NAMESPACE_CHECKING_AGETN,
                version='1.0')
        self.client = n_rpc.get_client(target)

    @property
    def context(self):
        # TODO(kevinbenton): the context should really be passed in to each of
        # these methods so a call can be tracked all of the way through the
        # system but that will require a larger refactor to pass the context
        # everywhere. We just generate a new one here on each call so requests
        # can be independently tracked server side.
        return context.get_admin_context_without_session()

    def get_router_info(self, router_id):
        """Make a remote process call to retrieve all network info."""
        cctxt = self.client.prepare(version='1.0')
        LOG.info("=====================before call host: %s" % self.host)
        LOG.info("=====================before call router_id: %s" % router_id)
        router_info = cctxt.call(self.context, 'get_router_info',
                                 router_id=router_id,
                                 host=self.host)
        LOG.info("=====================after call host: %s" % self.host)
        LOG.info("=====================after call router_id: %s" % router_id)
        return router_info
