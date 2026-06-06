import { useEffect, useState } from 'react';
import { billingApi } from '@/api/billing';
import { CreditCard, CheckCircle, Clock, AlertCircle, ChevronLeft, ChevronRight } from 'lucide-react';

interface Payment {
  id: string;
  amount: number;
  currency: string;
  status: string;
  description: string;
  created_at: string;
}

interface SubscriptionStatus {
  plan: string;
  is_active: boolean;
  trial_ends_at: string | null;
}

interface PaginatedPayments {
  data: Payment[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}

const PLAN_LABELS: Record<string, string> = {
  free: 'Free',
  starter: 'Starter',
  pro: 'Pro',
  enterprise: 'Enterprise',
};

const PLAN_COLORS: Record<string, string> = {
  free: 'bg-slate-100 text-slate-700',
  starter: 'bg-blue-50 text-blue-700',
  pro: 'bg-violet-50 text-violet-700',
  enterprise: 'bg-amber-50 text-amber-700',
};

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  success: { label: 'Paid', color: 'text-emerald-600', icon: <CheckCircle className="w-3.5 h-3.5" /> },
  captured: { label: 'Paid', color: 'text-emerald-600', icon: <CheckCircle className="w-3.5 h-3.5" /> },
  pending: { label: 'Pending', color: 'text-amber-600', icon: <Clock className="w-3.5 h-3.5" /> },
  failed: { label: 'Failed', color: 'text-red-600', icon: <AlertCircle className="w-3.5 h-3.5" /> },
};

export default function Billing() {
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null);
  const [payments, setPayments] = useState<PaginatedPayments | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [subLoading, setSubLoading] = useState(true);

  useEffect(() => {
    billingApi.getStatus()
      .then((res) => setSubscription(res.data))
      .catch(() => {})
      .finally(() => setSubLoading(false));
  }, []);

  useEffect(() => {
    setLoading(true);
    billingApi.getHistory(page, 10)
      .then((res) => setPayments(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page]);

  const formatAmount = (amount: number, currency = 'INR') => {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency }).format(amount / 100);
  };

  const formatDate = (dateStr: string) =>
    new Date(dateStr).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-lg font-semibold text-slate-800">Billing</h1>
        <p className="text-sm text-slate-500 mt-0.5">Manage your subscription and payment history</p>
      </div>

      {/* Subscription Status Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center shrink-0">
              <CreditCard className="w-5 h-5 text-slate-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-700">Current Plan</p>
              {subLoading ? (
                <div className="h-5 w-20 bg-slate-100 rounded animate-pulse mt-1" />
              ) : (
                <span
                  className={`inline-block mt-1 px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                    PLAN_COLORS[subscription?.plan ?? 'free']
                  }`}
                >
                  {PLAN_LABELS[subscription?.plan ?? 'free']}
                </span>
              )}
            </div>
          </div>

          <div className="text-right">
            <p className="text-xs text-slate-500">Account status</p>
            {subLoading ? (
              <div className="h-4 w-16 bg-slate-100 rounded animate-pulse mt-1" />
            ) : (
              <div className={`flex items-center gap-1.5 mt-1 justify-end ${subscription?.is_active ? 'text-emerald-600' : 'text-red-600'}`}>
                {subscription?.is_active ? (
                  <CheckCircle className="w-3.5 h-3.5" />
                ) : (
                  <AlertCircle className="w-3.5 h-3.5" />
                )}
                <span className="text-xs font-medium">
                  {subscription?.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            )}
          </div>
        </div>

        {subscription?.trial_ends_at && (
          <div className="mt-4 pt-4 border-t border-slate-100">
            <p className="text-xs text-slate-500">
              Trial ends on{' '}
              <span className="font-medium text-slate-700">
                {formatDate(subscription.trial_ends_at)}
              </span>
            </p>
          </div>
        )}
      </div>

      {/* Payment History */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100">
          <h2 className="text-sm font-semibold text-slate-700">Payment History</h2>
        </div>

        {loading ? (
          <div className="divide-y divide-slate-100">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="px-6 py-4 flex items-center gap-4">
                <div className="h-4 w-24 bg-slate-100 rounded animate-pulse" />
                <div className="h-4 w-32 bg-slate-100 rounded animate-pulse flex-1" />
                <div className="h-4 w-16 bg-slate-100 rounded animate-pulse" />
                <div className="h-4 w-14 bg-slate-100 rounded animate-pulse" />
              </div>
            ))}
          </div>
        ) : payments?.data.length === 0 ? (
          <div className="px-6 py-16 text-center">
            <CreditCard className="w-8 h-8 text-slate-300 mx-auto mb-3" />
            <p className="text-sm font-medium text-slate-600">No payments yet</p>
            <p className="text-xs text-slate-400 mt-1">Your payment history will appear here</p>
          </div>
        ) : (
          <>
            {/* Scrollable table wrapper */}
            <div className="overflow-x-auto">
              <table className="w-full text-sm min-w-[480px]">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50">
                    <th className="text-left px-6 py-2.5 text-xs font-medium text-slate-400 uppercase tracking-wide">Date</th>
                    <th className="text-left px-6 py-2.5 text-xs font-medium text-slate-400 uppercase tracking-wide">Description</th>
                    <th className="text-left px-6 py-2.5 text-xs font-medium text-slate-400 uppercase tracking-wide">Amount</th>
                    <th className="text-left px-6 py-2.5 text-xs font-medium text-slate-400 uppercase tracking-wide">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {payments?.data.map((payment) => {
                    const statusCfg = STATUS_CONFIG[payment.status] ?? STATUS_CONFIG.pending;
                    return (
                      <tr key={payment.id}>
                        <td className="px-6 py-4 text-slate-500 text-xs whitespace-nowrap">{formatDate(payment.created_at)}</td>
                        <td className="px-6 py-4 text-slate-700 font-medium max-w-[200px] truncate pr-4">
                          {payment.description || 'Payment'}
                        </td>
                        <td className="px-6 py-4 text-slate-800 font-semibold whitespace-nowrap">
                          {formatAmount(payment.amount, payment.currency)}
                        </td>
                        <td className={`px-6 py-4 flex items-center gap-1 font-medium ${statusCfg.color}`}>
                          {statusCfg.icon}
                          {statusCfg.label}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {payments && payments.pagination.total_pages > 1 && (
              <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between">
                <p className="text-xs text-slate-500">
                  Showing {(page - 1) * 10 + 1}–{Math.min(page * 10, payments.pagination.total)} of{' '}
                  {payments.pagination.total} payments
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="p-1.5 rounded-md border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <span className="text-xs font-medium text-slate-700">
                    Page {page} of {payments.pagination.total_pages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(payments.pagination.total_pages, p + 1))}
                    disabled={page === payments.pagination.total_pages}
                    className="p-1.5 rounded-md border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
