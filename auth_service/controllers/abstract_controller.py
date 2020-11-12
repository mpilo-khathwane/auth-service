import abc

from auth_service.clients import Clients
from auth_service.configuration import Config


class AbstractController(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.clients = Clients()
        self.config = Config()
