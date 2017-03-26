from django.conf.urls import include, url

from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register(r'images', views.ImageViewSet)
router.register(r'csvs', views.CSVViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_framework.urls',
                           namespace='rest_framework')),
]
