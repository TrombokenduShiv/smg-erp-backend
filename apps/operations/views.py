from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.throttling import UserRateThrottle
from django.utils import timezone
from django.shortcuts import get_object_or_404

# --- Local Imports ---
from .models import LeaveRequest, AttendanceLog
# FIX: Import all serializers from .serializers (assuming that's where you put them)
from .serializers import (
    LeaveApplicationSerializer, 
    AttendanceLogSerializer, 
    LeaveActionSerializer, 
    LeaveRequestSerializer
)
from apps.identity.permissions import IsOwnerOrAdmin, IsDeptAdmin
from apps.common.notifications import NotificationService 

# Initialize Notification Service
notifier = NotificationService()

# =============================================================================
# 1. SECURITY: THROTTLING
# =============================================================================
class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'

# =============================================================================
# 2. INTERN OPERATIONS
# =============================================================================

class MarkAttendanceView(APIView):
    """
    POST /api/v1/operations/attendance/mark/
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [BurstRateThrottle]

    def post(self, request):
        user = request.user
        now = timezone.now()
        today = now.date()
        current_time = now.time()

        log, created = AttendanceLog.objects.get_or_create(
            user=user, 
            date=today,
            defaults={'status': AttendanceLog.Status.ABSENT} 
        )

        if not log.check_in:
            log.check_in = current_time
            log.status = AttendanceLog.Status.PRESENT
            log.save()
            return Response({"message": f"Good Morning! Checked in at {current_time.strftime('%H:%M')}"})
        
        elif not log.check_out:
            log.check_out = current_time
            log.save()
            return Response({"message": f"Good Bye! Checked out at {current_time.strftime('%H:%M')}"})

        return Response({"message": "Attendance already completed for today."}, status=400)


class LeaveRequestListCreateView(APIView):
    """
    GET /api/v1/operations/leaves/  -> View History
    POST /api/v1/operations/leaves/ -> Apply
    """
    permission_classes = [permissions.IsAuthenticated]
    # Throttle POSTs (Apply), but let GETs (History) flow freely
    def get_throttles(self):
        if self.request.method == 'POST':
            return [BurstRateThrottle()]
        return []

    def get(self, request):
        # Intern sees their own history
        leaves = LeaveRequest.objects.filter(user=request.user).order_by('-applied_on')
        serializer = LeaveRequestSerializer(leaves, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LeaveApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Leave application submitted successfully.",
                "status": "PENDING_HOD"
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyAttendanceHistoryView(generics.ListAPIView):
    serializer_class = AttendanceLogSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return AttendanceLog.objects.filter(user=self.request.user).order_by('-date')


# =============================================================================
# 3. ADMIN OPERATIONS
# =============================================================================

class ManagerInboxView(APIView):
    """
    GET /api/v1/operations/admin/inbox/
    Lists PENDING requests for the Admin's department.
    """
    permission_classes = [IsDeptAdmin] # Zero Trust

    def get(self, request):
        user = request.user
        
        # 1. Base Query: Pending Leaves
        queryset = LeaveRequest.objects.filter(current_status=LeaveRequest.RequestStatus.PENDING_HOD)

        # 2. Dept Scope (Unless Super Admin)
        if user.role != 'SUP':
            queryset = queryset.filter(user__department=user.department)

        # 3. Serialize (Using the full serializer is better than manual dicts)
        serializer = LeaveRequestSerializer(queryset, many=True)
        return Response(serializer.data)


class ApproveLeaveView(APIView):
    """
    POST /api/v1/operations/leaves/<pk>/decide/
    """
    permission_classes = [IsDeptAdmin]

    def post(self, request, pk):
        # 1. Fetch & Verify Access
        query = LeaveRequest.objects.all()
        if request.user.role != 'SUP':
            query = query.filter(user__department=request.user.department)
        
        leave = get_object_or_404(query, pk=pk)

        # 2. Validate Action
        serializer = LeaveActionSerializer(data=request.data)
        if serializer.is_valid():
            action = serializer.validated_data['action']
            reason = serializer.validated_data.get('rejection_reason', '')

            if action == 'APPROVE':
                leave.current_status = LeaveRequest.RequestStatus.APPROVED
            else:
                leave.current_status = LeaveRequest.RequestStatus.REJECTED
                leave.rejection_reason = reason
            
            leave.save()

            # 3. NOTIFICATION TRIGGER (The Missing Piece)
            try:
                notifier.alert_leave_status(leave)
            except Exception as e:
                # Log error but don't fail the HTTP request
                print(f"Notification Error: {e}")

            return Response({"message": f"Request {action}D successfully."})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)