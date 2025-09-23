import React from "react";

import { Card } from "react-bootstrap";

import { CSRFToken, Context, reverse, templates } from "@reactivated";

import { Navbar } from "@client/components/class_tracker/Navbar";
import { Layout } from "@client/layouts/Layout";

export function Template(props: templates.ClassTrackerLogin) {
  const djangoContext = React.useContext(Context);

  const queryString = djangoContext.request.path.split("?")[1];
  const params = new URLSearchParams(queryString);
  const nextValue = params.get("next");

  return (
    <Layout title="Log In" description="Log in to your account - Class Tracker" Navbar={Navbar}>
      <Card className="border-light-shadow p-4 py-3">
        <form action={reverse("class_tracker:login_view")} method="POST">
          <CSRFToken />
          {props.is_invalid_credentials && (
            <div className="alert alert-danger" role="alert">
              Invalid username or password.
            </div>
          )}
          <fieldset>
            <legend className="mb-4">Log In</legend>
            <p>
              <label htmlFor="logger-username" className="form-label">
                Username
              </label>
              <input
                id="logger-username"
                name="username"
                type="text"
                className="form-control"
                autoComplete="username"
                required
              />
            </p>
            <p>
              <label htmlFor="logger-password" className="form-label">
                Password
              </label>
              <input
                id="logger-password"
                name="password"
                type="password"
                className="form-control"
                autoComplete="current-password"
                required
              />
            </p>
            <p>
              <button type="submit" className="btn btn-primary col-12">
                Submit
              </button>
            </p>
            <input type="hidden" name="next" value={nextValue ?? ""} />
          </fieldset>
        </form>
      </Card>
    </Layout>
  );
}
