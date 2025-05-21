# BE/appointments/views.py
from rest_framework import status, generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Schedule, Appointment
from .serializers import ScheduleSerializer, AppointmentSerializer
from users.models import Doctor, Patient
from users.serializers import DoctorSerializer
from rest_framework import serializers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny, IsAuthenticated

# Doctor Schedule Management
class DoctorScheduleListCreateView(generics.ListCreateAPIView):
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        if self.request.user.is_doctor:
            return Schedule.objects.filter(doctor__user=self.request.user)
        return Schedule.objects.none()

    def perform_create(self, serializer):
        try:
            print(f"User creating schedule: {self.request.user.username}, is_doctor: {self.request.user.is_doctor}")
            # Get the doctor associated with the current user
            doctor = Doctor.objects.get(user=self.request.user)
            print(f"Found doctor: {doctor.id}, specialization: {doctor.specialization}")
            # Save the serializer with the doctor
            serializer.save(doctor=doctor)
            print(f"Schedule created successfully")
        except Doctor.DoesNotExist:
            print(f"Error: No doctor profile found for user {self.request.user.username}")
            raise serializers.ValidationError("You must have a doctor profile to create schedules.")
        except Exception as e:
            print(f"Error creating schedule: {str(e)}")
            raise

    def create(self, request, *args, **kwargs):
        print(f"Creating schedule with data: {request.data}")
        return super().create(request, *args, **kwargs)

