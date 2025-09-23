import { templates } from "@reactivated";

import { ApiPromise, ApiResponse, IHttpError, TNotFoundErrorList } from "@client/types";

type ClassListInput = {
  [className: string]: boolean | undefined | null;
};

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "HEAD";

export function classList(classes: ClassListInput): string {
  return Object.entries(classes)
    .filter(([_, value]) => value == true)
    .map(([key, _]) => key)
    .join(" ");
}

export function fetchByReactivated<T>(
  url: string,
  csrfToken: string,
  method: HttpMethod,
  payloadBody: BodyInit | undefined = undefined,
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
  error: ApiResponse<TNotFoundErrorList | IHttpError> | Error,
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
      return ["An unexpected error occurred"];
    }
    // eslint-disable-next-line unused-imports/no-unused-vars
  } catch (jsonError) {
    return ["An unexpected error occurred"];
  }
}

export function randChoice<T>(items: T[]): T {
  const index = Math.floor(Math.random() * items.length);
  return items[index];
}

export function formatDateTypical(dateString: string | null) {
  if (dateString === null || dateString === "") return "n/a";

  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function createDummyDiscordServer(
  id: number,
): templates.DiscordTrackerWelcome["servers"][number] {
  return {
    id,
    server_id: "0",
    name: "Don't unblur me",
    icon_url: "",
    member_count: 0,
    privacy_level_info: {
      value: "private",
      label: "Private",
    },
    custom_title: "",
    description: "How could you unblur me?",
    is_active: true,
    is_featured: false,
    display_name: "Don't unblur me",
    is_general_server: false,
    subjects: [
      {
        id: 1,
        name: "Computer Science",
      },
    ],
    courses: [
      {
        id: 1,
        code: "CSCI",
        level: "300",
        title: "Comp Sci Course",
      },
    ],
    instructors: [
      {
        id: 1,
        name: "Login Required",
      },
    ],
  };
}
