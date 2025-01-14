"""Jenkins test report metric collector."""

from typing import cast, List

from dateutil.parser import parse
import requests

from ..collector import Collector
from ..type import Entity, Entities, URL, Value
from ..util import days_ago


class JenkinsTestReportTests(Collector):
    """Collector to get the amount of tests from a Jenkins test report."""

    jenkins_test_report_counts = dict(failed="failCount", passed="passCount", skipped="skipCount")

    def api_url(self) -> URL:
        return URL(f"{super().api_url()}/lastSuccessfulBuild/testReport/api/json")

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        statuses = [self.jenkins_test_report_counts[status] for status in self.test_statuses_to_count()]
        return str(sum(int(responses[0].json().get(status, 0)) for status in statuses))

    def test_statuses_to_count(self) -> List[str]:  # pylint: disable=no-self-use
        """Return the test statuses to count."""
        return ["failed", "passed", "skipped"]


class JenkinsTestReportFailedTests(JenkinsTestReportTests):
    """Collector to get the amount of tests from a Jenkins test report."""

    def test_statuses_to_count(self) -> List[str]:
        return cast(List[str], self.parameters.get("failure_type")) or ["failed", "skipped"]

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        """Return a list of failed tests."""

        def entity(case) -> Entity:
            """Transform a test case into a test case entity."""
            name = case.get("name", "<nameless test case>")
            return dict(key=name, name=name, class_name=case.get("className", ""), failure_type=status(case))

        def status(case) -> str:
            """Return the status of the test case."""
            # The Jenkins test report has three counts: passed, skipped, and failed. Individual test cases
            # can be skipped (indicated by the attribute skipped being "true") and/or have a status that can
            # take the values: "failed", "passed", "regression", and "fixed".
            status = "skipped" if case.get("skipped") == "true" else case.get("status", "").lower()
            return dict(regression="failed", fixed="passed").get(status, status)

        suites = [suite for suite in responses[0].json().get("suites", [])]
        statuses = self.test_statuses_to_count()
        return [entity(case) for suite in suites for case in suite.get("cases", []) if status(case) in statuses]


class JenkinsTestReportSourceUpToDateness(Collector):
    """Collector to get the age of the Jenkins test report."""

    def api_url(self) -> URL:
        return URL(f"{super().api_url()}/lastSuccessfulBuild/testReport/api/json")

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        timestamps = [suite.get("timestamp") for suite in responses[0].json().get("suites", [])
                      if suite.get("timestamp")]
        return str(days_ago(parse(max(timestamps))))
