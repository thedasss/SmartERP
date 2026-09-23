import uuid
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.procurement import PurchaseOrderRepository, GoodsReceiptRepository
from app.schemas.procurement import PurchaseOrderCreate, GoodsReceiptCreate
from app.models.procurement import PurchaseOrder, PurchaseOrderItem, GoodsReceipt, GoodsReceiptItem, POStatus
from app.services.inventory import InventoryService
from app.schemas.inventory import StockMovementCreate
from app.models.inventory import MovementType

class ProcurementService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.po_repo = PurchaseOrderRepository(session)
        self.gr_repo = GoodsReceiptRepository(session)
        self.inventory_service = InventoryService(session)

    def generate_po_number(self) -> str:
        # In a real system, use sequences. For now, random UUID prefix.
        return f"PO-{str(uuid.uuid4())[:8].upper()}"

    def generate_gr_number(self) -> str:
        return f"GR-{str(uuid.uuid4())[:8].upper()}"

    async def create_purchase_order(self, db: AsyncSession, company_id: str, data: PurchaseOrderCreate) -> PurchaseOrder:
        total_amount = sum(item.quantity * item.unit_price for item in data.items)
        
        po_number = self.generate_po_number()
        
        po_dict = data.model_dump(exclude={"items"})
        po_dict["company_id"] = company_id
        po_dict["po_number"] = po_number
        po_dict["total_amount"] = total_amount
        po_dict["status"] = POStatus.ISSUED
        
        po_items = [
            PurchaseOrderItem(**item.model_dump()) for item in data.items
        ]
        
        po_dict["items"] = po_items
        
        return await self.po_repo.create(**po_dict)

    async def receive_goods(self, db: AsyncSession, company_id: str, data: GoodsReceiptCreate) -> GoodsReceipt:
        # 1. Fetch PO
        po = await self.po_repo.get_by_id(data.po_id)
        if not po or str(po.company_id) != company_id:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        
        if po.status in (POStatus.RECEIVED, POStatus.CANCELLED):
            raise HTTPException(status_code=400, detail=f"Cannot receive goods for PO in status: {po.status}")

        # 2. Process receipt items
        receipt_items = []
        po_item_map = {str(item.id): item for item in po.items}
        
        all_received_fully = True

        for receipt_item_data in data.items:
            po_item_id_str = str(receipt_item_data.po_item_id)
            if po_item_id_str not in po_item_map:
                raise HTTPException(status_code=400, detail=f"PO Item {po_item_id_str} does not belong to this PO")
            
            po_item = po_item_map[po_item_id_str]
            qty_to_receive = receipt_item_data.quantity_received
            
            # Validate we aren't over-receiving
            remaining_qty = po_item.quantity - po_item.received_quantity
            if qty_to_receive > remaining_qty:
                raise HTTPException(status_code=400, detail=f"Cannot receive {qty_to_receive} for item {po_item_id_str}. Only {remaining_qty} remaining.")
            
            # Update PO Item
            po_item.received_quantity += qty_to_receive
            if po_item.received_quantity < po_item.quantity:
                all_received_fully = False

            # Create Receipt Item
            receipt_items.append(GoodsReceiptItem(
                po_item_id=po_item_id_str,
                quantity_received=qty_to_receive
            ))

            # 3. Create Stock Movement (Integrating Procurement with Inventory!)
            stock_movement = StockMovementCreate(
                product_id=str(po_item.product_id),
                warehouse_id=data.warehouse_id,
                movement_type=MovementType.IN,
                quantity=qty_to_receive,
                reference=f"Receipt against PO: {po.po_number}",
                notes=data.notes
            )
            # Notice we use the inventory_service instance, but since inventory_service uses session in init, we don't pass db here in our updated method signature.
            # Wait, record_movement takes (data, company_id)
            await self.inventory_service.record_movement(stock_movement, company_id)

        # Ensure we didn't miss checking unreceived items if this iteration thinks everything is fully received
        for item in po.items:
            if item.received_quantity < item.quantity:
                all_received_fully = False
                break
        
        # 4. Update PO Status
        await self.po_repo.update(po, status=POStatus.RECEIVED if all_received_fully else POStatus.PARTIALLY_RECEIVED)

        # 5. Create Goods Receipt Record
        return await self.gr_repo.create(
            company_id=company_id,
            po_id=str(po.id),
            warehouse_id=data.warehouse_id,
            receipt_number=self.generate_gr_number(),
            notes=data.notes,
            items=receipt_items
        )
