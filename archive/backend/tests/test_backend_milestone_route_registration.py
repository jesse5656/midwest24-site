from app.main import app


def test_backend_milestone_route_is_registered():
    paths = {route.path for route in app.routes}

    assert "/api/v1/archive-backend-milestone-scorecard" in paths


def test_backend_milestone_route_supports_post():
    route = next(
        route for route in app.routes
        if route.path == "/api/v1/archive-backend-milestone-scorecard"
    )

    assert "POST" in route.methods
