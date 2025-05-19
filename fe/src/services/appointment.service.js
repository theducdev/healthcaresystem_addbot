// fe/src/services/appointment.service.js
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/appointments/';

// Maintain consistent configuration with other services
axios.defaults.withCredentials = true;

const appointmentService = {
    // Doctor Schedule Management
    getDoctorSchedules: async () => {
        try {
            const response = await axios.get(API_URL + 'schedules/');
            return response.data;
        } catch (error) {
            console.error('Error fetching doctor schedules', error);
            return [];
        }
    },

    createSchedule: async (scheduleData) => {
        try {
            console.log('Creating schedule with data:', scheduleData);
            
            // Get CSRF token
            const getCookie = (name) => {
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            };
            
            const csrftoken = getCookie('csrftoken');
            console.log('CSRF Token:', csrftoken);
            
            // Note: We don't need to provide the doctor ID because 
            // the backend should identify the doctor from the authenticated user
            // However, the serializer might be expecting it, so let's add a placeholder
            // that will be overridden by the backend
            const dataToSend = {
                ...scheduleData,
                // This will be replaced by the backend with the actual doctor
                doctor: 1
            };
            
            console.log('Sending data to backend:', dataToSend);
            
            const response = await axios.post(API_URL + 'schedules/', dataToSend, {
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                },
                withCredentials: true
            });
            
            console.log('Schedule created successfully:', response.data);
            return response.data;
        } catch (error) {
            console.error('Error creating schedule:', error);
            console.error('Error response:', error.response?.data);
            throw error;
        }
    },

    updateSchedule: async (scheduleId, scheduleData) => {
        try {
            const response = await axios.put(`${API_URL}schedules/${scheduleId}/`, scheduleData);
            return response.data;
        } catch (error) {
            console.error('Error updating schedule', error);
            throw error;
        }
    },

    deleteSchedule: async (scheduleId) => {
        try {
            await axios.delete(`${API_URL}schedules/${scheduleId}/`);
            return true;
        } catch (error) {
            console.error('Error deleting schedule', error);
            throw error;
        }
    },

    // Patient Booking
    getDoctors: async (search = '') => {
        try {
            const response = await axios.get(`${API_URL}doctors/?search=${search}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching doctors', error);
            return [];
        }
    },

    getDoctorSchedulesByDoctor: async (doctorId) => {
        try {
            const response = await axios.get(`${API_URL}doctors/${doctorId}/schedules/`);
            return response.data;
        } catch (error) {
            console.error('Error fetching doctor schedules', error);
            return [];
        }
    },

    bookAppointment: async (bookingData) => {
        try {
            const response = await axios.post(`${API_URL}book/`, bookingData);
            return response.data;
        } catch (error) {
            console.error('Error booking appointment', error);
            throw error;
        }
    },

    // Appointment Management
    getPatientAppointments: async () => {
        try {
            const response = await axios.get(`${API_URL}patient/appointments/`);
            return response.data;
        } catch (error) {
            console.error('Error fetching patient appointments', error);
            return [];
        }
    },

    getDoctorAppointments: async () => {
        try {
            const response = await axios.get(`${API_URL}doctor/appointments/`);
            return response.data;
        } catch (error) {
            console.error('Error fetching doctor appointments', error);
            return [];
        }
    },

    cancelAppointment: async (appointmentId) => {
        try {
            const response = await axios.patch(`${API_URL}appointments/${appointmentId}/cancel/`);
            return response.data;
        } catch (error) {
            console.error('Error canceling appointment', error);
            throw error;
        }
    }
};

export default appointmentService;