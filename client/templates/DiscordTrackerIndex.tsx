import React from "react";

import { CSRFToken, reverse, templates } from "@reactivated";
import { Button, Card, Col, Container, Row } from "react-bootstrap";

import { faDiscord } from "@fortawesome/free-brands-svg-icons";
import { faCheckCircle, faTimesCircle } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { Navbar } from "@client/components/discord_tracker/Navbar";
import { Layout } from "@client/layouts/Layout";

export function Template(props: templates.DiscordTrackerIndex) {
  const { discord_user } = props;

  return (
    <Layout title="Discord Tracker" Navbar={Navbar}>
      <Container>
        <Row>
          <Col xs={12} md={8} lg={6} className="mx-auto">
            <Card className="shadow-sm">
              <Card.Body className="text-center p-4">
                {discord_user ? (
                  <>
                    <div className="mb-4">
                      <img
                        src={discord_user.avatar_url}
                        alt={`${discord_user.display_name}'s avatar`}
                        className="rounded-circle mb-3"
                        width="80"
                        height="80"
                        style={{ border: "3px solid #5865F2" }}
                      />
                    </div>

                    <h2 className="h3 mb-2">{discord_user.display_name}</h2>

                    <div className="d-flex justify-content-center align-items-center mb-3">
                      <FontAwesomeIcon
                        icon={discord_user.verified ? faCheckCircle : faTimesCircle}
                        className={
                          discord_user.verified ? "text-success me-2" : "text-warning me-2"
                        }
                      />
                      <span className={discord_user.verified ? "text-success" : "text-warning"}>
                        {discord_user.verified ? "Verified Account" : "Unverified Account"}
                      </span>
                    </div>

                    <Card className="bg-light mb-3">
                      <Card.Body className="py-2">
                        <Row className="text-center">
                          <Col xs={6}>
                            <div className="fw-bold">{discord_user.login_count}</div>
                            <small className="text-muted">Total Logins</small>
                          </Col>
                          <Col xs={6}>
                            <div className="fw-bold">
                              {new Date(discord_user.first_login).toLocaleDateString()}
                            </div>
                            <small className="text-muted">Member Since</small>
                          </Col>
                        </Row>
                      </Card.Body>
                    </Card>

                    <p className="text-muted small mb-3">
                      Last login: {new Date(discord_user.last_login).toLocaleString()}
                    </p>

                    <form action={reverse("account_logout")} method="POST">
                      <CSRFToken />
                      <Button variant="outline-secondary" className="w-100" type="submit">
                        <FontAwesomeIcon icon={faDiscord} className="me-2" />
                        Sign Out
                      </Button>
                    </form>
                  </>
                ) : (
                  <>
                    <FontAwesomeIcon icon={faDiscord} size="4x" className="text-primary mb-4" />
                    <h2 className="h3 mb-3">Welcome to Discord Tracker</h2>
                    <p className="text-muted mb-4">
                      Please log in to view your Discord profile and tracker features.
                    </p>
                    <Button
                      variant="primary"
                      size="lg"
                      href={reverse("discord_tracker:login")}
                      className="w-100 mb-3"
                    >
                      <FontAwesomeIcon icon={faDiscord} className="me-2" />
                      Sign in with Discord
                    </Button>
                  </>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </Layout>
  );
}
