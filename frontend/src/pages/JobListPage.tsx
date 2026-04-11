import { useState } from 'react';
import { Link } from 'react-router-dom';
import { getJobs, deleteJob } from '@/services/jobService';
import { useCachedFetch, clearCache } from '@/hooks/useApiCache';
import type { Job, JobListResponse } from '@/types';
import { Plus, Trash2, Loader2, RefreshCw } from 'lucide-react';
import { PageSpinner, Skeleton } from '@/components/ui/Spinner';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import { useToast } from '@/components/ui/Toast';

export default function JobListPage() {
  const { data, loading, error, refetch } = useCachedFetch<JobListResponse>('jobs:list', getJobs);
  const jobs: Job[] = data?.jobs ?? [];
  const [deleting, setDeleting] = useState<string | null>(null);
  const [confirmTarget, setConfirmTarget] = useState<{ id: string; title: string } | null>(null);
  const { toast } = useToast();

  const handleDelete = async () => {
    if (!confirmTarget) return;
    setDeleting(confirmTarget.id);
    setConfirmTarget(null);
    try {
      await deleteJob(confirmTarget.id);
      clearCache('jobs:list');
      clearCache('dashboard');
      toast('success', `"${confirmTarget.title}" deleted successfully.`);
      refetch();
    } catch {
      toast('error', 'Failed to delete job. Please try again.');
    } finally {
      setDeleting(null);
    }
  };

  if (loading && !data) return <PageSpinner label="Loading jobs…" />;

  if (error && !data) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <p className="text-sm text-red-600">Failed to load jobs.</p>
        <button onClick={refetch} className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors">
          <RefreshCw size={14} /> Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <ConfirmDialog
        open={!!confirmTarget}
        title="Delete Job"
        message={`Are you sure you want to delete "${confirmTarget?.title}"? All associated resumes, candidates, and analysis data will be permanently removed.`}
        confirmLabel="Delete"
        variant="danger"
        onConfirm={handleDelete}
        onCancel={() => setConfirmTarget(null)}
      />
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Jobs</h2>
        <Link
          to="/app/jobs/new"
          className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <Plus size={16} />
          Create Job
        </Link>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {loading && !data ? (
          <div className="p-6 space-y-3">
            {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 w-full" />)}
          </div>
        ) : jobs.length === 0 ? (
          <div className="p-6 text-center text-sm text-gray-500">
            No jobs found.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left px-5 py-3 font-medium text-gray-600">Title</th>
                <th className="text-left px-5 py-3 font-medium text-gray-600">Status</th>
                <th className="text-left px-5 py-3 font-medium text-gray-600">Created</th>
                <th className="text-right px-5 py-3 font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {jobs.map((job) => (
                <tr key={job.id} className="hover:bg-gray-50">
                  <td className="px-5 py-3">
                    <Link
                      to={`/app/jobs/${job.id}`}
                      className="font-medium text-gray-900 hover:text-indigo-600"
                    >
                      {job.title}
                    </Link>
                  </td>
                  <td className="px-5 py-3">
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
                  </td>
                  <td className="px-5 py-3 text-gray-500">
                    {new Date(job.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-5 py-3 text-right space-x-3">
                    <Link
                      to={`/app/upload/${job.id}`}
                      className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
                    >
                      Upload
                    </Link>
                    <Link
                      to={`/app/candidates/${job.id}`}
                      className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
                    >
                      Candidates
                    </Link>
                    <button
                      onClick={() => setConfirmTarget({ id: job.id, title: job.title })}
                      disabled={deleting === job.id}
                      className="text-sm text-red-500 hover:text-red-700 font-medium disabled:opacity-50"
                      title="Delete job"
                    >
                      {deleting === job.id ? (
                        <Loader2 size={15} className="inline animate-spin" />
                      ) : (
                        <Trash2 size={15} className="inline" />
                      )}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
