import requests
from typing import Optional, Dict, Tuple
from urllib.parse import urlencode
import logging
from datetime import datetime
from dto.olj_scraper_api_dto import OLJScraperAPIResponse


class OLJJobsAPIService:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            f"OLJJobsAPIService initialized with base URL: {self.base_url}"
        )

    def check_health(self) -> Dict[str, str]:
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Health check failed: {e}")
            raise

    def get_jobs(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        page: Optional[int] = None,
        salary: Optional[str] = None,
        posted_after: Optional[str] = None,
        posted_before: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = None,
        q: Optional[str] = None,
    ) -> OLJScraperAPIResponse:
        params = {}

        if limit is not None:
            if not (1 <= limit <= 100):
                raise ValueError("limit must be between 1 and 100")
            params["limit"] = limit

        if offset is not None:
            if offset < 0:
                raise ValueError("offset must be non-negative")
            params["offset"] = offset

        if page is not None:
            if page < 1:
                raise ValueError("page must be 1 or greater")
            params["page"] = page

        if salary is not None:
            params["salary"] = salary

        if posted_after is not None:
            try:
                datetime.strptime(posted_after, "%Y-%m-%d")
                params["posted_after"] = posted_after
            except ValueError:
                raise ValueError("posted_after must be in YYYY-MM-DD format")

        if posted_before is not None:
            try:
                datetime.strptime(posted_before, "%Y-%m-%d")
                params["posted_before"] = posted_before
            except ValueError:
                raise ValueError("posted_before must be in YYYY-MM-DD format")

        if sort_by is not None:
            valid_sort_fields = [
                "id",
                "job_id",
                "title",
                "work_type",
                "salary",
                "hours_per_week",
                "date_created",
            ]
            if sort_by not in valid_sort_fields:
                raise ValueError(
                    f"sort_by must be one of: {', '.join(valid_sort_fields)}"
                )
            params["sort_by"] = sort_by

        if order is not None:
            if order not in ["asc", "desc"]:
                raise ValueError("order must be 'asc' or 'desc'")
            params["order"] = order

        if q is not None:
            params["q"] = q

        try:
            url = f"{self.base_url}/api/jobs"
            if params:
                url += f"?{urlencode(params)}"

            self.logger.debug(f"Making request to: {url}")

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            return OLJScraperAPIResponse.from_dict(data)

        except requests.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise
        except (KeyError, TypeError, ValueError) as e:
            self.logger.error(f"Failed to parse API response: {e}")
            raise ValueError(f"Invalid API response format: {e}")

    def get_new_jobs(self, **kwargs) -> OLJScraperAPIResponse:
        try:
            response = self.get_jobs(**kwargs)
            self.logger.debug(f"Fetched {len(response.jobs)} jobs from API")

            new_response_data = {
                "jobs": [job.__dict__ for job in response.jobs],
                "pagination": {
                    "total_count": len(response.jobs),
                    "total_pages": response.pagination.total_pages,
                    "current_page": response.pagination.current_page,
                    "limit": response.pagination.limit,
                    "offset": response.pagination.offset,
                    "has_next": response.pagination.has_next,
                    "has_prev": response.pagination.has_prev,
                },
                "filters_applied": {
                    "salary": response.filters_applied.salary,
                    "posted_after": response.filters_applied.posted_after,
                    "posted_before": response.filters_applied.posted_before,
                    "search_query": response.filters_applied.search_query,
                    "sort_by": response.filters_applied.sort_by,
                    "order": response.filters_applied.order,
                },
            }

            self.logger.info(
                f"Found {len(response.jobs)} new jobs out of {len(response.jobs)} total jobs"
            )
            return OLJScraperAPIResponse.from_dict(new_response_data)

        except Exception as e:
            self.logger.error(f"Failed to get new jobs: {e}")
            raise

    def is_healthy(self) -> bool:
        try:
            health_status = self.check_health()
            return health_status.get("status") == "ok"
        except Exception:
            return False
