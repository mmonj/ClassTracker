import React from "react";

import { templates } from "@reactivated";
import { Card } from "react-bootstrap";

import { Navbar } from "@client/components/discord_tracker/Navbar";
import { Layout } from "@client/layouts/Layout";

export function Template(_props: templates.DiscordTrackerIndex) {
  return (
    <Layout title="Discord Tracker" Navbar={Navbar}>
      <Card>
        <Card.Body>
          <h1>Hello World</h1>
          <p>Welcome to the Discord Tracker application!</p>
        </Card.Body>
      </Card>
    </Layout>
  );
}
