"""
Tests for restocking API endpoints.
"""
from datetime import datetime, timedelta

import pytest


class TestRestockRecommendations:
    """Test suite for GET /api/restock/recommendations."""

    def test_get_recommendations_basic(self, client):
        """Test getting recommendations with a large budget."""
        response = client.get("/api/restock/recommendations?budget=200000")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert data["budget"] == 200000
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0
        assert isinstance(data["total_recommended_cost"], (int, float))

    def test_recommendation_item_structure(self, client):
        """Test that recommendation items have proper structure and types."""
        response = client.get("/api/restock/recommendations?budget=200000")
        data = response.json()

        required_fields = [
            "sku", "name", "category", "warehouse", "quantity_on_hand",
            "forecasted_demand", "shortfall", "recommended_qty",
            "unit_cost", "lead_time_days", "line_total"
        ]
        for item in data["items"]:
            for field in required_fields:
                assert field in item
            assert isinstance(item["quantity_on_hand"], int)
            assert isinstance(item["forecasted_demand"], int)
            assert isinstance(item["shortfall"], int)
            assert isinstance(item["recommended_qty"], int)
            assert isinstance(item["unit_cost"], (int, float))
            assert isinstance(item["lead_time_days"], int)
            assert isinstance(item["line_total"], (int, float))

    def test_recommendations_have_positive_shortfall(self, client):
        """Test that only items with a shortfall are recommended."""
        response = client.get("/api/restock/recommendations?budget=200000")
        data = response.json()

        for item in data["items"]:
            assert item["shortfall"] > 0
            assert item["shortfall"] == item["forecasted_demand"] - item["quantity_on_hand"]
            assert item["recommended_qty"] == item["shortfall"]

    def test_recommendation_line_total_calculation(self, client):
        """Test that line totals match quantity times unit cost."""
        response = client.get("/api/restock/recommendations?budget=200000")
        data = response.json()

        for item in data["items"]:
            expected = item["recommended_qty"] * item["unit_cost"]
            assert abs(item["line_total"] - expected) < 0.01

        total = sum(item["line_total"] for item in data["items"])
        assert abs(data["total_recommended_cost"] - total) < 0.01

    def test_recommendations_sorted_by_shortfall(self, client):
        """Test that recommendations are ordered by shortfall descending."""
        response = client.get("/api/restock/recommendations?budget=200000")
        data = response.json()

        shortfalls = [item["shortfall"] for item in data["items"]]
        assert shortfalls == sorted(shortfalls, reverse=True)

    def test_recommendations_respect_budget(self, client):
        """Test that total recommended cost never exceeds the budget."""
        for budget in [5000, 10000, 50000, 100000, 200000]:
            response = client.get(f"/api/restock/recommendations?budget={budget}")
            assert response.status_code == 200

            data = response.json()
            assert data["total_recommended_cost"] <= budget + 0.01

    def test_larger_budget_recommends_at_least_as_many_items(self, client):
        """Test that increasing the budget never shrinks the recommendation set."""
        small = client.get("/api/restock/recommendations?budget=20000").json()
        large = client.get("/api/restock/recommendations?budget=200000").json()

        assert len(large["items"]) >= len(small["items"])
        assert large["total_recommended_cost"] >= small["total_recommended_cost"]

    def test_zero_budget_returns_no_items(self, client):
        """Test that a zero budget yields an empty recommendation list."""
        response = client.get("/api/restock/recommendations?budget=0")
        assert response.status_code == 200

        data = response.json()
        assert data["items"] == []
        assert data["total_recommended_cost"] == 0

    def test_missing_budget_returns_validation_error(self, client):
        """Test that omitting the budget parameter is rejected."""
        response = client.get("/api/restock/recommendations")
        assert response.status_code == 422

    def test_negative_budget_returns_validation_error(self, client):
        """Test that a negative budget is rejected."""
        response = client.get("/api/restock/recommendations?budget=-100")
        assert response.status_code == 422

    def test_recommendations_by_warehouse(self, client):
        """Test filtering recommendations by warehouse."""
        response = client.get("/api/restock/recommendations?budget=200000&warehouse=Tokyo")
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) > 0
        for item in data["items"]:
            assert item["warehouse"] == "Tokyo"

    def test_recommendations_by_category(self, client):
        """Test filtering recommendations by category."""
        response = client.get("/api/restock/recommendations?budget=200000&category=Power Supplies")
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) > 0
        for item in data["items"]:
            assert item["category"].lower() == "power supplies"

    def test_recommended_skus_exist_in_inventory(self, client):
        """Test that every recommended SKU has an inventory record."""
        inventory_skus = {item["sku"] for item in client.get("/api/inventory").json()}

        response = client.get("/api/restock/recommendations?budget=200000")
        data = response.json()

        for item in data["items"]:
            assert item["sku"] in inventory_skus
            assert 1 <= item["lead_time_days"] <= 30


