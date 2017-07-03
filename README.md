# django_multitenant

**django_multitenant** is a set of apps for adding multitenant functionality to Django.

## Features

* A library for adding multitenant functionality to Django Channels.
    * Provides both decorators for funcion-based consumers and a corresponding generic base class generic that:
        * validates the user has been authenticated for both connect and all received messages.
        * authorizes received message based on the operation requested.
        * sets the sessions and user on the message.
        * creates a channel group for each user.
        * creates a channel group for each org and assigns users to their appropriate channel group.
        * provides models for both org subgroups as well as public groups to which users can be assigned. Creates corresponding channel groups for all and manages assigment of users to their appropriate channel groups during connection and removes users on disconnect.
        * Optional functionality for disconnecting channels if a http user is logged out.
     * Both function-based and generic class support multiplexing different applications (streams) across a single socket.

## Installing

You can install django_multitenant with the following command:

    $ pip install -e git+https://github.com/russellmorley/django_multitenant#egg=django_multitenant

or by adding the following line to your requirement.txt:

    --e git+https://github.com/russellmorley/django_multitenant#django_multitenant

Channels is dependent on:

```
django>=1.8.18
channels>=1.1.3
djangorestframework>=3.4.1
```

Check the [CHANGES](https://github.com/russellmorley/django_multitenant/blob/master/CHANGES)
before installing.

## Getting Started

Start the channels server:

```
python manage.py migrage
python manage.py runserver 0.0.0.0:8000
```

To send a message to application `test` to `do_stuff(boo=bah)` for org 1, receive a message back, and show it in an alert:

```javascript
socket = new WebSocket("ws://localhost:8000/genericmultitenantsocket/"); 
socket.onmessage = function(e) {
    alert(e.data); 
} 
socket.onopen = function() {
    socket.send(JSON.stringify({stream: "test", payload: {op:'do_stuff', for_org: 1, boo:'baa'}})); 
} 
if (socket.readyState == WebSocket.OPEN) socket.onopen();
```

## Documentation

### django_multitentant_sockets app

#### Message text format

```python
{
   #identifies the application. messages over a single socket are routed to appropriate consumers based on stream. See settings for both a consumer and genericconsumer below.
   stream: "test",   

   payload: {
         op:'do_stuff',  #denotes the operation the client is requesting of server. Required for authorization 
         for_org: 1,     #denotes the org the operation is to be performed on. This should typically be the same org as the calling user's
         boo:'baa'       #the 'parameters' of the op added as additional key/values of data
   }
}
```

#### Function-based consumers

* When wrapping a connect function, ``decorators.connect`` accepts connections if the django user is_authenticated() and adds the channel to the user's channel group, user's organization's channel group, all channel groups corresponding to the ``model.PublicGroup``s the user is a member of, and all channel groups corresponding to the ``model.OrgGroup``s the user is a member of.
* Similarly, when wrapping a disconnect function ``decorators.disconnect`` removes the user from all channel groups and disconnects the socket.
* Consumer provided automatically wraps functions with decorators as needed and delegates implementation to functions in a separate implementation module.

Example:

For setting up a (multiplexed) application to have messages sent to application (stream) `test` directed to consumer `testsite/consumers.py`:

Settings:

```python
MULTITENANT_SOCKETS_CONSUMERS = [
  {
    "stream": "test",
    "consumer": "testsite.consumers",
    "consumer_key_is_consumer_route_prefix": False,
  },
]
```
   
Implementation Module (testsite/consumers.py):

```python
from django_multitenant_sockets.decorators import has_permission_and_org
import logging
import json

logger = logging.getLogger(__name__)

def connect(message):
  logger.debug('connect')

def disconnect(message):
  logger.debug('disconnect')

@disconnect_if_http_logged_out()
@has_permission_and_org({'do_stuff': 'do_stuff_permission'})
def receive(message):
  logger.debug('receive: {}'.format(vars(message)))
  message.reply_channel.send({'text': message.content['text']})
```

#### Generic consumers

Generic consumers are derived from ``generic.consumers.MultitenantJsonWebsocketConsumer`` and:

* Automatically wraps appropriate underlying methods with ``channels.auth.channel_and_http_session_user_from_http``, ``decorators.connect``, ``decorators.disconnect``, and ``channels.auth.channel_session_user``. As a result connections are successful only if message.user is_authenticated(). When successful:
    * Http per-user session is assigned to ``message.http_session``.
    * Per-channel session is assigned to ``message.channel_session``.
    * ``message.user`` contains the django user.
    * The channel is added to the user's channel group, user's organization's channel group, all channel groups corresponding to the ``model.PublicGroup``s the user is a member of, and all channel groups corresponding to the ``model.OrgGroup``s the user is a member of.

Derivatives can override the following:

* ``generic.consumers.MultitenantJsonWebsocketConsumer.disconnect_if_http_logged_out``, which if not explicitly set defaults to True causing all the user's channels to be disconnected and the message discarded when a message is received and  ``message.http_session['_auth_user_id']`` isn't set (which happens when the django user is logged out).
* ``connect_impl(self, message, multiplexer, **kwargs)`` (optional)
* ``disconnect_impl(self, message, multiplexer, **kwargs)`` (optional)
* ``receive_impl(self, user, op, for_org, data_dict, multiplexer, **kwargs)``, where 
    * ``user`` is the sending user, 
    * ``op`` is the operation requested, 
    * ``for_org`` is the organization the message is for, 
    * ``data_dict`` is a dictionary of data representing the op's parameters, and 
    * ``multiplexer(op, data_dict)`` is for sending a message with a client op and corresponding data_dict. Note this ``op`` and ``data_dict`` would likely be different than the one received and have meaning to the client code.
        
Example

For setting up a (multiplexed) application to have messages sent to application (stream) `test` directed to consumer `testsite/genericconsumers.py`:

Settings:

```python
MULTITENANT_SOCKETS_GENERICCONSUMERS = {
  #stream_name: test
  'test': 'testsite.genericconsumers.TestMultitenantJsonWebsocketConsumer',
  #"other": AnotherConsumer,
}
```

Implementation module (testsite/genericconsumers.py):

```python
from django_multitenant_sockets.generic.consumers import MultitenantJsonWebsocketConsumer
from django_multitenant_sockets.decorators import has_permission_and_org

import logging
logger = logging.getLogger(__name__)

class TestMultitenantJsonWebsocketConsumer(MultitenantJsonWebsocketConsumer):
 def connect_impl(self, message, multiplexer, **kwargs):
   logger.debug('connect_impl')

 def disconnect_impl(self, message, multiplexer, **kwargs):
   logger.debug('disconnect_impl')

 @has_permission_and_org({'do_stuff': 'do_stuff_permission'})
 def receive_impl(self, user, op, for_org, data_dict, multiplexer, **kwargs):
   logger.debug('receive: user_id: {}, op:{}, for_org:{}, data_dict:{}'.format(user.pk, op, for_org, data_dict))
   # Simple echo
   multiplexer.send(op, data_dict)
  ```
   
#### Authorization

Receive methods should authorize the `ops` of all incoming messages from clients by adding the following decorator, which takes a dictionary of all the operations the receive method can handle mapped to permission_name values:

```python
@has_permission_and_org({'do_stuff': 'do_stuff_permission'})
def receive_impl(self, user, op, for_org, data_dict, multiplexer, **kwargs):
   pass
```

This decorator authorizes each op by confirming the calling user has been assigned the corresponding permission_name using a permissions adapter set as follows. If the `op` is not in the dict the call is not authorized.

Settings:
```
MULTITENANT_SOCKETS_PERMISSIONS_ADAPTER` = [the name of the class that contains a method `has_permission(user, permission)` and `has_role(user, role)`]
```

#### Other settings

* `MULTITENANT_SOCKETS_USER_ORG_FK_ATTR_NAME` is the name of the organization foreign key attribute on users. This defaults to ``org`` if not set.

## Testing


Run tests by first setting the database ROLE and PASSWORD in tests/test_settings.py then executing the following command:

    $./runtests.py

## Contributing

Bug reports, bug fixes, and new features are always welcome. Please raise issues on the
[django_multitenant project site](https://github.com/russellmorley/django_multitenant), and submit
pull requests for any new code.

    
## More information

The django_rest_cryptingfields project was developed by Russell Morley. You can get the code
from the [django_multitenant project site](https://github.com/russellmorley/django_multitenant).
    
[Compass Point, Inc. Website](http://www.compass-point.net/)
