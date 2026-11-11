# HBT v1.09 local gameplay parameter patches

These v1.09-only edits are implemented by scripts/port_hbt_v109.py and
scripts/port_hbt_v109_salma_thunder.py. Run both locally to apply the
modifications and both with --check to verify them. The main branch
is intentionally untouched.

## Sen Throw
SpEffectParam: soul=0 at IDs 127072-127077. Preserve IDs 127070-127071,
EquipParamWeapon ID 70400, and BehaviorParam_PC wepCost.

## Lazulite Confetti
SpEffectParam IDs 2801-2804: effectEndurance=3600 (one hour); IDs
2801-2803 motionInterval=3601; ID 2804 motionInterval=0. Preserve the
2800 startup and the 2801->2802->2803->2804 cycle, helper ID 104016,
and other effect properties.

## Crow's Bed Memorial Mob materials
ShopLineupParam: rows 1100020-1100031 (standard) and 1100070-1100081
(Promissory Note) provide 12 existing material Goods IDs each, at
1 Sen with unlimited stock. Divine Confetti rows 1100006/1100056 are
preserved at 300/270 Sen.

## Salma Spiritfall
EquipParamGoods ID 3131: consumeResourceItemA 10 -> 0 (free Spirit
Emblems); consumeHpRate 0.85 -> 0 (no activation HP cost).
SpEffectParam ID 3134: effectEndurance 40.1 -> -1 (indefinite).
3133->3134 startup, the 3134->9228 curse, 9228->9283 chain,
Salma's category=0, and Yashariku's separate category=162 are
preserved. Faster curse activation is NOT included: earlier tests
of a redirect in the shared chain did not work in-game.

## Cleaving Thunder Blade prosthetic
The functional prosthetic is EquipParamWeapon ID 75500; ID 755000
is an upgrade/menu row, whereas Goods 9458 is a display-only item.
The old shop substitution was temporary; two new, independent
Crow's Bed Memorial Mob shop entries grant the actual weapon:
- 1100016: Equip 75500, equipType 0, 250 Sen, release flag 6021
- 1100066: Equip 75500, equipType 0, 225 Sen (Promissory Note), flag 6021

Both new rows use eventFlag=-1 and sellQuantity=-1, consistent with
the previously successful direct-weapon merchant substitution test.
The old display-only Goods row 1100015 and Divine Confetti remain
untouched.

## Scope and testing
The combined parameter change is 14 SpEffect cells (13 previous plus
Salma), two EquipParamGoods fields, and 26 additional shop rows
(24 materials plus two Cleaving Thunder entries). No unrelated
parameter rows are intentionally rewritten; original upstream duplicate
shop IDs 1700005/1700055 remain in place.

These CSV source edits require importing into the matching v1.09
Smithbox project and exporting a new game parameter binder. Merchant
visibility, weapon equip behavior, Salma persistence, and interaction
with Yashariku require an actual in-game test.
