"""
verify_relationships.py
Run this once during startup or tests to ensure all SQLAlchemy relationships
are correctly paired via back_populates.
"""

import importlib
import pkgutil
import sys

from sqlalchemy.orm import DeclarativeBase, RelationshipProperty, configure_mappers


def import_all_models(package_name: str) -> None:
    """
    Imports all models from the given package to ensure they are registered or loaded properly.

    This function dynamically imports all modules in the specified package by iterating over
    its submodules. It can be useful in scenarios where models need to be imported
    to register them with a framework or system, such as ORM models or application
    plugins.
    """
    package = importlib.import_module(package_name)
    for _, modname, module_exists in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        if not module_exists:
            importlib.import_module(modname)


def verify_relationship_pairs(base: type[DeclarativeBase]) -> None:
    """Check that every relationship(back_populates=X) is mirrored correctly on the other side."""
    print("🔍 Verifying SQLAlchemy relationships...")

    errors = []

    configure_mappers()

    for mapper in base.registry.mappers:
        cls = mapper.class_
        for prop in mapper.iterate_properties:
            if isinstance(prop, RelationshipProperty) and prop.back_populates:
                target_cls = getattr(prop.mapper, "class_", None)
                if target_cls is None:
                    continue
                target_name = prop.back_populates

                if not hasattr(target_cls, target_name):
                    errors.append(
                        f"[Error] {cls.__name__}.{prop.key} -> back_populates='{target_name}' "
                        f"but {target_cls.__name__} has no such attribute."
                    )
                    continue

                target_prop = getattr(target_cls, target_name)

                if not hasattr(target_prop, "property") or not isinstance(
                    target_prop.property, RelationshipProperty
                ):
                    errors.append(
                        f"[Error] {target_cls.__name__}.{target_name} is not a relationship() property."
                    )
                    continue

                if target_prop.property.back_populates != prop.key:
                    errors.append(
                        f"[Warn] Mismatch: {cls.__name__}.{prop.key} ↔ {target_cls.__name__}.{target_name} "
                        f"(expected back_populates='{prop.key}', "
                        f"found '{target_prop.property.back_populates}')"
                    )

    if errors:
        print("\n".join(errors))
        print(f"\n Found {len(errors)} relationship definition issue(s).")
        sys.exit(1)
    else:
        print(" All back_populates relationships are correctly paired!")


if __name__ == "__main__":
    import_all_models("src.models")
    from src.infrastructure.database import Base

    verify_relationship_pairs(Base)
