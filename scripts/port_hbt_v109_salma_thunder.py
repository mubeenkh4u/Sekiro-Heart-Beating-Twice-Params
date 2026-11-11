#!/usr/bin/env python3
"""Port the verified Salma Spiritfall and Cleaving Thunder changes to HBT v1.09."""

import argparse
from pathlib import Path

THUNDER_ROWS = {
    "1100016": "1100016,Crow's Bed Memorial Mob - Cleaving Thunder Blade,75500,250,-1,-1,6021,-1,0,0,-1,[0|0],0,1",
    "1100066": "1100066,Crow's Bed Memorial Mob - Cleaving Thunder Blade (Promissory Note),75500,225,-1,-1,6021,-1,0,0,-1,[0|0],0,1",
}


def read(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def write(path, content):
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(content)


def edit_fields(content, row_id, edits, required):
    lines = content.splitlines(keepends=True)
    columns = lines[0].rstrip("\r\n").split(",")
    fields_needed = set(required) | {name for name, _, _ in edits}
    indexes = {key: columns.index(key) for key in fields_needed}
    found = changed = 0
    for pos, line in enumerate(lines[1:], start=1):
        if line.partition(",")[0] != row_id:
            continue
        found += 1
        ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        row = line[:-len(ending)].split(",") if ending else line.split(",")
        assert len(row) == len(columns), f"Unexpected schema in row {row_id}"
        for field, value in required.items():
            assert row[indexes[field]] == value, f"Dependency {row_id}.{field} changed"
        for field, before, after in edits:
            index = indexes[field]
            assert row[index] in (before, after), (
                f"Unexpected value for {row_id}.{field}: {row[index]}"
            )
            if row[index] != after:
                row[index] = after
                changed += 1
        lines[pos] = ",".join(row) + ending
    assert found == 1, f"Missing or duplicate row {row_id}"
    return "".join(lines), changed


def check_effect_dependencies(content):
    header, *lines = content.splitlines()
    columns = header.split(",")
    index = {name: columns.index(name) for name in ("replaceSpEffectId", "spCategory")}
    targets = {"3133": ("replaceSpEffectId", "3134"),
               "9228": ("replaceSpEffectId", "9283"),
               "3411": ("spCategory", "162")}
    seen = set()
    for line in lines:
        row_id = line.partition(",")[0]
        if row_id not in targets:
            continue
        assert row_id not in seen, f"Duplicate dependency effect {row_id}"
        seen.add(row_id)
        field, expected = targets[row_id]
        assert line.split(",")[index[field]] == expected, (
            f"Salma/curse/Yashariku dependency {row_id}.{field} changed"
        )
    assert seen == set(targets), "Missing Salma/curse/Yashariku effect references"


def patch_shop(content, weapon_content):
    assert any(row.startswith("75500,") for row in weapon_content.splitlines()), (
        "Cleaving Thunder weapon 75500 is missing"
    )
    lines = content.splitlines(keepends=True)
    header = lines[0].rstrip("\r\n").split(",")
    assert header == [
        "ID", "Name", "equipId", "value", "mtrlId", "eventFlag",
        "flagId_forRelease", "sellQuantity", "shopType", "equipType",
        "value_SAN", "pad", "value_Add", "value_Magnification"
    ], "ShopLineupParam schema changed"
    existing = lines[1:]
    by_id = {}
    for row in existing:
        key = row.partition(",")[0]
        if key in set(THUNDER_ROWS) | {"1100006", "1100056", "1100015"}:
            assert key not in by_id, f"Duplicate controlled merchant ID {key}"
            by_id[key] = row.rstrip("\r\n")
    for key, expected_equip in (("1100006", "3450"), ("1100056", "3450"),
                                ("1100015", "9458")):
        assert by_id.get(key, "").split(",")[2:3] == [expected_equip], (
            f"Existing Crow's Bed inventory {key} was altered"
        )
    present = set(THUNDER_ROWS) & set(by_id)
    assert present in (set(), set(THUNDER_ROWS)), "Partial Cleaving Thunder patch"
    for key in present:
        assert by_id[key] == THUNDER_ROWS[key], f"Conflicting shop row {key}"
    if present:
        return content, 0
    assert all(int(existing[i - 1].partition(",")[0]) <=
               int(existing[i].partition(",")[0])
               for i in range(1, len(existing))), "Shop rows were not sorted"
    newline = "\r\n" if "\r\n" in content else "\n"
    rows = list(existing)
    rows.extend(THUNDER_ROWS[key] + newline for key in sorted(THUNDER_ROWS, key=int))
    rows.sort(key=lambda row: int(row.partition(",")[0]))
    return lines[0] + "".join(rows), 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    effect_path = root / "SpEffectParam.csv"
    goods_path = root / "EquipParamGoods.csv"
    shop_path = root / "ShopLineupParam.csv"
    effects_before = read(effect_path)
    goods_before = read(goods_path)
    shop_before = read(shop_path)
    effects_after, effect_edits = edit_fields(
        effects_before, "3134", [("effectEndurance", "40.1", "-1")],
        {"spCategory": "0", "atkOccurrenceSpEffectId": "9228", "motionInterval": "0.9"})
    check_effect_dependencies(effects_after)
    goods_after, goods_edits = edit_fields(
        goods_before, "3131",
        [("consumeResourceItemA", "10", "0"), ("consumeHpRate", "0.85", "0")],
        {"refId_default": "3133"})
    shop_after, shop_adds = patch_shop(shop_before, read(root / "EquipParamWeapon.csv"))
    if args.check:
        assert (effect_edits, goods_edits, shop_adds) == (0, 0, 0), (
            f"Unapplied patch: effect={effect_edits}, goods={goods_edits}, shop={shop_adds}"
        )
    else:
        for path, old, new in (
            (effect_path, effects_before, effects_after),
            (goods_path, goods_before, goods_after),
            (shop_path, shop_before, shop_after),
        ):
            if old != new:
                write(path, new)
    print(f"Salma/Cleaving Thunder v1.09 OK: {effect_edits} effect fields, "
          f"{goods_edits} goods fields, {shop_adds} shop rows changed")


if __name__ == "__main__":
    main()
