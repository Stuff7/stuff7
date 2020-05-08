from django.http import JsonResponse, Http404
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from django.utils.translation import get_language_from_request

from stuff7.settings import LANGUAGES
from .serializers import UserSerializer
from .models import User

# ViewSets define the view behavior.
class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
  queryset = User.objects.prefetch_related("oauthuser_set").all()
  serializer_class = UserSerializer

  def retrieve(self, request, pk=None):
    """ Retrieving current logged in user
    GET /api/users/current/ """
    if pk != "current": raise Http404
    serializer = self.get_serializer(self.get_object())
    return Response(serializer.data)

  def update(self, request, pk=None):
    """ Updating current logged in user
    PUT /api/users/current/ """
    return self.update_fields(request, pk=pk)

  def partial_update(self, request, pk=None):
    """ Updating current logged in user
    PATCH /api/users/current/ """
    return self.update_fields(request, partial=True, pk=pk)

  def update_fields(self, request, partial=False, pk=None):
    """ Updating current logged in user """
    if pk != "current": return JsonResponse({
      "status_code": 400,
      "error": "Bad Request",
      "message": "Use /api/users/current/ to perform updates on the current user.",
    })
    data, session = request.data, request.session
    user = self.get_serializer(request.user, data=data, partial=partial)
    user.is_valid(raise_exception=True)

    for k,v in data.items():
      setattr(user, k, v)

    user.save()
    return Response(user.data)

  def get_serializer_context(self):
    """ Adding current request to context """
    context = super(UserViewSet, self).get_serializer_context()
    context.update({"request": self.request})
    return context

  def get_object(self):
    """ Adding custom behaviour for anonymous users """
    user = self.request.user
    field = User._meta.get_field
    return user if user.is_authenticated else {
      "is_authenticated": False,
      "language": get_language_from_request(self.request, check_path=False),
      "palette": field("palette").default,
    }

class LanguageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
  def list(self, request):
    """ Return supported languages """
    return Response(LANGUAGES)

def not_found(request, exception=None):
  """ Custom 404 API response """
  return JsonResponse({
    "status_code": 404,
    "error": "Not Found",
    "message": "No such endpoint.",
  }, status=404)
