"""Cloud configuration."""


class Config(object):
    """Cloud configuration helper."""
    __connection_obj = None
    __connection_cls = None
    __connection_fn = None

    @classmethod
    def from_settings(cls):
        """Create configuration from Django settings or environment."""
        from cloud_browser.app_settings import settings
        from django.core.exceptions import ImproperlyConfigured

        conn_cls = conn_fn = None
        if conn_cls is None:
            # Try Rackspace
            account = settings.CLOUD_BROWSER_RACKSPACE_ACCOUNT
            secret_key = settings.CLOUD_BROWSER_RACKSPACE_SECRET_KEY
            servicenet = settings.CLOUD_BROWSER_RACKSPACE_SERVICENET
            if (account and secret_key):
                from cloud_browser.cloud.rackspace import RackspaceConnection
                conn_cls = RackspaceConnection
                conn_fn = lambda: RackspaceConnection(
                    account, secret_key, servicenet)

        if conn_cls is None:
            # Mock filesystem
            root = settings.CLOUD_BROWSER_FILESYSTEM_ROOT
            if root is not None:
                from cloud_browser.cloud.fs import FilesystemConnection
                conn_cls = FilesystemConnection
                conn_fn = lambda: FilesystemConnection(root)

        if conn_cls is None:
            raise ImproperlyConfigured("No suitable credentials found.")

        # Adjust connection function.
        conn_fn = staticmethod(conn_fn)

        # Directly cache attributes.
        cls.__connection_cls = conn_cls
        cls.__connection_fn = conn_fn

        return conn_cls, conn_fn

    @classmethod
    def get_connection_cls(cls):
        """Get connection class."""
        if cls.__connection_cls is None:
            cls.__connection_cls, _ = cls.from_settings()
        return cls.__connection_cls

    @classmethod
    def get_connection(cls):
        """Get singleton object."""
        if cls.__connection_obj is None:
            if cls.__connection_fn is None:
                _, cls.__connection_fn = cls.from_settings()
            cls.__connection_obj = cls.__connection_fn()
        return cls.__connection_obj
