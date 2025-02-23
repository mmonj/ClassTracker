import React from "react";

import { Spinner } from "react-bootstrap";

interface Props {
  /** If set to true, the children are replaced with loading spinner; otherwise spinner appears besides them */
  hideChildren?: boolean;
  isLoadingState: boolean;
  isIdentifierMatching?: boolean;
  spinnerVariant?:
    | "primary"
    | "secondary"
    | "success"
    | "danger"
    | "warning"
    | "info"
    | "light"
    | "dark";
  onClick?: () => void;
  size: "sm" | "md";
  type: "button" | "submit" | "reset" | undefined;
  className?: string;
  children: React.ReactNode;
}

export function ButtonWithSpinner({
  className = "",
  spinnerVariant = "primary",
  hideChildren = false,
  isIdentifierMatching = true,
  ...props
}: Props) {
  const trueSize = props.size === "md" ? undefined : "sm";
  const masterIsHideChildren = hideChildren && props.isLoadingState && isIdentifierMatching;

  return (
    <button
      className={className}
      type={props.type}
      onClick={props.onClick}
      disabled={props.isLoadingState}
    >
      {!masterIsHideChildren && <> {props.children} </>}
      {props.isLoadingState && isIdentifierMatching && (
        <span>
          <Spinner variant={spinnerVariant} animation="border" role="status" size={trueSize}>
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </span>
      )}
    </button>
  );
}
