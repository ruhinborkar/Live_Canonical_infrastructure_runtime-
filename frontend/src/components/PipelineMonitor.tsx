import { PIPELINE_STAGES } from "../api/client";
import { useRuntime } from "../hooks/useRuntime";

export default function PipelineMonitor() {
  const { stageLog, currentStage, completedStages, loading } = useRuntime();

  const currentIndex = currentStage
    ? PIPELINE_STAGES.indexOf(currentStage as (typeof PIPELINE_STAGES)[number])
    : -1;

  const doneCount = PIPELINE_STAGES.filter((_, i) => {
    if (loading && currentIndex >= 0) return i <= currentIndex;
    return completedStages.has(PIPELINE_STAGES[i]);
  }).length;

  const progress = Math.round((doneCount / PIPELINE_STAGES.length) * 100);

  function stepClass(stage: string, index: number): string {
    if (loading && currentIndex >= 0) {
      if (index < currentIndex) return "done";
      if (index === currentIndex) return "active";
      return "pending";
    }
    if (completedStages.has(stage)) return "done";
    return "pending";
  }

  return (
    <div className="panel glass">
      <div className="panel-header">
        <h2>Pipeline Monitor</h2>
        <span className="progress-label">
          {doneCount}/{PIPELINE_STAGES.length} stages
        </span>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>

      <div className="pipeline">
        {PIPELINE_STAGES.map((stage, i) => (
          <span key={stage} style={{ display: "contents" }}>
            {i > 0 && <span className="pipeline-arrow">→</span>}
            <span className={`pipeline-step ${stepClass(stage, i)}`}>{stage}</span>
          </span>
        ))}
      </div>

      <div className="stage-log">
        {stageLog.length === 0 ? (
          <div className="loading">Waiting for pipeline events…</div>
        ) : (
          [...stageLog].reverse().map((entry, i) => (
            <div key={`${entry.stage}-${i}`}>
              <span className="stage-name">{entry.stage}</span>
              <span className="stage-arrow"> → </span>
              {entry.status}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
