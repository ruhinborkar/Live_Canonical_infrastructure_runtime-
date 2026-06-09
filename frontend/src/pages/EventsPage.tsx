import EventsTable from "../components/EventsTable";

export default function EventsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold">Events</h1>
        <p className="text-sm text-slate-400">Explore persisted runtime event log</p>
      </div>
      <EventsTable pageSize={25} />
    </div>
  );
}
