import OperationBar from "../components/OperationBar";
import EventExplorer from "../features/console/components/EventExplorer";
import HeroStatusHeader from "../features/console/components/HeroStatusHeader";
import PipelineFlowMonitor from "../features/console/components/PipelineFlowMonitor";
import RecentRunsTable from "../features/console/components/RecentRunsTable";
import ReportsPanel from "../features/console/components/ReportsPanel";
import RuntimeLogConsole from "../features/console/components/RuntimeLogConsole";
import RuntimeMetricsGrid from "../features/console/components/RuntimeMetricsGrid";
import TruthVerificationSummary from "../features/console/components/TruthVerificationSummary";
import OperationalHealthPanel from "../features/console/components/OperationalHealthPanel";
import OperationalProofPanels from "../features/console/components/OperationalProofPanels";
import ObservabilityMetrics from "../features/console/components/ObservabilityMetrics";
import { useRuntime } from "../hooks/useRuntime";
import { useQueryClient } from "@tanstack/react-query";

export default function Dashboard() {
  const { refreshAll, loadingMode } = useRuntime();
  const queryClient = useQueryClient();

  async function refreshConsole() {
    await refreshAll();
    await queryClient.invalidateQueries({ queryKey: ["console"] });
  }

  return (
    <>
      <a href="#dashboard-main" className="skip-link">
        Skip to dashboard content
      </a>

      <div id="dashboard-main" className="space-y-6 pb-8" role="main" aria-label="Runtime operations dashboard">
        <HeroStatusHeader />

        <section aria-label="Runtime operations">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <OperationBar />
            <button
              type="button"
              className="btn-secondary btn-sm shrink-0"
              disabled={loadingMode !== null}
              onClick={() => void refreshConsole()}
              aria-label="Sync all console data with backend"
            >
              Sync console data
            </button>
          </div>
        </section>

        <section aria-label="Runtime key performance indicators">
          <RuntimeMetricsGrid />
        </section>

        <section aria-label="Truth verification summary">
          <TruthVerificationSummary />
        </section>

        <section aria-label="Operational health and startup validation">
          <OperationalHealthPanel />
        </section>

        <section aria-label="Truth ledger and failure injection proof">
          <OperationalProofPanels />
        </section>

        <section aria-label="Pipeline and observability" className="grid gap-6 xl:grid-cols-5">
          <div className="xl:col-span-3">
            <PipelineFlowMonitor />
          </div>
          <div className="xl:col-span-2">
            <ObservabilityMetrics />
          </div>
        </section>

        <section aria-label="Runtime logs">
          <RuntimeLogConsole />
        </section>

        <section aria-label="Recent runs">
          <RecentRunsTable limit={10} />
        </section>

        <section aria-label="Event explorer">
          <EventExplorer pageSize={15} />
        </section>

        <section aria-label="Reports center">
          <ReportsPanel />
        </section>
      </div>
    </>
  );
}
