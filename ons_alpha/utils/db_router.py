from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import DEFAULT_DB_ALIAS, router, transaction


class ReadReplicaRouter:  # pylint: disable=unused-argument
    """
    A database router which routes reads to the read replica.
    """

    REPLICA_DB_ALIAS = "read_replica"

    REPLICA_DBS = {REPLICA_DB_ALIAS, DEFAULT_DB_ALIAS}

    def __init__(self):
        if self.REPLICA_DB_ALIAS not in settings.DATABASES:
            raise ImproperlyConfigured("Read replica is not configured.")

    def db_for_read(self, model, **hints):
        """
        Which database should be used for read queries?

        If the write database is in a (uncommitted) transaction,
        a subsequent SELECT (or other read query) may return inconsistent data.
        In this case, use the write connection for reads, with the aim of
        improved consistency.
        """

        write_db = router.db_for_write(model, **hints)

        if not transaction.get_autocommit(using=write_db):
            # In a transaction, use the write database
            return write_db

        return self.REPLICA_DB_ALIAS

    def db_for_write(self, model, **hints):
        """
        Which database should be used for write queries?

        This should always be the "default" database, since the replica
        doesn't allow writes.
        """
        return DEFAULT_DB_ALIAS

    def allow_relation(self, obj1, obj2, **hints):
        # If both instances are in the same database (or its replica), allow relations
        if obj1._state.db in self.REPLICA_DBS and obj2._state.db in self.REPLICA_DBS:
            return True

        # No preference
        return None

    def allow_migrate(self, db, app_label, model_name, **hints):
        # Don't allow migrations to run against the replica (they would fail anyway)
        if db == self.REPLICA_DB_ALIAS:
            return False

        # No preference
        return None
