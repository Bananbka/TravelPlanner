from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView

from apps.planner.models import TravelProject, Place
from apps.planner.serializers import TravelProjectSerializer, PlaceSerializer
from apps.planner.services.artic_api import validate_place_exists, search_places


@extend_schema(tags=['Travel Projects'])
class TravelProjectViewSet(viewsets.ModelViewSet):
    queryset = TravelProject.objects.all()
    serializer_class = TravelProjectSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'created_at']

    def get_queryset(self):
        return TravelProject.objects.filter(
            user=self.request.user
        ).prefetch_related('places').order_by('-created_at')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
        except ValidationError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Places'])
class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['project', 'is_visited']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return Place.objects.filter(
            project__user=self.request.user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        project = serializer.validated_data['project']

        if project.user != self.request.user:
            raise ValidationError({"project": "You do not have permission to add places to this project."})

        if project.places.count() >= 10:
            raise ValidationError({"detail": "This project already has the maximum of 10 places."})

        external_id = serializer.validated_data['external_id']
        if not validate_place_exists(external_id):
            raise ValidationError(
                {"external_id": f"Place with ID '{external_id}' does not exist in Art Institute API."})

        serializer.save()


@extend_schema(
    tags=['Places'],
    parameters=[
        OpenApiParameter(name='q', description='Search query', required=True, type=str),
        OpenApiParameter(name='limit', description='Number of results', required=False, type=int),
    ],
    responses={200: dict}
)
class PlaceSearchAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {"detail": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            limit = int(request.query_params.get('limit', 10))
        except ValueError:
            limit = 10

        try:
            results = search_places(query, limit)
            return Response(results, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
