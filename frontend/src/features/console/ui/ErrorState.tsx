interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="rounded-lg border border-red-500/30 bg-red-500/5 px-4 py-6 text-center" role="alert">
      <p className="text-sm text-red-300">{message}</p>
      {onRetry && (
        <button type="button" className="btn-secondary btn-sm mt-3" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}
