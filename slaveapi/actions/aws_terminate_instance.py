import logging

from ..clients import aws

log = logging.getLogger(__name__)


def aws_terminate_instance(name):
    """Attempts to terminate an aws instance


    :param name: hostname of slave

    :rtype: tuple of status, msg
    """
    # TODO update problem tracking bug if one exists
    return aws.terminate_instance(name)
