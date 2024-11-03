import { ApiPromise, ApiResponse, IHttpError, TNotFoundErrorList } from "@client/types";

type ClassListInput = {
  [className: string]: boolean | undefined | null;
};

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "HEAD";

export function classList(classes: ClassListInput): string {
  return Object.entries(classes)
    .filter(([_, value]) => value)
    .map(([key, _]) => key)
    .join(" ");
}

export function fetchByReactivated<T>(
  url: string,
  csrfToken: string,
  method: HttpMethod,
  payloadBody: BodyInit | undefined = undefined
): ApiPromise<T> {
  const headers = {
    Accept: "application/json",
    "X-CSRFToken": csrfToken,
  };

  return fetch(url, {
    method: method,
    body: payloadBody,
    headers: headers,
  });
}

export async function getErrorList(
  error: ApiResponse<TNotFoundErrorList | IHttpError> | Error
): Promise<string[]> {
  if (error instanceof Error) {
    return [error.message];
  }

  try {
    const jsonData = await error.json();

    if (Array.isArray(jsonData)) {
      return jsonData;
    } else if (typeof jsonData === "object" && "detail" in jsonData) {
      return [jsonData.detail];
    } else {
      return ["Unknown error occurred"];
    }
  } catch (jsonError) {
    return ["Error parsing response"];
  }
}
