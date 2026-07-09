from app.main import app


def test_branch_analysis_route_is_registered():
    paths = {route.path for route in app.routes}

    assert "/api/v1/repository-git-branch-analysis" in paths


def test_branch_analysis_route_supports_post():
    route = next(
        route for route in app.routes
        if route.path == "/api/v1/repository-git-branch-analysis"
    )

    assert "POST" in route.methods
