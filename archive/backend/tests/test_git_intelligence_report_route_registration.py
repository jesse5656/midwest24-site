from app.main import app


def test_git_intelligence_report_route_is_registered():
    paths = {route.path for route in app.routes}

    assert "/api/v1/repository-git-intelligence-report" in paths


def test_git_intelligence_report_route_supports_post():
    route = next(
        route for route in app.routes
        if route.path == "/api/v1/repository-git-intelligence-report"
    )

    assert "POST" in route.methods
