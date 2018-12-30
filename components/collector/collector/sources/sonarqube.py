"""Sources for SonarQube."""

from typing import Dict

import requests

from collector.source import Source
from collector.type import Measurement, URL


class SonarQube(Source):
    """Base class for SonarQube meteics."""

    name = "SonarQube"


class SonarQubeVersion(SonarQube):
    """SonarQube version source."""

    def api_url(self, url: URL, component: str) -> URL:
        return URL(f"{url}/api/server/version")


class SonarQubeViolations(SonarQube):
    """SonarQube violations source."""

    def landing_url(self, url: URL, component: str) -> URL:
        return URL(f"{url}/project/issues?id={component}&resolved=false")

    def api_url(self, url: URL, component: str) -> URL:
        return URL(f"{url}/api/issues/search?componentKeys={component}&resolved=false")

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(response.json()["total"])


class SonarQubeMetricsBaseClass(SonarQube):
    """Base class for metrics that use the SonarQube measures/component API."""

    metricKeys = "Subclass responsibility"

    def landing_url(self, url: URL, component: str) -> URL:
        return URL(f"{url}/component_measures?id={component}&metric={self.metricKeys}")

    def api_url(self, url: URL, component: str) -> URL:
        return URL(f"{url}/api/measures/component?component={component}&metricKeys={self.metricKeys}")

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(self._get_metrics(response)[self.metricKeys])

    @staticmethod
    def _get_metrics(response: requests.Response) -> Dict[str, int]:
        """Get the metric(s) from the response."""
        measures = response.json()["component"]["measures"]
        return dict((measure["metric"], int(measure["value"])) for measure in measures)


class SonarQubeTests(SonarQubeMetricsBaseClass):
    """SonarQube tests source."""

    metricKeys = "tests"


class SonarQubeFailedTests(SonarQubeMetricsBaseClass):
    """SonarQube failed tests source."""

    metricKeys = "test_failures"


class SonarQubeNCLOC(SonarQubeMetricsBaseClass):
    """SonarQube non-commented lines of code."""

    metricKeys = "ncloc"


class SonarQubeLOC(SonarQubeMetricsBaseClass):
    """SonarQube lines of code."""

    metricKeys = "lines"


class SonarQubeCoveredLines(SonarQubeMetricsBaseClass):
    """SonarQube covered lines of code."""

    metricKeys = "uncovered_lines,lines_to_cover"

    def parse_source_response(self, response: requests.Response) -> Measurement:
        metrics = self._get_metrics(response)
        return Measurement(metrics["lines_to_cover"] - metrics["uncovered_lines"])


class SonarQubeUncoveredLines(SonarQubeMetricsBaseClass):
    """SonarQube uncovered lines of code."""

    metricKeys = "uncovered_lines"


class SonarQubeCoveredBranches(SonarQubeMetricsBaseClass):
    """SonarQube covered branches."""

    metricKeys = "uncovered_conditions,conditions_to_cover"

    def parse_source_response(self, response: requests.Response) -> Measurement:
        metrics = self._get_metrics(response)
        return Measurement(metrics["conditions_to_cover"] - metrics["uncovered_conditions"])


class SonarQubeUncoveredBranches(SonarQubeMetricsBaseClass):
    """SonarQube uncovered branches."""

    metricKeys = "uncovered_conditions"