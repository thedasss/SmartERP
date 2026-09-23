import uuid
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.sales import SalesOrderRepository, ShipmentRepository
from app.schemas.sales import SalesOrderCreate, ShipmentCreate
from app.models.sales import SalesOrder, SalesOrderItem, Shipment, ShipmentItem, SOStatus
from app.services.inventory import InventoryService
from app.schemas.inventory import StockMovementCreate
from app.models.inventory import MovementType

class SalesService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.so_repo = SalesOrderRepository(session)
        self.ship_repo = ShipmentRepository(session)
        self.inventory_service = InventoryService(session)

    def generate_so_number(self) -> str:
        return f"SO-{str(uuid.uuid4())[:8].upper()}"

    def generate_shipment_number(self) -> str:
        return f"SHP-{str(uuid.uuid4())[:8].upper()}"

    async def create_sales_order(self, company_id: str, data: SalesOrderCreate) -> SalesOrder:
        total_amount = sum(item.quantity * item.unit_price for item in data.items)
        
        so_number = self.generate_so_number()
        
        so_dict = data.model_dump(exclude={"items"})
        so_dict["company_id"] = company_id
        so_dict["so_number"] = so_number
        so_dict["total_amount"] = total_amount
        so_dict["status"] = SOStatus.CONFIRMED
        
        so_items = [
            SalesOrderItem(**item.model_dump()) for item in data.items
        ]
        
        so_dict["items"] = so_items
        
        return await self.so_repo.create(**so_dict)

    async def ship_goods(self, company_id: str, data: ShipmentCreate) -> Shipment:
        # 1. Fetch SO
        so = await self.so_repo.get_by_id(data.so_id)
        if not so or str(so.company_id) != company_id:
            raise HTTPException(status_code=404, detail="Sales order not found")
        
        if so.status in (SOStatus.SHIPPED, SOStatus.CANCELLED):
            raise HTTPException(status_code=400, detail=f"Cannot ship goods for SO in status: {so.status}")

        # 2. Process shipment items
        shipment_items = []
        so_item_map = {str(item.id): item for item in so.items}
        
        all_shipped_fully = True

        for shipment_item_data in data.items:
            so_item_id_str = str(shipment_item_data.so_item_id)
            if so_item_id_str not in so_item_map:
                raise HTTPException(status_code=400, detail=f"SO Item {so_item_id_str} does not belong to this SO")
            
            so_item = so_item_map[so_item_id_str]
            qty_to_ship = shipment_item_data.quantity_shipped
            
            # Validate we aren't over-shipping
            remaining_qty = so_item.quantity - so_item.shipped_quantity
            if qty_to_ship > remaining_qty:
                raise HTTPException(status_code=400, detail=f"Cannot ship {qty_to_ship} for item {so_item_id_str}. Only {remaining_qty} remaining.")
            
            # 3. Create Stock Movement (Integrating Sales with Inventory!)
            # This will raise a ValidationError internally if stock is insufficient
            stock_movement = StockMovementCreate(
                product_id=str(so_item.product_id),
                warehouse_id=data.warehouse_id,
                movement_type=MovementType.OUT,
                quantity=qty_to_ship,
                reference=f"Shipment against SO: {so.so_number}",
                notes=data.notes
            )
            await self.inventory_service.record_movement(stock_movement, company_id)

            # Update SO Item
            so_item.shipped_quantity += qty_to_ship
            if so_item.shipped_quantity < so_item.quantity:
                all_shipped_fully = False

            # Create Shipment Item
            shipment_items.append(ShipmentItem(
                so_item_id=so_item_id_str,
                quantity_shipped=qty_to_ship
            ))

        # Ensure we didn't miss checking unshipped items if this iteration thinks everything is fully shipped
        for item in so.items:
            if item.shipped_quantity < item.quantity:
                all_shipped_fully = False
                break
        
        # 4. Update SO Status
        await self.so_repo.update(so, status=SOStatus.SHIPPED if all_shipped_fully else SOStatus.PARTIALLY_SHIPPED)

        # 5. Create Shipment Record
        return await self.ship_repo.create(
            company_id=company_id,
            so_id=str(so.id),
            warehouse_id=data.warehouse_id,
            shipment_number=self.generate_shipment_number(),
            notes=data.notes,
            items=shipment_items
        )
