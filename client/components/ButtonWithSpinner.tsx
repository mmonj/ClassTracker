import React from "react";

import { Spinner } from "react-bootstrap";

type TVariant =
  | "primary"
  | "secondary"
  | "success"
  | "danger"
  | "warning"
  | "info"
  | "light"
  | "dark";

interface Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  className?: string;
  /** If set to true, the children are replaced with loading spinner; otherwise spinner appears besides them */
  hideChildren?: boolean;
  isLoadingState: boolean;
  disabled?: boolean;
  /** If mapping a list of items such that many 'ButtonWithSpinner' elements are also mapped, this field makes sure
   * only one of those buttons changes state when loading. Done by comparing the fetchState.identifier against the target item id */
  isIdentifierMatching?: boolean;
  spinnerVariant?: TVariant;
  spinnerSize: "sm" | "md";
  children: React.ReactNode;
}

export function ButtonWithSpinner({
  className = "",
  hideChildren = false,
  isLoadingState,
  disabled = false,
  isIdentifierMatching = true,
  spinnerVariant = "dark",
  spinnerSize = "md",
  ...props
}: Props) {
  const masterIsHideChildren = hideChildren && isLoadingState && isIdentifierMatching;
  const trueSize = spinnerSize === "sm" ? "sm" : undefined; // undefined means default size 'md'

  return (
    <button
      className={className}
      type={props.type}
      disabled={disabled || isLoadingState}
      {...props}
    >
      {!masterIsHideChildren && <> {props.children} </>}
      {isLoadingState && isIdentifierMatching && (
        <span>
          <Spinner variant={spinnerVariant} animation="border" role="status" size={trueSize}>
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </span>
      )}
    </button>
  );
}
