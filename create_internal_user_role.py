from superset import db
from flask_appbuilder.security.sqla.models import Role, PermissionView


ROLE_NAME = "InternalUser"

REQUIRED_PERMISSIONS = [
    ("can_read", "AdvancedDataType"),
    ("can_query", "Api"),
    ("can_query_form_data", "Api"),
    ("can_time_range", "Api"),
    ("can_read", "AvailableDomains"),
    ("can_read", "Chart"),
    ("can_read", "CssTemplate"),
    ("can_read", "CurrentUserRestApi"),
    ("can_drill", "Dashboard"),
    ("can_get_embedded", "Dashboard"),
    ("can_read", "Dashboard"),
    ("can_view_chart_as_table", "Dashboard"),
    ("can_view_query", "Dashboard"),
    ("can_read", "DashboardFilterStateRestApi"),
    ("can_read", "DashboardPermalinkRestApi"),
    ("menu_access", "Dashboards"),
    ("can_read", "Database"),
    ("can_get_drill_info", "Dataset"),
    ("can_read", "Dataset"),
    ("can_external_metadata", "Datasource"),
    ("can_get", "Datasource"),
    ("can_query", "Datasource"),
    ("can_read", "Datasource"),
    ("can_list", "DynamicPlugin"),
    ("can_read", "EmbeddedDashboard"),
    ("can_read", "Explore"),
    ("can_read", "ExploreFormDataRestApi"),
    ("can_read", "ExplorePermalinkRestApi"),
    ("can_recent_activity", "Log"),
    ("can_read", "Realtime"),
    ("can_read", "SecurityRestApi"),
    ("can_read", "SemanticLayer"),
    ("can_csv", "Superset"),
    ("can_dashboard", "Superset"),
    ("can_fetch_datasource_metadata", "Superset"),
    ("can_file_handler", "Superset"),
    ("can_log", "Superset"),
    ("can_share_chart", "Superset"),
    ("can_share_dashboard", "Superset"),
    ("can_read", "Tag"),
    ("can_tags", "TagView"),
    ("can_read", "Task"),
    ("can_read", "Theme"),
    ("can_userinfo", "UserDBModelView"),
    ("can_userinfo", "UserLDAPModelView"),
    ("can_avatar", "UserRestApi"),
    ("all_database_access", "all_database_access"),
    ("all_datasource_access", "all_datasource_access"),
    ("all_query_access", "all_query_access"),
    ("can_read", "user"),
]


print("=" * 60)
print("Creating/configuring InternalUser role")
print("=" * 60)


# ---------------------------------------------------------
# Get existing role
# ---------------------------------------------------------

role = (
    db.session.query(Role)
    .filter(Role.name == ROLE_NAME)
    .one_or_none()
)


# ---------------------------------------------------------
# Create role if missing
# ---------------------------------------------------------

if role is None:
    print(f"Creating role: {ROLE_NAME}")

    role = Role(name=ROLE_NAME)

    db.session.add(role)
    db.session.flush()

    print(f"Created role: {ROLE_NAME} (id={role.id})")

else:
    print(f"Role already exists: {ROLE_NAME} (id={role.id})")


# ---------------------------------------------------------
# Add permissions
# ---------------------------------------------------------

added = 0
already_exists = 0
missing = 0


for permission_name, view_name in REQUIRED_PERMISSIONS:

    permission_view = (
        db.session.query(PermissionView)
        .filter(
            PermissionView.permission.has(
                name=permission_name
            ),
            PermissionView.view_menu.has(
                name=view_name
            ),
        )
        .one_or_none()
    )

    if permission_view is None:
        print(
            f"WARNING - permission not found: "
            f"{permission_name} -> {view_name}"
        )

        missing += 1
        continue

    if permission_view in role.permissions:

        print(
            f"EXISTS  - "
            f"{permission_name} -> {view_name}"
        )

        already_exists += 1

    else:

        role.permissions.append(permission_view)

        print(
            f"ADDED   - "
            f"{permission_name} -> {view_name}"
        )

        added += 1


# ---------------------------------------------------------
# Commit
# ---------------------------------------------------------

db.session.commit()


# ---------------------------------------------------------
# Final output
# ---------------------------------------------------------

print()
print("=" * 60)
print("InternalUser configuration completed")
print("=" * 60)

print(f"Role ID            : {role.id}")
print(f"Permissions added  : {added}")
print(f"Already existed    : {already_exists}")
print(f"Permissions missing: {missing}")
print(f"Total permissions  : {len(role.permissions)}")

print()
print("Final permissions:")
print("-" * 60)


for permission_view in sorted(
    role.permissions,
    key=lambda x: (
        x.view_menu.name,
        x.permission.name,
    ),
):
    print(
        f"{permission_view.permission.name} "
        f"-> "
        f"{permission_view.view_menu.name}"
    )


print("=" * 60)
