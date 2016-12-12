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

LOG = logging.getLogger(__name__)


class CoreCheckCallbackAPI(object):
    target = oslo_messaging.Target(version='1.0')

    def check_router_status(self, context, router_id, host):
        return {"123": "OK"}

    def check_floating_ip_status(self, context, router_id, ip_address, host):
        return {"456": "OK"}
