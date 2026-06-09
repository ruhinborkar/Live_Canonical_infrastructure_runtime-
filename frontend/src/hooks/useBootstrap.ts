import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { bootstrapRuntimeState } from "../lib/bootstrapState";

export function useBootstrap() {
  const queryClient = useQueryClient();

  useEffect(() => {
    bootstrapRuntimeState(queryClient);
  }, [queryClient]);
}
