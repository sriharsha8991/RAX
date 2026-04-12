import { useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getCandidates, deleteResume, notifyCandidate } from '@/services/candidateService';
import { useCachedFetch, clearCache } from '@/hooks/useApiCache';
import type { CandidateWithScores, CandidateListResponse } from '@/types';
import { Trash2, Loader2, RefreshCw, Mail } from 'lucide-react';
import { PageSpinner, Skeleton } from '@/components/ui/Spinner';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import NotifyModal from '@/components/ui/NotifyModal';
import { useToast } from '@/components/ui/Toast';

export default function CandidateListPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [sortBy, setSortBy] = useState('overall_score');
  const [minScore, setMinScore] = useState(0);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [confirmTarget, setConfirmTarget] = useState<{ resumeId: string; name: string } | null>(null);
  const [notifyTarget, setNotifyTarget] = useState<CandidateWithScores | null>(null);
  const { toast } = useToast();

  const fetcher = useCallback(
    () => getCandidates(jobId!, sortBy),
    [jobId, sortBy],
  );

  const { data, loading, error, refetch } = useCachedFetch<CandidateListResponse>(
    jobId ? `candidates:${jobId}:${sortBy}` : null,
    fetcher,
  );

  const candidates: CandidateWithScores[] = data?.candidates ?? [];

  const handleDelete = async () => {
    if (!confirmTarget) return;
    setDeletingId(confirmTarget.resumeId);
    setConfirmTarget(null);
    try {
      await deleteResume(confirmTarget.resumeId);
      clearCache(`candidates:${jobId}`);
      toast('success', `"${confirmTarget.name}" removed successfully.`);
      refetch();
    } catch {
      toast('error', 'Failed to delete candidate. Please try again.');
    } finally {
      setDeletingId(null);
    }
  };

  const filtered = candidates.filter((c) => c.overall_score >= minScore);

  const handleNotify = async (type: 'shortlisted' | 'rejected', customMessage?: string) => {
    if (!notifyTarget) return;
    try {
      await notifyCandidate(notifyTarget.id, type, customMessage);
      toast('success', `Email sent to ${notifyTarget.email}`);
      clearCache(`candidates:${jobId}`);
      setNotifyTarget(null);
      refetch();
    } catch {
      toast('error', 'Failed to send notification email.');
    }
  };

  if (loading && !data) return <PageSpinner label="Loading candidates…" />;

  if (error && !data) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <p className="text-sm text-red-600">Failed to load candidates.</p>
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
        title="Delete Candidate"
        message={`Remove "${confirmTarget?.name}"? This will permanently delete the resume and all analysis data.`}
        confirmLabel="Delete"
        variant="danger"
        onConfirm={handleDelete}
        onCancel={() => setConfirmTarget(null)}
      />
      <NotifyModal
        open={!!notifyTarget}
        candidateName={notifyTarget?.name || `Candidate ${notifyTarget?.id.slice(0, 8) ?? ''}`}
        candidateEmail={notifyTarget?.email ?? null}
        onSend={handleNotify}
        onClose={() => setNotifyTarget(null)}
      />
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h2 className="text-xl font-bold text-gray-900">Candidates</h2>
        <div className="flex items-center gap-4">
          <label className="text-sm text-gray-600 flex items-center gap-2">
            Min Score:
            <input
              type="range"
              min={0}
              max={100}
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="w-24"
            />
            <span className="text-sm font-medium text-gray-700 w-8">{minScore}</span>
          </label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="text-sm text-gray-900 bg-white border border-gray-300 rounded-lg px-2 py-1.5"
          >
            <option value="overall_score">Overall</option>
            <option value="skills_score">Skills</option>
            <option value="experience_score">Experience</option>
            <option value="education_score">Education</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-x-auto">
        {loading && !data ? (
          <div className="p-6 space-y-3">
            {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 w-full" />)}
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-6 text-center text-sm text-gray-500">
            No candidates found.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left px-4 py-3 font-medium text-gray-600">#</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Candidate</th>
                <th className="text-center px-4 py-3 font-medium text-gray-600 cursor-pointer" onClick={() => setSortBy('overall_score')}>
                  Overall
                </th>
                <th className="text-center px-4 py-3 font-medium text-gray-600 cursor-pointer" onClick={() => setSortBy('skills_score')}>
                  Skills
                </th>
                <th className="text-center px-4 py-3 font-medium text-gray-600 cursor-pointer" onClick={() => setSortBy('experience_score')}>
                  Exp
                </th>
                <th className="text-center px-4 py-3 font-medium text-gray-600 cursor-pointer" onClick={() => setSortBy('education_score')}>
                  Edu
                </th>
                <th className="text-center px-4 py-3 font-medium text-gray-600">Status</th>
                <th className="text-center px-4 py-3 font-medium text-gray-600">Notified</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((c, i) => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-500">{i + 1}</td>
                  <td className="px-4 py-3">
                    <span className="font-medium text-gray-900">
                      {c.name || `Candidate ${c.id.slice(0, 8)}`}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <ScoreBadge score={c.overall_score} />
                  </td>
                  <td className="px-4 py-3 text-center text-gray-600">{c.skills_score ?? '—'}</td>
                  <td className="px-4 py-3 text-center text-gray-600">{c.experience_score ?? '—'}</td>
                  <td className="px-4 py-3 text-center text-gray-600">{c.education_score ?? '—'}</td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                        c.pipeline_status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : c.pipeline_status === 'failed'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-yellow-100 text-yellow-700'
                      }`}
                    >
                      {c.pipeline_status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <NotificationBadge status={c.notification_status} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Link
                        to={`/app/candidates/${jobId}/${c.resume_id}`}
                        className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
                      >
                        Detail
                      </Link>
                      <button
                        onClick={() => setNotifyTarget(c)}
                        className="text-gray-400 hover:text-indigo-600 transition-colors"
                        title="Send notification email"
                      >
                        <Mail size={15} />
                      </button>
                      <button
                        onClick={() => setConfirmTarget({ resumeId: c.resume_id, name: c.name || `Candidate ${c.id.slice(0, 8)}` })}
                        disabled={deletingId === c.resume_id}
                        className="text-gray-400 hover:text-red-600 transition-colors disabled:opacity-50"
                        title="Delete"
                      >
                        {deletingId === c.resume_id ? (
                          <Loader2 size={15} className="animate-spin" />
                        ) : (
                          <Trash2 size={15} />
                        )}
                      </button>
                    </div>
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

function ScoreBadge({ score }: { score: number }) {
  let color = 'bg-red-100 text-red-700';
  if (score >= 70) color = 'bg-green-100 text-green-700';
  else if (score >= 40) color = 'bg-yellow-100 text-yellow-700';

  return (
    <span className={`inline-block text-xs font-bold px-2 py-0.5 rounded-full ${color}`}>
      {score}
    </span>
  );
}

function NotificationBadge({ status }: { status: string | null }) {
  if (!status || status === 'not_sent') {
    return <span className="text-xs text-gray-400">—</span>;
  }
  const color =
    status === 'shortlisted'
      ? 'bg-green-100 text-green-700'
      : 'bg-red-100 text-red-700';
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${color}`}>
      {status}
    </span>
  );
}
