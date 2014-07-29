from flask import make_response, current_app
from werkzeug.utils import cached_property
from transit.reader import Reader
from transit.writer import Writer
from StringIO import StringIO

__all__ = ['init_transit', 'transition']


class TransitRequestMixin(object):
    '''
    A mixin for flask requests that adds a transit property for decoding
    incoming Transit data.
    '''
    MIME_TYPE_MAPPING = {'application/transit+json': 'json',
                         'application/transit+msgpack': 'msgpack'}

    # READ_HANDLERS should be set to a tuple of (key_or_tag, f_val) pairs that
    # will be passed to the Transit reader & writer instances. Usually these
    # will be setup by the init_transit function.
    READ_HANDLERS = []

    @cached_property
    def transit(self):
        transit_protocol = self.MIME_TYPE_MAPPING.get(self.content_type)
        if transit_protocol:
            reader = Reader(transit_protocol)

            for key_or_tag, f_val in self.READ_HANDLERS:
                reader.register(key_or_tag, f_val)

            return reader.read(self.stream)


def make_request_class(base_class, read_handlers=None):
    '''
    A utility function for constructing a TransitRequest class from an existing
    base.
    '''
    class TransitRequest(base_class, TransitRequestMixin):
        READ_HANDLERS = read_handlers or []
        pass

    return TransitRequest


def init_transit(app, read_handlers=None, write_handlers=None):
    '''
    Initialises a flask application object with Flask-Transit support

    :param app:             The flask application object to initialise.
    :param read_handlers:   Optional extra read handlers.  Should be a
                            sequence of (key_or_tag, f_val) pairs.
                            See transit-python reader for more details.
    :param write_handlers:  Optional extra write handlers.  Should be a
                            sequence of (key_or_tag, f_val) pairs.
                            See transit-python writer for more details.
    '''
    app.request_class = make_request_class(app.request_class, read_handlers)
    app._transit_write_handlers = write_handlers


def _to_transit(in_data, protocol='json', write_handlers=None):
    io = StringIO()
    writer = Writer(io, protocol)

    for key_or_tag, f_val in (write_handlers or []):
        writer.register(key_or_tag, f_val)

    writer.write(in_data)
    return io.getvalue()


def transition(data, protocol='json'):
    '''
    Converts data into a Transit response.

    Equivalent to jsonify for transit.

    :param data:        The data to convert
    :param protocol:    The protocol to use.  Defaults to json.
    '''
    # TODO: thinking flask configuration should determine which
    #       protocol to use for a default.
    write_handlers = current_app._transit_write_handlers
    response = make_response(_to_transit(data, protocol, write_handlers))
    response.headers['content-type'] = 'application/transit+' + protocol
    return response
