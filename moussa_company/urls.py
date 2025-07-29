
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('',include('products.urls'))
    
]

#if this is not added, the get method on the differents files and images will return 404 (now that is very important)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)