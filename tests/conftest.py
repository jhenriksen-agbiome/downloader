import io
import pytest


class FakeContent:
    def __init__(self, content):
        self._content = content

    async def read(self, size=0):
        content = self._content
        self._content = None
        return content


class FakeResponse:
    def __init__(self, content=b'Fake content', status=200):
        self.content = FakeContent(content)
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class FakeFile:
    def __init__(self):
        self._buffer = io.BytesIO()

    async def write(self, content):
        self._buffer.write(content)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def fake_file():
    return FakeFile()


@pytest.fixture
def fake_response():
    return FakeResponse


@pytest.fixture
def fake_client_session(mocker):
    fake_session = mocker.Mock()

    class FakeClientSession:
        _session = fake_session

        def __init__(self, loop):
            self._loop = loop

        async def __aenter__(self):
            return self._session

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    return FakeClientSession
