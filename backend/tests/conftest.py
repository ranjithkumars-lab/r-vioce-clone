import io
import wave
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config_registry import ConfigRegistry
from app.database.base import Base
import app.models  # Register SQLAlchemy entities
from app.database.session import get_db
from app import database
from app.main import app

# Test SQLite in-memory database using StaticPool to maintain single shared connection
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Override session.engine and get_db dependency for tests
    database.session.engine = test_engine
    database.session.init_db = lambda: Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def generate_sample_wav():
    """Utility fixture to generate a valid 3-second 24kHz mono PCM WAV in memory."""
    def _create_wav(duration_sec: float = 3.0, sample_rate: int = 24000) -> bytes:
        num_samples = int(duration_sec * sample_rate)
        raw_data = b"\x00\x00" * num_samples
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(raw_data)
        return buf.getvalue()
    return _create_wav
