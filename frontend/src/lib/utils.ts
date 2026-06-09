export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

export function statusTone(value: string): "success" | "warning" | "danger" | "neutral" {
  if (
    value.includes("VERIFIED") ||
    value.includes("NOT_REQUIRED") ||
    value === "ok" ||
    value === "completed"
  ) {
    return "success";
  }
  if (
    value.includes("REQUIRED") ||
    value.includes("MISMATCH") ||
    value.includes("FAILED") ||
    value.includes("failed")
  ) {
    return "warning";
  }
  return "neutral";
}

export function badgeClass(tone: ReturnType<typeof statusTone>): string {
  const map = {
    success: "badge-success",
    warning: "badge-warning",
    danger: "badge-danger",
    neutral: "badge-neutral",
  };
  return map[tone];
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString();
}

export function downloadJson(filename: string, data: unknown): void {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
