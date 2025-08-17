import React from "react";

import { Context, reverse, templates } from "@reactivated";
import { Button, Card, Col, Container, Row } from "react-bootstrap";

import { faComments, faSchool } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { Layout } from "@client/layouts/Layout";

export function Template(_props: templates.Index) {
  const djangoContext = React.useContext(Context);

  return (
    <Layout title="Dashboard" className="bg-gradient">
      <Container fluid className="py-4">
        <div className="text-center mb-5">
          <h1 className="display-4 text-primary mb-3">Home</h1>
          <p className="lead text-muted">Choose an application to get started</p>
        </div>

        <Row className="g-4 justify-content-center">
          {djangoContext.user.is_superuser && (
            <Col xs={12}>
              <Card className="shadow-sm border-0 app-card">
                <Card.Body className="d-flex flex-column flex-md-row align-items-center p-4">
                  <div
                    className="mb-3 mb-md-0 me-md-4 flex-shrink-0 d-flex align-items-center justify-content-center bg-primary bg-opacity-10 text-primary rounded-4"
                    style={{
                      width: "80px",
                      height: "80px",
                    }}
                  >
                    <FontAwesomeIcon icon={faSchool} size="2x" />
                  </div>
                  <div className="flex-grow-1 text-center text-md-start">
                    <Card.Title className="h4 mb-2">Class Tracker</Card.Title>
                    <Card.Text className="text-muted mb-3">
                      Track and monitor class availability and schedules
                    </Card.Text>
                    <Card.Text className="text-muted small mb-0 d-none d-md-block">
                      Features automated notifications and schedule monitoring
                    </Card.Text>
                  </div>
                  <div className="mt-3 mt-md-0 ms-md-4 flex-shrink-0">
                    <Button
                      variant="primary"
                      href={reverse("class_tracker:index")}
                      size="lg"
                      className="w-100 w-md-auto"
                    >
                      Go to Class Tracker
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          )}

          <Col xs={12}>
            <Card className="shadow-sm border-0 app-card">
              <Card.Body className="d-flex flex-column flex-md-row align-items-center p-4">
                <div
                  className="mb-3 mb-md-0 me-md-4 flex-shrink-0 d-flex align-items-center justify-content-center bg-info bg-opacity-10 text-info rounded-4"
                  style={{
                    width: "80px",
                    height: "80px",
                  }}
                >
                  <FontAwesomeIcon icon={faComments} size="2x" />
                </div>
                <div className="flex-grow-1 text-center text-md-start">
                  <Card.Title className="h4 mb-2">Discord Tracker</Card.Title>
                  <Card.Text className="text-muted mb-3">
                    Monitor and track Discord server activities
                  </Card.Text>
                  <Card.Text className="text-muted small mb-0 d-none d-md-block">
                    Features server monitoring and activity tracking
                  </Card.Text>
                </div>
                <div className="mt-3 mt-md-0 ms-md-4 flex-shrink-0">
                  <Button
                    variant="info"
                    href={reverse("discord_tracker:index")}
                    size="lg"
                    className="w-100 w-md-auto"
                  >
                    Go to Discord Tracker
                  </Button>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

      <style>{`
        .app-card {
          transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }
        .app-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
        }
      `}</style>
    </Layout>
  );
}
