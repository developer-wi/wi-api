from blog.controller import router_blog
from serverlib.app import create_app

app = create_app()
app.include_router(router_blog, prefix="/api/v1")
