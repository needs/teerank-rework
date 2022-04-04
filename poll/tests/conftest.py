"""Configuration and fixtures for tests."""

import pytest


@pytest.fixture(name="update_stub")
def fixture_update_stub():
    """Create a fake update stub for testing."""

    class UpdateStub:
        def __init__(self):
            self.master_up_requests = []
            self.master_down_requests = []
            self.game_up_requests = []
            self.game_down_requests = []

        def master_server_up(self, request):
            self.master_up_requests.append(request)

        def master_server_down(self, request):
            self.master_down_requests.append(request)

        def game_server_up(self, request):
            self.game_up_requests.append(request)

        def game_server_down(self, request):
            self.game_down_requests.append(request)

    return UpdateStub()


@pytest.fixture(name="rank_stub")
def fixture_rank_stub():
    """Create a fake rank stub for testing."""

    class RankStub:
        def __init__(self):
            self.rank_requests = []

        def rank(self, request):
            self.rank_requests.append(request)

    return RankStub()
