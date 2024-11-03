import React, { useContext } from "react";

import { Context } from "@reactivated";

export function ContribMessages() {
  const djangoContext = useContext(Context);
  const messages = djangoContext.messages;

  if (messages.length === 0) {
    return null;
  }

  return (
    <section className="server-messages">
      <ul className="list-group fw-semibold text-center" style={{ listStyle: "none" }}>
        {messages.map((message, idx) => {
          const alert_type = message.level_tag === "error" ? "danger" : message.level_tag;
          return (
            <li key={idx} className={`alert alert-${alert_type} rounded-0`}>
              {message.message}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
