from flask import make_response
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

    @cached_property
    def transit(self):
        transit_protocol = self.MIME_TYPE_MAPPING.get(self.content_type)
        if transit_protocol:
            reader = Reader(transit_protocol)
            # TODO: Need to read custom handlers from somewhere.
            #       and add them to the reader.
            #
            #       Possibly the application configuration?
            return reader.read(self.stream)


def make_request_class(base_class):
    '''
    A utility function for constructing a TransitRequest class from an existing
    base.
    '''

    class TransitRequest(base_class, TransitRequestMixin):
        pass

    return TransitRequest


def init_transit(app):
    '''
    Initialises a flask application object with Flask-Transit support

    :param app:     The flask application object to initialise.
    '''
    # TODO: Think we need to accept read/write handlers as arguments here.
    #       These can then be passed to make_request_class/stored on the
    #       application object to be used by transition.
    app.request_class = make_request_class(app.request_class)


def _to_transit(in_data, protocol='json'):
    io = StringIO()
    writer = Writer(io, protocol)
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
    response = make_response(_to_transit(data, protocol))
    response.headers['content-type'] = 'application/transit+' + protocol
    return response
