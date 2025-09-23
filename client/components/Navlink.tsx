import React from "react";

import { Context } from "@reactivated";

import classNames from "classnames";

interface Props extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  href: string;
  children: React.ReactNode;
}

export function NavLink({ href, children, className, ...htmlAttributes }: Props) {
  const djangoContext = React.useContext(Context);
  const isActive = href === djangoContext.request.path;

  const combinedClassName = classNames(
    "nav-link",
    {
      active: isActive,
    },
    className,
  );

  return (
    <a className={combinedClassName} href={href} {...htmlAttributes}>
      {children}
    </a>
  );
}
