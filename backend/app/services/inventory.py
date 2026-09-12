from typing import List, Tuple
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.models.inventory import Warehouse, StockItem, StockMovement, MovementType
from app.repositories.inventory import WarehouseRepository, StockItemRepository, StockMovementRepository
from app.repositories.product import ProductRepository
from app.schemas.inventory import (
    WarehouseCreate, WarehouseUpdate,
    StockMovementCreate
)

class InventoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.warehouse_repo = WarehouseRepository(session)
        self.stock_item_repo = StockItemRepository(session)
        self.stock_movement_repo = StockMovementRepository(session)
        self.product_repo = ProductRepository(session)

    # --- Warehouses ---

    async def get_warehouses(
        self, company_id: str, offset: int = 0, limit: int = 50
    ) -> Tuple[List[Warehouse], int]:
        return await self.warehouse_repo.get_all(
            filters={"company_id": company_id}, offset=offset, limit=limit
        )

    async def get_warehouse(self, warehouse_id: str, company_id: str) -> Warehouse:
        warehouse = await self.warehouse_repo.get_by_id(warehouse_id)
        if not warehouse or str(warehouse.company_id) != str(company_id) or warehouse.is_deleted:
            raise NotFoundError("Warehouse not found")
        return warehouse

    async def create_warehouse(self, data: WarehouseCreate, company_id: str) -> Warehouse:
        existing = await self.warehouse_repo.get_by_code(company_id, data.code)
        if existing:
            raise ConflictError(f"Warehouse with code '{data.code}' already exists.")
        
        return await self.warehouse_repo.create(
            **data.model_dump(), company_id=company_id
        )

    async def update_warehouse(
        self, warehouse_id: str, data: WarehouseUpdate, company_id: str
    ) -> Warehouse:
        warehouse = await self.get_warehouse(warehouse_id, company_id)
        
        if data.code and data.code != warehouse.code:
            existing = await self.warehouse_repo.get_by_code(company_id, data.code)
            if existing:
                raise ConflictError(f"Warehouse with code '{data.code}' already exists.")
                
        return await self.warehouse_repo.update(warehouse, **data.model_dump(exclude_unset=True))

    async def delete_warehouse(self, warehouse_id: str, company_id: str) -> None:
        warehouse = await self.get_warehouse(warehouse_id, company_id)
        
        # Check if warehouse has any stock items with non-zero quantity
        items, count = await self.stock_item_repo.get_all(
            filters={"warehouse_id": warehouse_id, "company_id": company_id}
        )
        for item in items:
            if item.quantity > 0:
                raise ConflictError("Cannot delete warehouse with existing stock. Please transfer or adjust stock to zero first.")
                
        await self.warehouse_repo.soft_delete(warehouse)

    # --- Stock Items ---

    async def get_stock_items(
        self, company_id: str, warehouse_id: str = None, product_id: str = None,
        offset: int = 0, limit: int = 50
    ) -> Tuple[List[StockItem], int]:
        filters = {"company_id": company_id}
        if warehouse_id:
            filters["warehouse_id"] = warehouse_id
        if product_id:
            filters["product_id"] = product_id
            
        return await self.stock_item_repo.get_all(
            filters=filters, offset=offset, limit=limit
        )

    # --- Stock Movements ---
    
    async def get_movements(
        self, company_id: str, warehouse_id: str = None, product_id: str = None,
        offset: int = 0, limit: int = 50
    ) -> Tuple[List[StockMovement], int]:
        filters = {"company_id": company_id}
        if warehouse_id:
            filters["warehouse_id"] = warehouse_id
        if product_id:
            filters["product_id"] = product_id
            
        # We probably want sorting by created_at DESC, but the base repo doesn't do it right now.
        return await self.stock_movement_repo.get_all(
            filters=filters, offset=offset, limit=limit
        )

    async def record_movement(self, data: StockMovementCreate, company_id: str) -> StockMovement:
        # Validate warehouse
        warehouse = await self.get_warehouse(str(data.warehouse_id), company_id)
        
        # Validate product
        product = await self.product_repo.get_by_id(str(data.product_id))
        if not product or str(product.company_id) != str(company_id) or product.is_deleted:
            raise NotFoundError("Product not found")

        # Get or create stock item
        stock_item = await self.stock_item_repo.get_stock_item(
            company_id, str(warehouse.id), str(product.id)
        )
        
        if not stock_item:
            stock_item = await self.stock_item_repo.create(
                company_id=company_id,
                warehouse_id=str(warehouse.id),
                product_id=str(product.id),
                quantity=Decimal("0.00")
            )
            
        # Calculate new quantity based on movement type
        qty_change = data.quantity
        if data.movement_type == MovementType.OUT:
            qty_change = -data.quantity
            
        new_quantity = stock_item.quantity + qty_change
        
        # Check negative stock
        if new_quantity < 0:
            raise ValidationError(f"Insufficient stock for product '{product.name}' in warehouse '{warehouse.name}'. Current quantity: {stock_item.quantity}")

        # Update stock item
        await self.stock_item_repo.update(stock_item, quantity=new_quantity)
        
        # Create movement record
        movement_data = data.model_dump()
        movement_data["warehouse_id"] = str(movement_data["warehouse_id"])
        movement_data["product_id"] = str(movement_data["product_id"])
        
        movement = await self.stock_movement_repo.create(
            **movement_data, company_id=company_id
        )
        
        # Eager load the relationships for response by explicitly fetching the fresh instance if needed, 
        # or manually attaching them
        movement.product = product
        movement.warehouse = warehouse
        
        return movement
