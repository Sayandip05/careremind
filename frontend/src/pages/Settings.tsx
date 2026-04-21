import { useEffect, useState } from 'react';
import { authApi } from '@/api/auth';
import { useAuthStore } from '@/store/authStore';
import { User, Bell, Shield, CheckCircle, Loader2 } from 'lucide-react';

interface ProfileForm {
  doctor_name: string;
  clinic_name: string;
  specialty: string;
  whatsapp_number: string;
}

const SPECIALTIES = [
  { value: 'dental', label: 'Dental' },
  { value: 'eye', label: 'Eye / Ophthalmology' },
  { value: 'general', label: 'General Practice' },
  { value: 'orthopedic', label: 'Orthopedic' },
  { value: 'pediatric', label: 'Pediatric' },
  { value: 'skin', label: 'Skin / Dermatology' },
  { value: 'diagnosis', label: 'Diagnostic / Pathology' },
];

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

export default function Settings() {
  const { user, setUser } = useAuthStore();
  const [form, setForm] = useState<ProfileForm>({
    doctor_name: '',
    clinic_name: '',
    specialty: 'general',
    whatsapp_number: '',
  });
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    authApi.getProfile()
      .then((res) => {
        const data = res.data;
        setForm({
          doctor_name: data.doctor_name ?? '',
          clinic_name: data.clinic_name ?? '',
          specialty: data.specialty ?? 'general',
          whatsapp_number: data.whatsapp_number ?? '',
        });
      })
      .catch(() => {
        // Fall back to zustand store values
        setForm({
          doctor_name: user?.doctor_name ?? '',
          clinic_name: user?.clinic_name ?? '',
          specialty: user?.specialty ?? 'general',
          whatsapp_number: '',
        });
      })
      .finally(() => setLoading(false));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setSaveStatus('idle');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaveStatus('saving');
    try {
      const res = await authApi.updateProfile(form);
      setUser({ ...user, ...res.data });
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch {
      setSaveStatus('error');
    }
  };

  const inputClass =
    'w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-shadow';

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-5 h-5 text-slate-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-2xl">
      {/* Header */}
      <div>
        <h1 className="text-lg font-semibold text-slate-800">Settings</h1>
        <p className="text-sm text-slate-500 mt-0.5">Manage your clinic profile and preferences</p>
      </div>

      {/* Profile Section */}
      <section className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="flex items-center gap-3 px-6 py-4 border-b border-slate-100 bg-slate-50">
          <User className="w-4 h-4 text-slate-500" />
          <h2 className="text-sm font-semibold text-slate-700">Clinic Profile</h2>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-600">Doctor Name</label>
              <input
                type="text"
                name="doctor_name"
                value={form.doctor_name}
                onChange={handleChange}
                placeholder="Dr. Arjun Mehta"
                className={inputClass}
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-600">Clinic Name</label>
              <input
                type="text"
                name="clinic_name"
                value={form.clinic_name}
                onChange={handleChange}
                placeholder="City Health Clinic"
                className={inputClass}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-600">Specialty</label>
              <select
                name="specialty"
                value={form.specialty}
                onChange={handleChange}
                className={inputClass}
              >
                {SPECIALTIES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-600">WhatsApp Number</label>
              <input
                type="tel"
                name="whatsapp_number"
                value={form.whatsapp_number}
                onChange={handleChange}
                placeholder="+91 98765 43210"
                className={inputClass}
              />
              <p className="text-xs text-slate-400">
                Used to receive daily patient schedule PDFs
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            {saveStatus === 'saved' && (
              <span className="flex items-center gap-1.5 text-xs text-emerald-600 font-medium">
                <CheckCircle className="w-3.5 h-3.5" />
                Changes saved
              </span>
            )}
            {saveStatus === 'error' && (
              <span className="text-xs text-red-600 font-medium">Failed to save. Try again.</span>
            )}
            {saveStatus === 'idle' && <span />}

            <button
              type="submit"
              disabled={saveStatus === 'saving'}
              className="px-4 py-2 text-sm font-medium bg-slate-900 text-white rounded-lg hover:bg-slate-800 disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
            >
              {saveStatus === 'saving' && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
              {saveStatus === 'saving' ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </section>

      {/* Notification Preferences */}
      <section className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="flex items-center gap-3 px-6 py-4 border-b border-slate-100 bg-slate-50">
          <Bell className="w-4 h-4 text-slate-500" />
          <h2 className="text-sm font-semibold text-slate-700">Notification Preferences</h2>
        </div>
        <div className="p-6 space-y-4">
          {[
            {
              id: 'notif_whatsapp',
              label: 'WhatsApp reminders',
              description: 'Send patient appointment reminders via WhatsApp',
              defaultChecked: true,
            },
            {
              id: 'notif_sms',
              label: 'SMS fallback',
              description: 'Fall back to SMS if WhatsApp delivery fails',
              defaultChecked: true,
            },
            {
              id: 'notif_daily_pdf',
              label: 'Daily schedule PDF',
              description: 'Receive tomorrow\'s patient schedule at midnight on WhatsApp',
              defaultChecked: true,
            },
          ].map((pref) => (
            <div key={pref.id} className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-slate-700">{pref.label}</p>
                <p className="text-xs text-slate-400 mt-0.5">{pref.description}</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer shrink-0 mt-0.5">
                <input type="checkbox" defaultChecked={pref.defaultChecked} className="sr-only peer" />
                <div className="w-9 h-5 bg-slate-200 rounded-full peer peer-checked:bg-slate-900 transition-colors after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-4" />
              </label>
            </div>
          ))}
        </div>
      </section>

      {/* Security Info */}
      <section className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="flex items-center gap-3 px-6 py-4 border-b border-slate-100 bg-slate-50">
          <Shield className="w-4 h-4 text-slate-500" />
          <h2 className="text-sm font-semibold text-slate-700">Security</h2>
        </div>
        <div className="p-6 space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-600">Patient data encryption</span>
            <span className="text-emerald-600 font-medium flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5" /> AES-256 active
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-600">Session token</span>
            <span className="text-slate-500 text-xs">JWT · expires in 24h</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-600">Tenant isolation</span>
            <span className="text-emerald-600 font-medium flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5" /> Enabled
            </span>
          </div>
        </div>
      </section>
    </div>
  );
}
