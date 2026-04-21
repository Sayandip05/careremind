import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authApi } from '@/api/auth';
import { useAuthStore } from '@/store/authStore';
import { BellRing, ArrowRight } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL?.replace('/api/v1', '') || 'http://localhost:8000';

export default function Login() {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [doctorName, setDoctorName] = useState('');
  const [clinicName, setClinicName] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [customSpecialty, setCustomSpecialty] = useState('');
  const [whatsappNumber, setWhatsappNumber] = useState('');
  const [languagePreference, setLanguagePreference] = useState('english');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // The actual specialty value sent to the backend
  const effectiveSpecialty = specialty === 'other' ? customSpecialty.trim() : specialty;

  const { login } = useAuthStore();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Handle OAuth callback — detect token in URL params from backend redirect
  useEffect(() => {
    const token = searchParams.get('token');
    const tenantId = searchParams.get('tenant_id');
    const doctorName = searchParams.get('doctor_name');
    const oauthError = searchParams.get('error');

    if (oauthError) {
      setError(decodeURIComponent(oauthError));
      return;
    }

    if (token && tenantId && doctorName) {
      // OAuth login successful — store token and redirect to dashboard
      login(token, {
        id: tenantId,
        doctor_name: doctorName,
        clinic_name: '',
        email: '',
        specialty: null,
        plan: 'free',
      });
      navigate('/', { replace: true });
    }
  }, [searchParams, login, navigate]);

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
          whatsapp_number: whatsappNumber || undefined,
          language_preference: languagePreference,
        });
      }
      const res = await authApi.login(email, password);
      const { access_token, tenant_id, doctor_name, clinic_name, email: userEmail, specialty: userSpecialty, plan } = res.data;
      login(access_token, {
        id: tenant_id,
        doctor_name,
        clinic_name: clinic_name || clinicName,
        email: userEmail || email,
        specialty: userSpecialty || effectiveSpecialty || null,
        plan: plan || 'free',
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
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">WhatsApp Number</label>
                  <input 
                    type="tel" 
                    value={whatsappNumber} 
                    onChange={(e) => setWhatsappNumber(e.target.value)} 
                    className={inputClass} 
                    placeholder="+91 98765 43210" 
                  />
                  <p className="text-xs text-slate-500 mt-1">For receiving notifications and uploading via WhatsApp</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Preferred Language</label>
                  <select
                    value={languagePreference}
                    onChange={(e) => setLanguagePreference(e.target.value)}
                    className={inputClass}
                  >
                    <option value="english">English</option>
                    <option value="hindi">Hindi</option>
                    <option value="tamil">Tamil</option>
                    <option value="marathi">Marathi</option>
                    <option value="bengali">Bengali</option>
                  </select>
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

          {/* OAuth Divider + Buttons — only on sign-in */}
          {!isRegister && (
            <>
              <div className="my-5 flex items-center gap-3">
                <div className="flex-1 h-px bg-slate-200" />
                <span className="text-xs text-slate-400">or continue with</span>
                <div className="flex-1 h-px bg-slate-200" />
              </div>

              <div className="flex gap-3">
                <a
                  href={`${API_URL}/api/v1/auth/login/google`}
                  className="flex-1 h-10 flex items-center justify-center gap-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
                  Google
                </a>
                <a
                  href={`${API_URL}/api/v1/auth/login/facebook`}
                  className="flex-1 h-10 flex items-center justify-center gap-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="#1877F2"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                  Facebook
                </a>
              </div>
            </>
          )}

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
