import logging

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class NoMigrateRouter:
    """
    A router to control database operations on models in the 'buildings' application.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read 'buildings' models go to a different database.
        """
        if model._meta.app_label == 'buildings':
            logger.info(f"Routing READ operation for {model._meta.model_name} to 'buildings' database.")
            return 'buildings'
        logger.info(f"Routing READ operation for {model._meta.model_name} to default database.")
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write 'buildings' models go to a different database.
        """
        if model._meta.app_label == 'buildings':
            logger.info(f"Routing WRITE operation for {model._meta.model_name} to 'buildings' database.")
            return 'buildings'
        logger.info(f"Routing WRITE operation for {model._meta.model_name} to default database.")
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Do not allow migrations for the 'buildings' app.
        """
        migrate_decision = 'ALLOW' if app_label != 'buildings' else 'PREVENT'
        logger.info(f"Migrate Decision: {migrate_decision}. DB: {db}, App: {app_label}, Model: {model_name}")
        return app_label != 'buildings'
