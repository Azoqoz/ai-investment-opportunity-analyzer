function getApiBaseUrl() {
  const configuredUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

  if (!configuredUrl) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL is not configured");
  }

  return configuredUrl.replace(/\/+$/, "");
}

export class ApiRequestError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor(status: number, detail: unknown = null) {
    super(`API request failed with status ${status}`);
    this.name = "ApiRequestError";
    this.status = status;
    this.detail = detail;
  }
}

async function apiError(response: Response) {
  let detail: unknown = null;

  try {
    detail = await response.json();
  } catch {
    // The status code remains useful when an upstream service has no JSON body.
  }

  return new ApiRequestError(response.status, detail);
}

export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
    signal,
  });

  if (!response.ok) {
    throw await apiError(response);
  }

  return (await response.json()) as T;
}

export async function apiPost<TResponse, TBody>(
  path: string,
  body: TBody,
  signal?: AbortSignal,
): Promise<TResponse> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    method: "POST",
    cache: "no-store",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
    signal,
  });

  if (!response.ok) {
    throw await apiError(response);
  }

  return (await response.json()) as TResponse;
}
