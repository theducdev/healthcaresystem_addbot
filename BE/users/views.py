# BE/users/views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .serializers import UserRegistrationSerializer, LoginSerializer, UserSerializer, DoctorSerializer, PatientSerializer
from .models import User, Doctor, Patient
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Prepare response data
            response_data = UserSerializer(user).data

            # Add profile data if available
            if user.is_doctor and hasattr(user, 'doctor_profile'):
                response_data['doctor_profile'] = DoctorSerializer(user.doctor_profile).data

            if user.is_patient and hasattr(user, 'patient_profile'):
                response_data['patient_profile'] = PatientSerializer(user.patient_profile).data

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        print(f"Login attempt with data: {request.data}")
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user)
            print(f"User authenticated: {user.username}, is_doctor: {user.is_doctor}, is_patient: {user.is_patient}")

            # Prepare response data
            response_data = UserSerializer(user).data

            # Add profile data if available
            if user.is_doctor and hasattr(user, 'doctor_profile'):
                response_data['doctor_profile'] = DoctorSerializer(user.doctor_profile).data
                print(f"Added doctor profile data: {response_data['doctor_profile']}")

            if user.is_patient and hasattr(user, 'patient_profile'):
                response_data['patient_profile'] = PatientSerializer(user.patient_profile).data
                print(f"Added patient profile data: {response_data['patient_profile']}")

            return Response(response_data)
        print(f"Login validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.user.is_authenticated:
            response_data = UserSerializer(request.user).data

            # Add profile data if available
            if request.user.is_doctor and hasattr(request.user, 'doctor_profile'):
                response_data['doctor_profile'] = DoctorSerializer(request.user.doctor_profile).data

            if request.user.is_patient and hasattr(request.user, 'patient_profile'):
                response_data['patient_profile'] = PatientSerializer(request.user.patient_profile).data

            return Response(response_data)
        return Response({"detail": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        print(f"Updating profile for user: {user.username}")
        print(f"Update data: {request.data}")

        try:
            # Update user fields
            user_data = {
                'first_name': request.data.get('first_name', user.first_name),
                'last_name': request.data.get('last_name', user.last_name),
                'email': request.data.get('email', user.email),
                'phone_number': request.data.get('phone_number', user.phone_number)
            }
            
            user_serializer = UserSerializer(user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user = user_serializer.save()
                print(f"User basic info updated successfully")
            else:
                print(f"User serializer errors: {user_serializer.errors}")
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            response_data = user_serializer.data

            # Update doctor profile if applicable
            if user.is_doctor and hasattr(user, 'doctor_profile'):
                doctor_data = {
                    'specialization': request.data.get('specialization', user.doctor_profile.specialization)
                }
                doctor_serializer = DoctorSerializer(user.doctor_profile, data=doctor_data, partial=True)
                if doctor_serializer.is_valid():
                    doctor_serializer.save()
                    response_data['doctor_profile'] = doctor_serializer.data
                    print(f"Doctor profile updated successfully")
                else:
                    print(f"Doctor serializer errors: {doctor_serializer.errors}")
                    return Response(doctor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Update patient profile if applicable
            if user.is_patient and hasattr(user, 'patient_profile'):
                patient_data = {
                    'date_of_birth': request.data.get('date_of_birth', user.patient_profile.date_of_birth)
                }
                patient_serializer = PatientSerializer(user.patient_profile, data=patient_data, partial=True)
                if patient_serializer.is_valid():
                    patient_serializer.save()
                    response_data['patient_profile'] = patient_serializer.data
                    print(f"Patient profile updated successfully")
                else:
                    print(f"Patient serializer errors: {patient_serializer.errors}")
                    return Response(patient_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(response_data)

        except Exception as e:
            print(f"Error updating profile: {str(e)}")
            return Response(
                {"detail": "Failed to update profile", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )