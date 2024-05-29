from unittest import TestCase

import pytest
from unittest.mock import MagicMock, patch
from aiohttp import web
from database import CustomBase
from handlers import (
    AbstractHandler,
    CreateHandler,
    ReadHandler,
    UpdateHandler,
    PatchHandler,
    DeleteHandler,
    RetrieveAllHandler,
    OptionsHandler,
    HeadHandler,
)


class TestInitializationAndSetup(TestCase):
    @pytest.fixture
    def mock_model(self):
        return MagicMock(spec=CustomBase)

    @pytest.fixture
    def mock_request(self):
        return MagicMock(spec=web.Request)

    def test_abstract_handler_initialization(self, mock_model):
        abstract_handler = AbstractHandler(model=mock_model)
        assert abstract_handler.model == mock_model

    @patch("database.SessionLocal")
    async def test_abstract_handler_call(self, mock_session_local, mock_request):
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_handler = MagicMock(spec=AbstractHandler)

        abstract_handler = AbstractHandler()
        abstract_handler.handle = mock_handler.handle
        response = await abstract_handler(mock_request)

        mock_session_local.assert_called_once()
        assert mock_session.close.called
        assert response == mock_handler.handle.return_value

    def test_create_handler_initialization(self, mock_model):
        create_handler = CreateHandler(model=mock_model)
        assert create_handler.model == mock_model

    @patch("database.SessionLocal")
    async def test_create_handler_handle_success(self, mock_session_local, mock_request, mock_model):
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        data = {"name": "Test Item"}
        mock_request.json.return_value = data
        create_handler = CreateHandler(model=mock_model)
        response = await create_handler.handle(mock_session, mock_request)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert mock_session.refresh.called
        assert response.status == 201

    @patch("database.SessionLocal")
    async def test_create_handler_handle_invalid_data(self, mock_session_local, mock_request, mock_model):
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        invalid_data = {"invalid_field": "Invalid Value"}
        mock_request.json.return_value = invalid_data
        create_handler = CreateHandler(model=mock_model)
        response = await create_handler.handle(mock_session, mock_request)

        assert not mock_session.add.called
        assert not mock_session.commit.called
        assert not mock_session.refresh.called
        assert response.status == 400
