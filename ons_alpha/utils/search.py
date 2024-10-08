from wagtail.search.backends.database.postgres.postgres import PostgresSearchBackend


class ONSPostgresSearchBackend(PostgresSearchBackend):
    """
    A custom search backend which ensures the index uses the correct database backend.
    """

    def get_index_for_model(self, model, db_alias=None):
        # Always defer to DB router for search backend
        return super().get_index_for_model(model, None)