class TestCreateRestockOrder:
    """Test suite for POST /api/restock-orders."""

    def test_create_restock_order(self, client):
        """Test creating a restock order with valid items."""
        payload = {
            "items": [
                {"sku": "TMP-201", "quantity": 100},
                {"sku": "SRV-302", "quantity": 10}
            ]
        }
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert order["status"] == "Submitted"
        assert order["customer"] == "Internal Restocking"
        assert order["order_number"].startswith("RST-")
        # TMP-201: 100 * 89.5, SRV-302: 10 * 725.0
        assert abs(order["total_value"] - (100 * 89.5 + 10 * 725.0)) < 0.01
        # SRV-302 has the longest lead time of the two items (21 days)
        assert order["lead_time_days"] == 21

        order_date = datetime.fromisoformat(order["order_date"])
        expected_delivery = datetime.fromisoformat(order["expected_delivery"])
        assert expected_delivery - order_date == timedelta(days=21)

    def test_created_order_items_structure(self, client):
        """Test that created order items include name and unit price from inventory."""
        payload = {"items": [{"sku": "PCB-001", "quantity": 50}]}
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert len(order["items"]) == 1
        item = order["items"][0]
        assert item["sku"] == "PCB-001"
        assert item["name"] == "Single Layer PCB Assembly"
        assert item["quantity"] == 50
        assert abs(item["unit_price"] - 24.99) < 0.01

    def test_created_order_appears_in_orders_endpoints(self, client):
        """Test that a submitted order is returned by the orders endpoints."""
        payload = {"items": [{"sku": "HMD-202", "quantity": 20}]}
        created = client.post("/api/restock-orders", json=payload).json()

        by_status = client.get("/api/orders?status=submitted").json()
        assert any(order["id"] == created["id"] for order in by_status)
        for order in by_status:
            assert order["status"].lower() == "submitted"

        by_id = client.get(f"/api/orders/{created['id']}")
        assert by_id.status_code == 200
        assert by_id.json()["order_number"] == created["order_number"]

    def test_duplicate_skus_are_aggregated(self, client):
        """Test that duplicate SKUs in the request are combined into one line."""
        payload = {
            "items": [
                {"sku": "PSU-505", "quantity": 10},
                {"sku": "PSU-505", "quantity": 5}
            ]
        }
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert len(order["items"]) == 1
        assert order["items"][0]["quantity"] == 15

    def test_create_order_empty_items(self, client):
        """Test that an order with no items is rejected."""
        response = client.post("/api/restock-orders", json={"items": []})
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_create_order_unknown_sku(self, client):
        """Test that an unknown SKU is rejected."""
        payload = {"items": [{"sku": "NOPE-999", "quantity": 5}]}
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 400
        assert "NOPE-999" in response.json()["detail"]

    def test_create_order_invalid_quantity(self, client):
        """Test that zero or negative quantities are rejected."""
        for quantity in [0, -5]:
            payload = {"items": [{"sku": "PCB-001", "quantity": quantity}]}
            response = client.post("/api/restock-orders", json=payload)
            assert response.status_code == 400

    def test_create_order_increments_order_count(self, client):
        """Test that placing an order adds exactly one order to the list."""
        count_before = len(client.get("/api/orders").json())

        payload = {"items": [{"sku": "ACC-206", "quantity": 5}]}
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 201

        count_after = len(client.get("/api/orders").json())
        assert count_after == count_before + 1
