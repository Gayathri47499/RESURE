
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Path

from app.core.security import get_current_user

router = APIRouter()


@router.get("/fhir/metadata")
async def fhir_metadata(user: dict = Depends(get_current_user)):
    return {
        "resourceType": "CapabilityStatement",
        "status": "draft",
        "date": datetime.now(timezone.utc).isoformat(),
        "kind": "instance",
        "software": {
            "name": "HospiCare AI API",
            "version": "0.1.0",
        },
        "fhirVersion": "R4",
        "format": ["json"],
        "rest": [
            {
                "mode": "server",
                "resource": [
                    {
                        "type": "Patient",
                        "interaction": [{"code": "read"}],
                    },
                    {
                        "type": "Observation",
                        "interaction": [{"code": "read"}],
                    },
                ],
            }
        ],
        "note": (
            "FHIR R4-style prototype metadata only. "
            "Not a certified or production-ready FHIR server."
        ),
    }


@router.get("/fhir/Patient/{patient_id}")
async def get_fhir_patient(
    patient_id: str = Path(min_length=1, max_length=64),
    user: dict = Depends(get_current_user),
):
    # Deliberately do not return real patient information.
    # This prototype has no configured clinical patient repository.
    raise HTTPException(
        status_code=404,
        detail=(
            "Patient resource not found. "
            "This prototype does not store FHIR patient records."
        ),
    )


@router.get("/fhir/Observation/{observation_id}")
async def get_fhir_observation(
    observation_id: str = Path(min_length=1, max_length=64),
    user: dict = Depends(get_current_user),
):
    raise HTTPException(
        status_code=404,
        detail=(
            "Observation resource not found. "
            "This prototype does not store FHIR observation records."
        ),
    )
