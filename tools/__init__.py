# -*- coding: utf-8 -*-
"""Tooling for the Smart Travel Planner skill (cluster: lifestyle-personal).

This package ships the self-improving knowledge pipeline that grows
``SECOND-KNOWLEDGE-BRAIN.md`` for the skill. The command-line entry point lives
in :mod:`tools.knowledge_updater`.

Modules
-------
knowledge_updater
    Discover, score, deduplicate and append domain evidence to the knowledge
    brain with graceful offline degradation.
"""
__all__ = ["knowledge_updater"]
