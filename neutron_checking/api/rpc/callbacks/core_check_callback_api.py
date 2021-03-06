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

from neutron_checking.common import constants
from neutron_checking.common import topics

LOG = logging.getLogger(__name__)


class CoreCheckingCallbackAPI(object):
    target = oslo_messaging.Target(
        topic=topics.PLUGIN,
        version='1.0',
        namespace=constants.RPC_NAMESPACE_CHECKING_PLUGIN)

    def check_router_status(self, context, **kwargs):
        LOG.info("=====================check_router_status called")
        return {"123": "OK"}

    def check_floating_ip_status(self, context, **kwargs):
        LOG.info("=====================check_floating_ip_status called")
        return {"456": "OK"}
