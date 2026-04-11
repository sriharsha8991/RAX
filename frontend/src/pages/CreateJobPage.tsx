import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createJob } from '@/services/jobService';
import { clearCache } from '@/hooks/useApiCache';
import { Loader2 } from 'lucide-react';
import { useToast } from '@/components/ui/Toast';

export default function CreateJobPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [requirements, setRequirements] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    let requirementsRaw: Record<string, unknown> = {};
    if (requirements.trim()) {
      try {
        requirementsRaw = JSON.parse(requirements);
      } catch {
        // Treat as skills list if not valid JSON
        requirementsRaw = {
          skills: requirements.split(',').map((s) => s.trim()).filter(Boolean),
        };
      }
    }

    try {
      const job = await createJob({ title, description, requirements_raw: requirementsRaw });
      clearCache('jobs:list');
      clearCache('dashboard');
      toast('success', `Job "${title}" created successfully!`);
      navigate(`/app/jobs/${job.id}`);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      if ((err as { message?: string })?.message === 'Network Error') {
        setError('Cannot reach server. Please check your connection and try again.');
      } else {
        setError(msg || 'Failed to create job. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Create Job</h2>

      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-xl border border-gray-200 p-6 space-y-4"
      >
        {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3 flex items-start gap-2">
              <span className="shrink-0 mt-0.5">⚠</span>
              <span>{error}</span>
            </div>
          )}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Job Title</label>
          <input            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Senior Python Developer"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            required
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Describe the role, responsibilities, and team…"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Requirements{' '}
            <span className="text-gray-500 font-normal">(comma-separated skills or JSON)</span>
          </label>
          <textarea
            rows={3}
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder='Python, FastAPI, PostgreSQL, Docker'
          />
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Creating…
              </>
            ) : (
              'Create Job'
            )}
          </button>
          <button
            type="button"
            onClick={() => navigate('/app/jobs')}
            className="px-5 py-2.5 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
