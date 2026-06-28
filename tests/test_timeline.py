from app.services.timeline import TimelineService
from app.db.models_and_crud import TimelineEvent

def test_timeline_service(mocker):
    mock_db = mocker.MagicMock()
    mock_db.query().filter().order_by().all.return_value = [
        TimelineEvent(event_type="Diagnosis", date="2023-01-01")
    ]
    
    service = TimelineService(mock_db, "pat_1")
    events = service.get_chronological_history()
    assert len(events) == 1
    assert events[0].event_type == "Diagnosis"

