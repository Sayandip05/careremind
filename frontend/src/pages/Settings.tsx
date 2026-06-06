import { useEffect, useState } from 'react';
import { authApi } from '@/api/auth';
import { clinicsApi } from '@/api/clinics';
import { useAuthStore } from '@/store/authStore';
import {
  User, Bell, Shield, CheckCircle, Loader2,
  MapPin, Plus, Pencil, Trash2, X, Save, Building2,
} from 'lucide-react';

// ─── Types ────────────────────────────────────────────────────────────────────

interface ProfileForm {
  doctor_name: string;
  clinic_name: string;
  specialty: string;
  whatsapp_number: string;
}

interface ClinicLocation {
  id: string;
  clinic_name: string;
  address_line: string;
  city: string;
  pincode: string;
  state?: string;
  phone?: string;
  is_active: boolean;
}

interface ClinicForm {
  clinic_name: string;
  address_line: string;
  city: string;
  pincode: string;
  state: string;
  phone: string;
}

const EMPTY_CLINIC_FORM: ClinicForm = {
  clinic_name: '',
  address_line: '',
  city: '',
  pincode: '',
  state: '',
  phone: '',
};

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

// ─── Sub-components ───────────────────────────────────────────────────────────

const inputClass =
  'w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-shadow disabled:bg-slate-50 disabled:text-slate-400 disabled:cursor-not-allowed';

function SectionHeader({ icon, title }: { icon: React.ReactNode; title: string }) {
  return (
    <div className="flex items-center gap-3 px-6 py-4 border-b border-slate-100 bg-slate-50">
      <span className="text-slate-500">{icon}</span>
      <h2 className="text-sm font-semibold text-slate-700">{title}</h2>
    </div>
  );
}

// ─── Clinic Location Form Modal ───────────────────────────────────────────────

interface ClinicModalProps {
  initial?: ClinicLocation | null;
  onSave: (form: ClinicForm) => Promise<void>;
  onClose: () => void;
}

