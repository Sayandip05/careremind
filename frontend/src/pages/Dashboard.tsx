import { useEffect, useState } from 'react';
import { dashboardApi } from '@/api/dashboard';
import { useAuthStore } from '@/store/authStore';
import { Users, Clock, CheckCircle, XCircle, Upload, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Stats {
  total_patients: number;
  pending_reminders: number;
  sent_reminders: number;
  failed_reminders: number;
  success_rate: number;
  total_uploads: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    dashboardApi.getStats()
      .then((res) => setStats(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
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
        <h1 className="text-lg font-semibold text-slate-800">Dashboard</h1>
        <p className="text-sm text-slate-500 mt-0.5">Welcome back, Dr. {user?.doctor_name?.split(' ').pop() || 'Doctor'}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { label: 'Total Patients', value: stats?.total_patients ?? 0, icon: Users },
          { label: 'Pending', value: stats?.pending_reminders ?? 0, icon: Clock },
          { label: 'Sent', value: stats?.sent_reminders ?? 0, icon: CheckCircle },
          { label: 'Failed', value: stats?.failed_reminders ?? 0, icon: XCircle },
          { label: 'Uploads', value: stats?.total_uploads ?? 0, icon: Upload },
          { label: 'Success Rate', value: `${stats?.success_rate ?? 0}%`, icon: TrendingUp },
        ].map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} className="bg-white border border-slate-200 rounded-lg p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">{card.label}</p>
                  <p className="text-2xl font-semibold text-slate-800 mt-1">{card.value}</p>
                </div>
                <Icon className="w-5 h-5 text-slate-400" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-sm font-medium text-slate-700 mb-3">Quick actions</h2>
        <div className="flex gap-3">
          <button onClick={() => navigate('/upload')} className="px-4 py-2 text-sm font-medium bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors">
            Upload data
          </button>
          <button onClick={() => navigate('/patients')} className="px-4 py-2 text-sm font-medium border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors">
            View patients
          </button>
          <button onClick={() => navigate('/reminders')} className="px-4 py-2 text-sm font-medium border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors">
            Reminders
          </button>
        </div>
      </div>
    </div>
  );
}
