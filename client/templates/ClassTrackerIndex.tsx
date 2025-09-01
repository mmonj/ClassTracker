import React from "react";

import { Context, reverse, templates } from "@reactivated";
import { Alert, Button, Card, Col, Container, Row } from "react-bootstrap";

import { Navbar } from "@client/components/class_tracker/Navbar";
import { Layout } from "@client/layouts/Layout";

export function Template(_props: templates.ClassTrackerIndex) {
  const djangoContext = React.useContext(Context);

  if (djangoContext.user.is_authenticated === false) {
    return (
      <Layout title="Class Tracker Index" description="" Navbar={Navbar}>
        <Container className="mt-5">
          <Row className="justify-content-center">
            <Col md={8} lg={6}>
              <Card className="shadow">
                <Card.Body className="text-center p-5">
                  <h1 className="display-4 mb-4">🎓 Class Tracker</h1>
                  <p className="lead mb-4">
                    Track classes and receive notifications when they become available.
                  </p>
                  <Alert variant="info" className="mb-4">
                    Log in in to access the Class Tracker features.
                  </Alert>
                  <Button variant="primary" size="lg" href={reverse("class_tracker:login_view")}>
                    Log In
                  </Button>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </Layout>
    );
  }

  if (!djangoContext.user.is_superuser) {
    return (
      <Layout title="Class Tracker Index" description="" Navbar={Navbar}>
        <Container className="mt-5">
          <Row className="justify-content-center">
            <Col md={8} lg={6}>
              <Card className="shadow">
                <Card.Body className="text-center p-5">
                  <h1 className="display-4 mb-4">🎓 Class Tracker</h1>
                  <Alert variant="warning" className="mb-4">
                    <Alert.Heading>Access Restricted</Alert.Heading>
                    <p className="mb-0">
                      You are logged in as <strong>{djangoContext.user.name}</strong>, but you need
                      administrator privileges to access the Class Tracker dashboard.
                    </p>
                  </Alert>
                  <div className="d-flex gap-2 justify-content-center">
                    <Button
                      variant="outline-secondary"
                      href={reverse("class_tracker:logout_view")}
                      size="sm"
                    >
                      Log Out
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </Layout>
    );
  }

  const staffRoutes = [
    {
      name: "Manage Course List",
      href: reverse("class_tracker:manage_course_list"),
      description: "Add and manage available courses and terms",
      icon: "📚",
    },
    {
      name: "Add Classes",
      href: reverse("class_tracker:add_classes"),
      description: "Set up class notifications for recipients",
      icon: "➕",
    },
    {
      name: "Class Alerts",
      href: reverse("class_tracker:view_class_alerts"),
      description: "View all class availability alerts",
      icon: "🔔",
    },
  ];

  return (
    <Layout title="Class Tracker Index" description="" Navbar={Navbar}>
      <Container className="mt-4">
        <Row>
          <Col>
            <h1 className="display-4 mb-4">🎓 Class Tracker Dashboard</h1>
            <p className="lead mb-5">
              Manage class notifications and stay updated on course availability.
            </p>
          </Col>
        </Row>

        <Row>
          {staffRoutes.map((route) => (
            <Col key={route.name} md={6} lg={4} className="mb-4">
              <Card className="h-100 shadow-sm">
                <Card.Body className="d-flex flex-column">
                  <div className="text-center mb-3">
                    <span style={{ fontSize: "3rem" }}>{route.icon}</span>
                  </div>
                  <Card.Title className="text-center">{route.name}</Card.Title>
                  <Card.Text className="text-muted text-center flex-grow-1">
                    {route.description}
                  </Card.Text>
                  <Button variant="outline-primary" href={route.href} className="mt-auto">
                    Go to {route.name}
                  </Button>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>

        <Row className="mt-5">
          <Col>
            <Card className="bg-light">
              <Card.Body>
                <h5>Quick Links</h5>
                <div className="d-flex gap-3 flex-wrap">
                  <Button variant="outline-secondary" href="/admin" size="sm">
                    Django Admin
                  </Button>
                  <Button
                    variant="outline-secondary"
                    href={reverse("class_tracker:logout_view")}
                    size="sm"
                  >
                    Log Out
                  </Button>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </Layout>
  );
}
