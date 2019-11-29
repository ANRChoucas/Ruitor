class Modifier:
    def __init__(self, context):
        self.context = context

    def modifing(self, *args, **kwargs):
        return self._modifing(*args, **kwargs)

    def _changeVal(self, params, *args, **kwars):
        raise NotImplementedError


class Near(Modifier):
    def __init__(self, context):
        super().__init__(context)


class Not(Modifier):
    def __init__(self, context):
        super().__init__(context)

    def _modifing(self, values):
        return 1 - values

