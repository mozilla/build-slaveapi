===
API
===

---------
Endpoints
---------
/results
========
.. autoclass:: slaveapi.web.results.Results
    :members: get

/slaves/:slave/actions/aws_create_instance
===============================================
.. autoclass:: slaveapi.web.slave.AWSCreateInstance

/slaves/:slave/actions/buildslave_last_activity
===============================================
.. autoclass:: slaveapi.web.slave.GetLastActivity

/slaves/:slave/actions/buildslave_uptime
===========================================
.. autoclass:: slaveapi.web.slave.GetUptime

/slaves/:slave/actions/disable
==========================================
.. autoclass:: slaveapi.web.slave.Disable

/slaves/:slave/actions/reboot
=============================
.. autoclass:: slaveapi.web.slave.Reboot

/slaves/:slave/actions/shutdown_buildslave
==========================================
.. autoclass:: slaveapi.web.slave.ShutdownBuildslave

/slaves/:slave/actions/start
===============================================
.. autoclass:: slaveapi.web.slave.AWSStartInstance

/slaves/:slave/actions/stop
===============================================
.. autoclass:: slaveapi.web.slave.AWSStopInstance

/slaves/:slave/actions/terminate
===============================================
.. autoclass:: slaveapi.web.slave.AWSTerminateInstance

-------
Helpers
-------
ActionView
==========
.. autoclass:: slaveapi.web.action_base.ActionView
    :members: get, post
