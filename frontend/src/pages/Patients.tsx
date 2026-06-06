import { useEffect, useRef, useState } from 'react';
import { bookingApi } from '@/api/booking';
import { clinicsApi } from '@/api/clinics';
import { useGuestMode } from '@/context/GuestModeContext';
import { demoBookings } from '@/data/demoData';
import {
  CalendarDays,
  Download,
  Loader2,
  MapPin,
  RefreshCw,
  Wifi,
  CalendarCheck,
} from 'lucide-react';

// ─── Types ────────────────────────────────────────────────────────────────────

interface BookingRow {
  id: string;
  serial_number: number | null;
  booking_date: string;
  slot_time: string;
  slot_time_display: string;
  patient_name: string;
  clinic_name: string;
  clinic_address: string;
  clinic_location_id: string;
  status: string;
  payment_status: string;
  amount: number;
  confirmed_at: string | null;
}

interface ClinicOption {
  id: string;
  clinic_name: string;
}

const REFRESH_INTERVAL_MS = 30_000;

// ─── Helpers ─────────────────────────────────────────────────────────────────

function todayISO(): string {
  return new Date().toISOString().split('T')[0];
}

function formatDateLabel(iso: string): string {
  const d = new Date(iso + 'T00:00:00');
  const today = todayISO();
  const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
  if (iso === today) return 'Today';
  if (iso === yesterday) return 'Yesterday';
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

function statusBadge(status: string) {
  const map: Record<string, string> = {
    confirmed: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
    completed: 'bg-blue-50 text-blue-700 border border-blue-200',
    cancelled: 'bg-red-50 text-red-600 border border-red-200',
    reserved: 'bg-amber-50 text-amber-700 border border-amber-200',
    expired: 'bg-slate-100 text-slate-500 border border-slate-200',
  };
  return map[status] ?? 'bg-slate-100 text-slate-500 border border-slate-200';
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function Bookings() {
  const { isGuest, requireAuth } = useGuestMode();
  const [selectedDate, setSelectedDate] = useState<string>(todayISO());
  const [selectedClinic, setSelectedClinic] = useState<string>('');
  const [clinics, setClinics] = useState<ClinicOption[]>([]);
  const [bookings, setBookings] = useState<BookingRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [countdown, setCountdown] = useState(REFRESH_INTERVAL_MS / 1000);
  const [downloading, setDownloading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const refreshRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ── Fetch clinics once (skip for guests) ──────────────────────────────────
  useEffect(() => {
    if (isGuest) return;
    clinicsApi.list().then((res) => {
      setClinics(res.data?.clinics ?? []);
    }).catch(() => {});
  }, [isGuest]);

  // ── Fetch bookings (demo data for guests) ────────────────────────────────
  const fetchBookings = async (isBackground = false) => {
    if (isGuest) {
      setBookings(demoBookings as BookingRow[]);
      setLastUpdated(new Date());
      setLoading(false);
      setRefreshing(false);
      return;
    }
    if (isBackground) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    try {
      const res = await bookingApi.listBookings(
        selectedDate,
        selectedClinic || undefined,
      );
      setBookings(res.data ?? []);
      setLastUpdated(new Date());
    } catch {
      // Keep previous data on background refresh failure
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchBookings(false);
  }, [selectedDate, selectedClinic, isGuest]);

  // ── Auto-refresh every 30 s ───────────────────────────────────────────────
  useEffect(() => {
    setCountdown(REFRESH_INTERVAL_MS / 1000);

    if (refreshRef.current) clearInterval(refreshRef.current);
    if (countdownRef.current) clearInterval(countdownRef.current);

    refreshRef.current = setInterval(() => {
      fetchBookings(true);
      setCountdown(REFRESH_INTERVAL_MS / 1000);
    }, REFRESH_INTERVAL_MS);

    countdownRef.current = setInterval(() => {
      setCountdown((c) => (c > 0 ? c - 1 : 0));
    }, 1000);

    return () => {
      if (refreshRef.current) clearInterval(refreshRef.current);
      if (countdownRef.current) clearInterval(countdownRef.current);
    };
  }, [selectedDate, selectedClinic]);

  // ── PDF download (gated for guests) ──────────────────────────────────────
  const handleDownload = () => {
    requireAuth(() => {
      setDownloading(true);
      const url = bookingApi.getSchedulePdfUrl(
        selectedDate,
        selectedClinic || undefined,
      );
      const a = document.createElement('a');
      a.href = url;
      a.download = `schedule_${selectedDate}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => setDownloading(false), 2000);
    });
  };

  // ── Render ────────────────────────────────────────────────────────────────
  const dateLabel = formatDateLabel(selectedDate);
  const total = bookings.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-lg font-semibold text-slate-800">Online Bookings</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Patients who booked via WhatsApp — {dateLabel}
          </p>
        </div>

        {/* Live badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-full">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs font-medium text-emerald-700 flex items-center gap-1">
            <Wifi className="w-3 h-3" />
            Live · refreshes in {countdown}s
          </span>
          {refreshing && <Loader2 className="w-3 h-3 text-emerald-600 animate-spin" />}
        </div>
      </div>

      {/* Filters + Actions */}
      <div className="flex items-center gap-3 flex-wrap">
        {/* Date picker */}
        <div className="relative flex items-center">
          <CalendarDays className="absolute left-2.5 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
          <input
            type="date"
            id="booking-date-picker"
            value={selectedDate}
            max={todayISO()}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="pl-8 pr-3 py-2 text-sm border border-slate-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-shadow"
          />
        </div>

        {/* Clinic filter */}
        <div className="relative flex items-center">
          <MapPin className="absolute left-2.5 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
          <select
            id="clinic-filter"
            value={selectedClinic}
            onChange={(e) => setSelectedClinic(e.target.value)}
            className="pl-8 pr-8 py-2 text-sm border border-slate-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-shadow appearance-none min-w-[180px]"
          >
            <option value="">All Clinics</option>
            {clinics.map((c) => (
              <option key={c.id} value={c.id}>{c.clinic_name}</option>
            ))}
          </select>
        </div>

        {/* Manual refresh */}
        <button
          onClick={() => fetchBookings(false)}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-2 text-sm border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 disabled:opacity-50 transition-colors"
          title="Refresh now"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>

        {/* Download PDF */}
        <button
          id="download-pdf-btn"
          onClick={handleDownload}
          disabled={downloading}
          className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium bg-slate-900 text-white rounded-lg hover:bg-slate-800 disabled:opacity-60 disabled:cursor-not-allowed transition-colors ml-auto"
        >
          {downloading
            ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
            : <Download className="w-3.5 h-3.5" />}
          {downloading ? 'Preparing…' : 'Download PDF'}
        </button>
      </div>

      {/* Stats strip */}
      {!loading && (
        <div className="flex items-center gap-6 px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm">
          <div>
            <span className="text-2xl font-bold text-slate-800">{total}</span>
            <span className="text-slate-500 ml-1.5">
              {total === 1 ? 'booking' : 'bookings'}
            </span>
          </div>
          <div className="h-6 w-px bg-slate-200" />
          <div className="text-slate-500">
            <span className="font-medium text-slate-700">
              ₹{bookings.reduce((s, b) => s + b.amount, 0).toLocaleString('en-IN')}
            </span>
            {' '}total revenue
          </div>
          {lastUpdated && (
            <>
              <div className="h-6 w-px bg-slate-200" />
              <div className="text-slate-400 text-xs ml-auto">
                Last updated {lastUpdated.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </div>
            </>
          )}
        </div>
      )}

      {/* Table */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-6 h-6 text-slate-400 animate-spin" />
          </div>
        ) : bookings.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <CalendarCheck className="w-10 h-10 text-slate-300 mb-3" />
            <p className="text-sm font-medium text-slate-500">No bookings for {dateLabel}</p>
            <p className="text-xs text-slate-400 mt-1">
              Patients who book via WhatsApp will appear here.
            </p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50">
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500">#</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500">Time</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500">Patient Name</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500">Clinic</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500">Location</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500">Status</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500">Amount</th>
              </tr>
            </thead>
            <tbody>
              {bookings.map((b, idx) => (
                <tr
                  key={b.id}
                  className="border-b border-slate-50 last:border-0 hover:bg-slate-50/70 transition-colors"
                >
                  {/* Serial number */}
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-100 text-xs font-bold text-slate-600">
                      {b.serial_number ?? idx + 1}
                    </span>
                  </td>

                  {/* Time */}
                  <td className="px-4 py-3 font-mono text-xs text-slate-600 whitespace-nowrap">
                    {b.slot_time_display}
                  </td>

                  {/* Patient name */}
                  <td className="px-4 py-3 font-medium text-slate-800">
                    {b.patient_name}
                  </td>

                  {/* Clinic name */}
                  <td className="px-4 py-3 text-slate-600">{b.clinic_name}</td>

                  {/* Location */}
                  <td className="px-4 py-3 text-slate-400 text-xs max-w-[200px] truncate">
                    {b.clinic_address}
                  </td>

                  {/* Status */}
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${statusBadge(b.status)}`}>
                      {b.status}
                    </span>
                  </td>

                  {/* Amount */}
                  <td className="px-4 py-3 text-right font-medium text-slate-700">
                    ₹{b.amount.toLocaleString('en-IN')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Footer hint */}
      {!loading && bookings.length > 0 && (
        <p className="text-xs text-slate-400 text-center">
          Showing {total} confirmed booking{total !== 1 ? 's' : ''} · Auto-refreshes every 30 seconds
        </p>
      )}
    </div>
  );
}
