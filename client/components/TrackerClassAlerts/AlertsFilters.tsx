import React from "react";

import { Button, Col, Form, Row } from "react-bootstrap";
import Select, { SingleValue } from "react-select";

interface RecipientOption {
  value: number;
  label: string;
}

interface Props {
  selectedRecipient: RecipientOption | null;
  recipientOptions: RecipientOption[];
  filterText: string;
  onRecipientChange: (option: SingleValue<RecipientOption>) => void;
  onFilterChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onClearFilter: () => void;
}

const REACT_SELECT_PREFIX = "react-select";

export function AlertsFilters({
  selectedRecipient,
  recipientOptions,
  filterText,
  onRecipientChange,
  onFilterChange,
  onClearFilter,
}: Props) {
  return (
    <Row className="mb-3">
      <Col md={4}>
        <Form.Label>Filter by Recipient:</Form.Label>
        <Select<RecipientOption>
          value={selectedRecipient}
          onChange={onRecipientChange}
          options={recipientOptions}
          placeholder="Select recipient..."
          isClearable
          classNamePrefix={REACT_SELECT_PREFIX}
        />
      </Col>
      <Col md={6}>
        <Form.Label>Search in alerts:</Form.Label>
        <div className="d-flex">
          <Form.Control
            type="text"
            placeholder="Search by recipient, course, instructor, days, etc..."
            value={filterText}
            onChange={onFilterChange}
            className="me-2"
          />
          <Button variant="outline-secondary" onClick={onClearFilter} disabled={!filterText.trim()}>
            Clear
          </Button>
        </div>
      </Col>
    </Row>
  );
}
