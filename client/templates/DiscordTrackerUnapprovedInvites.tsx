import React, { useState } from "react";

import { Card, Col, Container, Row } from "react-bootstrap";

import { templates } from "@reactivated";

import { faDiscord } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { UnapprovedInviteCard } from "@client/components/discord_tracker/DiscordTrackerUnapprovedInvites";
import { Navbar } from "@client/components/discord_tracker/Navbar";
import { Layout } from "@client/layouts/Layout";

import { AnimatePresence } from "framer-motion";

export function Template(props: templates.DiscordTrackerUnapprovedInvites) {
  const [unapprovedInvites, setUnapprovedInvites] = useState(props.unapproved_invites);

  function handleInviteApproved(inviteId: number) {
    setUnapprovedInvites((prevInvites) => prevInvites.filter((invite) => invite.id !== inviteId));
  }

  function handleInviteRejected(inviteId: number) {
    setUnapprovedInvites((prevInvites) => prevInvites.filter((invite) => invite.id !== inviteId));
  }

  return (
    <Layout title="Unapproved Discord Invites - Class Cords" description="" Navbar={Navbar}>
      <Container fluid className="py-4 px-0">
        <Row className="justify-content-center">
          <Col lg={10} xl={8}>
            <div className="d-flex align-items-center mb-4">
              <FontAwesomeIcon icon={faDiscord} className="text-primary me-3" size="2x" />
              <div>
                <h1 className="mb-1">Unapproved Discord Invites</h1>
                <p className="text-muted mb-0">
                  Review and approve Discord server invites submitted by other users
                </p>
              </div>
            </div>

            {unapprovedInvites.length === 0 ? (
              <div className="text-center py-5">
                <Card className="border-0">
                  <Card.Body>
                    <FontAwesomeIcon icon={faDiscord} size="3x" className="text-muted mb-3" />
                    <h4>No Pending Invites</h4>
                    <p className="mb-0">All Discord invites have been reviewed and approved.</p>
                  </Card.Body>
                </Card>
              </div>
            ) : (
              <div className="d-grid gap-4">
                <AnimatePresence mode="popLayout">
                  {unapprovedInvites.map((invite) => (
                    <UnapprovedInviteCard
                      key={invite.id}
                      invite={invite}
                      onApproveSubmit={handleInviteApproved}
                      onRejectSubmit={handleInviteRejected}
                    />
                  ))}
                </AnimatePresence>
              </div>
            )}
          </Col>
        </Row>
      </Container>
    </Layout>
  );
}
