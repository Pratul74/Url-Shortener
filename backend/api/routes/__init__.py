from .url import router as url_router
from .auth import router as auth_router
from .analytics import router as analytics_router
from .redirect import router as redirect_router

__all__=[
    'url_router',
    'auth_router',
    'analytics_router',
    "redirect_router",
]