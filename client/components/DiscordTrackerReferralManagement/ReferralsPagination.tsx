import React from "react";

import { templates } from "@reactivated";
import { Button } from "react-bootstrap";

interface Props {
  pagination: templates.DiscordTrackerReferralManagement["pagination"];
  generatePaginationUrl: (page: number) => string;
}

export function ReferralsPagination({ pagination, generatePaginationUrl }: Props) {
  if (pagination.total_pages <= 1) {
    return null;
  }

  return (
    <nav aria-label="Referrals pagination" className="mt-3">
      <div className="d-flex justify-content-between align-items-center">
        <span className="text-muted">
          Page {pagination.current_page} of {pagination.total_pages}
        </span>
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
      </div>
    </nav>
  );
}
