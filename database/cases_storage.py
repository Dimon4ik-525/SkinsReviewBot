import asyncio
from typing import Optional, List, Dict, Any
from firebase_admin import firestore
from database.firebase_provider import get_firestore_client

db = get_firestore_client()

async def get_all_cases() -> List[Dict[str, Any]]:
    loop = asyncio.get_running_loop()
    docs = await loop.run_in_executor(
        None, lambda: list(db.collection("cases").order_by("case_name").stream())
    )
    return [{"case_id": doc.id, **doc.to_dict()} for doc in docs]

async def get_case(case_id: str) -> Optional[Dict[str, Any]]:
    loop = asyncio.get_running_loop()
    doc = await loop.run_in_executor(
        None, lambda: db.collection("cases").document(case_id).get()
    )
    if doc.exists:
        return {"case_id": doc.id, **doc.to_dict()}
    return None

async def add_case_to_db(case_name: str, image_case: str = None) -> str:
    loop = asyncio.get_running_loop()
    doc_ref = await loop.run_in_executor(
        None, lambda: db.collection("cases").add({"case_name": case_name, "image_case": image_case})
    )
    return doc_ref[1].id

async def update_case(case_id: str, field: str, value: str) -> bool:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, lambda: db.collection("cases").document(case_id).update({field: value})
    )
    return True

async def delete_case(case_id: str) -> bool:
    loop = asyncio.get_running_loop()
    def _delete():
        db.collection("cases").document(case_id).delete()
        # Видаляємо згадки цього кейсу з усіх скінів
        skins = db.collection("skins").where("cases", "array_contains", case_id).stream()
        for skin in skins:
            skin.reference.update({"cases": firestore.ArrayRemove([case_id])})
    await loop.run_in_executor(None, _delete)
    return True

async def get_case_skins(case_id: str) -> List[Dict[str, Any]]:
    loop = asyncio.get_running_loop()
    docs = await loop.run_in_executor(
        None, lambda: list(db.collection("skins").where("cases", "array_contains", case_id).stream())
    )
    skins = [{"skin_id": doc.id, **doc.to_dict()} for doc in docs]
    skins.sort(key=lambda s: (s.get("rarity", ""), s.get("weapon_name", ""), s.get("skin_name", "")))
    return skins

async def add_skin_to_case(case_id: str, skin_id: str) -> bool:
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(
            None, lambda: db.collection("skins").document(skin_id).update({
                "cases": firestore.ArrayUnion([case_id])
            })
        )
        return True
    except Exception:
        return False

async def remove_skin_from_case(case_id: str, skin_id: str) -> bool:
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(
            None, lambda: db.collection("skins").document(skin_id).update({
                "cases": firestore.ArrayRemove([case_id])
            })
        )
        return True
    except Exception:
        return False