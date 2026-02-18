import pytest
import threading
from app.services.draft_group_service import create_group
from app.models import DraftGroup, Location
from app.extensions import db

def test_receipt_number_concurrency(app, user, location, article, batch):
    """Stress test receipt_number generation under parallel load."""
    num_threads = 5
    results = []
    
    def worker(tid):
        with app.app_context():
            # Create a group with 1 line
            line = {
                'article_id': article,
                'batch_id': batch,
                'quantity': 10.0,
                'client_event_id': f"thread-event-{tid}-{threading.get_ident()}",
                'draft_type': 'WEIGH_IN'
            }
            try:
                group = create_group(
                    location_id=location,
                    user_id=user,
                    lines=[line],
                    description=f"Thread {tid}"
                )
                results.append(group.receipt_number)
            except Exception as e:
                # If everything works, IntegrityError is caught and retried, so we shouldn't see it here
                results.append(str(e))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Check for duplicates or errors
    receipts = [r for r in results if isinstance(r, str) and r.isdigit()]
    
    assert len(set(receipts)) == num_threads, f"Expected {num_threads} unique receipts, got {results}"
    
    with app.app_context():
        # Verify they are all unique in DB
        db_count = db.session.query(DraftGroup).filter(DraftGroup.receipt_number.in_(receipts)).count()
        assert db_count == num_threads
