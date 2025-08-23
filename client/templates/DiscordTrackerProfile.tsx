import React from "react";

import { templates } from "@reactivated";
import { Badge, Card, Col, Container, Row } from "react-bootstrap";

import { Navbar } from "@client/components/discord_tracker/Navbar";
import { Layout } from "@client/layouts/Layout";

export function Template(props: templates.DiscordTrackerProfile) {
  const { discord_user } = props;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case "discord_manager":
        return "danger";
      case "trusted":
        return "success";
      default:
        return "secondary";
    }
  };

  const getRoleDisplayName = (role: string) => {
    switch (role) {
      case "discord_manager":
        return "Discord Manager";
      case "trusted":
        return "Trusted User";
      default:
        return "Regular User";
    }
  };

  return (
    <Layout title="Discord Profile" Navbar={Navbar}>
      <Container className="mt-4">
        <Row className="justify-content-center">
          <Col md={8} lg={6}>
            <Card>
              <Card.Header className="bg-primary text-white">
                <h4 className="mb-0">Discord Profile</h4>
              </Card.Header>
              <Card.Body>
                <div className="text-center mb-4">
                  {discord_user.avatar_url && (
                    <img
                      src={discord_user.avatar_url}
                      alt="Discord Avatar"
                      className="rounded-circle mb-3"
                      style={{ width: "80px", height: "80px" }}
                    />
                  )}
                  <h5 className="mb-1">{discord_user.display_name}</h5>
                  <p className="text-muted mb-2">
                    @{discord_user.username}
                    {discord_user.discriminator && `#${discord_user.discriminator}`}
                  </p>
                  <Badge bg={getRoleBadgeVariant(discord_user.role)}>
                    {getRoleDisplayName(discord_user.role)}
                  </Badge>
                </div>

                <Row>
                  <Col sm={6}>
                    <strong>Discord ID:</strong>
                  </Col>
                  <Col sm={6}>
                    <code className="text-muted">{discord_user.discord_id}</code>
                  </Col>
                </Row>

                <hr />

                <Row>
                  <Col sm={6}>
                    <strong>Email Verified:</strong>
                  </Col>
                  <Col sm={6}>
                    <Badge bg={discord_user.is_verified ? "success" : "warning"}>
                      {discord_user.is_verified ? "Verified" : "Not Verified"}
                    </Badge>
                  </Col>
                </Row>

                <hr />

                {/* {discord_user.school && (
                  <>
                    <Row>
                      <Col sm={6}>
                        <strong>School:</strong>
                      </Col>
                      <Col sm={6}>{discord_user.school.name}</Col>
                    </Row>
                    <hr />
                  </>
                )} */}

                <Row>
                  <Col sm={6}>
                    <strong>First Login:</strong>
                  </Col>
                  <Col sm={6}>{formatDate(discord_user.first_login)}</Col>
                </Row>

                <hr />

                <Row>
                  <Col sm={6}>
                    <strong>Last Login:</strong>
                  </Col>
                  <Col sm={6}>{formatDate(discord_user.last_login)}</Col>
                </Row>

                <hr />

                <Row>
                  <Col sm={6}>
                    <strong>Total Logins:</strong>
                  </Col>
                  <Col sm={6}>
                    <Badge bg="info">{discord_user.login_count}</Badge>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </Layout>
  );
}
