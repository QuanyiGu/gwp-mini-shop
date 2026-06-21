"""测试健康检查API - TDD RED阶段"""
import pytest


class TestHealthEndpoint:
    """测试 /health 端点"""

    def test_health_returns_200(self, client):
        """健康检查应返回200"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status_ok(self, client):
        """健康检查应返回 status: ok"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_returns_timestamp(self, client):
        """健康检查应返回时间戳"""
        response = client.get("/health")
        data = response.json()
        assert "timestamp" in data
