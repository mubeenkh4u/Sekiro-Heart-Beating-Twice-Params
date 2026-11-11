#!/usr/bin/env python3
"""Apply and verify the previously chosen HBT custom CSV patches on v1.09."""

from pathlib import Path
import argparse

MATERIALS = [
    (6000, "Scrap Iron"),
    (6010, "Scrap Magnetite"),
    (6020, "Adamantite Scrap"),
    (6100, "Black Gunpowder"),
    (6200, "Yellow Gunpowder"),
    (6210, "Fulminated Mercury"),
    (6300, "Lump of Fat Wax"),
    (6310, "Lump of Grave Wax"),
    (6400, "Lapis Lazuli"),
    (9701, "Phantom Kunai"),
    (9721, "Pine Resin Ember"),
    (9791, "Malcontent's Ring"),
]
SEN = {
    "127072": "-1", "127073": "-1", "127074": "-8",
    "127075": "-5", "127076": "-15", "127077": "-10",
}
CONFETTI = {"2801", "2802", "2803", "2804"}
SHOP_HEADER = (
    "ID,Name,equipId,value,mtrlId,eventFlag,flagId_forRelease,"
    "sellQuantity,shopType,equipType,value_SAN,pad,value_Add,value_Magnification"
)

def read(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()

def write(path, content):
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(content)

def patch_effects(content):
    header = content.split("\n", 1)[0].split(",")
    assert len(header) == 410, f"Unexpected SpEffectParam schema: {len(header)} columns"
    indexes = {name: header.index(name) for name in ("soul", "effectEndurance", "motionInterval")}
    targets = set(SEN) | CONFETTI
    seen, changes, result = set(), 0, []
    for line in content.splitlines(keepends=True):
        row_id = line.partition(",")[0]
        if row_id not in targets:
            result.append(line)
            continue
        assert row_id not in seen, f"Repeated effect ID {row_id}"
        seen.add(row_id)
        ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        fields = line[:-len(ending)].split(",") if ending else line.split(",")
        assert len(fields) == len(header), f"Malformed effect row {row_id}"
        if row_id in SEN:
            patches = [("soul", SEN[row_id], "0")]
        else:
            patches = [("effectEndurance", "105", "3600")]
            patches.append(("motionInterval", "0" if row_id == "2804" else "106",
                            "0" if row_id == "2804" else "3601"))
        for name, before, after in patches:
            column = indexes[name]
            assert fields[column] in (before, after), (
                f"Unexpected SpEffect value ID={row_id} {name}={fields[column]}"
            )
            if fields[column] != after:
                fields[column] = after
                changes += 1
        result.append(",".join(fields) + ending)
    assert seen == targets, f"Missing SpEffect IDs: {targets - seen}"
    return "".join(result), changes

def patch_shop(content, goods_content):
    lines = content.splitlines(keepends=True)
    assert lines[0].rstrip("\r\n") == SHOP_HEADER, "ShopLineupParam column layout changed"
    ids_in_goods = {row.partition(",")[0] for row in goods_content.splitlines()[1:]}
    existing = lines[1:]
    existing_ids = {row.partition(",")[0] for row in existing}
    for goods_id, _ in MATERIALS:
        assert str(goods_id) in ids_in_goods, f"Missing material goods ID {goods_id}"
    planned = {}
    for offset, (goods_id, name) in enumerate(MATERIALS):
        for base, tag in ((1100020, ""), (1100070, " (Promissory Note)")):
            row_id = str(base + offset)
            planned[row_id] = ",".join([
                row_id, "Crow's Bed Memorial Mob - " + name + tag,
                str(goods_id), "1", "-1", "-1", "-1", "-1",
                "0", "3", "-1", "[0|0]", "0", "1",
            ])
    present = set(planned) & existing_ids
    assert not present or present == set(planned), (
        "Partial patch already present in shop; inspect before proceeding"
    )
    rows = list(existing)
    if present:
        for row in existing:
            row_id = row.partition(",")[0]
            if row_id in planned:
                assert row.rstrip("\r\n") == planned[row_id], f"Conflicting shop ID {row_id}"
        return content, 0
    assert len(planned) == 24, "Expected 24 unique material shop rows"
    newline = "\r\n" if "\r\n" in content else "\n"
    rows += [planned[row_id] + newline for row_id in planned]
    assert all(int(rows[i - 1].partition(",")[0]) <= int(rows[i].partition(",")[0])
               for i in range(1, len(existing))), "Original shop order is not sorted"
    rows.sort(key=lambda row: int(row.partition(",")[0]))
    for confetti_id in ("1100006", "1100056"):
        before = [row for row in existing if row.startswith(confetti_id + ",")]
        after = [row for row in rows if row.startswith(confetti_id + ",")]
        assert before == after and len(before) == 1, "Existing Divine Confetti was altered"
    return lines[0] + "".join(rows), 24

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Require patches to be applied already")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    effect_path, shop_path, goods_path = (root / name for name in (
        "SpEffectParam.csv", "ShopLineupParam.csv", "EquipParamGoods.csv"))
    before_effects, before_shop = read(effect_path), read(shop_path)
    patched_effects, edited = patch_effects(before_effects)
    patched_shop, inserted = patch_shop(before_shop, read(goods_path))
    if args.check:
        assert edited == 0 and inserted == 0, (
            f"Patch not fully applied: {edited} effect fields, {inserted} shop rows"
        )
    else:
        if patched_effects != before_effects:
            write(effect_path, patched_effects)
        if patched_shop != before_shop:
            write(shop_path, patched_shop)
    print(f"v1.09 patch check OK: {edited} effect fields changed, {inserted} shop rows added")

if __name__ == "__main__":
    main()
