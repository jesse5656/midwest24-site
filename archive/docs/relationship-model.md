# Midwest24 Archive Relationship Model

Version: 0.1.0

Status:
Foundational Draft

------------------------------------------------------------------------------

## Purpose

This document defines how Midwest24 Archive knowledge objects relate to one another.

Archive creates value through relationships, not merely storage.

------------------------------------------------------------------------------

## Core Principle

A knowledge object gains meaning through context.

Context is created by relationships.

------------------------------------------------------------------------------

## MVP Relationship Types

### belongs_to

Used when one object belongs within another.

Example:

Observation belongs_to Project

------------------------------------------------------------------------------

### involves

Used when a person or organization is connected to an object.

Example:

Observation involves Person

------------------------------------------------------------------------------

### generates

Used when one object creates another.

Example:

Observation generates Question

------------------------------------------------------------------------------

### supports

Used when evidence supports a question, hypothesis, or decision.

Example:

Evidence supports Question

------------------------------------------------------------------------------

### challenges

Used when evidence challenges a question, hypothesis, or decision.

Example:

Evidence challenges Hypothesis

------------------------------------------------------------------------------

### resolves

Used when a decision resolves or advances a question.

Example:

Decision resolves Question

------------------------------------------------------------------------------

### documents

Used when a document supports another knowledge object.

Example:

Document documents Evidence

------------------------------------------------------------------------------

## MVP Relationship Map

Observation -> belongs_to -> Project

Observation -> involves -> Person

Observation -> generates -> Question

Question -> supported_by -> Evidence

Question -> resolved_by -> Decision

Decision -> supported_by -> Evidence

Document -> documents -> Evidence

Project -> involves -> Person

Project -> involves -> Organization

------------------------------------------------------------------------------

## Relationship Fields

Every relationship should include:

id

source_entity_id

source_entity_type

relationship_type

target_entity_id

target_entity_type

created_at

created_by

notes

confidence_level

------------------------------------------------------------------------------

## Guiding Principle

Relationships should be simple enough for users to understand and structured enough for software to reason over.

