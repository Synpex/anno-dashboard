class BuildingsRouter:
    """
    A router to control all database operations on models in the buildings application.
    """

    route_app_labels = {'buildings'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read buildings models go to buildings db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'buildings'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write buildings models go to buildings db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'buildings'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the buildings app is involved.
        """
        if obj1._meta.app_label in self.route_app_labels or \
           obj2._meta.app_label in self.route_app_labels:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the buildings app only appears in the 'buildings' database.
        """
        if app_label in self.route_app_labels:
            return db == 'buildings'
        return None
