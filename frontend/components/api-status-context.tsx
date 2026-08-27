"use client";

import {
  createContext,
  useContext,
  useMemo,
  useState,
  type Dispatch,
  type ReactNode,
  type SetStateAction,
} from "react";

export type ApiStatus = "idle" | "checking" | "online" | "offline";

interface ApiStatusContextValue {
  apiStatus: ApiStatus;
  datasetRows: number | null;
  setApiStatus: Dispatch<SetStateAction<ApiStatus>>;
  setDatasetRows: Dispatch<SetStateAction<number | null>>;
}

const ApiStatusContext = createContext<ApiStatusContextValue | null>(null);

export function ApiStatusProvider({ children }: { children: ReactNode }) {
  const [apiStatus, setApiStatus] = useState<ApiStatus>("idle");
  const [datasetRows, setDatasetRows] = useState<number | null>(null);
  const value = useMemo(
    () => ({ apiStatus, datasetRows, setApiStatus, setDatasetRows }),
    [apiStatus, datasetRows],
  );

  return <ApiStatusContext.Provider value={value}>{children}</ApiStatusContext.Provider>;
}

export function useApiStatus() {
  const context = useContext(ApiStatusContext);

  if (!context) {
    throw new Error("useApiStatus must be used within ApiStatusProvider");
  }

  return context;
}
