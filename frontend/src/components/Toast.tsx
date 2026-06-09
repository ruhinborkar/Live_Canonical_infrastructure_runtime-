import { useToast } from "../hooks/useToast";
import { cn } from "../lib/utils";

export default function ToastContainer() {
  const { toasts, dismissToast } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex max-w-sm flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          onClick={() => dismissToast(toast.id)}
          className={cn(
            "cursor-pointer rounded-lg border px-4 py-3 text-sm shadow-xl backdrop-blur-sm",
            toast.type === "success" && "border-emerald-500/50 bg-emerald-500/10 text-emerald-300",
            toast.type === "error" && "border-red-500/50 bg-red-500/10 text-red-300",
            toast.type === "info" && "border-blue-500/50 bg-blue-500/10 text-blue-300"
          )}
        >
          {toast.message}
        </div>
      ))}
    </div>
  );
}
