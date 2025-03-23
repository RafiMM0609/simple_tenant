import unittest
from unittest.mock import MagicMock, patch
import pytest
import os
import yaml
from repository.tenant import add_tenant, get_tenants, generate_service_yaml
from schemas.tenant import RegisTenantRequest, DataTenant

class TestTenant:
    
    @pytest.mark.asyncio
    async def test_add_tenant_success(self):
        db = MagicMock()
        db.table.return_value.insert.return_value.execute.return_value = {"id": 1, "tenant_name": "Test Tenant"}
        
        payload = RegisTenantRequest(
            tenant_name="Test Tenant",
            contact_email="test@example.com",
            phone="1234567890",
            subdomain="test-tenant"
        )
        
        response = await add_tenant(db, payload)
        
        # Assertions
        db.table.assert_called_once_with("tenants")
        db.table().insert.assert_called_once_with({
            "tenant_name": "Test Tenant",
            "contact_email": "test@example.com",
            "phone": "1234567890",
            "subdomain": "test-tenant",
            "tenant_code": "test"
        })
        assert response == {"id": 1, "tenant_name": "Test Tenant"}

    @pytest.mark.asyncio
    async def test_add_tenant_with_custom_subdomain(self):
        db = MagicMock()
        db.table.return_value.insert.return_value.execute.return_value = {"id": 1}
        
        payload = RegisTenantRequest(
            tenant_name="Custom Domain",
            contact_email="custom@example.com",
            phone="9876543210",
            subdomain="mycustom"
        )
        
        response = await add_tenant(db, payload)
        
        db.table().insert.assert_called_once_with({
            "tenant_name": "Custom Domain",
            "contact_email": "custom@example.com",
            "phone": "9876543210",
            "subdomain": "mycustom",
            "tenant_code": "cust"
        })

    @pytest.mark.asyncio
    async def test_add_tenant_failure(self):
        db = MagicMock()
        db.table.return_value.insert.return_value.execute.side_effect = Exception("Database error")
        
        payload = RegisTenantRequest(
            tenant_name="Test Tenant",
            contact_email="test@example.com",
            phone="1234567890",
            subdomain="test-tenant"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await add_tenant(db, payload)
        
        assert str(exc_info.value) == "Failed to add tenant. Please check the provided data and try again."

    @pytest.mark.asyncio
    async def test_get_tenants_success(self):
        db = MagicMock()
        tenant_data = [
            {"id": 1, "tenant_name": "Tenant 1", "contact_email": "tenant1@example.com", 
             "phone": "1111111111", "subdomain": "tenant1", "tenant_code": "ten1"},
            {"id": 2, "tenant_name": "Tenant 2", "contact_email": "tenant2@example.com", 
             "phone": "2222222222", "subdomain": "tenant2", "tenant_code": "ten2"}
        ]
        db.table.return_value.select.return_value.execute.return_value = MagicMock(data=tenant_data)
        
        result = await get_tenants(db)
        
        db.table.assert_called_once_with("tenants")
        db.table().select.assert_called_once_with("*")
        assert len(result) == 2
        assert all(isinstance(tenant, dict) for tenant in result)
        assert result[0]["tenant_name"] == "Tenant 1"
        assert result[1]["tenant_name"] == "Tenant 2"

    @pytest.mark.asyncio
    async def test_get_tenants_empty(self):
        db = MagicMock()
        db.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
        
        result = await get_tenants(db)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_tenants_failure(self):
        db = MagicMock()
        db.table.return_value.select.return_value.execute.side_effect = Exception("Database error")
        
        with pytest.raises(ValueError) as exc_info:
            await get_tenants(db)
        
        assert str(exc_info.value) == "Failed to retrieve tenants. Please try again."

    @pytest.mark.asyncio
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=MagicMock)
    @patch("yaml.dump")
    async def test_generate_service_yaml(self, mock_yaml_dump, mock_open, mock_makedirs):
        db = MagicMock()
        tenant_data = {
            "tenant_code": "test", 
            "subdomain": "test-tenant",
            "tenant_name": "Test Tenant"
        }
        db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[tenant_data])
        
        result = await generate_service_yaml(db, "test")
        
        mock_makedirs.assert_called_once_with("./generated_services", exist_ok=True)
        assert mock_open.call_count >= 2  # At least deployment.yaml and service.yaml
        assert mock_yaml_dump.called
        assert "deployment_file" in result
        assert "service_file" in result

    @pytest.mark.asyncio
    async def test_generate_service_yaml_no_tenant_code(self):
        db = MagicMock()
        
        with pytest.raises(ValueError) as exc_info:
            await generate_service_yaml(db, "")
        
        assert "Tenant code is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_service_yaml_tenant_not_found(self):
        db = MagicMock()
        db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
        
        with pytest.raises(ValueError) as exc_info:
            await generate_service_yaml(db, "nonexistent")
        
        assert "Tenant not found" in str(exc_info.value)
        db.table().insert.assert_called_once_with({
            "tenant_name": "Test Tenant",
            "contact_email": "test@example.com",
            "phone": "1234567890",
            "subdomain": "test-tenant"
        })
        self.assertEqual(response, {"id": 1, "tenant_name": "Test Tenant"})

    async def test_add_tenant_failure(self):
        db = MagicMock()
        db.table.return_value.insert.return_value.execute.side_effect = Exception("Database error")
        
        payload = RegisTenantRequest(
            tenant_name="Test Tenant",
            contact_email="test@example.com",
            phone="1234567890",
            subdomain="test-tenant"
        )
        
        with self.assertRaises(ValueError) as context:
            await add_tenant(db, payload)
        
        # Assertions
        db.table.assert_called_once()
        db.table().insert.assert_called_once_with({
            "tenant_name": "Test Tenant",
            "contact_email": "test@example.com",
            "phone": "1234567890",
            "subdomain": "test-tenant"
        })
        self.assertEqual(str(context.exception), "Failed to add tenant. Please check the provided data and try again.")

if __name__ == "__main__":
    unittest.main()