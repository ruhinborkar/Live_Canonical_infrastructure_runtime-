import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { operationsApi } from "../api/operationsApi";

export const opsKeys = {
  status: ["ops", "status"] as const,
  situation: ["ops", "situation"] as const,
  readiness: ["ops", "readiness"] as const,
  queue: ["ops", "queue"] as const,
  alerts: ["ops", "alerts"] as const,
  topology: ["ops", "topology"] as const,
  operatorTimeline: ["ops", "operator-timeline"] as const,
  resources: ["ops", "resources"] as const,
};

export function useEngineStatus() {
  return useQuery({ queryKey: opsKeys.status, queryFn: operationsApi.status, refetchInterval: 2_000 });
}
export function useSituation() {
  return useQuery({ queryKey: opsKeys.situation, queryFn: operationsApi.situation, refetchInterval: 4_000 });
}
export function useReadiness() {
  return useQuery({ queryKey: opsKeys.readiness, queryFn: operationsApi.readiness, refetchInterval: 5_000 });
}
export function useOpsQueue() {
  return useQuery({ queryKey: opsKeys.queue, queryFn: operationsApi.queue, refetchInterval: 2_000 });
}
export function useOpsAlerts() {
  return useQuery({ queryKey: opsKeys.alerts, queryFn: operationsApi.alerts, refetchInterval: 3_000 });
}
export function useOpsTopology() {
  return useQuery({ queryKey: opsKeys.topology, queryFn: operationsApi.topology, refetchInterval: 6_000 });
}
export function useOperatorTimeline() {
  return useQuery({
    queryKey: opsKeys.operatorTimeline,
    queryFn: () => operationsApi.operatorTimeline(40),
    refetchInterval: 5_000,
  });
}
export function useOpsResources() {
  return useQuery({ queryKey: opsKeys.resources, queryFn: operationsApi.resources, refetchInterval: 5_000 });
}

export function useSubmitWork() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { payload: Record<string, unknown>; priority?: number }) =>
      operationsApi.submit(vars.payload, vars.priority),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["ops"] });
    },
  });
}

export function useAcknowledgeAlert() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (alertId: string) => operationsApi.acknowledge(alertId),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["ops"] });
    },
  });
}
