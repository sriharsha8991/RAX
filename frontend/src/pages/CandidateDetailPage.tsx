import { useParams } from 'react-router-dom';
import { getAnalysis } from '@/services/candidateService';
import { useCachedFetch } from '@/hooks/useApiCache';
import type { Analysis } from '@/types';
import ScoreRadarChart from '@/components/RadarChart';
import ScoreCard from '@/components/ScoreCard';
import { PageSpinner } from '@/components/ui/Spinner';
import { RefreshCw } from 'lucide-react';

export default function CandidateDetailPage() {
  const { resumeId } = useParams<{ jobId: string; resumeId: string }>();
  const { data: analysis, loading, error, refetch } = useCachedFetch<Analysis>(
    resumeId ? `analysis:${resumeId}` : null,
    () => getAnalysis(resumeId!),
  );

  if (loading) return <PageSpinner label="Loading analysis…" />;
  if (error || !analysis) return (
    <div className="flex flex-col items-center justify-center py-20 gap-3">
      <p className="text-sm text-red-600">{error ? 'Failed to load analysis.' : 'Analysis not found.'}</p>
      <button onClick={refetch} className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors">
        <RefreshCw size={14} /> Retry
      </button>
    </div>
  );

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">
          Candidate Analysis
        </h2>
        <span className="text-2xl font-bold text-indigo-600">
          {analysis.overall_score}/100
        </span>
      </div>

      {/* Radar chart */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <ScoreRadarChart
          skills={analysis.skills_score}
          experience={analysis.experience_score}
          education={analysis.education_score}
        />
      </div>

      {/* Score breakdowns */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Skills', score: analysis.skills_score },
          { label: 'Experience', score: analysis.experience_score },
          { label: 'Education', score: analysis.education_score },
          { label: 'Semantic', score: Math.round((analysis.semantic_similarity ?? 0) * 100) },
        ].map((item) => (
          <div key={item.label} className="bg-white rounded-lg border border-gray-200 p-3 text-center">
            <p className="text-2xl font-bold text-gray-900">{item.score}</p>
            <p className="text-sm text-gray-600 font-medium">{item.label}</p>
          </div>
        ))}
      </div>

      {/* Strengths & Gaps */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <ScoreCard items={analysis.strengths ?? []} type="strength" />
        <ScoreCard items={analysis.gaps ?? []} type="gap" />
      </div>

      {/* Explanation */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">AI Explanation</h3>
        <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">{analysis.explanation}</p>
      </div>
    </div>
  );
}
