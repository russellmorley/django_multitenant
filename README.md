#django_multitenant

**django_multitenant** is a set of apps for adding multitenant functionality to Django.

##Features

* A library for adding multitenant functionality to Django Channels.
    * Provides both decorators for funcion-based consumers and a corresponding generic base class generic that:
        * sets the sessions and user on the message.
        * creates a channel group for each user.
        * creates a channel group for each org and assigns users to their appropriate channel group.
        * provides models for both org subgroups as well as public groups to which users can be assigned. Creates corresponding channel groups for all and manages assigment of users to their appropriate channel groups during connection and removes users on disconnect.
        * Optional functionality for disconnecting channels if a http user is logged out.

##Installing

You can install django_multitenant with the following command:

    $ pip install -e git+https://github.com/russellmorley/django_multitenant#egg=django_multitenant

or by adding the following line to your requirement.txt:

    --e git+https://github.com/russellmorley/django_multitenant#django_multitenant

Check the [CHANGES](https://github.com/russellmorley/django_multitenant/blob/master/CHANGES)
before installing.

##Getting Started

To run the example:

    socket = new WebSocket("ws://localhost:8000/genericmultitenantsocket/'); 
    socket.onmessage = function(e) {
        alert(e.data); 
    } 
    socket.onopen = function() {
        socket.send(JSON.stringify({stream: "test", payload: {op:'do_stuff', for_org: 1, boo:'baa'}})); 
    } 
    if (socket.readyState == WebSocket.OPEN) socket.onopen();


##Documentation

###django_multitentant_sockets app

####Function-based consumers

* When wrapping a connect function, ``decorators.connect`` accepts connections if the django user is_authenticated() and adds the channel to the user's channel group, user's organization's channel group, all channel groups corresponding to the ``model.PublicGroup``s the user is a member of, and all channel groups corresponding to the ``model.OrgGroup``s the user is a member of.
* Similarly, when wrapping a disconnect function ``decorators.disconnect`` removes the user from all channel groups and disconnects the socket.

Example:


####Generic consumers

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






Testing
------------

Run tests by first setting the database ROLE and PASSWORD in tests/test_settings.py then executing the following command:

    $./runtests.py

Contributing
------------

Bug reports, bug fixes, and new features are always welcome. Please raise issues on the
`django_multitenant project site <https://github.com/russellmorley/django_multitenant>`_, and submit
pull requests for any new code.

    
More information
----------------

The django_rest_cryptingfields project was developed by Russell Morley. You can get the code
from the [django_multitenant project site](https://github.com/russellmorley/django_multitenant).
    
[Compass Point, Inc. Website](http://www.compass-point.net/)
