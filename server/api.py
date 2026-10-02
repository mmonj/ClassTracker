from ninja import NinjaAPI

from class_tracker.api import router as class_tracker_router

# public, read-only api. No auth; open to all origins (see CORS_URLS_REGEX in settings)
public_api = NinjaAPI(title="ClassTracker Public API", version="1")

public_api.add_router("", class_tracker_router)
