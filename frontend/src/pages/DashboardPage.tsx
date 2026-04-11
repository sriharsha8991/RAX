import { Link } from 'react-router-dom';
import { getJobs } from '@/services/jobService';
import { useCachedFetch } from '@/hooks/useApiCache';
import type { Job, JobListResponse } from '@/types';
import { Briefcase, FileText, Plus, RefreshCw } from 'lucide-react';
import { PageSpinner, Skeleton } from '@/components/ui/Spinner';

export default function DashboardPage() {
  const { data, loading, error, refetch } = useCachedFetch<JobListResponse>('dashboard:jobs', getJobs);
  const jobs: Job[] = data?.jobs ?? [];

  const activeCount = jobs.filter((j) => j.status === 'active').length;

  if (loading && !data) return <PageSpinner label="Loading dashboard…" />;

  if (error && !data) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <p className="text-sm text-red-600">Failed to load dashboard data.</p>
        <button onClick={refetch} className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors">
          <RefreshCw size={14} /> Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Dashboard</h2>
        <Link
          to="/app/jobs/new"
          className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <Plus size={16} />
          New Job
        </Link>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
              <Briefcase size={18} className="text-indigo-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {loading ? <Skeleton className="h-7 w-10" /> : activeCount}
              </p>
              <p className="text-sm text-gray-500">Active Jobs</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center">
              <FileText size={18} className="text-emerald-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {loading ? <Skeleton className="h-7 w-10" /> : jobs.length}
              </p>
              <p className="text-sm text-gray-500">Total Jobs</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent jobs */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="px-5 py-4 border-b border-gray-200">
          <h3 className="text-sm font-semibold text-gray-900">Recent Jobs</h3>
        </div>
        {loading ? (
          <div className="p-5 space-y-3">
            {[1, 2, 3].map((i) => <Skeleton key={i} className="h-10 w-full" />)}
          </div>
        ) : jobs.length === 0 ? (
          <div className="p-5 text-center text-sm text-gray-500">
            No jobs yet.{' '}
            <Link to="/app/jobs/new" className="text-indigo-600 hover:underline">
              Create your first job
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {jobs.slice(0, 5).map((job) => (
              <Link
                key={job.id}
                to={`/app/jobs/${job.id}`}
                className="flex items-center justify-between px-5 py-3 hover:bg-gray-50 transition-colors"
              >
                <div>
                  <p className="text-sm font-medium text-gray-900">{job.title}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(job.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span
                  className={`text-xs font-medium px-2.5 py-1 rounded-full ${
                    job.status === 'active'
                      ? 'bg-green-100 text-green-700'
                      : job.status === 'closed'
                        ? 'bg-gray-100 text-gray-600'
                        : 'bg-yellow-100 text-yellow-700'
                  }`}
                >
                  {job.status}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
