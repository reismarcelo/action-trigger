# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.dp import Action


# ---------------------------------------------
# ACTIONS
# ---------------------------------------------
class FetchKeysAction(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):

        with ncs.maapi.single_read_trans(uinfo.username, "system") as read_t:
            root = ncs.maagic.get_root(read_t)
            device = root.devices.device[input.device]

            output.result = device.ssh.fetch_host_keys().result


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')

        self.register_action('action-trigger-action', FetchKeysAction)

    def teardown(self):
        self.log.info('Main FINISHED')
