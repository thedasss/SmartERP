"""
Database seeder — creates the initial company, super admin, and default
system roles/permissions. Run once after `alembic upgrade head`.
"""
import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.company import Company
from app.models.user import Permission, Role, RolePermission, User, UserRole
from app.models.base import generate_uuid

settings = get_settings()

# All system permissions
SYSTEM_PERMISSIONS = [
    # Users
    ("user.read", "user", "read", "View users"),
    ("user.create", "user", "create", "Create users"),
    ("user.update", "user", "update", "Update users"),
    ("user.delete", "user", "delete", "Deactivate users"),
    # Roles
    ("role.read", "role", "read", "View roles"),
    ("role.create", "role", "create", "Create roles"),
    ("role.update", "role", "update", "Update roles"),
    ("role.delete", "role", "delete", "Delete roles"),
    # Inventory
    ("inventory.read", "inventory", "read", "View inventory"),
    ("inventory.create", "inventory", "create", "Create inventory records"),
    ("inventory.update", "inventory", "update", "Update inventory"),
    ("inventory.delete", "inventory", "delete", "Delete inventory records"),
    # Products
    ("product.read", "product", "read", "View products"),
    ("product.create", "product", "create", "Create products"),
    ("product.update", "product", "update", "Update products"),
    ("product.delete", "product", "delete", "Delete products"),
    # Suppliers
    ("supplier.read", "supplier", "read", "View suppliers"),
    ("supplier.create", "supplier", "create", "Create suppliers"),
    ("supplier.update", "supplier", "update", "Update suppliers"),
    ("supplier.delete", "supplier", "delete", "Delete suppliers"),
    # Customers
    ("customer.read", "customer", "read", "View customers"),
    ("customer.create", "customer", "create", "Create customers"),
    ("customer.update", "customer", "update", "Update customers"),
    ("customer.delete", "customer", "delete", "Delete customers"),
    # Purchase
    ("purchase.read", "purchase", "read", "View purchase orders"),
    ("purchase.create", "purchase", "create", "Create purchase requests"),
    ("purchase.update", "purchase", "update", "Update purchase orders"),
    ("purchase.approve", "purchase", "approve", "Approve/reject purchase orders"),
    # Sales
    ("sales.read", "sales", "read", "View sales orders"),
    ("sales.create", "sales", "create", "Create sales orders"),
    ("sales.update", "sales", "update", "Update sales orders"),
    ("sales.approve", "sales", "approve", "Approve sales orders"),
    # Invoices
    ("invoice.read", "invoice", "read", "View invoices"),
    ("invoice.create", "invoice", "create", "Create invoices"),
    ("invoice.approve", "invoice", "approve", "Approve invoices"),
    ("invoice.update", "invoice", "update", "Update invoices"),
    # Payments
    ("payment.read", "payment", "read", "View payments"),
    ("payment.create", "payment", "create", "Record payments"),
    # Documents
    ("document.read", "document", "read", "View documents"),
    ("document.upload", "document", "upload", "Upload documents"),
    ("document.delete", "document", "delete", "Delete documents"),
    # Reports
    ("report.read", "report", "read", "View reports"),
    ("report.create", "report", "create", "Generate reports"),
    # AI
    ("ai.use", "ai", "use", "Use AI assistant"),
    # Warehouse
    ("warehouse.read", "warehouse", "read", "View warehouses"),
    ("warehouse.create", "warehouse", "create", "Create warehouses"),
    ("warehouse.update", "warehouse", "update", "Update warehouses"),
    # Audit
    ("audit.read", "audit", "read", "View audit logs"),
]

