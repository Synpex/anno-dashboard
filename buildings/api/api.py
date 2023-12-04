from rest_framework import serializers, viewsets
from buildings.models.building_model import Building  # Import the Building model class directly

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = '__all__'

class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()  # Use Building model class for the queryset
    serializer_class = BuildingSerializer
