from app.main import app


def test_code_scorecard_route_is_registered():
    paths = {route.path for route in app.routes}

    assert "/api/v1/repository-code-objective-scorecard" in paths


def test_code_scorecard_route_supports_post():
    route = next(
        route for route in app.routes
        if route.path == "/api/v1/repository-code-objective-scorecard"
    )

    assert "POST" in route.methods
