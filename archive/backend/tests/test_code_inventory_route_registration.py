from app.main import app


def test_code_inventory_route_is_registered():
    paths = {route.path for route in app.routes}

    assert "/api/v1/repository-code-inventory" in paths


def test_code_inventory_route_supports_post():
    route = next(
        route for route in app.routes
        if route.path == "/api/v1/repository-code-inventory"
    )

    assert "POST" in route.methods
