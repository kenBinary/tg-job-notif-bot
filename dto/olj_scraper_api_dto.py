from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Job:
    id: int
    job_id: str
    title: str
    work_type: str
    salary: str
    hours_per_week: str
    job_overview: str
    summary: str
    link: str
    raw_text: str
    date_created: str


@dataclass
class Pagination:
    total_count: int
    total_pages: int
    current_page: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool


@dataclass
class FiltersApplied:
    salary: Optional[str]
    posted_after: Optional[str]
    posted_before: Optional[str]
    search_query: Optional[str]
    sort_by: Optional[str]
    order: Optional[str]


@dataclass
class OLJScraperAPIResponse:
    jobs: List[Job]
    pagination: Pagination
    filters_applied: FiltersApplied

    @classmethod
    def from_dict(cls, data: dict) -> "OLJScraperAPIResponse":
        jobs = [Job(**job_data) for job_data in data.get("jobs", [])]
        pagination = Pagination(**data.get("pagination", {}))
        filters_applied = FiltersApplied(**data.get("filters_applied", {}))

        return cls(jobs=jobs, pagination=pagination, filters_applied=filters_applied)

    def to_dict(self) -> dict:
        return {
            "jobs": [
                {
                    "id": job.id,
                    "job_id": job.job_id,
                    "title": job.title,
                    "work_type": job.work_type,
                    "salary": job.salary,
                    "hours_per_week": job.hours_per_week,
                    "job_overview": job.job_overview,
                    "summary": job.summary,
                    "link": job.link,
                    "raw_text": job.raw_text,
                    "date_created": job.date_created,
                }
                for job in self.jobs
            ],
            "pagination": {
                "total_count": self.pagination.total_count,
                "total_pages": self.pagination.total_pages,
                "current_page": self.pagination.current_page,
                "limit": self.pagination.limit,
                "offset": self.pagination.offset,
                "has_next": self.pagination.has_next,
                "has_prev": self.pagination.has_prev,
            },
            "filters_applied": {
                "salary": self.filters_applied.salary,
                "posted_after": self.filters_applied.posted_after,
                "posted_before": self.filters_applied.posted_before,
                "search_query": self.filters_applied.search_query,
                "sort_by": self.filters_applied.sort_by,
                "order": self.filters_applied.order,
            },
        }
