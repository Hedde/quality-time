"""Unit tests for the Jenkins source."""

from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from src.collector import MetricCollector


class JenkinsTestCase(unittest.TestCase):
    """Fixture for Jenkins unit tests."""

    def setUp(self):
        """Test fixture."""
        self.mock_response = Mock()
        self.sources = dict(source_id=dict(
            type="jenkins", parameters=dict(url="http://jenkins/", failure_type=["Red"])))


class JenkinsFailedJobsTest(JenkinsTestCase):
    """Unit tests for the failed jobs metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="failed_jobs", sources=self.sources, addition="sum")

    def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        self.mock_response.json.return_value = dict(
            jobs=[dict(name="job", url="http://job", buildable=True, color="red", builds=[dict(result="red")],
                       jobs=[dict(name="child_job", url="http://child_job", buildable=True, color="red",
                                  builds=[dict(result="red")])])])
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual("2", response["sources"][0]["value"])

    def test_failed_jobs(self):
        """Test that the failed jobs are returned."""
        self.mock_response.json.return_value = dict(
            jobs=[dict(name="job", url="http://job", buildable=True, color="red",
                       builds=[dict(result="red", timestamp="1552686540953")])])
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(self.metric).get()
        build_age = str((datetime.now() - datetime.utcfromtimestamp(1552686540953 / 1000.)).days)
        self.assertEqual(
            [dict(build_date="2019-03-15", build_age=build_age, build_status="Red",
                  key="job", name="job", url="http://job")], response["sources"][0]["entities"])

    def test_no_builds(self):
        """Test no builds."""
        self.mock_response.json.return_value = dict(
            jobs=[dict(name="job", url="http://job", buildable=True, color="notbuilt", builds=[])])
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual([], response["sources"][0]["entities"])


class JenkinsUnusedJobsTest(JenkinsTestCase):
    """Unit tests for the unused jobs metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="unused_jobs", sources=self.sources, addition="sum")

    def test_unused_jobs(self):
        """Test that the number of unused jobs is returned."""
        self.mock_response.json.return_value = dict(
            jobs=[dict(
                name="job", url="http://job", buildable=True, color="red", builds=[dict(timestamp="1548311610349")])])
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual("1", response["sources"][0]["value"])

    def test_unbuild_job(self):
        """Test that jobs without builds are ignored."""
        self.mock_response.json.return_value = dict(
            jobs=[dict(name="job", url="http://job", buildable=True, color="red")])
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual("0", response["sources"][0]["value"])
