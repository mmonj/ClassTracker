import React from "react";

import { CSRFToken, Context, reverse } from "@reactivated";
import { Navbar as BSNavbar, Container, Nav } from "react-bootstrap";

import { NavLink } from "../Navlink";

type TRoute = {
  name: string;
  href: string;
};

export function Navbar() {
  const djangoContext = React.useContext(Context);

  const publicRoutes = [
    { name: "Home", href: reverse("discord_tracker:index") },
  ] satisfies TRoute[];
  const staffRoutes = [{ name: "Admin", href: "/admin" }] satisfies TRoute[];

  return (
    <BSNavbar expand="lg">
      <Container fluid>
        <BSNavbar.Brand href={reverse("discord_tracker:index")}>Discord Tracker</BSNavbar.Brand>
        <BSNavbar.Toggle aria-controls="basic-navbar-nav" />
        <BSNavbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto mb-2 mb-lg-0">
            {djangoContext.user.is_superuser &&
              publicRoutes.map((route) => (
                <NavLink key={route.name} href={route.href}>
                  {route.name}
                </NavLink>
              ))}

            {djangoContext.user.is_superuser &&
              staffRoutes.map((route) => (
                <NavLink key={route.name} href={route.href}>
                  {route.name}
                </NavLink>
              ))}
          </Nav>

          <Nav className="mb-2 mb-lg-0">
            {djangoContext.user.is_superuser && <NavLink href={reverse("index")}>Home</NavLink>}
            {!djangoContext.user.is_authenticated && (
              <NavLink href={reverse("discord_tracker:login")}>Log In</NavLink>
            )}
            {djangoContext.user.is_authenticated && (
              <>
                <form action={reverse("account_logout")} method="POST" className="d-inline">
                  <CSRFToken />
                  <button type="submit" className="nav-link">
                    Log Out
                  </button>
                </form>
              </>
            )}
          </Nav>
        </BSNavbar.Collapse>
      </Container>
    </BSNavbar>
  );
}