# Roles and their permission sets
SYSTEM_ROLES = {
    "Super Admin": list(set(p[0] for p in SYSTEM_PERMISSIONS)),
    "Admin": [
        p[0] for p in SYSTEM_PERMISSIONS
        if not p[0].startswith("audit")
    ],
    "Manager": [
        "user.read", "inventory.read", "inventory.update",
        "product.read", "product.create", "product.update",
        "supplier.read", "customer.read",
        "purchase.read", "purchase.approve",
        "sales.read", "sales.approve",
        "invoice.read", "invoice.approve",
        "payment.read", "report.read", "report.create",
        "document.read", "ai.use",
    ],
    "Procurement Officer": [
        "product.read", "supplier.read",
        "purchase.read", "purchase.create", "purchase.update",
        "inventory.read", "document.read", "document.upload",
        "ai.use",
    ],
    "Warehouse Officer": [
        "inventory.read", "inventory.create", "inventory.update",
        "product.read", "warehouse.read",
        "purchase.read", "document.read",
    ],
    "Sales Officer": [
        "customer.read", "customer.create",
        "product.read", "inventory.read",
        "sales.read", "sales.create",
        "invoice.read", "invoice.create",
        "payment.read", "document.read", "ai.use",
    ],
    "Accountant": [
        "invoice.read", "invoice.create", "invoice.approve",
        "payment.read", "payment.create",
        "report.read", "report.create",
        "supplier.read", "customer.read",
        "purchase.read", "document.read",
    ],
}


async def seed():
    async with AsyncSessionLocal() as session:
        try:
            # 1. Create default company if not exists
            result = await session.execute(
                select(Company).where(Company.code == "SMARTERP")
            )
            company = result.scalar_one_or_none()
            if not company:
                company = Company(
                    id=generate_uuid(),
                    name=settings.seed_company_name,
                    code="SMARTERP",
                    email="admin@smarterp.local",
                )
                session.add(company)
                await session.flush()
                print(f"[*] Created company: {company.name} (ID: {company.id})")
            else:
                print(f"[*] Company already exists: {company.name}")

            # 2. Create permissions
            perm_map: dict[str, Permission] = {}
            for name, module, action, description in SYSTEM_PERMISSIONS:
                result = await session.execute(
                    select(Permission).where(Permission.name == name)
                )
                perm = result.scalar_one_or_none()
                if not perm:
                    perm = Permission(
                        id=generate_uuid(),
                        name=name,
                        module=module,
                        action=action,
                        description=description,
                    )
                    session.add(perm)
                    await session.flush()
                perm_map[name] = perm

            print(f"[*] {len(perm_map)} permissions ready")

            # 3. Create system roles
            role_map: dict[str, Role] = {}
            for role_name, perms in SYSTEM_ROLES.items():
                result = await session.execute(
                    select(Role).where(
                        Role.name == role_name,
                        Role.is_system.is_(True),
                    )
                )
                role = result.scalar_one_or_none()
                if not role:
                    role = Role(
                        id=generate_uuid(),
                        name=role_name,
                        is_system=True,
                        company_id=None,
                        description=f"System role: {role_name}",
                    )
                    session.add(role)
                    await session.flush()

                    # Assign permissions
                    for perm_name in perms:
                        if perm_name in perm_map:
                            rp = RolePermission(
                                role_id=role.id,
                                permission_id=perm_map[perm_name].id,
                            )
                            session.add(rp)
                    await session.flush()
                    print(f"  [*] Role '{role_name}' created with {len(perms)} permissions")
                else:
                    print(f"  [*] Role '{role_name}' already exists")

                role_map[role_name] = role

            # 4. Create super admin user
            result = await session.execute(
                select(User).where(
                    User.email == settings.seed_admin_email,
                    User.company_id == company.id,
                )
            )
            admin = result.scalar_one_or_none()
            if not admin:
                admin = User(
                    id=generate_uuid(),
                    company_id=company.id,
                    email=settings.seed_admin_email,
                    password_hash=hash_password(settings.seed_admin_password),
                    first_name="Super",
                    last_name="Admin",
                    is_active=True,
                    is_super_admin=True,
                )
                session.add(admin)
                await session.flush()

                # Assign Super Admin role
                ur = UserRole(
                    user_id=admin.id,
                    role_id=role_map["Super Admin"].id,
                )
                session.add(ur)
                await session.flush()

                print(f"\n[*] Super Admin created:")
                print(f"  Email: {settings.seed_admin_email}")
                print(f"  Password: {settings.seed_admin_password}")
                print(f"  Company ID: {company.id}")
            else:
                print(f"\n[*] Super Admin already exists: {admin.email}")

            await session.commit()
            print("[INFO] Seeding completed successfully.")

        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Seeding failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed())
