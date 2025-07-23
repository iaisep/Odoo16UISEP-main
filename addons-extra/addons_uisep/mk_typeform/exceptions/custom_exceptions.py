# -*- coding: utf-8 -*-


class Error(Exception):
    """
        Clase base de control de excepciones
    """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class InvalidJson(Error):
    """
        Excepcion que controla el contenido del JSON
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

