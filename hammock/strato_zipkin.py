import requests
import logging
from py_zipkin.zipkin import zipkin_span
from py_zipkin.zipkin import ZipkinAttrs
from py_zipkin.thread_local import get_zipkin_attrs
from py_zipkin.util import generate_random_64bit_string


MY_SERVICE_NAME = '(service_name_not_set)'  # Change this at the beginning of the service.


def http_transport(encoded_span):
    # The collector expects a thrift-encoded list of spans. Instead of
    # decoding and re-encoding the already thrift-encoded message, we can just
    # add header bytes that specify that what follows is a list of length 1.
    try:
        body = '\x0c\x00\x00\x00\x01' + encoded_span
        requests.post(
            'http://zipkin.service.strato:9411/api/v1/spans',
            data=body,
            headers={'Content-Type': 'application/x-thrift'},
        )
    except:
        try:
            logging.debug("Sending to zipkin transport failed.")
        except:
            pass


def wrap_zipkin(span_name, service_name=None, root_sample_rate=100.0):
    parent_attrs = get_zipkin_attrs()
    if parent_attrs is None:
        # I am the root span
        sample_rate = root_sample_rate
        my_attrs = None
    else:
        sample_rate = None
        my_attrs = ZipkinAttrs(
            trace_id=parent_attrs.trace_id,
            span_id=generate_random_64bit_string(),
            parent_span_id=parent_attrs.span_id,
            flags=parent_attrs.flags,
            is_sampled=parent_attrs.is_sampled)

    return zipkin_span(
        service_name=service_name or MY_SERVICE_NAME,
        span_name=span_name,
        transport_handler=http_transport,
        sample_rate=sample_rate,
        zipkin_attrs=my_attrs)
