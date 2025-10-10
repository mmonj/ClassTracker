import React from "react";

import { Card, Col, Container, Row } from "react-bootstrap";

import { CSRFToken, interfaces, reverse, templates } from "@reactivated";

import { faDiscord } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { ButtonWithSpinner } from "@client/components/ButtonWithSpinner";
import { Navbar } from "@client/components/discord_tracker/Navbar";
import { useFetch } from "@client/hooks/useFetch";
import { Layout } from "@client/layouts/Layout";

export function Template(_props: templates.DiscordTrackerLogin) {
  const referralFetcher = useFetch<interfaces.BlankResponse>();

  return (
    <Layout
      title="Discord Login"
      description="Log in to your Discord account - Class Cords"
      Navbar={Navbar}
    >
      <Container className="d-flex align-items-center justify-content-center min-vh-100 px-0">
        <Row className="w-100">
          <Col xs={12} md={6} lg={4} className="mx-auto">
            <Card className="shadow-lg border-0">
              <Card.Body className="text-center p-5">
                <div className="mb-4">
                  <FontAwesomeIcon icon={faDiscord} size="4x" className="text-primary" />
                </div>
                <h2 className="h3 mb-3">Welcome to Class Cords</h2>
                <p className="text-muted mb-4">
                  Sign in with your Discord account to access the private class discord servers.
                </p>

                <form method="POST" action={reverse("discord_login")}>
                  <CSRFToken />
                  <ButtonWithSpinner
                    className="btn btn-primary btn-lg w-100 mb-3"
                    type="submit"
                    spinnerVariant="dark"
                    isLoadingState={referralFetcher.isLoading}
                    spinnerSize="sm"
                  >
                    <FontAwesomeIcon icon={faDiscord} className="me-2" />
                    Sign in with Discord
                  </ButtonWithSpinner>
                </form>
                <div className="text-center">
                  <small className="text-muted">
                    In order to be able to sign up, you must get a referral from another user.
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
