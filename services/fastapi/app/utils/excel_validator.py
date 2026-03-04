def validate_excel(columns: list) -> bool:
    required = ["name", "phone", "next_visit"]
    return all(col.lower() in [c.lower() for c in columns] for col in required)
