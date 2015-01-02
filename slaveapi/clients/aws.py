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


def terminate_instance(name):
    instance, logging_output = _query_aws_instance(name)
    if instance:
        std_output, logging_output = _manage_instance(name, 'terminate', force=True)
        # we rely on logging module output to determine if instance has been terminated
        terminated = re.search("%s terminated" % name, logging_output)
        if terminated:
            return SUCCESS, "Instance '%s' has been terminated" % (name,)
        else:
            # output should include '$name NOT terminated' but return all output for debugging
            return (FAILURE, "Instance '%s' could not be terminated. "
                             "output received: '%s'" % (name, logging_output))
    else:
        return FAILURE, INSTANCE_NOT_FOUND_MSG % name
