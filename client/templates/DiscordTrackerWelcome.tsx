import React, { useContext, useEffect, useState } from "react";

import { Context, reverse, templates } from "@reactivated";
import type { OverlayTriggerProps } from "react-bootstrap";
import { Alert, Button, Container, OverlayTrigger, Popover } from "react-bootstrap";

import { faPlus, faSearch } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { createDummyDiscordServer } from "@client/utils";

import {
  AddInviteModal,
  LoginBanner,
  ServerSectionsDisplay,
  ViewInvitesModal,
} from "@client/components/DiscordTrackerServerListings";
import { Navbar } from "@client/components/discord_tracker/Navbar";
import { Layout } from "@client/layouts/Layout";

interface ExploreAllButtonProps {
  isAuthenticated: boolean;
  overlayPlacement?: OverlayTriggerProps["placement"];
}

type TServer = templates.DiscordTrackerWelcome["servers"][number];

export function Template(props: templates.DiscordTrackerWelcome) {
  const context = useContext(Context);
  const [servers, setServers] = useState(props.servers);
  const [showInvitesModal, setShowInvitesModal] = useState(false);
  const [selectedServer, setSelectedServer] = useState<TServer | null>(null);
  const [showAddInviteModal, setShowAddInviteModal] = useState(false);
  const [referralCode, setReferralCode] = useState<string | null>(null);

  const canUserAddInvites = context.user.discord_user !== null;
  const isAuthenticated = context.user.discord_user !== null;
  const isManager = context.user.discord_user?.role_info.value === "manager";

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("referral");

    if (code !== null && code.trim() !== "") {
      setReferralCode(code);
    }

    // add dummy private servers
    if (!isAuthenticated) {
      const dummyPrivateServers = Array.from(
        { length: 16 },
        (_, index) => createDummyDiscordServer(-(index + 1)), // use negative ids to avoid conflicts
      );
      setServers((prevServers) => [...prevServers, ...dummyPrivateServers]);
    }
  }, []);

  function handleShowInvites(serverId: number) {
    // avoid interacting with dummy servers
    if (serverId < 0) {
      return;
    }

    const server = servers.find((s) => s.id === serverId);
    if (server) {
      setSelectedServer(server);
      setShowInvitesModal(true);
    }
  }

  function handleCloseInvitesModal() {
    setShowInvitesModal(false);
    setSelectedServer(null);
  }

  function handleShowAddInviteModal() {
    setShowAddInviteModal(true);
  }

  function handleCloseAddInviteModal() {
    setShowAddInviteModal(false);
  }

  return (
    <Layout
      title="Class Cords"
      description="Find and join Discord servers for your college classes"
      Navbar={Navbar}
    >
      <Container className="py-4">
        {!context.user.is_authenticated && <LoginBanner referralCode={referralCode ?? undefined} />}

        {isManager && props.pending_invites_count > 0 && (
          <Alert variant="warning" className="mb-4">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <strong>{props.pending_invites_count}</strong> pending invite submission(s) awaiting
                approval
              </div>
              <Button
                variant="outline-secondary"
                size="sm"
                href={reverse("discord_tracker:unapproved_invites")}
              >
                Review Invites
              </Button>
            </div>
          </Alert>
        )}

        <div className="text-center mb-4">
          <div className="mb-3">
            <h1 className="mb-1">Welcome to Class Cords</h1>
            <p className="text-muted mb-0">Recently added Discord servers for your classes</p>
          </div>

          <div className="d-flex flex-column flex-sm-row justify-content-center gap-2">
            {/* add new discord invite */}
            {canUserAddInvites && (
              <Button
                variant="success"
                size="sm"
                onClick={handleShowAddInviteModal}
                className="d-flex align-items-center justify-content-center"
              >
                <FontAwesomeIcon icon={faPlus} className="me-2" />
                Add Discord Invite
              </Button>
            )}

            {/* 'explore all' button */}
            <ExploreAllButton isAuthenticated={isAuthenticated} />
          </div>
        </div>

        <ServerSectionsDisplay
          servers={servers}
          onShowInvites={handleShowInvites}
          showGroupingControls={true}
          initialGrouped={true}
        />

        <div className="text-center mt-4">
          <ExploreAllButton isAuthenticated={isAuthenticated} overlayPlacement="top" />
        </div>

        <ViewInvitesModal
          show={showInvitesModal}
          onHide={handleCloseInvitesModal}
          server={selectedServer}
        />

        <AddInviteModal show={showAddInviteModal} onHide={handleCloseAddInviteModal} />
      </Container>
    </Layout>
  );
}

function ExploreAllButton({ isAuthenticated, overlayPlacement = "bottom" }: ExploreAllButtonProps) {
  if (isAuthenticated) {
    return (
      <Button
        href={reverse("discord_tracker:explore_all_listings")}
        variant="outline-primary"
        size="sm"
        className="d-flex align-items-center justify-content-center"
      >
        <FontAwesomeIcon icon={faSearch} className="me-2" />
        Explore All Class Servers
      </Button>
    );
  }

  return (
    <OverlayTrigger
      trigger="click"
      placement={overlayPlacement}
      overlay={
        <Popover id="login-required-popover">
          <Popover.Header as="h3">Login Required</Popover.Header>
          <Popover.Body>Please log in to view more Discord servers for your classes</Popover.Body>
        </Popover>
      }
    >
      <Button
        href="#"
        variant="outline-primary"
        size="sm"
        className="d-flex align-items-center justify-content-center"
        onClick={(e) => e.preventDefault()}
      >
        <FontAwesomeIcon icon={faSearch} className="me-2" />
        Explore All Class Servers
      </Button>
    </OverlayTrigger>
  );
}
