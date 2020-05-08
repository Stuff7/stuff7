import json

from django.http import HttpResponse
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import SeriesSerializer

# ViewSets define the view behavior.
class SeriesViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
  serializer_class = SeriesSerializer
  permission_classes = [IsAuthenticated]

  def list(self, request):
    """ Retrieving user's series list
    GET /api/tvsm/ """
    return HttpResponse(request.user.series_list, content_type="application/json")

  def create(self, request):
    """ Updating user's series list
    POST /api/tvsm/ """
    user = request.user
    serializer = self.get_serializer(data=request.data, many=True)
    serializer.is_valid(raise_exception=True)
    user.series_list = json.dumps(serializer.data)
    user.save()
    headers = self.get_success_headers(serializer.data)
    return Response(serializer.data, headers=headers)
