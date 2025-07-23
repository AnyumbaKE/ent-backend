from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from echofy.models import TestModel
from echofy.serializers import TestModelSerializer
from ..permissions import IsAdminUserRole
from django.db.models import Q

import os, base64
from gtts import gTTS
from django.conf import settings

LANG_MAP = {
    'en': 'en',
    'fr': 'fr',
    'de': 'de',
    'sw': 'sw'
}

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tests_with_audio(request):
    filters = request.GET.dict()
    tests = TestModel.objects.filter(**filters)

    audio_dir = os.path.join(settings.MEDIA_ROOT, 'mp3')
    os.makedirs(audio_dir, exist_ok=True)

    response_data = []
    for test in tests:
        lang_code = LANG_MAP.get(test.language.lower(), 'en')
        text = test.audio
        filename = f"test_{test.id}_{test.language}.mp3"
        filepath = os.path.join(audio_dir, filename)

        # Generate TTS if not exists
        if not os.path.exists(filepath):
            try:
                tts = gTTS(text=text, lang=lang_code)
                tts.save(filepath)
            except Exception as e:
                print(f"Error generating TTS for test ID {test.id}: {e}")
                continue  # Skip this entry if TTS fails

        # Encode audio to base64
        try:
            with open(filepath, 'rb') as f:
                audio_base64 = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"Error reading audio file for test ID {test.id}: {e}")
            audio_base64 = None

        response_data.append({
            "id": test.id,
            "type": test.type,
            "question": test.question,
            "audioText": test.audio,
            "audio": audio_base64,
            "correctAnswer": test.correctAnswer,
            "level": test.level,
            "added_by": str(test.added_by),
            "language": test.language
        })

    return Response(response_data)


# All tests
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tests(request):
    # tests = TestModel.objects.all()
    filters = request.GET.dict() 
    tests = TestModel.objects.filter(**filters)
    serializer = TestModelSerializer(tests, many=True)
    return Response(serializer.data)


# POST
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUserRole])
def create_test(request):
    data = request.data.copy()
    data['added_by'] = request.user.id
    serializer = TestModelSerializer(data=data)
    if serializer.is_valid():
        serializer.save(added_by=request.user) 
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=400)

# PUT 
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUserRole])
def update_test(request, pk):
    try:
        test = TestModel.objects.get(pk=pk)
    except TestModel.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    serializer = TestModelSerializer(test, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

# DELETE
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUserRole])
def delete_test(request, pk):
    try:
        test = TestModel.objects.get(pk=pk)
    except TestModel.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    test.delete()
    return Response({'deleted': True})
