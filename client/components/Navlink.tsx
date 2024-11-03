import React from "react";

import { Context } from "@reactivated";

interface Props {
  href: string;
  children: React.ReactNode;
}

export function NavLink(props: Props) {
  const djangoContext = React.useContext(Context);
  const activeClassName = props.href === djangoContext.request.path ? "active" : "";

  return (
    <a className={"nav-link " + activeClassName} href={props.href}>
      {props.children}
    </a>
  );
}
