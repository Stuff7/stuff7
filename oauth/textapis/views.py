from rest_framework import viewsets, mixins
from rest_framework.response import Response

from .serializers import CustomAPIsSerializer

# ViewSets define the view behavior.
class CustomAPIsViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):

  def list(self, request):
    serializer = CustomAPIsSerializer()
    return Response(serializer.data)
