from ..config import S3Settings, get_s3_settings


def test_import_config():
    assert isinstance(get_s3_settings, S3Settings)
