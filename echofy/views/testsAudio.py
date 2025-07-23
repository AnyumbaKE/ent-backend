import os, base64, random
from gtts import gTTS
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from echofy.models import TestModel

LANG_MAP = {
    'en': 'en',
    'fr': 'fr',
    'de': 'de',
    'sw': 'sw'
}

def generate_audio_file(text, lang_code, filepath):
    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save(filepath)
        return True
    except Exception as e:
        print(f"Error generating TTS: {e}")
        return False

def get_or_generate_audio_file(test):
    lang_code = LANG_MAP.get(test.language, 'en')
    filename = f"test_{test.id}_{test.language}.mp3"
    audio_dir = os.path.join(settings.MEDIA_ROOT, 'mp3')
    os.makedirs(audio_dir, exist_ok=True)
    filepath = os.path.join(audio_dir, filename)

    # Generate TTS if not cached
    if not os.path.exists(filepath):
        success = generate_audio_file(test.audio, lang_code, filepath)
        if not success:
            return None  # Signal failure

    return filepath

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_audio_test_base64(request):
    language = request.data.get('language', '').strip().lower()
    level = request.data.get('level', '').strip().lower()

    filters = {'type': 'audio'}
    if language:
        filters['language__iexact'] = language
    if level:
        filters['level__iexact'] = level

    tests = TestModel.objects.filter(**filters)
    if not tests.exists():
        return Response({"error": "No matching audio tests found"}, status=404)

    test = random.choice(tests)
    filepath = get_or_generate_audio_file(test)

    if not filepath:
        return Response({"error": "TTS generation failed. Try again later."}, status=429)

    with open(filepath, 'rb') as f:
        audio_base64 = base64.b64encode(f.read()).decode('utf-8')

    return Response({
        "id": test.id,
        "question": test.question,
        "language": test.language,
        "level": test.level,
        "correctAnswer": test.correctAnswer,
        "audio": audio_base64
    })