function ClinicModal({ initial, onSave, onClose }: ClinicModalProps) {
  const [form, setForm] = useState<ClinicForm>(
    initial
      ? {
          clinic_name: initial.clinic_name,
          address_line: initial.address_line,
          city: initial.city,
          pincode: initial.pincode,
          state: initial.state ?? '',
          phone: initial.phone ?? '',
        }
      : EMPTY_CLINIC_FORM,
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handle = (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((p) => ({ ...p, [e.target.name]: e.target.value }));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await onSave(form);
      onClose();
    } catch {
      setError('Failed to save clinic. Please check the details and try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50">
          <div className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-slate-500" />
            <h3 className="text-sm font-semibold text-slate-700">
              {initial ? 'Edit Clinic Location' : 'Add New Clinic Location'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-slate-200 transition-colors"
            aria-label="Close"
          >
            <X className="w-4 h-4 text-slate-500" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={submit} className="p-6 space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-600">Clinic Name *</label>
            <input
              name="clinic_name"
              value={form.clinic_name}
              onChange={handle}
              placeholder="e.g. Morning Clinic – Andheri"
              className={inputClass}
              required
              minLength={2}
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-600">Address *</label>
            <input
              name="address_line"
              value={form.address_line}
              onChange={handle}
              placeholder="123 MG Road, Near City Mall"
              className={inputClass}
              required
              minLength={5}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-600">City *</label>
              <input
                name="city"
                value={form.city}
                onChange={handle}
                placeholder="Mumbai"
                className={inputClass}
                required
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-600">Pincode *</label>
              <input
                name="pincode"
                value={form.pincode}
                onChange={handle}
                placeholder="400001"
                className={inputClass}
                required
                pattern="^\d{6}$"
                maxLength={6}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-600">State</label>
              <input
                name="state"
                value={form.state}
                onChange={handle}
                placeholder="Maharashtra"
                className={inputClass}
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-600">Phone</label>
              <input
                name="phone"
                value={form.phone}
                onChange={handle}
                placeholder="+91 98765 43210"
                className={inputClass}
                type="tel"
              />
            </div>
          </div>

          {error && (
            <p className="text-xs text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 text-sm font-medium bg-slate-900 text-white rounded-lg hover:bg-slate-800 disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
            >
              {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
              {saving ? 'Saving…' : 'Save Clinic'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Main Settings Page ───────────────────────────────────────────────────────

export default function Settings() {
  const { user, setUser } = useAuthStore();

  // Profile state
  const [profileEditing, setProfileEditing] = useState(false);
  const [form, setForm] = useState<ProfileForm>({
    doctor_name: '',
    clinic_name: '',
    specialty: 'general',
    whatsapp_number: '',
  });
  const [savedForm, setSavedForm] = useState<ProfileForm | null>(null);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [profileLoading, setProfileLoading] = useState(true);

  // Clinic locations state
  const [clinics, setClinics] = useState<ClinicLocation[]>([]);
  const [clinicsLoading, setClinicsLoading] = useState(true);
  const [clinicModal, setClinicModal] = useState<{
    open: boolean;
    editing: ClinicLocation | null;
  }>({ open: false, editing: null });
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // ── Load profile ────────────────────────────────────────────────────────────
  useEffect(() => {
    authApi
      .getProfile()
      .then((res) => {
        const data = res.data;
        const loaded: ProfileForm = {
          doctor_name: data.doctor_name ?? '',
          clinic_name: data.clinic_name ?? '',
          specialty: data.specialty ?? 'general',
          whatsapp_number: data.whatsapp_number ?? '',
        };
        setForm(loaded);
        setSavedForm(loaded);
      })
      .catch(() => {
        const fallback: ProfileForm = {
          doctor_name: user?.doctor_name ?? '',
          clinic_name: user?.clinic_name ?? '',
          specialty: user?.specialty ?? 'general',
          whatsapp_number: '',
        };
        setForm(fallback);
        setSavedForm(fallback);
      })
      .finally(() => setProfileLoading(false));
  }, []);

  // ── Load clinic locations ───────────────────────────────────────────────────
  const fetchClinics = async () => {
    setClinicsLoading(true);
    try {
      const res = await clinicsApi.list();
      setClinics(res.data?.clinics ?? []);
    } catch {
      setClinics([]);
    } finally {
      setClinicsLoading(false);
    }
  };

  useEffect(() => {
    fetchClinics();
  }, []);

  // ── Profile handlers ────────────────────────────────────────────────────────
  const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm((p) => ({ ...p, [e.target.name]: e.target.value }));
  };

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaveStatus('saving');
    try {
      const res = await authApi.updateProfile(form);
      setUser({ ...user, ...res.data });
      setSavedForm(form);
      setSaveStatus('saved');
      setProfileEditing(false);
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch {
      setSaveStatus('error');
    }
  };

  const cancelProfileEdit = () => {
    if (savedForm) setForm(savedForm);
    setProfileEditing(false);
    setSaveStatus('idle');
  };

  // ── Clinic handlers ─────────────────────────────────────────────────────────
  const handleClinicSave = async (form: ClinicForm) => {
    if (clinicModal.editing) {
      await clinicsApi.update(clinicModal.editing.id, form);
    } else {
      await clinicsApi.create(form);
    }
    await fetchClinics();
  };

  const handleClinicDelete = async (id: string) => {
    if (!window.confirm('Remove this clinic location?')) return;
    setDeletingId(id);
    try {
      await clinicsApi.delete(id);
      await fetchClinics();
    } finally {
      setDeletingId(null);
    }
  };

  // ── Render ──────────────────────────────────────────────────────────────────
  if (profileLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-5 h-5 text-slate-400 animate-spin" />
      </div>
    );
  }

  return (
    <>
      {/* Clinic modal */}
      {clinicModal.open && (
        <ClinicModal
          initial={clinicModal.editing}
          onSave={handleClinicSave}
          onClose={() => setClinicModal({ open: false, editing: null })}
        />
      )}

      <div className="space-y-8 max-w-2xl mx-auto">
        {/* Header */}
        <div>
          <h1 className="text-lg font-semibold text-slate-800">Settings</h1>
          <p className="text-sm text-slate-500 mt-0.5">Manage your clinic profile and preferences</p>
        </div>

        {/* ── Clinic Profile ─────────────────────────────────────────────────── */}
        <section className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <div className="flex items-center justify-between pr-4 border-b border-slate-100 bg-slate-50">
            <SectionHeader icon={<User className="w-4 h-4" />} title="Clinic Profile" />
            {!profileEditing && (
              <button
                onClick={() => setProfileEditing(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 border border-slate-200 rounded-lg hover:bg-white hover:border-slate-300 transition-all"
              >
                <Pencil className="w-3 h-3" />
                Edit
              </button>
            )}
          </div>

          <form onSubmit={handleProfileSave} className="p-6 space-y-5">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-600">Doctor Name</label>
                <input
                  type="text"
                  name="doctor_name"
                  value={form.doctor_name}
                  onChange={handleProfileChange}
                  placeholder="Dr. Arjun Mehta"
                  className={inputClass}
                  disabled={!profileEditing}
                  required
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-600">Clinic Name</label>
                <input
                  type="text"
                  name="clinic_name"
                  value={form.clinic_name}
                  onChange={handleProfileChange}
                  placeholder="City Health Clinic"
                  className={inputClass}
                  disabled={!profileEditing}
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
                  onChange={handleProfileChange}
                  className={inputClass}
                  disabled={!profileEditing}
                >
                  {SPECIALTIES.map((s) => (
                    <option key={s.value} value={s.value}>{s.label}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-600">WhatsApp Number</label>
                <input
                  type="tel"
                  name="whatsapp_number"
                  value={form.whatsapp_number}
                  onChange={handleProfileChange}
                  placeholder="+91 98765 43210"
                  className={inputClass}
                  disabled={!profileEditing}
                />
                <p className="text-xs text-slate-400">Used to receive daily patient schedule PDFs</p>
              </div>
            </div>

            {profileEditing && (
              <div className="flex items-center justify-between pt-2 border-t border-slate-100">
                <div>
                  {saveStatus === 'saved' && (
                    <span className="flex items-center gap-1.5 text-xs text-emerald-600 font-medium">
                      <CheckCircle className="w-3.5 h-3.5" /> Changes saved
                    </span>
                  )}
                  {saveStatus === 'error' && (
                    <span className="text-xs text-red-600 font-medium">Failed to save. Try again.</span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={cancelProfileEdit}
                    className="px-4 py-2 text-sm font-medium border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={saveStatus === 'saving'}
                    className="px-4 py-2 text-sm font-medium bg-slate-900 text-white rounded-lg hover:bg-slate-800 disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
                  >
                    {saveStatus === 'saving' && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                    {saveStatus === 'saving' ? 'Saving…' : 'Save Changes'}
                  </button>
                </div>
              </div>
            )}
          </form>
        </section>

        {/* ── Clinic Locations ───────────────────────────────────────────────── */}
        <section className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <div className="flex items-center justify-between pr-4 border-b border-slate-100 bg-slate-50">
            <SectionHeader icon={<MapPin className="w-4 h-4" />} title="Clinic Locations" />
            <button
              onClick={() => setClinicModal({ open: true, editing: null })}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-slate-900 rounded-lg hover:bg-slate-800 transition-colors"
            >
              <Plus className="w-3 h-3" />
              Add Clinic
            </button>
          </div>

          <div className="p-6">
            {clinicsLoading ? (
              <div className="flex items-center justify-center py-10">
                <Loader2 className="w-5 h-5 text-slate-400 animate-spin" />
              </div>
            ) : clinics.length === 0 ? (
              <div className="text-center py-10">
                <Building2 className="w-8 h-8 text-slate-300 mx-auto mb-3" />
                <p className="text-sm font-medium text-slate-500">No clinic locations yet</p>
                <p className="text-xs text-slate-400 mt-1">
                  Add your clinic addresses so patients can find you.
                </p>
                <button
                  onClick={() => setClinicModal({ open: true, editing: null })}
                  className="mt-4 flex items-center gap-1.5 px-4 py-2 text-xs font-medium bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors mx-auto"
                >
                  <Plus className="w-3 h-3" />
                  Add First Clinic
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {clinics.map((clinic) => (
                  <div
                    key={clinic.id}
                    className="flex items-start justify-between gap-4 p-4 border border-slate-200 rounded-xl hover:border-slate-300 hover:bg-slate-50/60 transition-all group"
                  >
                    <div className="flex items-start gap-3 min-w-0">
                      <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center shrink-0 mt-0.5">
                        <Building2 className="w-4 h-4 text-slate-500" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-slate-800 truncate">{clinic.clinic_name}</p>
                        <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">
                          {clinic.address_line}, {clinic.city}
                          {clinic.state ? `, ${clinic.state}` : ''} — {clinic.pincode}
                        </p>
                        {clinic.phone && (
                          <p className="text-xs text-slate-400 mt-0.5">{clinic.phone}</p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-1 shrink-0 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => setClinicModal({ open: true, editing: clinic })}
                        className="p-1.5 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition-colors"
                        title="Edit clinic"
                      >
                        <Pencil className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleClinicDelete(clinic.id)}
                        disabled={deletingId === clinic.id}
                        className="p-1.5 rounded-md text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors disabled:opacity-50"
                        title="Remove clinic"
                      >
                        {deletingId === clinic.id
                          ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          : <Trash2 className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* ── Notification Preferences ───────────────────────────────────────── */}
        <section className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <SectionHeader icon={<Bell className="w-4 h-4" />} title="Notification Preferences" />
          <div className="p-6 space-y-4">
            {[
              {
                id: 'notif_whatsapp',
                label: 'WhatsApp reminders',
                description: 'Send patient appointment reminders via WhatsApp',
                defaultChecked: true,
              },
              {
                id: 'notif_daily_pdf',
                label: 'Daily schedule PDF',
                description: "Receive tomorrow's patient schedule at midnight on WhatsApp",
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

        {/* ── Security ───────────────────────────────────────────────────────── */}
        <section className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <SectionHeader icon={<Shield className="w-4 h-4" />} title="Security" />
          <div className="p-6 space-y-3">
            {[
              { label: 'Patient data encryption', value: 'AES-256 active', green: true },
              { label: 'Session token', value: 'JWT · expires in 24h', green: false },
              { label: 'Tenant isolation', value: 'Enabled', green: true },
            ].map(({ label, value, green }) => (
              <div key={label} className="flex items-center justify-between text-sm">
                <span className="text-slate-600">{label}</span>
                <span className={`text-xs font-medium flex items-center gap-1 ${green ? 'text-emerald-600' : 'text-slate-500'}`}>
                  {green && <CheckCircle className="w-3.5 h-3.5" />}
                  {value}
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </>
  );
}
