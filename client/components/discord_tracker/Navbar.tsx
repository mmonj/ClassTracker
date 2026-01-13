import React, { useContext, useEffect } from "react";

import { Navbar as BSNavbar, Badge, Container, Nav, NavDropdown } from "react-bootstrap";

import { CSRFToken, Context, interfaces, reverse } from "@reactivated";

import { faBell, faUser } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { useFetch } from "@client/hooks/useFetch";
import { fetchByReactivated } from "@client/utils";

import { NavLink } from "../Navlink";

type TRoute = {
  name: string;
  href: string;
};

export function Navbar() {
  const djangoContext = React.useContext(Context);

  const publicRoutes = [] as TRoute[];

  function getAuthenticatedRoutes() {
    if (djangoContext.user.discord_user === null) return [];

    return [
      {
        name: "Explore All Servers",
        href: reverse("discord_tracker:explore_all_listings"),
      },
      {
        name: "Referrals",
        href: reverse("discord_tracker:referral_management"),
      },
    ] satisfies TRoute[];
  }

  function getManagerRoutes() {
    if (djangoContext.user.discord_user?.role_info.value !== "manager") return [];
    return [
      { name: "Unapproved Invites", href: reverse("discord_tracker:unapproved_invites") },
    ] satisfies TRoute[];
  }

  return (
    <>
      <BSNavbar expand="lg">
        <Container fluid>
          <BSNavbar.Brand href={reverse("discord_tracker:welcome")}>Class Cords</BSNavbar.Brand>
          <BSNavbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto mb-2 mb-lg-0">
              {publicRoutes.map((route) => (
                <NavLink key={route.name} href={route.href}>
                  {route.name}
                </NavLink>
              ))}
              {getAuthenticatedRoutes().map((route) => (
                <NavLink key={route.name} href={route.href}>
                  {route.name}
                </NavLink>
              ))}
              {getManagerRoutes().map((route) => (
                <NavLink key={route.name} href={route.href}>
                  {route.name}
                </NavLink>
              ))}
            </Nav>

            <Nav className="mb-2 mb-lg-0">
              {djangoContext.user.discord_user !== null && <AlertsBellIcon />}
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
                      <NavDropdown.Item href={"/admin"} target="_blank">
                        Admin
                      </NavDropdown.Item>
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
                <NavLink className="sign-in" href={reverse("discord_tracker:login")}>
                  Sign In
                </NavLink>
              )}
            </Nav>
          </BSNavbar.Collapse>

          <div className="d-flex d-lg-none">
            {djangoContext.user.discord_user !== null && <AlertsBellIcon />}
            <BSNavbar.Toggle aria-controls="basic-navbar-nav" className="ms-2" />
          </div>
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

function AlertsBellIcon() {
  const context = useContext(Context);
  const alertsFetcher = useFetch<interfaces.GetUserAlertsResponse>();

  useEffect(() => {
    const discordUserId = context.user.discord_user?.id;
    if (discordUserId === undefined) return;

    void alertsFetcher
      .fetchData(() =>
        fetchByReactivated(
          reverse("discord_tracker:get_user_alerts", { user_id: discordUserId, is_read: "false" }),
          context.csrf_token,
          "GET",
        ),
      )
      .then((result) => {
        if (!result.ok) {
          console.error("Failed to fetch unread alerts. Errors:", result.errors);
        }
      });
  }, []);

  const unreadCount = alertsFetcher.data?.user_alerts.length ?? 0;

  return (
    <NavLink
      href={reverse("discord_tracker:alerts")}
      className="d-flex align-items-center nav-link position-relative p-0 me-2"
    >
      <FontAwesomeIcon icon={faBell} size="xl" />
      {unreadCount > 0 && (
        <Badge
          bg="danger"
          className="position-absolute"
          style={{
            top: "-2px",
            right: "-5px",
            fontSize: "0.65rem",
            padding: "0.2rem 0.2rem",
          }}
        >
          {unreadCount}
        </Badge>
      )}
    </NavLink>
  );
}
