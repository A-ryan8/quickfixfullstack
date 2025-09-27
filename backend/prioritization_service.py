from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from database import get_db_connection, close_db_connection


# -----------------------------
# Date/time helpers (ported from prototype)
# -----------------------------

def _parse_iso8601(timestamp: str) -> datetime:
	"""Parse ISO-8601 strings with optional trailing 'Z' into aware datetimes (UTC)."""
	if not timestamp:
		return datetime.now(timezone.utc)
	if timestamp.endswith("Z"):
		# Replace 'Z' with +00:00 to satisfy fromisoformat
		return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
	parsed = datetime.fromisoformat(timestamp)
	# If naive, assume UTC
	if parsed.tzinfo is None:
		parsed = parsed.replace(tzinfo=timezone.utc)
	return parsed


def _days_between(start: datetime, end: datetime) -> int:
	"""Return whole days between two datetimes (floor)."""
	delta = end - start
	return max(0, int(delta.total_seconds() // 86400))


# -----------------------------
# Scoring logic (ported from prototype)
# -----------------------------

def _calculate_priority_score(ai_urgency: float, upvotes: int, created_at: str) -> Tuple[float, int]:
	"""Compute weighted score and return (score, hours_old)."""
	# Weights for the scoring formula
	W_URGENCY = 2.0
	W_UPVOTES = 1.5
	# Reduced because we now use hours instead of days
	W_TIME = 0.05

	now_utc = datetime.now(timezone.utc)
	try:
		created_dt = _parse_iso8601(created_at)
	except Exception:
		created_dt = now_utc

	# Use hours instead of days for finer-grained prioritization
	try:
		elapsed_seconds = max(0, int((now_utc - created_dt).total_seconds()))
	except Exception:
		elapsed_seconds = 0
	hours_old = elapsed_seconds // 3600
	priority_score = (ai_urgency * W_URGENCY) + (upvotes * W_UPVOTES) + (hours_old * W_TIME)
	return round(priority_score, 2), hours_old


# -----------------------------
# Database integration
# -----------------------------

def update_all_priority_scores() -> Dict[str, Any]:
	"""
	Fetch unresolved complaints (status not in ['Resolved', 'Closed']), calculate priority scores,
	and update the `priority_score` column in the database for each complaint.

	Returns a summary dict with counts and any errors encountered.
	"""
	conn = get_db_connection()
	if not conn:
		return {"updated": 0, "errors": ["Database connection failed"], "skipped": 0}

	cursor = conn.cursor(dictionary=True)
	updated_count = 0
	skipped_count = 0
	errors: List[str] = []

	try:
		# Ensure the column exists; if not, skip updates but still compute to validate logic
		cursor.execute("SHOW COLUMNS FROM complaints LIKE 'priority_score'")
		col_exists = cursor.fetchone() is not None

		# Fetch unresolved complaints
		cursor.execute(
			"""
			SELECT id,
			       COALESCE(ai_urgency, 0) AS ai_urgency,
			       COALESCE(upvotes, 0) AS upvotes,
			       created_at,
			       status
			FROM complaints
			WHERE status NOT IN ('Resolved', 'Closed') OR status IS NULL
			"""
		)
		rows = cursor.fetchall() or []

		# Prepare update statement only if column exists
		if col_exists:
			update_sql = "UPDATE complaints SET priority_score = %s WHERE id = %s"

		for row in rows:
			cid = row.get("id")
			ai_urgency = float(row.get("ai_urgency") or 0.0)
			upvotes = int(row.get("upvotes") or 0)
			created_at = row.get("created_at")
			created_at_str = created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at or "")

			try:
				score, _days = _calculate_priority_score(ai_urgency, upvotes, created_at_str)
				if col_exists:
					cursor.execute(update_sql, (score, cid))
					updated_count += 1
				else:
					skipped_count += 1
			except Exception as e:
				errors.append(f"id={cid}: {e}")

		if col_exists and updated_count:
			conn.commit()

		return {"updated": updated_count, "errors": errors, "skipped": skipped_count, "total_unresolved": len(rows)}
	except Exception as e:
		conn.rollback()
		errors.append(str(e))
		return {"updated": updated_count, "errors": errors, "skipped": skipped_count}
	finally:
		cursor.close()
		close_db_connection(conn)
