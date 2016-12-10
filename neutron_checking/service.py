# Copyright 2011 VMware, Inc
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

import inspect
import os
import random

from neutron_lib.plugins import directory
from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_log import log as logging
from oslo_messaging import server as rpc_server
from oslo_service import loopingcall
from oslo_service import service as common_service
from oslo_utils import excutils
from oslo_utils import importutils

from neutron_checking.common import config
from neutron_checking.common import rpc as n_rpc

from neutron_checking.conf import common
from neutron_checking import context
from neutron_checking.db import api as session
from neutron_checking import manager
from neutron_checking import worker as neutron_worker
from neutron_checking import wsgi
from neutron_checking._i18n import _LE, _LI

common.register_service_opts(common.service_opts)
LOG = logging.getLogger(__name__)


class WsgiService(object):
    """Base class for WSGI based services.

    For each api you define, you must also define these flags:
    :<api>_listen: The address on which to listen
    :<api>_listen_port: The port on which to listen

    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.wsgi_app = None

    def start(self):
        self.wsgi_app = _run_wsgi(self.app_name)

    def wait(self):
        self.wsgi_app.wait()


class NeutronApiService(WsgiService):
    """Class for neutron-api service."""
    def __init__(self, app_name):
        super(NeutronApiService, self).__init__(app_name)

    @classmethod
    def create(cls, app_name='neutron-checking'):
        # Setup logging early
        config.setup_logging()
        service = cls(app_name)
        return service


def serve_wsgi(cls):

    try:
        service = cls.create()
        service.start()
    except Exception:
        with excutils.save_and_reraise_exception():
            LOG.exception(_LE('Unrecoverable error: please check log '
                              'for details.'))

    return service


class RpcWorker(neutron_worker.NeutronWorker):
    """Wraps a worker to be handled by ProcessLauncher"""
    start_listeners_method = 'start_rpc_listeners'

    def __init__(self, plugins, worker_process_count=1):
        super(RpcWorker, self).__init__(
            worker_process_count=worker_process_count
        )

        self._plugins = plugins
        self._servers = []

    def start(self):
        super(RpcWorker, self).start()
        for plugin in self._plugins:
            if hasattr(plugin, self.start_listeners_method):
                try:
                    servers = getattr(plugin, self.start_listeners_method)()
                except NotImplementedError:
                    continue
                self._servers.extend(servers)

    def wait(self):
        try:
            self._wait()
        except Exception:
            LOG.exception(_LE('done with wait'))
            raise

    def _wait(self):
        LOG.debug('calling RpcWorker wait()')
        for server in self._servers:
            if isinstance(server, rpc_server.MessageHandlingServer):
                LOG.debug('calling wait on %s', server)
                server.wait()
            else:
                LOG.debug('NOT calling wait on %s', server)
        LOG.debug('returning from RpcWorker wait()')

    def stop(self):
        LOG.debug('calling RpcWorker stop()')
        for server in self._servers:
            if isinstance(server, rpc_server.MessageHandlingServer):
                LOG.debug('calling stop on %s', server)
                server.stop()

    @staticmethod
    def reset():
        config.reset_service()


class RpcReportsWorker(RpcWorker):
    start_listeners_method = 'start_rpc_state_reports_listener'


def _get_rpc_workers():
    plugin = manager.NeutronManager.load_class_for_provider(
        manager.CORE_PLUGINS_NAMESPACE, cfg.CONF.core_plugin)()
    LOG.info("=========================plugin: %s" % plugin)

    if cfg.CONF.rpc_workers < 1:
        cfg.CONF.set_override('rpc_workers', 1)

    rpc_workers = [RpcWorker([plugin],
                             worker_process_count=cfg.CONF.rpc_workers)]

    return rpc_workers


def _get_plugins_workers():
    # NOTE(twilson) get_plugins also returns the core plugin
    plugins = directory.get_unique_plugins()

    # TODO(twilson) Instead of defaulting here, come up with a good way to
    # share a common get_workers default between NeutronPluginBaseV2 and
    # ServicePluginBase
    return [
        plugin_worker
        for plugin in plugins if hasattr(plugin, 'get_workers')
        for plugin_worker in plugin.get_workers()
    ]


class AllServicesNeutronWorker(neutron_worker.NeutronWorker):
    def __init__(self, services, worker_process_count=1):
        super(AllServicesNeutronWorker, self).__init__(worker_process_count)
        self._services = services
        self._launcher = common_service.Launcher(cfg.CONF)

    def start(self):
        for srv in self._services:
            self._launcher.launch_service(srv)
        super(AllServicesNeutronWorker, self).start()

    def stop(self):
        self._launcher.stop()

    def wait(self):
        self._launcher.wait()

    def reset(self):
        self._launcher.restart()


def _start_workers(workers):
    process_workers = [
        plugin_worker for plugin_worker in workers
        if plugin_worker.worker_process_count > 0
    ]

    try:
        if process_workers:
            worker_launcher = common_service.ProcessLauncher(
                cfg.CONF, wait_interval=1.0
            )

            # add extra process worker and spawn there all workers with
            # worker_process_count == 0
            thread_workers = [
                plugin_worker for plugin_worker in workers
                if plugin_worker.worker_process_count < 1
            ]
            if thread_workers:
                process_workers.append(
                    AllServicesNeutronWorker(thread_workers)
                )

            # dispose the whole pool before os.fork, otherwise there will
            # be shared DB connections in child processes which may cause
            # DB errors.
            session.context_manager.dispose_pool()

            for worker in process_workers:
                worker_launcher.launch_service(worker,
                                               worker.worker_process_count)
        else:
            worker_launcher = common_service.ServiceLauncher(cfg.CONF)
            for worker in workers:
                worker_launcher.launch_service(worker)
        return worker_launcher
    except Exception:
        with excutils.save_and_reraise_exception():
            LOG.exception(_LE('Unrecoverable error: please check log for '
                              'details.'))


def start_all_workers():
    workers = _get_rpc_workers()
    return _start_workers(workers)


def _get_api_workers():
    workers = cfg.CONF.api_workers
    if workers is None:
        workers = processutils.get_worker_count()
    return workers


def _run_wsgi(app_name):
    app = config.load_paste_app(app_name)
    if not app:
        LOG.error(_LE('No known API applications configured.'))
        return
    return run_wsgi_app(app)


def run_wsgi_app(app):
    server = wsgi.Server("neutron-checking")
    server.start(app, cfg.CONF.bind_port, cfg.CONF.bind_host,
                 workers=_get_api_workers())
    LOG.info(_LI("neutron-checking service started, "
                 "listening on %(host)s:%(port)s"),
             {'host': cfg.CONF.bind_host, 'port': cfg.CONF.bind_port})
    return server


class Service(n_rpc.Service):
    """Service object for binaries running on hosts.

    A service takes a manager and enables rpc by listening to queues based
    on topic. It also periodically runs tasks on the manager.
    """

    def __init__(self, host, binary, topic, manager, report_interval=None,
                 periodic_interval=None, periodic_fuzzy_delay=None,
                 *args, **kwargs):

        self.binary = binary
        self.manager_class_name = manager
        manager_class = importutils.import_class(self.manager_class_name)
        self.manager = manager_class(host=host, *args, **kwargs)
        self.report_interval = report_interval
        self.periodic_interval = periodic_interval
        self.periodic_fuzzy_delay = periodic_fuzzy_delay
        self.saved_args, self.saved_kwargs = args, kwargs
        self.timers = []
        super(Service, self).__init__(host, topic, manager=self.manager)

    def start(self):
        self.manager.init_host()
        super(Service, self).start()
        if self.report_interval:
            pulse = loopingcall.FixedIntervalLoopingCall(self.report_state)
            pulse.start(interval=self.report_interval,
                        initial_delay=self.report_interval)
            self.timers.append(pulse)

        if self.periodic_interval:
            if self.periodic_fuzzy_delay:
                initial_delay = random.randint(0, self.periodic_fuzzy_delay)
            else:
                initial_delay = None

            periodic = loopingcall.FixedIntervalLoopingCall(
                self.periodic_tasks)
            periodic.start(interval=self.periodic_interval,
                           initial_delay=initial_delay)
            self.timers.append(periodic)
        self.manager.after_start()

    def __getattr__(self, key):
        manager = self.__dict__.get('manager', None)
        return getattr(manager, key)

    @classmethod
    def create(cls, host=None, binary=None, topic=None, manager=None,
               report_interval=None, periodic_interval=None,
               periodic_fuzzy_delay=None):
        """Instantiates class and passes back application object.

        :param host: defaults to cfg.CONF.host
        :param binary: defaults to basename of executable
        :param topic: defaults to bin_name - 'neutron-' part
        :param manager: defaults to cfg.CONF.<topic>_manager
        :param report_interval: defaults to cfg.CONF.report_interval
        :param periodic_interval: defaults to cfg.CONF.periodic_interval
        :param periodic_fuzzy_delay: defaults to cfg.CONF.periodic_fuzzy_delay

        """
        if not host:
            host = cfg.CONF.host
        if not binary:
            binary = os.path.basename(inspect.stack()[-1][1])
        if not topic:
            topic = binary.rpartition('neutron-')[2]
            topic = topic.replace("-", "_")
        if not manager:
            manager = cfg.CONF.get('%s_manager' % topic, None)
        if report_interval is None:
            report_interval = cfg.CONF.report_interval
        if periodic_interval is None:
            periodic_interval = cfg.CONF.periodic_interval
        if periodic_fuzzy_delay is None:
            periodic_fuzzy_delay = cfg.CONF.periodic_fuzzy_delay
        service_obj = cls(host, binary, topic, manager,
                          report_interval=report_interval,
                          periodic_interval=periodic_interval,
                          periodic_fuzzy_delay=periodic_fuzzy_delay)

        return service_obj

    def kill(self):
        """Destroy the service object."""
        self.stop()

    def stop(self):
        super(Service, self).stop()
        for x in self.timers:
            try:
                x.stop()
            except Exception:
                LOG.exception(_LE("Exception occurs when timer stops"))
        self.timers = []

    def wait(self):
        super(Service, self).wait()
        for x in self.timers:
            try:
                x.wait()
            except Exception:
                LOG.exception(_LE("Exception occurs when waiting for timer"))

    def reset(self):
        config.reset_service()

    def periodic_tasks(self, raise_on_error=False):
        """Tasks to be run at a periodic interval."""
        ctxt = context.get_admin_context()
        self.manager.periodic_tasks(ctxt, raise_on_error=raise_on_error)

    def report_state(self):
        """Update the state of this service."""
        # Todo(gongysh) report state to neutron server
        pass
