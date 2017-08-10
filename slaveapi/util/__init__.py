# general util helper methods

import re
import sys
import traceback


def normalize_truthiness(target_value):
    true_values = ['y', 'yes', '1', 'true']
    false_values = ['n', 'no', '0', 'false']

    # let's see if target_value is an accepted value first
    if not value_in_values(target_value, true_values + false_values):
        raise ValueError(
            "Unsupported value `%s` for truthiness. Accepted values: "
            "truthy - %s, falsy - %s" % (target_value, true_values, false_values)
        )

    if value_in_values(target_value, true_values):
        # target_value is a valid str and represents true
        return True
    else:
        # target_value is a valid str and represents false
        return False


def value_in_values(target_value, valid_values, case_sensitive=False):
    if not case_sensitive:
        # lower case all the things
        target_value = str(target_value).lower()
        valid_values = [str(valid_value).lower() for valid_value in valid_values]

    if target_value in valid_values:
        return True
    else:
        return False


def logException(log_fn, message=None):
    """ A helper to dump exceptions with log filtered prefix
    Useful for when you need to grep a log"""

    tb_type, tb_value, tb_traceback = sys.exc_info()
    if message is None:
        message = ""
    else:
        message = "%s\n" % message
    for s in traceback.format_exception(tb_type, tb_value, tb_traceback):
        message += "%s\n" % s
    for line in message.split("\n"):
        # avoid logging secrets when hitting exceptions
        if "CalledProcessError: Command" in line:
            cmd = []
            p = re.findall(r'(?<=\[)(.*?)(?=\])', line)
            p = p[0].split(", ")
            for i in range(0, len(p)):
                cmd.append(str(p[i]))

            if cmd[0] == "'ipmitool'":
                for i in range(1, len(cmd)):
                    if cmd[i] == "'-P'":
                        line = line.replace(cmd[i+1], "***")
            if cmd[0] == "'snmpset'":
                for i in range(1, len(cmd)):
                    if cmd[i] == "'-c'":
                        line = line.replace(cmd[i+1], "***")
        log_fn(line)
