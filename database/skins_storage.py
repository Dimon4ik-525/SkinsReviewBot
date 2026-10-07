import asyncio
from typing import Optional, List, Dict, Any
from database.firebase_provider import get_firestore_client

db = get_firestore_client()

# --- WEAPONS ---

async def get_all_weapons() -> List[Dict[str, Any]]:
    loop = asyncio.get_running_loop()
    docs = await loop.run_in_executor(
        None, lambda: list(db.collection("weapons").order_by("weapon_name").stream())
    )
    return [{"weapon_id": doc.id, **doc.to_dict()} for doc in docs]

async def get_weapon(weapon_id: str) -> Optional[Dict[str, Any]]:
    loop = asyncio.get_running_loop()
    doc = await loop.run_in_executor(
        None, lambda: db.collection("weapons").document(weapon_id).get()
    )
    if doc.exists:
        return {"weapon_id": doc.id, **doc.to_dict()}
    return None

async def add_weapon_to_db(weapon_name: str) -> str:
    loop = asyncio.get_running_loop()
    doc_ref = await loop.run_in_executor(
        None, lambda: db.collection("weapons").add({"weapon_name": weapon_name})
    )
    return doc_ref[1].id

async def update_weapon(weapon_id: str, weapon_name: str) -> bool:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, lambda: db.collection("weapons").document(weapon_id).update({"weapon_name": weapon_name})
    )
    return True

async def delete_weapon(weapon_id: str) -> bool:
    loop = asyncio.get_running_loop()
    # Видаляємо зброю та пов'язані скіни
    def _delete():
        db.collection("weapons").document(weapon_id).delete()
        skins_query = db.collection("skins").where("weapon_id", "==", weapon_id).stream()
        for s in skins_query:
            s.reference.delete()
    await loop.run_in_executor(None, _delete)
    return True


# --- SKINS ---

async def get_all_skins() -> List[Dict[str, Any]]:
    loop = asyncio.get_running_loop()
    docs = await loop.run_in_executor(
        None, lambda: list(db.collection("skins").stream())
    )
    skins = [{"skin_id": doc.id, **doc.to_dict()} for doc in docs]
    skins.sort(key=lambda s: (s.get("weapon_name", ""), s.get("skin_name", "")))
    return skins

async def get_skin(skin_id: str) -> Optional[Dict[str, Any]]:
    loop = asyncio.get_running_loop()
    doc = await loop.run_in_executor(
        None, lambda: db.collection("skins").document(skin_id).get()
    )
    if doc.exists:
        return {"skin_id": doc.id, **doc.to_dict()}
    return None

async def get_weapon_skins(weapon_id: str) -> List[Dict[str, Any]]:
    loop = asyncio.get_running_loop()
    docs = await loop.run_in_executor(
        None, lambda: list(db.collection("skins").where("weapon_id", "==", weapon_id).stream())
    )
    skins = [{"skin_id": doc.id, **doc.to_dict()} for doc in docs]
    skins.sort(key=lambda s: (s.get("rarity", ""), s.get("skin_name", "")))
    return skins

async def add_skin_to_db(skin_name: str, weapon_id: str, weapon_name: str,
                         rarity: str = None, stattrak: bool = False,
                         souvenir: bool = False, image_skin: str = None) -> str:
    loop = asyncio.get_running_loop()
    skin_data = {
        "skin_name": skin_name,
        "weapon_id": weapon_id,
        "weapon_name": weapon_name,
        "rarity": rarity,
        "stattrak": stattrak,
        "souvenir": souvenir,
        "image_skin": image_skin,
        "wears": [],
        "cases": []
    }
    doc_ref = await loop.run_in_executor(
        None, lambda: db.collection("skins").add(skin_data)
    )
    return doc_ref[1].id

async def update_skin(skin_id: str, field: str, value: Any) -> bool:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, lambda: db.collection("skins").document(skin_id).update({field: value})
    )
    return True

async def delete_skin(skin_id: str) -> bool:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, lambda: db.collection("skins").document(skin_id).delete()
    )
    return True

async def add_skinwear_to_db(skin_id: str, weartype: str, floatmin: float, floatmax: float) -> bool:
    loop = asyncio.get_running_loop()
    wear_item = {"weartype": weartype, "floatmin": floatmin, "floatmax": floatmax}
    await loop.run_in_executor(
        None, lambda: db.collection("skins").document(skin_id).update({
            "wears": firestore.ArrayUnion([wear_item])
        })
    )
    return True