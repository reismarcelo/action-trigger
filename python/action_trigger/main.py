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
            self.log.info('Done fetch-keys')

        with ncs.maapi.single_write_trans(uinfo.username, "system") as write_t:
            root = ncs.maagic.get_root(write_t)
            device = root.devices.device[input.device]
            svc_vars = {
                'vrf_id': input.vrf_id
            }
            apply_template('service-template', device, svc_vars)
            write_t.apply()
            self.log.info('Done service call')


def apply_template(template_name, context, var_dict=None, none_value=''):
    """
    Facilitate applying templates by setting template variables via an optional dictionary

    By default, if a dictionary item has value None it is converted to an empty string. In the template,
    'when' statements can be used to prevent rendering of a template block if the variable is an empty string.

    :param template_name: Name of the template file
    :param context: Context in which the template is rendered
    :param var_dict: Optional dictionary containing additional variables to be passed to the template
    :param none_value: Optional, defines the replacement for variables with None values. Default is an empty string.
    """
    template = ncs.template.Template(context)
    t_vars = ncs.template.Variables()

    if var_dict is not None:
        for name, value in var_dict.items():
            t_vars.add(name, value or none_value)

    template.apply(template_name, t_vars)


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')

        self.register_action('action-trigger-action', FetchKeysAction)

    def teardown(self):
        self.log.info('Main FINISHED')
