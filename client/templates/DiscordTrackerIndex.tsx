import React, { useContext, useState } from "react";

import { Context, templates } from "@reactivated";
import { Alert, Button, Card, Container, Row } from "react-bootstrap";

import { faDiscord } from "@fortawesome/free-brands-svg-icons";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import {
  AddInviteModal,
  DiscordServerCard,
  InvitesModal,
  LoginBanner,
} from "@client/components/DiscordTrackerIndex";
import { Navbar } from "@client/components/discord_tracker/Navbar";
import { Layout } from "@client/layouts/Layout";

export function Template(props: templates.DiscordTrackerIndex) {
  const context = useContext(Context);
  const [selectedServerId, setSelectedServerId] = useState<number | null>(null);
  const [selectedServerName, setSelectedServerName] = useState("");
  const [showInvitesModal, setShowInvitesModal] = useState(false);
  const [showAddInviteModal, setShowAddInviteModal] = useState(false);

  const discordUser = context.user.discord_user;

  const publicServers = props.public_servers;
  const privilegedServers = props.privileged_servers;

  const canUserAddInvites =
    discordUser !== null && (discordUser.is_trusted === true || discordUser.is_manager === true);

  const handleShowInvites = (serverId: number) => {
    const allServers = [...publicServers, ...privilegedServers];
    const server = allServers.find((s) => s.id === serverId);
    if (server !== undefined) {
      setSelectedServerId(serverId);
      setSelectedServerName(server.display_name);
      setShowInvitesModal(true);
    }
  };

  const handleCloseModal = () => {
    setShowInvitesModal(false);
    setSelectedServerId(null);
    setSelectedServerName("");
  };

  const handleCloseAddInviteModal = () => {
    setShowAddInviteModal(false);
  };

  return (
    <Layout title="Discord Tracker" Navbar={Navbar}>
      <Container>
        {!discordUser && <LoginBanner />}

        <div className="text-center mb-5">
          <div className="d-flex align-items-center justify-content-center mb-3">
            <FontAwesomeIcon icon={faDiscord} size="3x" className="text-primary me-3" />
            <h1 className="h2 mb-0">Discord Servers</h1>
          </div>
          <p className="text-muted lead">Discover and join Discord servers for your classes</p>

          {/* 'add invite' button */}
          {canUserAddInvites && (
            <div className="mt-3">
              <Button
                variant="success"
                onClick={() => setShowAddInviteModal((prev) => !prev)}
                className="d-flex align-items-center mx-auto"
              >
                <FontAwesomeIcon icon={faPlus} className="me-2" />
                Add Discord Invite
              </Button>
            </div>
          )}
        </div>

        {/* public Servers Section */}
        {publicServers.length > 0 && (
          <section className="mb-5">
            <h2 className="h3 mb-4">Public Servers</h2>
            <Row>
              {publicServers.map((server) => (
                <DiscordServerCard
                  key={server.id}
                  server={server}
                  onShowInvites={handleShowInvites}
                />
              ))}
            </Row>
          </section>
        )}

        {/* privileged servers section */}
        {privilegedServers.length > 0 && (
          <section className="mb-5">
            <h2 className="h3 mb-4">Privileged Servers</h2>
            <Alert variant="info" className="mb-3">
              <strong>Note:</strong> These servers are only visible to trusted and manager users.
            </Alert>
            <Row>
              {privilegedServers.map((server) => (
                <DiscordServerCard
                  key={server.id}
                  server={server}
                  onShowInvites={handleShowInvites}
                />
              ))}
            </Row>
          </section>
        )}

        {/* no servers msg */}
        {publicServers.length === 0 && privilegedServers.length === 0 && (
          <div className="text-center py-5">
            <Card className="border-0">
              <Card.Body>
                <FontAwesomeIcon icon={faDiscord} size="4x" className="text-muted mb-3" />
                <h3 className="text-muted">No Discord Servers Available</h3>
                <p className="text-muted">No Discord servers have been added yet</p>
              </Card.Body>
            </Card>
          </div>
        )}

        <InvitesModal
          show={showInvitesModal}
          onHide={handleCloseModal}
          serverId={selectedServerId}
          serverName={selectedServerName}
        />

        <AddInviteModal show={showAddInviteModal} onHide={handleCloseAddInviteModal} />
      </Container>
    </Layout>
  );
}
