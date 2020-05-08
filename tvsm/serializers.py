from rest_framework import serializers

# Serializers define the API representation.
class EpisodeSerializer(serializers.Serializer):
  display = serializers.CharField()
  date = serializers.DateTimeField(allow_null=True)

  class Meta:
    fields = ("display", "date")

class SeriesSerializer(serializers.Serializer):
  id = serializers.IntegerField()
  name = serializers.CharField()
  lastUpdated = serializers.DateTimeField()
  status = serializers.CharField()
  network = serializers.CharField(allow_null=True)
  rating = serializers.FloatField(allow_null=True)
  nextEp = EpisodeSerializer()
  prevEp = EpisodeSerializer()
  seasons = serializers.IntegerField()
  episodes = serializers.IntegerField()

  class Meta:
    fields = ("id", "name", "lastUpdated", "status", "network",
              "rating", "nextEp", "prevEp", "seasons", "episodes")
