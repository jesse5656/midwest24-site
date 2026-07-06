# Midwest24 Archive Entity Specification

Version: 0.1.0

Status:
Foundational Draft

------------------------------------------------------------------------------

## Purpose

This document defines the initial fields for the core Midwest24 Archive entities.

The database schema, API contracts, backend models, frontend forms, and search indexing should derive from this specification.

------------------------------------------------------------------------------

## Shared Fields

Every primary entity should include:

id

type

title

summary

status

created_at

updated_at

created_by

updated_by

visibility

tags

------------------------------------------------------------------------------

## Observation

Purpose:
Capture a fact, event, insight, or experience.

Fields:

id

title

summary

body

source_type

source_reference

occurred_at

confidence_level

project_id

person_ids

organization_ids

tags

status

------------------------------------------------------------------------------

## Question

Purpose:
Capture something that requires investigation.

Fields:

id

title

summary

body

question_type

status

priority

related_observation_ids

related_project_ids

owner_id

due_date

tags

------------------------------------------------------------------------------

## Evidence

Purpose:
Capture information that supports or challenges a question, hypothesis, or decision.

Fields:

id

title

summary

body

evidence_type

source_type

source_reference

reliability_level

supports_ids

challenges_ids

document_ids

tags

------------------------------------------------------------------------------

## Decision

Purpose:
Record a decision and the reasoning behind it.

Fields:

id

title

summary

decision_statement

rationale

alternatives_considered

tradeoffs

decided_at

decided_by

related_question_ids

related_evidence_ids

impacted_project_ids

status

tags

------------------------------------------------------------------------------

## Person

Purpose:
Represent a person connected to organizational knowledge.

Fields:

id

display_name

role

organization_id

email

phone

notes

tags

status

------------------------------------------------------------------------------

## Organization

Purpose:
Represent a company, department, customer, vendor, or institution.

Fields:

id

name

organization_type

website

notes

tags

status

------------------------------------------------------------------------------

## Project

Purpose:
Represent a bounded body of work.

Fields:

id

name

summary

project_type

status

start_date

end_date

owner_id

organization_ids

tags

------------------------------------------------------------------------------

## Document

Purpose:
Represent a file or supporting artifact.

Fields:

id

title

summary

file_path

file_type

mime_type

file_size

checksum

uploaded_at

uploaded_by

related_entity_ids

tags

status

------------------------------------------------------------------------------

## MVP Entities

The MVP should prioritize:

Observation

Question

Evidence

Decision

Person

Organization

Project

Document

------------------------------------------------------------------------------

## Deferred Entities

The following are deferred until after the MVP:

Hypothesis

System

Process

Framework

Paper

Task

Meeting

Risk

Incident

Policy

Training

