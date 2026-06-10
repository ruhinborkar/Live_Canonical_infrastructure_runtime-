import { useSearchParams } from "react-router-dom";
import EventExplorer from "../features/console/components/EventExplorer";
import OperationBar from "../components/OperationBar";
import { LogType } from "../lib/eventLog";

export default function EventsPage() {
  const [searchParams] = useSearchParams();
  const initialLog = (searchParams.get("log") as LogType | null) ?? undefined;
  const initialCategory = searchParams.get("category") ?? undefined;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold">Events</h1>
        <p className="text-sm text-slate-400">Full event explorer with server-side filtering</p>
      </div>
      <OperationBar modes={["live", "replay", "recover"]} />
      <EventExplorer
        pageSize={25}
        initialLog={initialLog}
        initialCategory={initialCategory as "normal" | "corrupted" | "interrupted" | undefined}
      />
    </div>
  );
}
