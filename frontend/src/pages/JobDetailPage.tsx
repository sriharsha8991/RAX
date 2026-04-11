import { useParams, Link } from 'react-router-dom';
import { getJob } from '@/services/jobService';
import { useCachedFetch } from '@/hooks/useApiCache';
import type { Job } from '@/types';
import { Upload, Users, RefreshCw } from 'lucide-react';
import { PageSpinner } from '@/components/ui/Spinner';

export default function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: job, loading, error, refetch } = useCachedFetch<Job>(
    id ? `job:${id}` : null,
    () => getJob(id!),
  );

  if (loading) return <PageSpinner label="Loading job details…" />;
  if (error || !job) return (
    <div className="flex flex-col items-center justify-center py-20 gap-3">
      <p className="text-sm text-red-600">{error ? 'Failed to load job details.' : 'Job not found.'}</p>
      <button onClick={refetch} className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors">
        <RefreshCw size={14} /> Retry
      </button>
    </div>
  );

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 className="text-xl font-bold text-gray-900">{job.title}</h2>
          <p className="text-sm text-gray-500 mt-1">
            Created {new Date(job.created_at).toLocaleDateString()}
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
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-1">Description</h3>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{job.description}</p>
        </div>
        {job.requirements_raw && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-1">Requirements</h3>
            <pre className="text-sm text-gray-700 bg-gray-50 rounded-lg p-3 overflow-x-auto">
              {JSON.stringify(job.requirements_raw, null, 2)}
            </pre>
          </div>
        )}
      </div>

      <div className="flex gap-3">
        <Link
          to={`/app/upload/${job.id}`}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <Upload size={16} />
          Upload Resumes
        </Link>
        <Link
          to={`/app/candidates/${job.id}`}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
        >
          <Users size={16} />
          View Candidates
        </Link>
      </div>
    </div>
  );
}
