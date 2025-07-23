from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import TestSession
from ..serializers import TestSessionSerializer

from ..models import TestSession, TestModel
from ..serializers import TestSessionSerializer
from ..permissions import IsAdminUserRole
from django.utils import timezone
from datetime import timedelta



#All
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUserRole])
def get_all_test_sessions(request):
    filter = request.GET.dict()
    sessions = TestSession.objects.filter(**filter).order_by('-started_at')
    serializer = TestSessionSerializer(sessions, many=True)
    return Response(serializer.data)

#Starting
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_test_session(request):
    mode = request.data.get('mode')
    if mode not in ['easy', 'medium', 'hard']:
        return Response({'error': 'Invalid mode'}, status=400)

    session = TestSession.objects.create(user=request.user, mode=mode)
    serializer = TestSessionSerializer(session)
    return Response(serializer.data)

#Get by user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_test_sessions(request):
    sessions = TestSession.objects.filter(user=request.user).order_by('-started_at')
    serializer = TestSessionSerializer(sessions, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_test_answer(request):
    user = request.user
    test_id = request.data.get("test_id")
    user_answer = request.data.get("answer", "").strip().lower()

    if not test_id or not user_answer:
        return Response({"error": "Both test_id and answer are required."}, status=400)

    # Get the latest open test session for the user
    try:
        session = TestSession.objects.filter(user=user, closed=False).latest('started_at')
    except TestSession.DoesNotExist:
        return Response({"error": "No active test session found."}, status=400)

    # Check if session expired
    if timezone.now() > session.started_at + timedelta(minutes=5):
        session.closed = True
        session.save()
        serializer = TestSessionSerializer(session)
        return Response({
            "error": "Session expired. Please start a new one.",
            "session": serializer.data
        }, status=400)

    # Find the test question
    try:
        test = TestModel.objects.get(id=test_id)
    except TestModel.DoesNotExist:
        return Response({"error": "Test not found."}, status=404)

    is_correct = user_answer == test.correctAnswer.strip().lower()

    # Increment score if correct
    if is_correct:
        session.correct_no += 1

    # Check if session needs to be closed (e.g. after 10 questions)
    if session.correct_no >= 10:
        session.closed = True

    session.save()
    serializer = TestSessionSerializer(session)

    return Response({
        "correct": is_correct,
        "correct_answer": test.correctAnswer,
        "session": serializer.data,
        "time_remaining_seconds": max(0, int((session.started_at + timedelta(minutes=5) - timezone.now()).total_seconds()))
    })