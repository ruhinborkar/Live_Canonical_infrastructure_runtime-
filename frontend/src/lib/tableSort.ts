export type SortDirection = "asc" | "desc";

export function compareValues(a: unknown, b: unknown): number {
  if (a == null && b == null) return 0;
  if (a == null) return 1;
  if (b == null) return -1;
  if (typeof a === "number" && typeof b === "number") return a - b;
  return String(a).localeCompare(String(b), undefined, { numeric: true });
}

export function sortRows<T>(
  rows: T[],
  key: keyof T,
  direction: SortDirection
): T[] {
  const sorted = [...rows].sort((a, b) => compareValues(a[key], b[key]));
  return direction === "asc" ? sorted : sorted.reverse();
}

export function nextSortDirection(
  currentKey: string,
  clickedKey: string,
  currentDir: SortDirection
): SortDirection {
  if (currentKey !== clickedKey) return "desc";
  return currentDir === "asc" ? "desc" : "asc";
}
