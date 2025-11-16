# This single file contains serializers, views, router, and admin registration
from django.urls import path, include
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.contrib import admin
from django.db import models as dj_models

from .models import Note

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'

def translate_text(text, target_language):
    # simple deterministic pseudo-translation (replace with real API if needed)
    return f"TRANSLATED({target_language}): " + text[::-1]

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all().order_by('-created_at')
    serializer_class = NoteSerializer

    @action(detail=True, methods=['post'])
    def translate(self, request, pk=None):
        note = get_object_or_404(Note, pk=pk)
        target = request.data.get('target_language', 'en')
        translated = translate_text(note.text, target)
        note.translated_text = translated
        note.translated_language = target
        note.save()
        cache.delete('stats_v1')
        return Response(NoteSerializer(note).data, status=status.HTTP_200_OK)

@api_view(['GET'])
def stats(request):
    data = cache.get('stats_v1')
    if data:
        return Response(data)
    total = Note.objects.count()
    translations = Note.objects.exclude(translated_text__isnull=True).exclude(translated_text__exact='').count()
    qs = Note.objects.values('language').order_by().annotate(count=dj_models.Count('id'))
    breakdown = {item['language']: item['count'] for item in qs}
    data = {
        'total_notes': total,
        'translations_performed': translations,
        'breakdown_by_language': breakdown
    }
    cache.set('stats_v1', data, timeout=60)
    return Response(data)


from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.encoding import force_str

@api_view(['POST'])
def upload_note(request):
    """Accepts multipart/form-data with a 'file' field (plain text .txt).
    Creates a Note from file content. Optional fields: title, language.
    """
    parser_classes = (MultiPartParser, FormParser)
    f = request.FILES.get('file')
    if not f:
        return Response({'detail':'No file provided (use field name "file").'}, status=400)
    # read small text files only
    try:
        content = force_str(f.read(), encoding='utf-8')
    except Exception:
        return Response({'detail':'Could not read file; ensure it is plain text.'}, status=400)
    title = request.POST.get('title') or (f.name or 'uploaded_note')
    language = request.POST.get('language') or 'en'
    note = Note.objects.create(title=title, text=content, language=language)
    cache.delete('stats_v1')
    return Response(NoteSerializer(note).data, status=201)

# Router and URL exports
router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')

urlpatterns = [
    path('notes/upload/', upload_note, name='notes-upload'),
    path('', include(router.urls)),
    path('stats/', stats, name='stats'),
]

# admin registration (kept minimal)
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id','title','language','translated_language','created_at')
