import { useEffect, useState } from 'react';
import { patientsApi } from '@/api/patients';

interface Patient {
  id: string;
  name: string;
  phone: string;
  age: number | null;
  gender: string | null;
  language: string | null;
  preferred_channel: string;
  opted_out: boolean;
  created_at: string;
}

export default function Patients() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const perPage = 15;

  useEffect(() => {
    setLoading(true);
    patientsApi.list(page, perPage)
      .then((res) => { setPatients(res.data.patients); setTotal(res.data.total); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page]);

  const totalPages = Math.ceil(total / perPage);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-6 h-6 border-2 border-slate-200 border-t-slate-600 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-800">Patients</h1>
        <p className="text-sm text-slate-500 mt-0.5">{total} patients</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 bg-slate-50">
              <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Name</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Phone</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Age</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Gender</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Channel</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-slate-500">Status</th>
            </tr>
          </thead>
          <tbody>
            {patients.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-10 text-center text-slate-400">No patients yet. Upload data to get started.</td></tr>
            ) : patients.map((p) => (
              <tr key={p.id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-medium text-slate-700">{p.name}</td>
                <td className="px-4 py-3 text-slate-500 font-mono text-xs">{p.phone}</td>
                <td className="px-4 py-3 text-slate-500">{p.age || '—'}</td>
                <td className="px-4 py-3 text-slate-500 capitalize">{p.gender || '—'}</td>
                <td className="px-4 py-3">
                  <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600">{p.preferred_channel}</span>
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-0.5 rounded ${p.opted_out ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-700'}`}>
                    {p.opted_out ? 'Opted out' : 'Active'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-slate-100">
            <span className="text-xs text-slate-400">Page {page} of {totalPages}</span>
            <div className="flex gap-1">
              <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="px-3 py-1 text-xs border border-slate-200 rounded hover:bg-slate-50 disabled:opacity-40">Prev</button>
              <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages} className="px-3 py-1 text-xs border border-slate-200 rounded hover:bg-slate-50 disabled:opacity-40">Next</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
