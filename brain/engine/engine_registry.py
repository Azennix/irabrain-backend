from brain.engine.engine import Engine


class EngineRegistry:

    """
    Stores every engine inside IRABRAIN.
    """

    def __init__(self):

        self._engines = {}

    def register(

        self,

        name: str,

        engine: Engine

    ):

        self._engines[name] = engine

    def get(

        self,

        name: str

    ) -> Engine | None:

        return self._engines.get(name)

    def all(self):

        return self._engines