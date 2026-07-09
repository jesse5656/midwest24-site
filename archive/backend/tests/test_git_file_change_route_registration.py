from app.main import app


def test_git_file_change_preview_route_is_registered():
    paths = {route.path for route in app.routes}

    assert "/api/v1/repository-git-file-change-preview" in paths


def test_git_file_change_preview_route_supports_post():
    route = next(
        route for route in app.routes
        if route.path == "/api/v1/repository-git-file-change-preview"
    )

    assert "POST" in route.methods
