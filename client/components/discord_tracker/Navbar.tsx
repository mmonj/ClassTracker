import React from "react";

import { Context, reverse } from "@reactivated";
import { Navbar as BSNavbar, Container, Nav } from "react-bootstrap";

import { NavLink } from "../Navlink";

type TRoute = {
  name: string;
  href: string;
};

export function Navbar() {
  const djangoContext = React.useContext(Context);

  const staffRoutes = [
    { name: "Admin", href: "/admin" },
    { name: "Discord Servers", href: reverse("discord_tracker:index") },
  ] satisfies TRoute[];

  return (
    <BSNavbar expand="lg">
      <Container fluid>
        <BSNavbar.Brand href={reverse("discord_tracker:index")}>Discord Tracker</BSNavbar.Brand>
        <BSNavbar.Toggle aria-controls="basic-navbar-nav" />
        <BSNavbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto mb-2 mb-lg-0">
            {djangoContext.user.is_superuser &&
              staffRoutes.map((route) => (
                <NavLink key={route.name} href={route.href}>
                  {route.name}
                </NavLink>
              ))}
          </Nav>

          <Nav className="mb-2 mb-lg-0">
            {!djangoContext.user.is_authenticated && (
              <>
                <NavLink href={reverse("class_tracker:login_view")}>Log In</NavLink>
              </>
            )}
            {djangoContext.user.is_authenticated && (
              <>
                <NavLink href={reverse("class_tracker:logout_view")}>Log Out</NavLink>
              </>
            )}
          </Nav>
        </BSNavbar.Collapse>
      </Container>
    </BSNavbar>
  );
}
