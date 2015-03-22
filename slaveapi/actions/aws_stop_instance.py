import logging

from ..clients import aws

log = logging.getLogger(__name__)


def aws_stop_instance(name):
    """Attempts to stop an aws instance


    :param name: hostname of slave

    :rtype: tuple of status, msg
    """
    return aws.stop_instance(name)
