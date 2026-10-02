"""Simulation and Change Proposal API Router (Sprint 4, TAD §10, §27.2)."""

from __future__ import annotations

import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.auth import AuthUser
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from packages.contracts.simulation import (
    ChangeProposal,
    ProposalDecisionRequest,
    ProposalSimulateRequest,
)
from packages.domain.database import get_db_session
from packages.domain.models import AuditRecord
from packages.domain.seed import GoldenSeed, load_golden_seed
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, require_permission
from services.workers.simulation.branch_manager import BranchManager, get_branch_manager

router = APIRouter(prefix="/api/v1/proposals", tags=["Simulation & Change Proposals"])


@router.post(
    "/simulate",
    response_model=ResponseEnvelope[ChangeProposal],
    summary="Simulate what-if scenario and assemble Change Proposal (branch only)",
    dependencies=[Depends(require_permission(Permission.PROPOSAL_READ))],
)
async def simulate_proposal(
    request: Request,
    payload: ProposalSimulateRequest,
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[ChangeProposal]:
    manager = get_branch_manager()
    seed = load_golden_seed()
    proposal = manager.create_simulation_branch(
        request=payload,
        seed=seed,
        created_by=user.user_id,
        baseline_revision=1,
    )
    return make_success_envelope(
        proposal,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=proposal.version,
    )


@router.get(
    "",
    response_model=ResponseEnvelope[list[ChangeProposal]],
    summary="List simulation change proposals",
    dependencies=[Depends(require_permission(Permission.PROPOSAL_READ))],
)
async def list_proposals(
    request: Request,
    event_id: str | None = None,
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[list[ChangeProposal]]:
    manager = get_branch_manager()
    proposals = manager.list_proposals(event_id=event_id)
    return make_success_envelope(
        proposals,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
    )


@router.get(
    "/{proposal_id}",
    response_model=ResponseEnvelope[ChangeProposal],
    summary="Get simulation change proposal by ID",
    dependencies=[Depends(require_permission(Permission.PROPOSAL_READ))],
)
async def get_proposal(
    proposal_id: str,
    request: Request,
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[ChangeProposal]:
    manager = get_branch_manager()
    proposal = manager.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Proposal '{proposal_id}' not found")
    return make_success_envelope(
        proposal,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=proposal.version,
    )


@router.post(
    "/{proposal_id}/approve",
    response_model=ResponseEnvelope[ChangeProposal],
    summary="Approve and commit Change Proposal to operational state",
    dependencies=[Depends(require_permission(Permission.PROPOSAL_APPROVE))],
)
async def approve_proposal(
    proposal_id: str,
    request: Request,
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[ChangeProposal]:
    manager = get_branch_manager()
    expected_version = int(if_match) if if_match and if_match.isdigit() else None
    try:
        updated = manager.approve_proposal(
            proposal_id=proposal_id,
            actor_id=user.user_id,
            expected_version=expected_version,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    # Emit audit record
    audit_rec = AuditRecord(
        audit_id=str(uuid.uuid4()),
        event_id=updated.event_id,
        entity_type="proposal",
        entity_id=proposal_id,
        action="approve_proposal",
        actor_id=user.user_id,
        before_state={"status": "branch_only"},
        after_state={"status": "approved", "commit_result": updated.commit_result},
    )
    db.add(audit_rec)
    try:
        await db.commit()
    except Exception:
        await db.rollback()

    return make_success_envelope(
        updated,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=updated.version,
    )


@router.post(
    "/{proposal_id}/reject",
    response_model=ResponseEnvelope[ChangeProposal],
    summary="Reject Change Proposal (produces 0 operational writes)",
    dependencies=[Depends(require_permission(Permission.PROPOSAL_REJECT))],
)
async def reject_proposal(
    proposal_id: str,
    request: Request,
    payload: ProposalDecisionRequest | None = None,
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[ChangeProposal]:
    manager = get_branch_manager()
    expected_version = int(if_match) if if_match and if_match.isdigit() else None
    reason = payload.reason if payload else "Rejected by operator"
    try:
        updated = manager.reject_proposal(
            proposal_id=proposal_id,
            actor_id=user.user_id,
            reason=reason,
            expected_version=expected_version,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    # Emit audit record
    audit_rec = AuditRecord(
        audit_id=str(uuid.uuid4()),
        event_id=updated.event_id,
        entity_type="proposal",
        entity_id=proposal_id,
        action="reject_proposal",
        actor_id=user.user_id,
        before_state={"status": "branch_only"},
        after_state={"status": "rejected", "rejection_reason": updated.rejection_reason},
    )
    db.add(audit_rec)
    try:
        await db.commit()
    except Exception:
        await db.rollback()

    return make_success_envelope(
        updated,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=updated.version,
    )
