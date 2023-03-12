from ext_tnt.apps import ExtTntConfig
from django.db import models


class ext_tnt_db_router(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'ext_tnt':
            return 'ext_tnt'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'ext_tnt':
            return 'ext_tnt'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'ext_tnt':
            return db == 'ext_tnt'
        else:
            return db == 'default'
