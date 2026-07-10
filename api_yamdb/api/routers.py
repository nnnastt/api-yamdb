from rest_framework.routers import SimpleRouter


class NestedRouter(SimpleRouter):
    """
    Роутер для вложенных ресурсов.
    """

    def __init__(self, parent_prefix=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_prefix = parent_prefix

    def register(self, prefix, view, basename=None, parent_prefix=None):
        if parent_prefix:
            prefix = f'{parent_prefix}/{prefix}'
        return super().register(prefix, view, basename)
