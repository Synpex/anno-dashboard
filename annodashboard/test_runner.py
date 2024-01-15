# test_runner.py

"""from django.test.runner import DiscoverRunner
from django.apps import apps

class DisableMigrations(DiscoverRunner):
    def setup_databases(self, **kwargs):
        # No-op to prevent database creation
        pass

    def teardown_databases(self, old_config, **kwargs):
        # No-op to prevent database destruction
        pass"""