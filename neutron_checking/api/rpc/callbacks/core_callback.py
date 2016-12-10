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

import oslo_messaging
from oslo_log import log as logging

from neutron_checking.common import constants

LOG = logging.getLogger(__name__)


class CoreRpcCallback(object):
    # API version history:
    #     1.0 - Initial version.

    target = oslo_messaging.Target(
        namespace=constants.CORE,
        version='1.0')

    def get_agent_id(self):
        LOG.info("=====================this is a id test")
        return "1"
