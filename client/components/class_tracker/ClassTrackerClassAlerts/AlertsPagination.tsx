import React from "react";

import { templates } from "@reactivated";
import { Button, Col, Row } from "react-bootstrap";

interface Props {
  pagination: templates.ClassTrackerClassAlerts["pagination"];
  generatePaginationUrl: (page: number) => string;
}

export function AlertsPagination({ pagination, generatePaginationUrl }: Props) {
  if (pagination.total_pages <= 1) {
    return null;
  }

  return (
    <nav aria-label="Class alerts pagination">
      <Row className="justify-content-between align-items-center mt-3">
        <Col md="auto">
          <span className="text-muted">
            Page {pagination.current_page} of {pagination.total_pages}
          </span>
        </Col>
        <Col md="auto">
          <div className="btn-group" role="group">
            {pagination.has_previous && (
              <>
                <Button
                  variant="outline-primary"
                  size="sm"
                  href={generatePaginationUrl(1)}
                  disabled={pagination.current_page === 1}
                >
                  First
                </Button>
                <Button
                  variant="outline-primary"
                  size="sm"
                  href={generatePaginationUrl(pagination.previous_page_number)}
                >
                  Previous
                </Button>
              </>
            )}

            <Button variant="primary" size="sm" disabled>
              {pagination.current_page}
            </Button>

            {pagination.has_next && (
              <>
                <Button
                  variant="outline-primary"
                  size="sm"
                  href={generatePaginationUrl(pagination.next_page_number)}
                >
                  Next
                </Button>
                <Button
                  variant="outline-primary"
                  size="sm"
                  href={generatePaginationUrl(pagination.total_pages)}
                  disabled={pagination.current_page === pagination.total_pages}
                >
                  Last
                </Button>
              </>
            )}
          </div>
        </Col>
      </Row>
    </nav>
  );
}
