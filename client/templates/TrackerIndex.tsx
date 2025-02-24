import React from "react";

import { templates } from "@reactivated";

import { Navbar } from "@client/components/Navbar";
import { Layout } from "@client/layouts/Layout";

export function Template(props: templates.TrackerIndex) {
  return (
    <Layout title={props.title} Navbar={Navbar}>
      Hello there
    </Layout>
  );
}
