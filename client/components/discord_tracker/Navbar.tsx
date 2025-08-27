import React from "react";

import { CSRFToken, Context, reverse } from "@reactivated";
import { Navbar as BSNavbar, Container, Nav, NavDropdown } from "react-bootstrap";

import { faUser } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { NavLink } from "../Navlink";

type TRoute = {
  name: string;
  href: string;
};

export function Navbar() {
  const djangoContext = React.useContext(Context);

  const publicRoutes = [] as TRoute[];
  const managerRoutes = [
    { name: "Unapproved Invites", href: reverse("discord_tracker:unapproved_invites") },
  ] satisfies TRoute[];

  return (
    <>
      <BSNavbar expand="lg">
        <Container fluid>
          <BSNavbar.Brand href={reverse("discord_tracker:listings")}>
            Discord Tracker
          </BSNavbar.Brand>
          <BSNavbar.Toggle aria-controls="basic-navbar-nav" />
          <BSNavbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto mb-2 mb-lg-0">
              {publicRoutes.map((route) => (
                <NavLink key={route.name} href={route.href}>
                  {route.name}
                </NavLink>
              ))}
              {djangoContext.user.discord_user?.is_manager === true &&
                managerRoutes.map((route) => (
                  <NavLink key={route.name} href={route.href}>
                    {route.name}
                  </NavLink>
                ))}
            </Nav>

            <Nav className="mb-2 mb-lg-0">
              {djangoContext.user.discord_user !== null && (
                <NavDropdown
                  title={
                    <span className="d-flex align-items-center justify-content-center">
                      <ProfileDropdownTitle djangoContext={djangoContext} />
                    </span>
                  }
                  id="profile-dropdown"
                  align="end"
                  className="profile-dropdown"
                >
                  <NavDropdown.Item href={reverse("discord_tracker:profile")}>
                    My Profile
                  </NavDropdown.Item>
                  <NavDropdown.Divider />
                  {djangoContext.user.is_superuser && (
                    <>
                      <NavDropdown.Item href={reverse("index")}>Home</NavDropdown.Item>
                      <NavDropdown.Item href={"/admin"}>Admin</NavDropdown.Item>
                      <NavDropdown.Divider />
                    </>
                  )}
                  <NavDropdown.Item as="div" className="p-0">
                    <form action={reverse("account_logout")} method="POST" className="w-100">
                      <CSRFToken />
                      <button
                        type="submit"
                        className="dropdown-item w-100 text-start border-0 bg-transparent"
                      >
                        Log Out
                      </button>
                    </form>
                  </NavDropdown.Item>
                </NavDropdown>
              )}
              {!djangoContext.user.is_authenticated && (
                <NavLink href={reverse("discord_tracker:login")}>Log In</NavLink>
              )}
            </Nav>
          </BSNavbar.Collapse>
        </Container>
      </BSNavbar>

      {/* get the down arrow to be aligned right */}
      <style>{`
        .profile-dropdown .dropdown-toggle::after {
          margin-left: 0.5em !important;
          vertical-align: middle !important;
        }
        .profile-dropdown .dropdown-toggle {
          display: flex !important;
          align-items: center !important;
        }
      `}</style>
    </>
  );
}

function ProfileDropdownTitle({
  djangoContext,
}: {
  djangoContext: React.ContextType<typeof Context>;
}) {
  const discordUser = djangoContext.user.discord_user;
  if (discordUser && discordUser.avatar_url.trim() !== "") {
    return (
      <>
        <img
          src={discordUser.avatar_url}
          alt="Discord Avatar"
          className="rounded-circle me-2"
          style={{ width: "24px", height: "24px" }}
        />
        {discordUser.display_name}
      </>
    );
  }

  return (
    <>
      <FontAwesomeIcon icon={faUser} className="me-2" />
      Profile
    </>
  );
}
