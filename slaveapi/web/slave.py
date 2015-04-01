import logging

from flask import jsonify, request, make_response
from flask.views import MethodView

from .action_base import ActionView, missing_fields_response
from ..actions.reboot import reboot
from ..actions.shutdown_buildslave import shutdown_buildslave
from ..actions.buildslave_uptime import buildslave_uptime
from ..actions.buildslave_last_activity import buildslave_last_activity
from ..actions.disable import disable
from ..slave import Slave as SlaveClass
from ..actions.aws_create_instance import aws_create_instance
from ..actions.aws_terminate_instance import aws_terminate_instance
from ..actions.aws_start_instance import aws_start_instance
from ..actions.aws_stop_instance import aws_stop_instance
from ..util import normalize_truthiness, value_in_values

log = logging.getLogger(__name__)


class Slave(MethodView):
    def get(self, slave):
        slave = SlaveClass(slave)
        slave.load_all_info()
        return jsonify(slave.to_dict())


class Reboot(ActionView):
    """Request a reboot of a slave or get status on a previously requested
    reboot. See :py:class:`slaveapi.web.action_base.ActionView` for details
    on GET and POST methods. See :py:func:`slaveapi.actions.reboot.reboot` for
    details on how reboots are performed."""

    def __init__(self, *args, **kwargs):
        self.action = reboot
        ActionView.__init__(self, *args, **kwargs)


class ShutdownBuildslave(ActionView):
    """Request a shutdown of a buildslave or get status on a previously requested
    shutdown. See :py:class:`slaveapi.web.action_base.ActionView` for details
    on GET and POST methods. See :py:func:`slaveapi.actions.shutdown_buildslave.shutdown_buildslave`
    for details on how buildslave shutdowns are performed."""
    def __init__(self, *args, **kwargs):
        self.action = shutdown_buildslave
        ActionView.__init__(self, *args, **kwargs)

class GetUptime(ActionView):
    """Request the build slave uptime (in seconds).  See
    :py:class:`slaveapi.web.action_base.ActionView` for details on GET and POST
    methods. See :py:func:`slaveapi.actions.buildslave_uptime.buildslave_uptime`
    for details on how Uptime is retrieved."""
    def __init__(self, *args, **kwargs):
        self.action = buildslave_uptime
        ActionView.__init__(self, *args, **kwargs)

class GetLastActivity(ActionView):
    """Request the last activity age (in seconds).  See
    :py:class:`slaveapi.web.action_base.ActionView` for details on GET and POST
    methods. See :py:func:`slaveapi.actions.buildslave_last_activity.buildslave_last_activity`
    for details on how LastActivity is retrieved."""
    def __init__(self, *args, **kwargs):
        self.action = buildslave_last_activity
        ActionView.__init__(self, *args, **kwargs)


class Disable(ActionView):
    """Request a slave to be disabled. See
    :py:class:`slaveapi.web.action_base.ActionView` for details on GET and POST
    methods. See :py:func:`slaveapi.actions.disable.disable`
    for details on what options are supported"""
    def __init__(self, *args, **kwargs):
        self.action = disable
        ActionView.__init__(self, *args, **kwargs)

    def post(self, slave, *args, **kwargs):
        reason = request.form.get('reason')
        try:
            force = normalize_truthiness(request.form.get('force', False))
        except ValueError as e:
            return make_response(
                jsonify({'error': 'incorrect args for use_force in post',
                         'msg': str(e)}),
                400
            )
        return super(Disable, self).post(slave, *args, force=force,
                                         reason=reason, **kwargs)


class AWSCreateInstance(ActionView):
    """Request an AWS slave to be instantiated. See
    :py:class:`slaveapi.web.action_base.ActionView` for details on GET and POST
    methods. See
    :py:func:`slaveapi.actions.aws_create_instance.aws_create_instance
    for details on what options are supported"""
    def __init__(self, *args, **kwargs):
        self.action = aws_create_instance
        ActionView.__init__(self, *args, **kwargs)

    def post(self, slave, *args, **kwargs):
        required_fields = {
            'email': request.form.get('email'),
            'bug': request.form.get('bug'),
            'instance_type': request.form.get('instance_type'),
        }
        optional_fields = {
            'arch': request.form.get('arch')
        }

        if not all(required_fields.values()):
            return missing_fields_response(required_fields)

        if not value_in_values(required_fields['instance_type'],
                               ['build', 'test']):
            return make_response(
                jsonify(
                    {'error': 'incorrect arg for instance_type in post',
                     'msg': 'Got: %s, expected: %s' % (
                         required_fields['instance_type'], ['build', 'test'])}
                ), 400
            )

        if (required_fields['instance_type'] == 'build' and
                optional_fields == '32'):
            return make_response(
                jsonify(
                    {'error': 'mismatching instance_type and arch',
                     'msg': '32bit instances are not used for building'}
                ), 400
            )

        return super(AWSCreateInstance, self).post(
            slave, *args, email=required_fields['email'],
            bug=required_fields['bug'],
            instance_type=required_fields['instance_type'],
            arch=optional_fields['arch'], **kwargs
        )

class AWSTerminateInstance(ActionView):
    """Terminate aws instance if it exists.
    :py:class:`slaveapi.web.action_base.ActionView` for details on GET and POST
    methods. See :py:func:`slaveapi.actions.aws_terminate_instance.aws_terminate_instance`
    for details on how LastActivity is retrieved."""
    def __init__(self, *args, **kwargs):
        self.action = aws_terminate_instance
        ActionView.__init__(self, *args, **kwargs)


class AWSStopInstance(ActionView):
    """Stop aws instance if it exists.
    :py:class:`slaveapi.web.action_base.ActionView` for details on GET and POST
    methods. See :py:func:`slaveapi.actions.aws_stop_instance.aws_stop_instance`
    for details on how LastActivity is retrieved."""
    def __init__(self, *args, **kwargs):
        self.action = aws_stop_instance
        ActionView.__init__(self, *args, **kwargs)


class AWSStartInstance(ActionView):
    """Start aws instance if it exists.
    :py:class:`slaveapi.web.action_base.ActionView` for details on GET and POST
    methods. See :py:func:`slaveapi.actions.aws_start_instance.aws_start_instance`
    for details on how LastActivity is retrieved."""
    def __init__(self, *args, **kwargs):
        self.action = aws_start_instance
        ActionView.__init__(self, *args, **kwargs)
