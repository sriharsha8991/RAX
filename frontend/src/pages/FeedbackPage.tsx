import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getFeedback } from '@/services/feedbackService';
import type { Feedback } from '@/types';
import { Copy, Check } from 'lucide-react';
import { PageSpinner } from '@/components/ui/Spinner';

export default function FeedbackPage() {
  const { id } = useParams<{ id: string }>();
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [feedbackError, setFeedbackError] = useState(false);

  useEffect(() => {
    if (!id) return;
    getFeedback(id)
      .then(setFeedback)
      .catch(() => setFeedbackError(true))
      .finally(() => setLoading(false));
  }, [id]);

  const handleCopy = async () => {
    if (!feedback) return;
    await navigator.clipboard.writeText(feedback.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) return <PageSpinner label="Loading feedback…" />;
  if (feedbackError || !feedback) return (
    <div className="flex flex-col items-center justify-center py-20 gap-3">
      <p className="text-sm text-red-600">{feedbackError ? 'Failed to load feedback.' : 'Feedback not found.'}</p>
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Candidate Feedback</h2>
        <button
          onClick={handleCopy}
          className="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors"
        >
          {copied ? <Check size={14} className="text-green-600" /> : <Copy size={14} />}
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
          {feedback.content}
        </p>
      </div>

      <p className="text-sm text-gray-500">
        Generated {new Date(feedback.created_at).toLocaleString()}
      </p>
    </div>
  );
}
