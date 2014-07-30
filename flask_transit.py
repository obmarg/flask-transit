import operator
from functools import partial
from flask import make_response, current_app
from werkzeug.utils import cached_property
from transit.reader import Reader
from transit.writer import Writer
from StringIO import StringIO

__version__ = "0.1"
__all__ = ['init_transit', 'transition']


class TransitRequestMixin(object):
    '''
    A mixin for flask requests that adds a transit property for decoding
    incoming Transit data.
    '''
    MIME_TYPE_MAPPING = {'application/transit+json': 'json',
                         'application/transit+msgpack': 'msgpack'}

    # READ_HANDLERS should be set to a dict of {key: reader} pairs that will be
    # passed to the Transit reader. Usually these will be setup by the
    # init_transit function.
    READ_HANDLERS = {}

    @cached_property
    def transit(self):
        transit_protocol = self.MIME_TYPE_MAPPING.get(self.content_type)
        if transit_protocol:
            reader = Reader(transit_protocol)

            for read_handler in self.READ_HANDLERS.values():
                # TODO: Documentation should mention that tag() is required.
                reader.register(read_handler.tag(''), read_handler)

            return reader.read(self.stream)


def make_request_class(base_class, read_handlers=None):
    '''
    A utility function for constructing a TransitRequest class from an existing
    base.
    '''
    class TransitRequest(base_class, TransitRequestMixin):
        READ_HANDLERS = read_handlers or {}
        BASE_REQUEST = base_class

    return TransitRequest


def _split_handlers(custom_handlers):
    '''
    Splits a custom_handlers dict into readers and writers.

    :param custom_handlers:     A dict of custom handlers as passed to
                                init_transit.

    :returns:       A tuple (write_handlers_dict, read_handers_dict)
    '''
    write_handlers = {handled_type: handler
                      for handled_type, handler in custom_handlers.items()
                      if hasattr(handler, 'rep')}

    read_handlers = {handled_type: handler
                     for handled_type, handler in custom_handlers.items()
                     if hasattr(handler, 'from_rep')}

    return (write_handlers, read_handlers)


def init_transit(app, custom_handlers=None):
    '''
    Initialises a flask application object with Flask-Transit support

    :param app:             The flask application object to initialise.
    :param custom_handlers: Optional extra read/write handlers.
                            Should be a dictionary of {key: handler}.
                            Where each handler implements the transit-python
                            read_handler and/or write_handler interface.
    '''
    custom_handlers = custom_handlers or {}
    write_handlers, read_handlers = _split_handlers(custom_handlers)

    app.request_class = make_request_class(app.request_class, read_handlers)
    app._transit_write_handlers = write_handlers


def _to_transit(in_data, protocol='json', write_handlers=None):
    write_handlers = write_handlers or {}

    io = StringIO()
    writer = Writer(io, protocol)

    for key, write_handler in write_handlers.items():
        writer.register(key, write_handler)

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


_concat = partial(reduce, operator.concat)


def _merge_dicts(*dicts):
    ''' Merges some dictionaries '''
    return dict(_concat(d.items() for d in dicts))


def register_handlers(app, custom_handlers):
    '''
    Registers additional transit read/write handlers on an application.

    The application must have already been initialised with init_transit.

    :param app:             The application to register the handlers on.
    :param custom_handlers: Extra read/write handlers.
                            Should be a dictionary of {key: handler}.
                            Where each handler implements the transit-python
                            read_handler and/or write_handler interface.
    '''
    write_handlers, read_handlers = _split_handlers(custom_handlers)

    write_handlers = _merge_dicts(app._transit_write_handlers, write_handlers)

    if read_handlers:
        read_handlers = _merge_dicts(read_handlers,
                                     app.request_class.READ_HANDLERS)

        app.request_class = make_request_class(app.request_class.BASE_REQUEST,
                                               read_handlers)

    app._transit_write_handlers = write_handlers
