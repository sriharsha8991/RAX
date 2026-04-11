import { Loader2 } from 'lucide-react';

interface SpinnerProps {
  size?: number;
  className?: string;
  label?: string;
}

export default function Spinner({ size = 20, className = '', label }: SpinnerProps) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Loader2 size={size} className="animate-spin text-indigo-600" />
      {label && <span className="text-sm text-gray-500">{label}</span>}
    </div>
  );
}

/** Full-page centered spinner */
export function PageSpinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3">
      <Loader2 size={28} className="animate-spin text-indigo-600" />
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  );
}

/** Skeleton placeholder block */
export function Skeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse bg-gray-200 rounded-lg ${className}`} />
  );
}
