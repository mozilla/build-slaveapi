import logging
import os
import re
import subprocess
from ..actions.results import SUCCESS, FAILURE

log = logging.getLogger(__name__)
from ..global_state import config

INSTANCE_NOT_FOUND_MSG = "Instance '%s' could not be found. Does it exist?"


def _manage_instance(name, action, dry_run=False, force=False):
    query_script = os.path.join(config['cloud_tools_path'],
                                'scripts/aws_manage_instances.py')
    options = []
    if dry_run:
        options.append('--dry-run')
    if force:
        options.append('--force')

    p = subprocess.Popen(['python', query_script] + options + [action, name],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (std_output, logging_output) = p.communicate()
    p.wait()
    return std_output, logging_output


def _query_aws_instance(name):
    """
    :param name: short-name of host
    :return:
        {'FQDN': 'dev-linux64-ec2-jlund.dev.releng.use1.mozilla.com',
         'Name': 'dev-linux64-ec2-jlund',
         'created': '2014-12-0501:11:43PST',
         'moz-bug': '858797',
         'moz-loaned-to': 'jlund@mozilla.com',
         'moz-state': 'ready',
         'moz-type': 'dev-linux64'}
    """
    std_output, logging_output = _manage_instance(name, 'status')

    # we rely on print statements (std out) for instance status
    if std_output:  # instance exists
        # TODO - this is fragile. aws_manage_instances.py 'status' should return a dict ready string
        #      - filed: Bug 1117173 - aws_manage_instances should return status codes and json output
        # parse the output for all the tags
        tags = std_output.split('Tags:', 1)[1].split('\n', 1)[0].split(',')
        # make a dict out of the tags and return that
        return dict(tag.replace(" ", "").split('->') for tag in tags), logging_output
    return {}, logging_output


def _action_on_instance(name, action, force, success_regex, success_msg):
    instance, logging_output = _query_aws_instance(name)
    if instance:
        std_output, logging_output = _manage_instance(name, action, force=force)
        # we rely on logging module output to determine if instance has been terminated
        terminated = re.search(success_regex, logging_output)
        if terminated:
            return SUCCESS, success_msg
        else:
            # output should include '$name NOT terminated' but return all output for debugging
            return (FAILURE, "Action could not be completed. Something went wrong"
                             "output received: '%s'" % logging_output)
    else:
        return FAILURE, INSTANCE_NOT_FOUND_MSG % name


def terminate_instance(name):
    return _action_on_instance(name, 'terminate', force=True,
                               success_regex="%s terminated" % (name,),
                               success_msg="Instance '%s' has been terminated" % (name,))


def start_instance(name):
    return _action_on_instance(name, 'start', force=False,
                               success_regex="Starting %s" % (name,),
                               success_msg="Instance '%s' starting" % (name,))


def stop_instance(name):
    return _action_on_instance(name, 'stop', force=False,
                               success_regex="Stopping %s" % (name,),
                               success_msg="Instance '%s' stopping" % (name,))


def instance_status(name):
    instance, logging_output = _query_aws_instance(name)
    if instance:
        return SUCCESS, "Instance '%s': %s" % (name, str(instance))
    else:
        return FAILURE, INSTANCE_NOT_FOUND_MSG % name
