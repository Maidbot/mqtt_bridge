# -*- coding: utf-8 -*-
import ssl
import os
import paho.mqtt.client as mqtt
import rospy


def get_ssl_context(params):
    ssl_context = ssl.create_default_context()
    
    cafile = os.path.expanduser(params['ca_certs'])
    certfile = os.path.expanduser(params['certfile'])
    keyfile = os.path.expanduser(params['keyfile'])

    ssl_context.set_alpn_protocols(params['alpn_protocols'])
    ssl_context.load_verify_locations(cafile=cafile)
    ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    return ssl_context

def default_mqtt_client_factory(params):
    u""" MQTT Client factory

    :param dict param: configuration parameters
    :return mqtt.Client: MQTT Client
    """
    # create client
    client_params = params.get('client', {})
    client = mqtt.Client(**client_params)

    # configure tls
    tls_params = params.get('tls', {})
    if tls_params:
        client.tls_set_context(context=get_ssl_context(tls_params))

    # configure username and password
    account_params = params.get('account', {})
    if account_params:
        client.username_pw_set(**account_params)

    # configure message params
    message_params = params.get('message', {})
    if message_params:
        inflight = message_params.get('max_inflight_messages')
        if inflight is not None:
            client.max_inflight_messages_set(inflight)
        queue_size = message_params.get('max_queued_messages')
        if queue_size is not None:
            client.max_queued_messages_set(queue_size)
        retry = message_params.get('message_retry')
        if retry is not None:
            client.message_retry_set(retry)

    # configure userdata
    userdata = params.get('userdata', {})
    if userdata:
        client.user_data_set(userdata)

    # configure will params
    will_params = params.get('will', {})
    if will_params:
        client.will_set(**will_params)

    return client


def create_private_path_extractor(mqtt_private_path):
    def extractor(topic_path):
        if topic_path.startswith('~/'):
            return '{}/{}'.format(mqtt_private_path, topic_path[2:])
        return topic_path
    return extractor


__all__ = ['default_mqtt_client_factory', 'create_private_path_extractor']
