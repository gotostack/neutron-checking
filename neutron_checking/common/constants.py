# Copyright (c) 2012 OpenStack Foundation.
#
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

from neutron_lib import constants as lib_constants


ROUTER_PORT_OWNERS = lib_constants.ROUTER_INTERFACE_OWNERS_SNAT + \
    (lib_constants.DEVICE_OWNER_ROUTER_GW,)

ROUTER_STATUS_ACTIVE = 'ACTIVE'
# NOTE(kevinbenton): a BUILD status for routers could be added in the future
# for agents to indicate when they are wiring up the ports. The following is
# to indicate when the server is busy building sub-components of a router
ROUTER_STATUS_ALLOCATING = 'ALLOCATING'

DEVICE_ID_RESERVED_DHCP_PORT = "reserved_dhcp_port"

HA_ROUTER_STATE_KEY = '_ha_state'
METERING_LABEL_KEY = '_metering_labels'
FLOATINGIP_AGENT_INTF_KEY = '_floatingip_agent_interfaces'
SNAT_ROUTER_INTF_KEY = '_snat_router_interfaces'

HA_NETWORK_NAME = 'HA network tenant %s'
HA_SUBNET_NAME = 'HA subnet tenant %s'
HA_PORT_NAME = 'HA port tenant %s'
MINIMUM_MINIMUM_AGENTS_FOR_HA = 1
DEFAULT_MINIMUM_AGENTS_FOR_HA = 2
HA_ROUTER_STATE_ACTIVE = 'active'
HA_ROUTER_STATE_STANDBY = 'standby'

PAGINATION_INFINITE = 'infinite'

SORT_DIRECTION_ASC = 'asc'
SORT_DIRECTION_DESC = 'desc'

ETHERTYPE_NAME_ARP = 'arp'
ETHERTYPE_ARP = 0x0806
ETHERTYPE_IP = 0x0800
ETHERTYPE_IPV6 = 0x86DD

IP_PROTOCOL_NAME_ALIASES = {lib_constants.PROTO_NAME_IPV6_ICMP_LEGACY:
                            lib_constants.PROTO_NAME_IPV6_ICMP}

VALID_DSCP_MARKS = [0, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34,
                    36, 38, 40, 46, 48, 56]

IP_PROTOCOL_NUM_TO_NAME_MAP = {
    str(v): k for k, v in lib_constants.IP_PROTOCOL_MAP.items()}

# Special provisional prefix for IPv6 Prefix Delegation
PROVISIONAL_IPV6_PD_PREFIX = '::/64'

# Timeout in seconds for getting an IPv6 LLA
LLA_TASK_TIMEOUT = 40

# length of all device prefixes (e.g. qvo, tap, qvb)
LINUX_DEV_PREFIX_LEN = 3
# must be shorter than linux IFNAMSIZ (which is 16)
LINUX_DEV_LEN = 14

# Possible prefixes to partial port IDs in interface names used by the OVS,
# Linux Bridge, and IVS VIF drivers in Nova and the neutron agents. See the
# 'get_ovs_interfaceid' method in Nova (nova/virt/libvirt/vif.py) for details.
INTERFACE_PREFIXES = (lib_constants.TAP_DEVICE_PREFIX,
                      lib_constants.VETH_DEVICE_PREFIX,
                      lib_constants.SNAT_INT_DEV_PREFIX)

ATTRIBUTES_TO_UPDATE = 'attributes_to_update'

# Maximum value integer can take in MySQL and PostgreSQL
# In SQLite integer can be stored in 1, 2, 3, 4, 6, or 8 bytes,
# but here it will be limited by this value for consistency.
DB_INTEGER_MAX_VALUE = 2 ** 31 - 1

# TODO(amuller): Re-define the RPC namespaces once Oslo messaging supports
# Targets with multiple namespaces. Neutron will then implement callbacks
# for its RPC clients in order to support rolling upgrades.

# RPC Interface for agents to call DHCP API implemented on the plugin side
RPC_NAMESPACE_DHCP_PLUGIN = None
# RPC interface for the metadata service to get info from the plugin side
RPC_NAMESPACE_METADATA = None
# RPC interface for agent to plugin security group API
RPC_NAMESPACE_SECGROUP = None
# RPC interface for agent to plugin DVR api
RPC_NAMESPACE_DVR = None
# RPC interface for reporting state back to the plugin
RPC_NAMESPACE_STATE = None
# RPC interface for agent to plugin resources API
RPC_NAMESPACE_RESOURCES = None
# RPC interface for agent to plugin checking resources API
RPC_NAMESPACE_CHECKING_PLUGIN = None
# RPC interface for plugin to checking agent API
RPC_NAMESPACE_CHECKING_AGETN = None

