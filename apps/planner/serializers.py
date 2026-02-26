from rest_framework import serializers
from .models import TravelProject, Place
from .services.artic_api import validate_place_exists


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'project', 'external_id', 'notes', 'is_visited', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_external_id(self, value):
        if not validate_place_exists(value):
            raise serializers.ValidationError(f"Place with ID '{value}' does not exist.")
        return value


class PlaceImportSerializer(serializers.Serializer):
    external_id = serializers.CharField()
    notes = serializers.CharField(allow_blank=True, required=False, default="")

    def validate_external_id(self, value):
        if not validate_place_exists(value):
            raise serializers.ValidationError(f"Place with ID '{value}' does not exist.")
        return value


class TravelProjectSerializer(serializers.ModelSerializer):
    places = PlaceSerializer(many=True, read_only=True)
    is_completed = serializers.BooleanField(read_only=True)

    import_places = PlaceImportSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = TravelProject
        fields = [
            'id', 'name', 'description', 'start_date', 'is_completed',
            'places', 'import_places', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_completed', 'created_at', 'updated_at']

    def validate_import_places(self, value):
        if value and len(value) > 10:
            raise serializers.ValidationError("A project can have a maximum of 10 places.")

        external_ids = [place['external_id'] for place in value]
        if len(external_ids) != len(set(external_ids)):
            raise serializers.ValidationError("Duplicate places are not allowed in the same request.")

        return value

    def create(self, validated_data):
        places_data = validated_data.pop('import_places', [])
        user = self.context['request'].user

        project = TravelProject.objects.create(user=user, **validated_data)

        places_to_create = [
            Place(
                project=project,
                external_id=place_data['external_id'],
                notes=place_data.get('notes', '')
            )
            for place_data in places_data
        ]

        if places_to_create:
            Place.objects.bulk_create(places_to_create)

        return project
