from ext_tnt.apps import ExtTntConfig
from django.db import models


class ext_tnt_db_router(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'ext_tnt':
            return 'ext_tnt'
        elif model._meta.app_label == 'hub_gtd':
            return 'hub_gtd'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'ext_tnt':
            return 'ext_tnt'
        elif model._meta.app_label == 'hub_gtd':
            return 'hub_gtd'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'ext_tnt':
            return db == 'ext_tnt'
        elif app_label == 'hub_gtd':
            return db == 'hub_gtd'
        else:
            return db == 'default'
