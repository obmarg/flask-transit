from werkzeug.utils import cached_property
from transit.reader import Reader


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
    app.request_class = make_request_class(app.request_class)
