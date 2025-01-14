import React from 'react';
import { Table } from 'semantic-ui-react';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { SourceEntityDetails } from './SourceEntityDetails';
import { SourceEntityAttribute } from './SourceEntityAttribute';

export function SourceEntity(props) {
  const ignored_entity = ["wont_fix", "fixed", "false_positive"].includes(props.status);
  if (props.hide_ignored_entities && ignored_entity) {
    return null;
  }
  const style = ignored_entity ? { textDecoration: "line-through" } : {};
  var positive, negative, warning, active;
  props.entity_attributes.forEach((entity_attribute) => {
    let cell_contents = props.entity[entity_attribute.key];
    if (entity_attribute.color && entity_attribute.color[cell_contents]) {
      positive = (entity_attribute.color[cell_contents] === "positive");
      negative = (entity_attribute.color[cell_contents] === "negative");
      warning = (entity_attribute.color[cell_contents] === "warning");
      active = (entity_attribute.color[cell_contents] === "active");
      return;
    }
  });
  const details = <SourceEntityDetails
    entity={props.entity}
    fetch_measurement_and_reload={props.fetch_measurement_and_reload}
    metric_uuid={props.metric_uuid}
    name={props.entity_name}
    rationale={props.rationale}
    readOnly={props.readOnly}
    source_uuid={props.source_uuid}
    status={props.status}
  />;
  return (
    <TableRowWithDetails
      active={active}
      details={details}
      key={props.entity.key}
      negative={negative}
      positive={positive}
      style={style}
      warning={warning}
    >
      {props.entity_attributes.map((entity_attribute, col_index) =>
        <Table.Cell key={col_index}>
          <SourceEntityAttribute entity={props.entity} entity_attribute={entity_attribute} />
        </Table.Cell>)}
    </TableRowWithDetails>
  );
}
