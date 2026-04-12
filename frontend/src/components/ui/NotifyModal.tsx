import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Loader2 } from 'lucide-react';

interface NotifyModalProps {
  open: boolean;
  candidateName: string;
  candidateEmail: string | null;
  onSend: (type: 'shortlisted' | 'rejected', customMessage?: string) => Promise<void>;
  onClose: () => void;
}

export default function NotifyModal({
  open,
  candidateName,
  candidateEmail,
  onSend,
  onClose,
}: NotifyModalProps) {
  const [type, setType] = useState<'shortlisted' | 'rejected'>('shortlisted');
  const [customMessage, setCustomMessage] = useState('');
  const [sending, setSending] = useState(false);

  const handleSend = async () => {
    setSending(true);
    try {
      await onSend(type, customMessage || undefined);
    } finally {
      setSending(false);
      setCustomMessage('');
      setType('shortlisted');
    }
  };

  const handleClose = () => {
    if (sending) return;
    setCustomMessage('');
    setType('shortlisted');
    onClose();
  };

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/40"
            onClick={handleClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="relative bg-white rounded-xl shadow-xl border border-gray-200 p-6 max-w-md w-full"
          >
            <div className="flex items-start gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center shrink-0">
                <Mail size={18} className="text-indigo-600" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-gray-900">
                  Notify {candidateName}
                </h3>
                <p className="text-sm text-gray-500 mt-0.5">
                  {candidateEmail || 'No email on file'}
                </p>
              </div>
            </div>

            {!candidateEmail ? (
              <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-700">
                  This candidate has no email address. The notification cannot be sent.
                </p>
              </div>
            ) : (
              <>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notification type
                  </label>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => setType('shortlisted')}
                      className={`flex-1 px-3 py-2 text-sm font-medium rounded-lg border transition-colors ${
                        type === 'shortlisted'
                          ? 'bg-green-50 border-green-300 text-green-700'
                          : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      Shortlisted
                    </button>
                    <button
                      type="button"
                      onClick={() => setType('rejected')}
                      className={`flex-1 px-3 py-2 text-sm font-medium rounded-lg border transition-colors ${
                        type === 'rejected'
                          ? 'bg-red-50 border-red-300 text-red-700'
                          : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      Rejected
                    </button>
                  </div>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Custom message <span className="text-gray-400">(optional)</span>
                  </label>
                  <textarea
                    rows={3}
                    value={customMessage}
                    onChange={(e) => setCustomMessage(e.target.value)}
                    placeholder="Add a personal note to the email…"
                    className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                  />
                </div>
              </>
            )}

            <div className="flex justify-end gap-2">
              <button
                onClick={handleClose}
                disabled={sending}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              {candidateEmail && (
                <button
                  onClick={handleSend}
                  disabled={sending}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
                >
                  {sending ? (
                    <>
                      <Loader2 size={14} className="animate-spin" />
                      Sending…
                    </>
                  ) : (
                    <>
                      <Mail size={14} />
                      Send Email
                    </>
                  )}
                </button>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
