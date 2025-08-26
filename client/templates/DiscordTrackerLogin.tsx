import React from "react";

import { CSRFToken, reverse, templates } from "@reactivated";
import { Button, Card, Col, Container, Row } from "react-bootstrap";

import { faDiscord } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { Navbar } from "@client/components/discord_tracker/Navbar";
import { Layout } from "@client/layouts/Layout";

export function Template(_props: templates.DiscordTrackerLogin) {
  return (
    <Layout title="Discord Login" Navbar={Navbar}>
      <Container className="d-flex align-items-center justify-content-center min-vh-100">
        <Row className="w-100">
          <Col xs={12} md={6} lg={4} className="mx-auto">
            <Card className="shadow-lg border-0">
              <Card.Body className="text-center p-5">
                <div className="mb-4">
                  <FontAwesomeIcon icon={faDiscord} size="4x" className="text-primary" />
                </div>
                <h2 className="h3 mb-3">Welcome to Discord Tracker</h2>
                <p className="text-muted mb-4">
                  Sign in with your Discord account to access the Discord tracking features.
                </p>

                <form method="POST" action={reverse("discord_login")}>
                  <CSRFToken />
                  <Button variant="primary" size="lg" className="w-100 mb-3" type="submit">
                    <FontAwesomeIcon icon={faDiscord} className="me-2" />
                    Sign in with Discord
                  </Button>
                </form>
                <div className="text-center">
                  <small className="text-muted">
                    We only request minimal permissions to verify your identity.
                  </small>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </Layout>
  );
}
