from django.urls import path 
from .views import RoomListView, RoomDetailView, RoomCreateView, RoomToogleFavouriteView, RoomUpdateView, RoomDeleteView

urlpatterns = [
    path('', RoomListView.as_view(), name='home'),
    path('room/<int:pk>/', RoomDetailView.as_view(), name='room'),
    path('room-create/', RoomCreateView.as_view(), name='room-create'),
    path('room-update/<int:pk>/', RoomUpdateView.as_view(), name='room-update'),
    path('room-delete/<int:pk>/', RoomDeleteView.as_view(), name='room-delete'),
    path('room-toggle-favourite/<int:pk>/', RoomToogleFavouriteView.as_view(), name='room-toggle-favourite'),
]