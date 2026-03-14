import { useEffect, useState } from 'react';
import { remindersApi } from '@/api/reminders';
import { MessageSquare, Smartphone } from 'lucide-react';

interface Reminder {
  id: string;
  reminder_number: number;
  channel: string;
  status: string;
  scheduled_at: string;
  sent_at: string | null;
  error_log: string | null;
}

const filters = ['All', 'Pending', 'Sent', 'Failed', 'Optout'];

export default function Reminders() {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    remindersApi.list(page, 20, filter === 'All' ? undefined : filter)
      .then((res) => { setReminders(res.data.reminders); setTotal(res.data.total); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page, filter]);

  const totalPages = Math.ceil(total / 20);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-800">Reminders</h1>
        <p className="text-sm text-slate-500 mt-0.5">{total} reminders</p>
      </div>

      <div className="flex gap-1">
        {filters.map((f) => (
          <button
            key={f}
            onClick={() => { setFilter(f); setPage(1); }}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              filter === f ? 'bg-slate-900 text-white' : 'text-slate-500 hover:bg-slate-100'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <div className="w-6 h-6 border-2 border-slate-200 border-t-slate-600 rounded-full animate-spin" />
        </div>
      ) : reminders.length === 0 ? (
        <div className="text-center py-12 text-sm text-slate-400 bg-white border border-slate-200 rounded-lg">No reminders found.</div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-lg divide-y divide-slate-100">
          {reminders.map((r) => (
            <div key={r.id} className="flex items-center justify-between px-4 py-3.5 hover:bg-slate-50 transition-colors">
              <div className="flex items-center gap-3">
                {r.channel === 'whatsapp' ? <MessageSquare className="w-4 h-4 text-slate-400" /> : <Smartphone className="w-4 h-4 text-slate-400" />}
                <div>
                  <p className="text-sm text-slate-700">Reminder #{r.reminder_number} · {r.channel}</p>
                  <p className="text-xs text-slate-400">
                    {new Date(r.scheduled_at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}
                    {r.sent_at && ` · Sent ${new Date(r.sent_at).toLocaleString('en-IN', { timeStyle: 'short' })}`}
                  </p>
                  {r.error_log && <p className="text-xs text-red-500 mt-0.5">{r.error_log}</p>}
                </div>
              </div>
              <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                r.status === 'Sent' ? 'bg-green-50 text-green-700' :
                r.status === 'Failed' ? 'bg-red-50 text-red-600' :
                r.status === 'Pending' ? 'bg-amber-50 text-amber-700' :
                'bg-slate-100 text-slate-500'
              }`}>
                {r.status}
              </span>
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Page {page} of {totalPages}</span>
          <div className="flex gap-1">
            <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="px-3 py-1 text-xs border border-slate-200 rounded hover:bg-slate-50 disabled:opacity-40">Prev</button>
            <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages} className="px-3 py-1 text-xs border border-slate-200 rounded hover:bg-slate-50 disabled:opacity-40">Next</button>
          </div>
        </div>
      )}
    </div>
  );
}
