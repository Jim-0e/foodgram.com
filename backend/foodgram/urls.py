"""Urls.py."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from foods.views import IngredientsListView, RecipeListView, TagsListView
from users.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'recipes', RecipeListView)
router.register(r'tags', TagsListView)
router.register(r'ingredients', IngredientsListView)
router.register(r'users', UserViewSet)


urlpatterns = [
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/users/me/avatar/', UserViewSet.as_view({'put': 'avatar'})),
    path("s/", include("urlshortner.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
