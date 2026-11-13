import inspect
import os
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace


os.environ.update(
    {
        "DATABASE_URL": "postgresql+asyncpg://localhost/test",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "BASE_URL": "http://localhost:8000/",
        "SECRET_KEY": "test-secret",
        "RABBITMQ_HOST": "localhost",
        "RABBITMQ_PORT": "5672",
        "RABBITMQ_USER": "user",
        "RABBITMQ_PASS": "pass",
        "RABBITMQ_EXCHANGE": "events",
        "RABBITMQ_QUEUE": "analytics",
        "RABBITMQ_ROUTING_KEY": "click",
    }
)

from backend.core.config import RabbitMqSetting
from backend.mappers.url_mapper import UrlMapper
from backend.messaging.events import QrCodeJobEvent
from backend.services.url_service import _ALIAS_RE
from backend.workers import qr_worker


class SettingsAndMappingTests(unittest.TestCase):
    def test_legacy_rabbitmq_environment_names_are_supported(self):
        settings = RabbitMqSetting()

        self.assertEqual(settings.ANALYTICS_QUEUE, "analytics")
        self.assertEqual(settings.ANALYTICS_ROUTING_KEY, "click")

    def test_url_details_accepts_qr_url_and_normalizes_base_url(self):
        url = SimpleNamespace(
            id=1,
            original_url="https://example.com",
            short_code="abc",
            clicks=0,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            expires_at=None,
        )

        details = UrlMapper.to_details(
            url,
            "http://localhost:8000/",
            qr_url="https://qr.example/abc.png",
        )

        self.assertEqual(details.short_url, "http://localhost:8000/abc")
        self.assertEqual(details.qr_url, "https://qr.example/abc.png")

    def test_aliases_cannot_exceed_database_column_length(self):
        self.assertIsNotNone(_ALIAS_RE.match("valid-url"))
        self.assertIsNone(_ALIAS_RE.match("eleven_chars"))


class QrWorkerTests(unittest.TestCase):
    def test_upload_job_calls_the_session_factory(self):
        source = inspect.getsource(qr_worker.QrJobWorker.process_job)

        self.assertIn("async with self.session_factory() as db:", source)

    def test_qr_jobs_default_to_upload(self):
        self.assertEqual(QrCodeJobEvent(short_code="abc").action, "upload")