# Default network MTU value when not configured
DEFAULT_NETWORK_MTU = 1500
IPV6_MIN_MTU = 1280

ROUTER_MARK_MASK = "0xffff"

# Agent states as detected by server, used to reply on agent's state report
# agent has just been registered
AGENT_NEW = 'new'
# agent is alive
AGENT_ALIVE = 'alive'
# agent has just returned to alive after being dead
AGENT_REVIVED = 'revived'

INGRESS_DIRECTION = 'ingress'
EGRESS_DIRECTION = 'egress'

VALID_DIRECTIONS = (INGRESS_DIRECTION, EGRESS_DIRECTION)
VALID_ETHERTYPES = (lib_constants.IPv4, lib_constants.IPv6)

IP_ALLOWED_VERSIONS = [lib_constants.IP_VERSION_4, lib_constants.IP_VERSION_6]

PORT_RANGE_MIN = 1
PORT_RANGE_MAX = 65535

# Configuration values for accept_ra sysctl, copied from linux kernel
# networking (netdev) tree, file Documentation/networking/ip-sysctl.txt
#
# Possible values are:
#         0 Do not accept Router Advertisements.
#         1 Accept Router Advertisements if forwarding is disabled.
#         2 Overrule forwarding behaviour. Accept Router Advertisements
#           even if forwarding is enabled.
ACCEPT_RA_DISABLED = 0
ACCEPT_RA_WITHOUT_FORWARDING = 1
ACCEPT_RA_WITH_FORWARDING = 2

# Some components communicate using private address ranges, define
# them all here. These address ranges should not cause any issues
# even if they overlap since they are used in disjoint namespaces,
# but for now they are unique.
# We define the metadata cidr since it falls in the range.
PRIVATE_CIDR_RANGE = '169.254.0.0/16'
DVR_FIP_LL_CIDR = '169.254.64.0/18'
L3_HA_NET_CIDR = '169.254.192.0/18'
METADATA_CIDR = '169.254.169.254/32'

CORE = "CORE"
DUMMY = "DUMMY"
LOADBALANCER = "LOADBALANCER"
LOADBALANCERV2 = "LOADBALANCERV2"
FIREWALL = "FIREWALL"
VPN = "VPN"
METERING = "METERING"
L3_ROUTER_NAT = "L3_ROUTER_NAT"
FLAVORS = "FLAVORS"
QOS = "QOS"

# Maps extension alias to service type that
# can be implemented by the core plugin.
EXT_TO_SERVICE_MAPPING = {
    'dummy': DUMMY,
    'lbaas': LOADBALANCER,
    'lbaasv2': LOADBALANCERV2,
    'fwaas': FIREWALL,
    'vpnaas': VPN,
    'metering': METERING,
    'router': L3_ROUTER_NAT,
    'qos': QOS,
}

# Maps default service plugins entry points to their extension aliases
DEFAULT_SERVICE_PLUGINS = {}

# Service operation status constants
ACTIVE = "ACTIVE"
DOWN = "DOWN"
CREATED = "CREATED"
PENDING_CREATE = "PENDING_CREATE"
PENDING_UPDATE = "PENDING_UPDATE"
PENDING_DELETE = "PENDING_DELETE"
INACTIVE = "INACTIVE"
ERROR = "ERROR"

ACTIVE_PENDING_STATUSES = (
    ACTIVE,
    PENDING_CREATE,
    PENDING_UPDATE
)

# Network Type constants
TYPE_FLAT = 'flat'
TYPE_GENEVE = 'geneve'
TYPE_GRE = 'gre'
TYPE_LOCAL = 'local'
TYPE_VXLAN = 'vxlan'
TYPE_VLAN = 'vlan'
TYPE_NONE = 'none'

# Values for network_type

# For VLAN Network
MIN_VLAN_TAG = 1
MAX_VLAN_TAG = 4094

# For Geneve Tunnel
MIN_GENEVE_VNI = 1
MAX_GENEVE_VNI = 2 ** 24 - 1

# For GRE Tunnel
MIN_GRE_ID = 1
MAX_GRE_ID = 2 ** 32 - 1

# For VXLAN Tunnel
MIN_VXLAN_VNI = 1
MAX_VXLAN_VNI = 2 ** 24 - 1
VXLAN_UDP_PORT = 4789

# Overlay (tunnel) protocol overhead
GENEVE_ENCAP_MIN_OVERHEAD = 30
GRE_ENCAP_OVERHEAD = 22
VXLAN_ENCAP_OVERHEAD = 30

# IP header length
IP_HEADER_LENGTH = {
    4: 20,
    6: 40,
}
