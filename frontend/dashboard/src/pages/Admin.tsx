import { useEffect, useState } from 'react';
import client from '@/api/client';
import { Users, Bell, Upload, TrendingUp } from 'lucide-react';

interface Tenant {
  id: string;
  doctor_name: string;
  clinic_name: string;
  email: string;
  specialty: string | null;
  plan: string;
  created_at: string;
}

interface PlatformStats {
  total_tenants: number;
  total_patients: number;
  total_reminders: number;
  total_uploads: number;
}

export default function Admin() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      client.get('/admin/tenants').catch(() => ({ data: [] })),
      client.get('/admin/stats').catch(() => ({ data: null })),
    ]).then(([tenantsRes, statsRes]) => {
      setTenants(Array.isArray(tenantsRes.data) ? tenantsRes.data : []);
      setStats(statsRes.data);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-6 h-6 border-2 border-slate-200 border-t-slate-600 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-lg font-semibold text-slate-800">Admin Panel</h1>
        <p className="text-sm text-slate-500 mt-0.5">Platform overview & tenant management</p>
      </div>

      {/* Platform Stats */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'Doctors', value: stats.total_tenants, icon: Users },
            { label: 'All Patients', value: stats.total_patients, icon: Users },
            { label: 'All Reminders', value: stats.total_reminders, icon: Bell },
            { label: 'All Uploads', value: stats.total_uploads, icon: Upload },
          ].map((card) => {
            const Icon = card.icon;
            return (
              <div key={card.label} className="bg-white border border-slate-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">{card.label}</p>
                    <p className="text-xl font-semibold text-slate-800 mt-1">{card.value}</p>
                  </div>
                  <Icon className="w-4 h-4 text-slate-400" />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Tenants Table */}
      <div>
        <h2 className="text-sm font-medium text-slate-700 mb-3">Registered Doctors</h2>
        <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50">
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Doctor</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Clinic</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Email</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Specialty</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Plan</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Joined</th>
              </tr>
            </thead>
            <tbody>
              {tenants.length === 0 ? (
                <tr><td colSpan={6} className="px-4 py-10 text-center text-slate-400">No doctors registered yet.</td></tr>
              ) : tenants.map((t) => (
                <tr key={t.id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-slate-700">{t.doctor_name}</td>
                  <td className="px-4 py-3 text-slate-500">{t.clinic_name}</td>
                  <td className="px-4 py-3 text-slate-500 text-xs">{t.email}</td>
                  <td className="px-4 py-3 text-slate-500 capitalize">{t.specialty || '—'}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                      t.plan === 'pro' ? 'bg-blue-50 text-blue-700' :
                      t.plan === 'enterprise' ? 'bg-violet-50 text-violet-700' :
                      'bg-slate-100 text-slate-500'
                    }`}>
                      {t.plan}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">
                    {new Date(t.created_at).toLocaleDateString('en-IN', { dateStyle: 'medium' })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