@method_decorator(csrf_exempt, name='dispatch')
class DoctorScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_doctor:
            return Schedule.objects.filter(doctor__user=self.request.user)
        return Schedule.objects.none()

    def destroy(self, request, *args, **kwargs):
        print(f"Attempting to delete schedule {kwargs.get('pk')} by user {request.user.username}")
        try:
            schedule = self.get_object()
            
            # Kiểm tra xem có lịch hẹn nào không
            existing_appointments = Appointment.objects.filter(
                schedule=schedule,
                status__in=['CONFIRMED', 'PENDING']
            ).exists()
            
            if existing_appointments:
                print(f"Cannot delete schedule {schedule.id} - has active appointments")
                return Response(
                    {"detail": "Cannot delete schedule that has active appointments"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"Deleting schedule {schedule.id}")
            schedule.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            print(f"Error deleting schedule: {str(e)}")
            return Response(
                {"detail": "Failed to delete schedule", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Patient Appointment Booking
class DoctorListView(generics.ListAPIView):
    serializer_class = DoctorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['specialization', 'user__first_name', 'user__last_name']

    def get_queryset(self):
        return Doctor.objects.all()

class DoctorScheduleView(generics.ListAPIView):
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        doctor_id = self.kwargs.get('doctor_id')
        return Schedule.objects.filter(
            doctor_id=doctor_id,
            date__gte=datetime.now().date(),
            is_available=True
        )

@method_decorator(csrf_exempt, name='dispatch')
class BookAppointmentView(APIView):
    permission_classes = [AllowAny]  # Cho phép tất cả request

    def post(self, request, *args, **kwargs):
        print("=== DEBUG BOOKING REQUEST ===")
        print(f"Request data: {request.data}")
        print(f"Request headers: {request.headers}")
        print(f"Request method: {request.method}")
        print("===========================")

        try:
            # Lấy dữ liệu từ request
            data = request.data
            if isinstance(data, str):
                import json
                data = json.loads(data)
            
            schedule_id = data.get('schedule_id')
            slot_time = data.get('time')
            patient_id = data.get('patient_id')
            reason = data.get('reason', '')

            print(f"Parsed data: schedule_id={schedule_id}, time={slot_time}, patient_id={patient_id}, reason={reason}")

            # Validate required fields
            if not all([schedule_id, slot_time, patient_id]):
                return Response({
                    "detail": "Missing required fields",
                    "required": {
                        "schedule_id": bool(schedule_id),
                        "time": bool(slot_time),
                        "patient_id": bool(patient_id)
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get patient
            try:
                patient = Patient.objects.get(id=patient_id)
                print(f"Found patient: {patient.user.username}")
            except Patient.DoesNotExist:
                return Response({"detail": f"Patient with id {patient_id} not found"}, 
                              status=status.HTTP_404_NOT_FOUND)

            # Get schedule
            try:
                schedule = Schedule.objects.get(id=schedule_id)
                print(f"Found schedule: date={schedule.date}, doctor={schedule.doctor.user.username}")
                if not schedule.is_available:
                    return Response({"detail": "Schedule is not available"}, 
                                  status=status.HTTP_400_BAD_REQUEST)
            except Schedule.DoesNotExist:
                return Response({"detail": f"Schedule with id {schedule_id} not found"}, 
                              status=status.HTTP_404_NOT_FOUND)

            # Validate time format and calculate end time
            try:
                start_time = datetime.strptime(slot_time, '%H:%M').time()
                end_time_dt = datetime.combine(datetime.today(), start_time) + timedelta(minutes=schedule.slot_duration)
                end_time = end_time_dt.time()

                # Validate time is within schedule's time range
                if start_time < schedule.start_time or end_time > schedule.end_time:
                    return Response({
                        "detail": "Time slot is outside schedule's time range",
                        "schedule_range": f"{schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}"
                    }, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({
                    "detail": "Invalid time format. Use HH:MM (e.g., 09:00)"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if slot is already booked
            existing_appointment = Appointment.objects.filter(
                schedule=schedule,
                date=schedule.date,
                time=start_time,
                status='CONFIRMED'
            ).exists()

            if existing_appointment:
                return Response({
                    "detail": "This time slot is already booked"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create appointment
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=schedule.doctor,
                schedule=schedule,
                date=schedule.date,
                time=start_time,
                end_time=end_time,
                reason=reason or "No reason provided"
            )

            print(f"Created appointment: id={appointment.id}")

            # Update schedule availability if needed
            if not self._has_available_slots(schedule):
                schedule.is_available = False
                schedule.save()
                print(f"Updated schedule {schedule.id} to not available")

            return Response(
                AppointmentSerializer(appointment).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print(f"Error in booking appointment: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return Response({
                "detail": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _has_available_slots(self, schedule):
        booked_slots = Appointment.objects.filter(
            schedule=schedule,
            status='CONFIRMED'
        ).count()

        total_minutes = (datetime.combine(datetime.min, schedule.end_time) -
                         datetime.combine(datetime.min, schedule.start_time)).seconds / 60
        total_slots = total_minutes / schedule.slot_duration

        return booked_slots < total_slots

# Patient Appointment Management
class PatientAppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        if self.request.user.is_patient:
            from users.models import Patient
            patient = Patient.objects.get(user=self.request.user)
            return Appointment.objects.filter(patient=patient)
        return Appointment.objects.none()

# Doctor Appointment Management
class DoctorAppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        if self.request.user.is_doctor:
            doctor = Doctor.objects.get(user=self.request.user)
            return Appointment.objects.filter(doctor=doctor)
        return Appointment.objects.none()

# Appointment Cancellation (for both doctor and patient)
@method_decorator(csrf_exempt, name='dispatch')
class CancelAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, appointment_id):
        print(f"Cancelling appointment {appointment_id} by user {request.user.username}")
        print(f"Request headers: {request.headers}")
        
        try:
            if request.user.is_doctor:
                appointment = Appointment.objects.get(
                    id=appointment_id,
                    doctor__user=request.user
                )
                print(f"Found appointment for doctor: {appointment.id}")
            elif request.user.is_patient:
                appointment = Appointment.objects.get(
                    id=appointment_id,
                    patient__user=request.user
                )
                print(f"Found appointment for patient: {appointment.id}")
            else:
                print(f"User {request.user.username} is neither doctor nor patient")
                return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

            # Kiểm tra trạng thái hiện tại của lịch hẹn
            if appointment.status == 'CANCELLED':
                return Response({"detail": "Appointment is already cancelled"}, status=status.HTTP_400_BAD_REQUEST)
            
            if appointment.status == 'COMPLETED':
                return Response({"detail": "Cannot cancel completed appointment"}, status=status.HTTP_400_BAD_REQUEST)

            appointment.status = 'CANCELLED'
            appointment.save()
            print(f"Appointment {appointment.id} cancelled successfully")

            # If this was the only booked slot, make schedule available again
            self._update_schedule_availability(appointment.schedule)

            return Response(AppointmentSerializer(appointment).data)

        except Appointment.DoesNotExist:
            print(f"Appointment {appointment_id} not found")
            return Response({"detail": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error cancelling appointment: {str(e)}")
            return Response(
                {"detail": "Failed to cancel appointment", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _update_schedule_availability(self, schedule):
        active_appointments = Appointment.objects.filter(
            schedule=schedule,
            status='CONFIRMED'
        ).count()

        if active_appointments == 0:
            schedule.is_available = True
            schedule.save()