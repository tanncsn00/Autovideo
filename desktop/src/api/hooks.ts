import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";

export function useTasks(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ["tasks", page, pageSize],
    queryFn: () => api.getTasks(page, pageSize),
  });
}

export function useTask(taskId: string | null) {
  return useQuery({
    queryKey: ["task", taskId],
    queryFn: () => api.getTask(taskId!),
    enabled: !!taskId,
    refetchInterval: (query) => {
      const data = query.state.data as Record<string, unknown> | undefined;
      return data?.state === 4 ? 2000 : false;
    },
  });
}

export function useCreateVideo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.createVideo,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tasks"] }),
  });
}

export function useDeleteTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.deleteTask,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tasks"] }),
  });
}

export function useSystemInfo() {
  return useQuery({ queryKey: ["system-info"], queryFn: api.systemInfo });
}

export function usePlugins(type?: string) {
  return useQuery({
    queryKey: ["plugins", type],
    queryFn: () => api.getPlugins(type),
  });
}

export function useConfig() {
  return useQuery({ queryKey: ["config"], queryFn: api.getConfig });
}

export function useTemplates(category?: string) {
  return useQuery({
    queryKey: ["templates", category],
    queryFn: () => api.getTemplates(category),
  });
}

export function useColorPresets() {
  return useQuery({
    queryKey: ["color-presets"],
    queryFn: api.getColorPresets,
  });
}

export function useCaptionStyles() {
  return useQuery({
    queryKey: ["caption-styles"],
    queryFn: api.getCaptionStyles,
  });
}
