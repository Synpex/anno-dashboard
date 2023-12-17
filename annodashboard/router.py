class NoMigrateRouter:
    """
    A router to control database operations on models in the 'buildings' application.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read 'buildings' models go to a different database.
        """
        if model._meta.app_label == 'buildings':
            return 'buildings'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write 'buildings' models go to a different database.
        """
        if model._meta.app_label == 'buildings':
            return 'buildings'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Do not allow migrations for the 'buildings' app.
        """
        if app_label == 'buildings':
            return False
        return True
