import client from './client';

export const bookingApi = {
  // Get all clinic locations for booking
  getClinics: () => client.get('/booking/clinics'),

  // Get available slots for a specific date and clinic
  getSlots: (clinicLocationId: string, bookingDate: string) =>
    client.get('/booking/slots', {
      params: { clinic_location_id: clinicLocationId, booking_date: bookingDate },
    }),

  // Reserve a slot (temporary hold for 10 minutes)
  reserveSlot: (data: {
    clinic_location_id: string;
    booking_date: string;
    slot_time: string;
    patient_id: string;
  }) => client.post('/booking/reserve', data),

  // Confirm booking after payment
  confirmBooking: (data: {
    booking_id: string;
    razorpay_payment_id: string;
    razorpay_order_id: string;
    razorpay_signature: string;
  }) => client.post('/booking/confirm', data),

  // Cancel a booking
  cancelBooking: (data: { booking_id: string; reason?: string }) =>
    client.post('/booking/cancel', data),

  // Get daily schedule PDF for a specific date
  getSchedule: (date: string) => client.get(`/booking/schedule/${date}`),

  // Get current user's bookings
  getMyBookings: (page = 1, perPage = 20) =>
    client.get('/booking/my-bookings', {
      params: { page, per_page: perPage },
    }),
};
