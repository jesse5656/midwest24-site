from app.main import app


def test_source_outline_route_is_registered():
    paths = {route.path for route in app.routes}

    assert "/api/v1/repository-source-outline" in paths


def test_source_outline_route_supports_post():
    route = next(
        route for route in app.routes
        if route.path == "/api/v1/repository-source-outline"
    )

    assert "POST" in route.methods
