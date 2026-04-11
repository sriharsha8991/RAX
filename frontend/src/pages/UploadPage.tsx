import { useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { uploadResumes } from '@/services/resumeService';
import { useProcessingStream } from '@/hooks/useProcessingStream';
import { clearCache } from '@/hooks/useApiCache';
import ProcessingCard from '@/components/ProcessingCard';
import { Upload, X, FileText, ChevronRight, Loader2 } from 'lucide-react';
import { useToast } from '@/components/ui/Toast';

export default function UploadPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [files, setFiles] = useState<File[]>([]);
  const [uploadedIds, setUploadedIds] = useState<{ resumeId: string; filename: string }[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const { toast } = useToast();

  // Only connect WS after upload
  const { statuses } = useProcessingStream(uploadedIds.length > 0 ? (jobId ?? null) : null);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer.files).filter(
      (f) => f.name.endsWith('.pdf') || f.name.endsWith('.docx')
    );
    setFiles((prev) => [...prev, ...dropped]);
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles((prev) => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (!jobId || files.length === 0) return;
    setUploading(true);
    setError('');
    try {
      const results = await uploadResumes(files, jobId);
      setUploadedIds(
        results.map((r, i) => ({ resumeId: r.id, filename: files[i]?.name ?? 'resume' }))
      );
      setFiles([]);
      clearCache(`candidates:${jobId}`);
      toast('success', `${results.length} resume${results.length > 1 ? 's' : ''} uploaded — processing started.`);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      if ((err as { message?: string })?.message === 'Network Error') {
        setError('Cannot reach server. Please check your connection and try again.');
      } else {
        setError(msg || 'Upload failed. Please try again.');
      }
    } finally {
      setUploading(false);
    }
  };

  // Check if all resumes are done processing
  const allComplete = uploadedIds.length > 0 && uploadedIds.every(({ resumeId }) => {
    const completedKey = `${resumeId}:completed`;
    const failedKey = `${resumeId}:scoring`;
    const ev = statuses.get(completedKey) || statuses.get(failedKey);
    return ev?.status === 'complete' || ev?.status === 'failed';
  });

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Upload Resumes</h2>

      {uploadedIds.length === 0 ? (
        <>
          {/* Drop zone */}
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dashed border-gray-300 rounded-xl p-10 text-center hover:border-indigo-400 transition-colors cursor-pointer"
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <Upload size={32} className="mx-auto text-gray-500 mb-3" />
            <p className="text-sm text-gray-600">
              Drop PDF or DOCX files here, or click to browse
            </p>
            <input
              id="file-input"
              type="file"
              multiple
              accept=".pdf,.docx"
              className="hidden"
              onChange={handleFileInput}
            />
          </div>

          {/* File list */}
          {files.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
              {files.map((f, i) => (
                <div key={i} className="flex items-center justify-between px-4 py-3">
                  <div className="flex items-center gap-2">
                    <FileText size={16} className="text-gray-500" />
                    <span className="text-sm text-gray-700 truncate max-w-xs">{f.name}</span>
                    <span className="text-xs text-gray-500">
                      {(f.size / 1024).toFixed(0)} KB
                    </span>
                  </div>
                  <button onClick={() => removeFile(i)} className="text-gray-400 hover:text-red-500">
                    <X size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3 flex items-start gap-2">
              <span className="shrink-0 mt-0.5">⚠</span>
              <span>{error}</span>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={files.length === 0 || uploading}
            className="w-full py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
          >
            {uploading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Uploading…
              </>
            ) : (
              `Upload ${files.length} file${files.length !== 1 ? 's' : ''}`
            )}
          </button>
        </>
      ) : (
        <>
          {/* Processing cards */}
          <div className="space-y-3">
            {uploadedIds.map(({ resumeId, filename }) => (
              <ProcessingCard
                key={resumeId}
                resumeId={resumeId}
                filename={filename}
                stageStatuses={statuses}
              />
            ))}
          </div>

          {allComplete && (
            <Link
              to={`/app/candidates/${jobId}`}
              className="flex items-center justify-center gap-2 w-full py-2.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
            >
              View Candidates
              <ChevronRight size={16} />
            </Link>
          )}
        </>
      )}
    </div>
  );
}
