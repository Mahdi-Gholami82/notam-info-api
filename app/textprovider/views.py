from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
from django_filters.rest_framework import DjangoFilterBackend

from textprovider.filters import NotamsFilter
from . import serializers
from .models import Notams, ParsedNotams
from .pagination import NotamsPagination

class NotamsViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = NotamsPagination
    permission_classes = [HasAPIKey]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotamsFilter
    

    def _validate_queryparams(self):
        serializer = serializers.QueryParamsSerializer(data=self.request.query_params)
        validation_error = False
        if not serializer.is_valid():
            validation_error = Response({'error': f"Invalid query params."}, status=status.HTTP_400_BAD_REQUEST)
        return validation_error
    
    def _get_query_options(self):
        parsed = self.request.query_params.get('parsed', 'false').lower() == 'true'
        coordinates = self.request.query_params.get('coordinates', 'false').lower() == 'true'
        return parsed, coordinates

    def retrieve(self, request, *args, **kwargs):
        validation_error = self._validate_queryparams()
        if validation_error:
            return validation_error
    
        if self.get_queryset().model is ParsedNotams:
            notam_pk = self.kwargs.get('pk')
            queryset = self.get_queryset()         
            instance = get_object_or_404(queryset,notam=notam_pk)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
   
        return super().retrieve(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        validation_error = self._validate_queryparams()
        if validation_error:
            return validation_error
        return super().list(request, *args, **kwargs)
        
    def get_queryset(self):
        requested_parsed, requested_coordinates = self._get_query_options()
        match (requested_parsed,requested_coordinates):
            case True,False:
                notams_queryset = ParsedNotams.objects.select_related('notam').order_by('notam__id')
            case True,True:
                notams_queryset = ParsedNotams.objects.select_related('notam').prefetch_related('notam__coordinates').order_by('notam__id')
            case False,True:
                notams_queryset = Notams.objects.prefetch_related('coordinates').order_by('id')
            case _:    
                notams_queryset = Notams.objects.order_by('id')

        return notams_queryset
    
    def get_serializer_class(self):
        requested_parsed, requested_coordinates = self._get_query_options()
        match (requested_parsed,requested_coordinates):
            case True,False:
                notams_serializer = serializers.ParsedNotamsSerializer
            case True,True:
                notams_serializer = serializers.ParsedNotamsIncludeCoordinatesSerializer
            case False,True:
                notams_serializer = serializers.NotamsIncludeCoordinatesSerializer
            case _:
                notams_serializer = serializers.NotamsSerializer

        return notams_serializer

        

        

