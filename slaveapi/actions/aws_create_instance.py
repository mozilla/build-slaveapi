import logging
import time

from ..clients import inventory
from ..clients import aws
from .results import SUCCESS, FAILURE
from ..util import value_in_values

log = logging.getLogger(__name__)


def aws_create_instance(name, email, bug, instance_type, arch=None):
    """Attempts to create an aws instance for a given owner


    :param email: the full ldap username of owner requesting instance
    :type email: str
    :param bug: the number of the bug that needs the instance
    :type bug: str
    :param instance_type: accepted values are 'build' and 'test'
    :type instance_type: str

    :rtype: tuple
    """
    # TODO allow for region us west as well
    # TODO allow for more platforms as more platforms get aws'ified

    # web end point will verify these validations but we should still double
    # check in case this is called from another location, e.g. another action
    assert value_in_values(instance_type, ['build', 'test'])
    assert not (arch == 32 and instance_type == 'build')

    if not arch:
        arch = 64

    # strip out the nickname of the loanee from their email
    nick = email.split('@')[0]

    if instance_type == 'build':
        if name == 'default':
            # since this slave does not exist yet, this allows for a default to be created
            name = 'dev-linux64-ec2-%s' % nick
        fqdn = '%s.dev.releng.use1.mozilla.com' % name
        aws_config = 'dev-linux%s' % arch
        data = 'us-east-1.instance_data_dev.json'
    else:  # instance_type == 'test'
        if name == 'default':
            # since this slave does not exist yet, this allows for a default to be created
            name = 'tst-linux%s-ec2-%s' % (arch, nick)
        fqdn = '%s.test.releng.use1.mozilla.com' % name
        aws_config = 'tst-linux%s' % arch
        data = 'us-east-1.instance_data_tests.json'

    status_msgs = ["Creating aws instance: `{0}`\n".format(fqdn)]
    return_code = SUCCESS  # innocent until proven guilty!


    status_msgs.append("generating free ip...")
    ip = aws.get_free_ip(aws_config)

    if ip:
        status_msgs.append("Success\ncreating dns records...")

        record_desc = "bug {num}: loaner for {nick}".format(num=bug, nick=nick)
        return_code, return_msg = inventory.create_dns(ip, fqdn, record_desc)

        if return_code == SUCCESS:
            status_msgs.append("Success\nwaiting for DNS to propagate...")
            log.info("host: {0} - waiting for DNS to propagate".format(name))
            # TODO - rather than waiting 20 min, maybe we can poll
            # inventory.get_system(name) and if that yields a result, we can say
            # it's propagated?
            time.sleep(20 * 60)
            status_msgs.append("Success\ncreating and assimilating aws instance...")
            return_code, instance = aws.create_aws_instance(fqdn, name, email, bug, aws_config,
                                                            data, ip)
            if return_code == SUCCESS:
                return SUCCESS, instance  # just return instance info

            status_msgs.append(instance)
        else:
            log.warning(return_msg)
            status_msgs.append(return_msg)
    else:
        log.warning("host: {0} - failed to generate a free ip".format(name))
        status_msgs.append("failed to generate a free ip")

    return return_code, "\n".join(status_msgs)
