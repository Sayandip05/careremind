/**
 * demoData.ts
 *
 * Hardcoded realistic demo data used exclusively when a guest (unauthenticated)
 * user is browsing the app in preview mode.  No API calls are made for guests.
 */

export const demoStats = {
  total_patients: 128,
  pending_reminders: 14,
  sent_reminders: 312,
  failed_reminders: 8,
  success_rate: 97,
  total_uploads: 23,
};

const TODAY = new Date().toISOString().split('T')[0];

export const demoBookings = [
  {
    id: 'd1',
    serial_number: 1,
    booking_date: TODAY,
    slot_time: '09:00',
    slot_time_display: '09:00 AM',
    patient_name: 'Rajesh Kumar',
    clinic_name: 'CareRemind Demo Clinic',
    clinic_address: 'Sector 5, Salt Lake, Kolkata',
    clinic_location_id: 'demo-loc',
    status: 'confirmed',
    payment_status: 'paid',
    amount: 500,
    confirmed_at: new Date().toISOString(),
  },
  {
    id: 'd2',
    serial_number: 2,
    booking_date: TODAY,
    slot_time: '09:30',
    slot_time_display: '09:30 AM',
    patient_name: 'Priya Singh',
    clinic_name: 'CareRemind Demo Clinic',
    clinic_address: 'Sector 5, Salt Lake, Kolkata',
    clinic_location_id: 'demo-loc',
    status: 'confirmed',
    payment_status: 'paid',
    amount: 500,
    confirmed_at: new Date().toISOString(),
  },
  {
    id: 'd3',
    serial_number: 3,
    booking_date: TODAY,
    slot_time: '10:00',
    slot_time_display: '10:00 AM',
    patient_name: 'Amit Sharma',
    clinic_name: 'CareRemind Demo Clinic',
    clinic_address: 'Sector 5, Salt Lake, Kolkata',
    clinic_location_id: 'demo-loc',
    status: 'reserved',
    payment_status: 'pending',
    amount: 500,
    confirmed_at: null,
  },
  {
    id: 'd4',
    serial_number: 4,
    booking_date: TODAY,
    slot_time: '10:30',
    slot_time_display: '10:30 AM',
    patient_name: 'Neha Gupta',
    clinic_name: 'CareRemind Demo Clinic',
    clinic_address: 'Sector 5, Salt Lake, Kolkata',
    clinic_location_id: 'demo-loc',
    status: 'confirmed',
    payment_status: 'paid',
    amount: 300,
    confirmed_at: new Date().toISOString(),
  },
  {
    id: 'd5',
    serial_number: 5,
    booking_date: TODAY,
    slot_time: '11:00',
    slot_time_display: '11:00 AM',
    patient_name: 'Mohan Roy',
    clinic_name: 'CareRemind Demo Clinic',
    clinic_address: 'Sector 5, Salt Lake, Kolkata',
    clinic_location_id: 'demo-loc',
    status: 'cancelled',
    payment_status: 'refunded',
    amount: 0,
    confirmed_at: null,
  },
];

export const demoReminders = [
  { id: 'r1', reminder_number: 312, channel: 'whatsapp', status: 'Sent', scheduled_at: new Date(Date.now() - 3_600_000).toISOString(), sent_at: new Date(Date.now() - 3_590_000).toISOString(), error_log: null },
  { id: 'r2', reminder_number: 311, channel: 'whatsapp', status: 'Sent', scheduled_at: new Date(Date.now() - 7_200_000).toISOString(), sent_at: new Date(Date.now() - 7_190_000).toISOString(), error_log: null },
  { id: 'r3', reminder_number: 310, channel: 'whatsapp', status: 'Failed', scheduled_at: new Date(Date.now() - 10_800_000).toISOString(), sent_at: null, error_log: 'WhatsApp number not registered' },
  { id: 'r4', reminder_number: 309, channel: 'whatsapp', status: 'Pending', scheduled_at: new Date(Date.now() + 3_600_000).toISOString(), sent_at: null, error_log: null },
  { id: 'r5', reminder_number: 308, channel: 'whatsapp', status: 'Sent', scheduled_at: new Date(Date.now() - 86_400_000).toISOString(), sent_at: new Date(Date.now() - 86_390_000).toISOString(), error_log: null },
  { id: 'r6', reminder_number: 307, channel: 'whatsapp', status: 'Sent', scheduled_at: new Date(Date.now() - 90_000_000).toISOString(), sent_at: new Date(Date.now() - 89_990_000).toISOString(), error_log: null },
];
