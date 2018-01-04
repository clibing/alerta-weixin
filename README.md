Weixin Plugin
=====================

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/clibing/alerta-weixin.git#subdirectory=plugins/weixin

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `weixin` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['alerta_weixin']
CORP_ID = 'not empty'
CORP_SECRET = 'not empty'
AGENT_ID = 'agent id'
PARTY_ID = ''
USER_ID = '' # user1|user2  or @all
TAG_ID = 11
```

Note: By default the AMQP plugin is configured to use MongoDB as the
AMQP transport so it is not necessary to install RabbitMQ or some other
messaging backbone to make use of this plugin.

**RabbitMQ Example**

```python
PLUGINS = ['reject','alerta_weixin']
CORP_ID = 'not empty'
CORP_SECRET = 'not empty'
AGENT_ID = 'agent id'
PARTY_ID = ''
USER_ID = '' # user1|user2  or @all
TAG_ID = 11
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries similar to below:

```
--------------------------------------------------------------------------------
```

References
----------

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.
