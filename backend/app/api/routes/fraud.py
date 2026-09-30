from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.fraud import FraudPredictionRequest, FraudPredictionResponse
from app.services.ml_service import predict_risk

router = APIRouter(prefix="/api/fraud", tags=["fraud"])


@router.post("/predict", response_model=FraudPredictionResponse, status_code=status.HTTP_200_OK)
def predict_transaction_risk(
    payload: FraudPredictionRequest,
    request: Request,
) -> FraudPredictionResponse:
    model = getattr(request.app.state, "risk_model", None)
    if model is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Fraud model is not loaded.")

    transaction_data = payload.model_dump(exclude_none=True)
    try:
        result = predict_risk(transaction_data, model=model)
    except Exception as exc:  # pragma: no cover - defensive error handling
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return FraudPredictionResponse(**result)
