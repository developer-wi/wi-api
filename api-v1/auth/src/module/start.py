from auth.controller import router_auth
from server.app import create_app

app = create_app()
app.include_router(router_auth, prefix="/api/v1")
