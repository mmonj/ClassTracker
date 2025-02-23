import React from "react";

import { Spinner } from "react-bootstrap";

interface Props {
  /** If set to true, the children are replaced with loading spinner; otherwise spinner appears besides them */
  hideChildren?: boolean;
  isLoadingState: boolean;
  /** If mapping a list of items such that many 'ButtonWithSpinner' elements are also mapped, this field makes sure
   * only one of those buttons changes state when loading. Done by comparing the fetchState.identifier against the target item id */
  isIdentifierMatching?: boolean;
  variant?: "primary" | "secondary" | "success" | "danger" | "warning" | "info" | "light" | "dark";
  onClick?: () => void;
  size: "sm" | "md";
  type: "button" | "submit" | "reset" | undefined;
  disabled?: boolean;
  className?: string;
  children: React.ReactNode;
}

export function ButtonWithSpinner({
  className = "",
  variant = "dark",
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
      disabled={props.disabled === true || props.isLoadingState}
    >
      {!masterIsHideChildren && <> {props.children} </>}
      {props.isLoadingState && isIdentifierMatching && (
        <span>
          <Spinner variant={variant} animation="border" role="status" size={trueSize}>
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </span>
      )}
    </button>
  );
}
