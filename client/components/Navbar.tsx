import React from "react";

import { Context } from "@reactivated";
import { Navbar as BSNavbar, Container, Nav } from "react-bootstrap";

import { NavLink } from "./Navlink";

export function Navbar() {
  const djangoContext = React.useContext(Context);

  return (
    <BSNavbar expand="lg" className="navbar navbar-expand-lg bg-primary" data-bs-theme="dark">
      <Container fluid>
        <BSNavbar.Brand href={"/fix-me"}>Home</BSNavbar.Brand>
        <BSNavbar.Toggle aria-controls="basic-navbar-nav" />
        <BSNavbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto mb-2 mb-lg-0">
            <NavLink href={"/fix-me"}>Add Classes</NavLink>
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
