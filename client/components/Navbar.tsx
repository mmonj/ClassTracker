import React from "react";

import { Context, reverse } from "@reactivated";
import { Navbar as BSNavbar, Container, Nav } from "react-bootstrap";

import { NavLink } from "./Navlink";

export function Navbar() {
  const djangoContext = React.useContext(Context);

  return (
    <BSNavbar expand="lg" className="navbar navbar-expand navbar-light navbar-bg">
      <Container fluid>
        <BSNavbar.Brand href={"/fix-me"}>Home</BSNavbar.Brand>
        <BSNavbar.Toggle aria-controls="navbar-nav" />
        <BSNavbar.Collapse>
          <Nav className="me-auto mb-2 mb-lg-0">
            <NavLink href={reverse("course_searcher:add_classes")}>Add Classes</NavLink>
            <NavLink href={reverse("course_searcher:admin")}>Admin</NavLink>
          </Nav>

          <Nav className="mb-2 mb-lg-0">
            {!djangoContext.user.is_authenticated && (
              <>
                <NavLink href={"/fix-me"}>Create Account</NavLink>
                <NavLink href={"/fix-me"}>Log In</NavLink>
              </>
            )}
          </Nav>
        </BSNavbar.Collapse>
      </Container>
    </BSNavbar>
  );
}
