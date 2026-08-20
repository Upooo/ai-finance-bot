# Permissions Model

## Design Principles

1. **Centralized RBAC** — No `if role == "founder"` checks in handlers.
2. **Explicit Permissions** — Every action requires a specific `PermissionKey`.
3. **Role Hierarchy** — Limits management scope (can't manage roles at or above your level).
4. **Founder Wildcard** — Founder has ALL permissions implicitly, no explicit assignment needed.
5. **Everyone else is explicit** — Owner, Admin, Worker, Customer have ONLY what's assigned.

## Authorization Flow

```
Request
  → Auth Middleware: inject user + roles + permissions
  → Handler: auth_service.require_permission(user, PermissionKey.STAFF_MANAGE)
  → AuthService:
      1. Check user.has_permission(key)  → PermissionDeniedError if no
      2. If managing a role: check hierarchy  → RoleHierarchyError if violates
      3. If target is Founder: check FounderProtection  → FounderProtectionError
      4. Audit log the attempt (success or failure)
  → Execute action
```

## Role Hierarchy

| Role     | Level | Description                                  |
|----------|-------|----------------------------------------------|
| Founder  | 1     | Immutable root identity. Has ALL permissions. |
| Owner    | 2     | Operational lead. Permissions via RBAC.       |
| Admin    | 3     | Group/staff management. Permissions via RBAC. |
| Worker   | 4     | Operational staff. Permissions via RBAC.      |
| Customer | 5     | End user. Permissions via RBAC.               |

## Key Rules

- A user can only manage roles with a **higher level number** than their own.
- Founder (level 1) can manage ALL roles.
- Owner (level 2) can manage Admin (3), Worker (4), Customer (5) — but NOT Founder (1) or other Owners (2) unless they have `roles.assign`.
- Hierarchy is a **ceiling**, not the sole authority — you also need the explicit permission.

## Founder Protection (V1)

- Founder **cannot** be deleted.
- Founder **cannot** be demoted.
- Founder **cannot** be transferred.
- Founder **cannot** be modified via normal bot operations.
- Founder identity comes **exclusively** from `FOUNDER_TELEGRAM_ID` env var.

## Permission Keys

See `src/domain/enums.py` → `PermissionKey` for the complete list.

## Configuring Permissions

Founder can manage all role-permission mappings via bot:
- Assign/remove permissions to Owner, Admin, Worker, Customer roles
- No source code changes needed
- All changes are audited
