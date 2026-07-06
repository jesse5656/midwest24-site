# Midwest24 Archive Domain Model

Version: 0.1.0

Status:
Foundational Draft

------------------------------------------------------------------------------

## Purpose

This document defines the core domain model for Midwest24 Archive.

The domain model represents the business concepts that Archive manages.

Database design, APIs, UI, AI services, and automation should derive from this model.

------------------------------------------------------------------------------

## Design Principle

Archive is object-centric.

Files are supporting artifacts.

Knowledge Objects are the primary entities.

------------------------------------------------------------------------------

## Core Entity Types

### Observation

A captured fact, event, insight, or experience.

------------------------------------------------------------------------------

### Question

A problem requiring investigation.

------------------------------------------------------------------------------

### Hypothesis

A proposed explanation.

------------------------------------------------------------------------------

### Evidence

Information supporting or challenging a hypothesis.

------------------------------------------------------------------------------

### Decision

A recorded decision together with its reasoning.

------------------------------------------------------------------------------

### Person

An individual connected to knowledge.

------------------------------------------------------------------------------

### Organization

A company, customer, department, or institution.

------------------------------------------------------------------------------

### Project

A bounded initiative.

------------------------------------------------------------------------------

### System

A business system or technical system.

------------------------------------------------------------------------------

### Process

A repeatable workflow.

------------------------------------------------------------------------------

### Framework

A reusable methodology.

------------------------------------------------------------------------------

### Paper

A structured research publication.

------------------------------------------------------------------------------

### Document

Supporting material.

------------------------------------------------------------------------------

### Task

Work requiring completion.

------------------------------------------------------------------------------

## Relationship Principles

Every entity may have relationships.

Examples include:

Observation -> Project

Observation -> Person

Observation -> Question

Question -> Evidence

Evidence -> Decision

Decision -> Process

Process -> Organization

Paper -> Framework

Framework -> System

System -> Project

Document -> Evidence

------------------------------------------------------------------------------

## Future Domain Objects

The following entities are intentionally deferred.

Meeting

Policy

Risk

Incident

Asset

Product

API

Prompt

Conversation

Training

Customer

Vendor

------------------------------------------------------------------------------

## Guiding Principle

Relationships create value.

Objects preserve knowledge.

