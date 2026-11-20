# Bench session, 2026-11-19

NanoVNA-H, firmware 1.2.50, 50 kHz–900 MHz, 101 points. The port-1 connector is the NanoVNA kit's SMA female–female barrel on the end of cable 1. Each file's metadata records its label, calibration slot, the analyzer's calibration flags, firmware version and time. Times below are local (PST) and come from the file names.

| Time | Files | What was connected |
|---|---|---|
| 11:53 | `thru_115311` | Thru on the slot 2 calibration from Nov 12. It read −0.14 dB at 900 MHz, so I recalibrated. |
| 11:53–12:03 | none | New SOLT and isolation calibration at the cable ends, saved over slot 2. |
| 12:03 | `thru_120355` | Taken with the thru **disconnected** by mistake, so it measures the open-port noise floor (median −72 dB), not a thru. |
| 12:05 | `thru_120501` | Thru check on the new slot 2 calibration. |
| 12:22–12:59 | `pad_<n>db_run1`, `pad_<n>db_run2` | Each pad twice: male end into the barrel, cable 2 on the female end. Between runs the pad was loosened and retightened, not always fully removed. |
| 12:43, 12:51, 13:02 | `thru_124329`, `thru_125148`, `thru_130257` | Thru checks between pads. The barrel on cable 1 loosened slightly a few times while pads were unscrewed; these checks stayed within 0.09 dB up to 676 MHz. |
| 13:03, 13:04 | `thru_slot0_130357`, `thru_slot0_130448` | Thru on the factory calibration (slot 0), reconnected between the two runs. |
| before 16:45 | none | 10 dB pad screwed onto cable 2, its male end becoming port 2. Full recalibration with the pad in place, saved to slot 3. |
| 16:45–17:22 | `pad_<n>db_padded_10db_run1`, `..._run2` | 1, 2, 3, 6 and 20 dB pads, two runs each, with the 10 dB pad on port 2. |
| 17:38 | `thru_slot3_173825` | Taken after the 10 dB pad was removed, so it is **not** a padded thru check: slot 3's calibration expects that pad, and the thru reads its loss inverted (about +9.9 dB). It matches the slot 2 measurement of the 10 dB pad within 0.07 dB up to 676 MHz. |
| 17:38 | `thru_slot2_173853` | Thru check on slot 2 after the experiment. |
| 17:53, 17:58 | `vlf120_run1`, `vlf120_run2` | Mini-Circuits VLF-120+ low-pass filter on slot 2. |
