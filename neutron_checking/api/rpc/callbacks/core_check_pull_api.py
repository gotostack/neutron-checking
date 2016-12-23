# Copyright (c) 2013 OpenStack Foundation.
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

from oslo_log import log as logging
import oslo_messaging

from neutron_checking.common import constants as n_const
from neutron_checking.common import rpc as n_rpc
from neutron_checking.common import topics


LOG = logging.getLogger(__name__)


class CoreCheckingPullAPI(object):
    """Server side of Core Resource Check RPC API.

    API version history:
        1.0 - Initial version.
    """
    def __init__(self, topic=topics.PLUGIN):
        self.topic = topic
        target = oslo_messaging.Target(
                topic=topic,
                namespace=n_const.RPC_NAMESPACE_CHECKING_PLUGIN,
                version='1.0')
        self.client = n_rpc.get_client(target)

    def check_router_status(self, context, router_id, host):
        cctxt = self.client.prepare(topic=self.topic,
                                    version='1.0',
                                    server=host)
        return cctxt.call(context, 'check_router_status', router_id=router_id)

    def check_floating_ip_status(self, context, router_id, ip_address, host):
        cctxt = self.client.prepare(topic=self.topic,
                                    version='1.0',
                                    server=host)
        return cctxt.call(context, 'check_floating_ip_status',
                          router_id=router_id,
                          ip_address=ip_address)
