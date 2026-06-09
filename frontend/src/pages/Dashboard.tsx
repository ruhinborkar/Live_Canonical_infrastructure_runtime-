import ActionBar from "../components/ActionBar";
import EventsTable from "../components/EventsTable";
import PipelineMonitor from "../components/PipelineMonitor";
import RunHistory from "../components/RunHistory";
import RuntimeCharts from "../components/RuntimeCharts";
import StatusCards from "../components/StatusCards";

export default function Dashboard() {
  return (
    <>
      <StatusCards />
      <ActionBar />
      <PipelineMonitor />
      <RuntimeCharts />
      <div className="two-col">
        <EventsTable compact />
        <RunHistory compact />
      </div>
    </>
  );
}
