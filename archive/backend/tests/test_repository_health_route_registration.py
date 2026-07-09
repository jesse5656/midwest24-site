from app.main import app


def test_repository_health_route_is_registered():
    paths = {route.path for route in app.routes}

    assert "/api/v1/archive-backend-health" in paths


def test_repository_health_route_supports_post():
    route = next(
        route for route in app.routes
        if route.path == "/api/v1/archive-backend-health"
    )

    assert "POST" in route.methods
