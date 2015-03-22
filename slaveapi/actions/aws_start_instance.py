import logging

from ..clients import aws

log = logging.getLogger(__name__)


def aws_start_instance(name):
    """Attempts to start an aws instance


    :param name: hostname of slave

    :rtype: tuple of status, msg
    """
    return aws.start_instance(name)
