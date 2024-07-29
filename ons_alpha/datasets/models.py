import logging
import re

from django.conf import settings
from django.db import models
from queryish.rest import APIModel, APIQuerySet


logger = logging.getLogger(__name__)

EDITIONS_PATTERN = re.compile(r"/editions/([^/]+)/")


# This needs a revisit. Consider caching + fewer requests
class ONSApiQuerySet(APIQuerySet):
    def get_results_from_response(self, response):
        logger.info("Fetching results from response")
        return response["items"]

    # Override as ONS API returns 'total_count' instead of 'count'
    def run_count(self):
        params = self.get_filters_as_query_dict()

        if self.pagination_style in ("offset-limit", "page-number"):
            if self.pagination_style == "offset-limit":
                params[self.limit_query_param] = 1
            else:
                params[self.page_query_param] = 1

            response_json = self.fetch_api_response(params=params)
            count = response_json["total_count"]
            # count is the full result set without considering slicing;
            # we need to adjust it to the slice
            if self.limit is not None:
                count = min(count, self.limit)
            count = max(0, count - self.offset)
            return count

        # default to standard behaviour of getting all results and counting them
        return super().run_count()


class ONSDataset(APIModel):
    base_query_class = ONSApiQuerySet

    class Meta:
        base_url = settings.ONS_API_DATASET_BASE_URL
        detail_url = f"{settings.ONS_API_DATASET_BASE_URL}/%s"
        fields = ["id", "description", "title", "version", "url", "edition"]
        pagination_style = "offset-limit"
        verbose_name_plural = "ONS Datasets"

    @classmethod
    def from_query_data(cls, data):
        url = data["links"]["latest_version"]["href"]
        edition = EDITIONS_PATTERN.search(url).group(1)
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            version=data["links"]["latest_version"]["id"],
            url=url,
            edition=edition,
        )

    @property
    def formatted_edition(self):
        return self.edition.replace("-", " ").title()

    def __str__(self):
        return self.title


class Dataset(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    version = models.CharField(max_length=255)
    url = models.URLField()
    edition = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title} (Edition: {self.formatted_edition}, Ver: {self.version})"

    @property
    def formatted_edition(self):
        return self.edition.replace("-", " ").title()

    @property
    def website_url(self):
        return self.url.replace(settings.ONS_API_DATASET_BASE_URL, settings.ONS_WEBSITE_DATASET_BASE_URL)
