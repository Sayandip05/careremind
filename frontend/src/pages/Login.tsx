import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '@/api/auth';
import { useAuthStore } from '@/store/authStore';
import { BellRing, ArrowRight } from 'lucide-react';

export default function Login() {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [doctorName, setDoctorName] = useState('');
  const [clinicName, setClinicName] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [customSpecialty, setCustomSpecialty] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // The actual specialty value sent to the backend
  const effectiveSpecialty = specialty === 'other' ? customSpecialty.trim() : specialty;

  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isRegister) {
        await authApi.register({
          doctor_name: doctorName,
          clinic_name: clinicName,
          email,
          password,
          specialty: effectiveSpecialty || undefined,
        });
      }
      const res = await authApi.login(email, password);
      const { access_token, tenant_id, doctor_name } = res.data;
      const profileRes = await authApi.getProfile();
      login(access_token, {
        id: tenant_id,
        doctor_name,
        clinic_name: profileRes.data.clinic_name,
        email: profileRes.data.email,
        specialty: profileRes.data.specialty,
        plan: profileRes.data.plan,
      });
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = "w-full h-10 px-3 text-sm border border-slate-200 rounded-lg bg-white text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:ring-offset-1 transition-shadow";

  return (
    <div className="min-h-screen flex">
      {/* Left — Branding */}
      <div className="hidden lg:flex lg:w-[480px] bg-[#1E5F3A] flex-col justify-between p-10 text-white">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
            <BellRing className="w-5 h-5" />
          </div>
          <span className="text-lg font-semibold">CareRemind</span>
        </div>
        <div>
          <p className="text-2xl font-medium leading-snug mb-4">
            Automate patient reminders<br />for your clinic.
          </p>
          <p className="text-sm text-white/70 leading-relaxed max-w-sm">
            Upload your patient register, and our AI handles follow-up reminders via WhatsApp — automatically.
          </p>
        </div>
        <p className="text-xs text-white/40">© 2026 CareRemind. All rights reserved.</p>
      </div>

      {/* Right — Form */}
      <div className="flex-1 flex items-center justify-center bg-white px-6">
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-[#1E5F3A] rounded-lg flex items-center justify-center text-white">
              <BellRing className="w-5 h-5" />
            </div>
            <span className="text-lg font-semibold text-slate-800">CareRemind</span>
          </div>

          <h1 className="text-xl font-semibold text-slate-800 mb-1">
            {isRegister ? 'Create your account' : 'Sign in'}
          </h1>
          <p className="text-sm text-slate-500 mb-6">
            {isRegister ? 'Start your 14-day free trial' : 'Welcome back. Enter your credentials.'}
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Doctor Name</label>
                  <input type="text" value={doctorName} onChange={(e) => setDoctorName(e.target.value)} required className={inputClass} placeholder="Dr. John Smith" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Clinic Name</label>
                  <input type="text" value={clinicName} onChange={(e) => setClinicName(e.target.value)} required className={inputClass} placeholder="HealthCare Plus" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Specialty</label>
                  <select
                    value={specialty}
                    onChange={(e) => { setSpecialty(e.target.value); setCustomSpecialty(''); }}
                    className={inputClass}
                  >
                    <option value="">Select specialty</option>
                    <option value="general">General Medicine</option>
                    <option value="dental">Dental</option>
                    <option value="eye">Eye / Ophthalmology</option>
                    <option value="orthopedic">Orthopedic</option>
                    <option value="pediatric">Pediatric / Child</option>
                    <option value="skin">Skin / Dermatology</option>
                    <option value="diagnosis">Diagnosis / Lab</option>
                    <option value="other">Other (type below)</option>
                  </select>
                  {specialty === 'other' && (
                    <input
                      type="text"
                      value={customSpecialty}
                      onChange={(e) => setCustomSpecialty(e.target.value)}
                      required
                      className={`mt-2 ${inputClass}`}
                      placeholder="e.g. Psychiatrist, Pulmonologist, Cardiologist..."
                      autoFocus
                    />
                  )}
                </div>
              </>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Email address</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className={inputClass} placeholder="you@clinic.com" />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} className={inputClass} placeholder="Min. 8 characters" />
            </div>

            {error && (
              <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full h-10 bg-slate-900 text-white text-sm font-medium rounded-lg hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {loading ? 'Please wait...' : (
                <>{isRegister ? 'Create account' : 'Continue'} <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button onClick={() => { setIsRegister(!isRegister); setError(''); }} className="text-slate-900 font-medium hover:underline">
              {isRegister ? 'Sign in' : 'Sign up'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
