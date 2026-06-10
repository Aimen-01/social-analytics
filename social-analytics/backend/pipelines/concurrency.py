from db import db, locks_col
import datetime

def acquire_lock(resource_id, owner):
    """
    Try to lock a post for editing.
    Returns True if lock acquired, False if already locked.
    """
    try:
        locks_col.insert_one({
            "resource_id": resource_id,
            "owner":       owner,
            "created_at":  datetime.datetime.utcnow()
        })
        return {"success": True, "message": f"Lock acquired by {owner}"}
    except Exception:
        # Unique index prevents duplicate locks
        existing = locks_col.find_one({"resource_id": resource_id})
        return {
            "success": False,
            "message": f"Post is currently locked by {existing['owner']}",
            "locked_by": existing["owner"]
        }

def release_lock(resource_id, owner):
    """
    Release a lock — only the owner can release it.
    """
    result = locks_col.delete_one({
        "resource_id": resource_id,
        "owner":       owner
    })
    if result.deleted_count == 0:
        return {"success": False, "message": "Lock not found or not owned by you"}
    return {"success": True, "message": "Lock released"}

def check_lock(resource_id):
    """
    Check if a post is currently locked.
    """
    lock = locks_col.find_one({"resource_id": resource_id})
    if lock:
        return {
            "locked":     True,
            "locked_by":  lock["owner"],
            "locked_at":  lock["created_at"].isoformat()
        }
    return {"locked": False}
