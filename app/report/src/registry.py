from json import dumps


class Registry(object):

    _registry = {}

    def __repr__(self):
        return dumps(self._registry, indent=4, default=str)

    def __iter__(self):
        for value in self._registry.values():
            yield value
