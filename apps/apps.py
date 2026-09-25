from django.apps import AppConfig


class AppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'

    def ready(self):
        # Blog: kufuta cache + IndexNow makala zikibadilika
        from . import blog_signals  # noqa: F401
