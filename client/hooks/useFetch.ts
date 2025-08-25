import { useState } from "react";

import { getErrorList } from "@client/utils";

import {
  ApiPromise,
  ApiResponse,
  IHttpError,
  TNotFoundErrorList,
  TUseFetchResult,
} from "@client/types";

export function useFetch<T>() {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessages, setErrorMessages] = useState<string[]>([]);
  const [identifier, setIdentifier] = useState<number | undefined>(undefined);

  async function fetchData(
    fetchCallback: () => ApiPromise<T>,
    identifier?: number,
    onSuccess?: () => void,
  ): Promise<TUseFetchResult<T>> {
    setData(() => null);
    setIsLoading(() => true);
    setErrorMessages(() => []);
    setIdentifier(() => identifier);

    return fetchCallback()
      .then((resp) => {
        if (!resp.ok) {
          throw resp;
        }

        return resp.json();
      })
      .then((data: T) => {
        setData(() => data);
        onSuccess?.();

        return { ok: true, data: data, errors: [] as string[] } as const;
      })
      .catch(async function (errorResp: ApiResponse<IHttpError | TNotFoundErrorList | Error>) {
        setData(() => null);

        const errorList = await getErrorList(errorResp);
        setErrorMessages(() => errorList);
        return {
          ok: false,
          data: null,
          errors: errorList,
        } as const;
      })
      .finally(() => {
        setIsLoading(() => false);
      });
  }

  function reset() {
    setData(() => null);
    setIsLoading(() => false);
    setErrorMessages(() => []);
    setIdentifier(() => undefined);
  }

  return { data, isLoading, errorMessages, identifier, reset, fetchData };
}
