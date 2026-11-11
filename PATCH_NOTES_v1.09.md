# v1.09 local gameplay parameter patches

The historical local HBT customizations are applied via scripts/port_hbt_v109.py. Run the script from the repository checkout to patch CSVs, or use --check to verify they are already present. Changes are intended for v1.09 only; main is not updated.

## Sen Throw
SpEffectParam.csv: set soul=0 on IDs 127072-127077. Preserve IDs 127070-127071, EquipParamWeapon ID 70400, and BehaviorParam_PC wepCost.

## Lazulite Confetti
SpEffectParam.csv: set IDs 2801-2804 effectEndurance=3600 (one hour); set IDs 2801-2803 motionInterval=3601; keep ID 2804 motionInterval=0. Preserve 2800's 0.1-second startup, its replaceSpEffectId=2801, all 2801->2802->2803->2804 cycleOccurrenceSpEffectId references, helper ID 104016, and other effect properties. This is the final previously accepted 3600/3601 setting, not the earlier infinite-duration experiment.

## Crow's Bed Memorial Mob
ShopLineupParam.csv: add rows 1100020-1100031 (standard) and 1100070-1100081 (Promissory Note) for material goods IDs 6000, 6010, 6020, 6100, 6200, 6210, 6300, 6310, 6400, 9701, 9721, 9791. Price 1 Sen, sellQuantity=-1, eventFlag=-1, flagId_forRelease=-1, shopType=0, equipType=3. Preserve Divine Confetti shop rows 1100006/1100056 (300/270 Sen).

## Validation and caveats
The patch changes 13 SpEffectParam cells and adds 24 shop rows. Original shop rows are otherwise unchanged, including upstream duplicate IDs 1700005 and 1700055. Temporary tests (Cleaving Thunder Blade shop substitution, Indigo bullet redirection, unresolved curse/Spiritfall compatibility investigations) are excluded.

The CSVs are source data. They still need importing into the matching v1.09 Smithbox project and exporting into the active game parameter binder before their effects can be tested in-game.
